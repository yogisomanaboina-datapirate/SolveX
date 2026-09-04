from datetime import datetime, timezone
from typing import Optional
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from tools.insurance_tools import calculate_coverage_estimate, inspect_and_match_claims
from agents.insurance.schemas import (
    ClaimAnalysisRequest,
    ClaimAnalysisResponse,
)

INSURANCE_AGENT_SYSTEM_PROMPT = """You are LifeLink AI Insurance & Claims Coordination Agent.

YOUR MANDATE:
1. Interpret the user's insurance inquiry.
2. Analyze the supplied claim inspection data and policy coverage terms.
3. Formulate transparent, helpful insurance coordination guidance.
4. Output ONLY a valid JSON object matching these exact keys:
{
  "assistance_type": "EXISTING_CLAIM_STATUS" | "NEW_CLAIM_FILING_GUIDANCE" | "COVERAGE_VERIFICATION" | "PRE_AUTH_ASSISTANCE",
  "decision": "Summary decision regarding insurance claim / assistance status",
  "reasoning": "Detailed rationale explaining policy coverage, matched claim status, and financial breakdown",
  "recommended_next_step": "Actionable step for the user or backend workflow execution",
  "confidence": 0.95
}

CRITICAL RULES:
- Do NOT hallucinate that a claim exists if the backend match indicates no claim exists.
- State clearly whether cashless pre-authorization or reimbursement is applicable.
"""


class InsuranceClaimsAgent:
    """
    AI Agent responsible for insurance query analysis, claim matching, and policy assistance.
    """

    def analyze_claim_request(self, request: ClaimAnalysisRequest) -> ClaimAnalysisResponse:
        """
        Analyze user insurance inquiry against backend claims source of truth and policy terms.
        """
        logger.info(f"InsuranceClaimsAgent analyzing inquiry: '{request.user_request}'")
        log_workflow_event(
            workflow_name="Insurance Claims",
            step_number=1,
            step_name="Received Insurance Inquiry",
            details={"user_request": request.user_request}
        )

        steps = [
            WorkflowStepLog(
                step_number=1,
                step_name="Received Insurance Inquiry",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"query": request.user_request}
            )
        ]

        # STEP 1: Deterministic Tool — Inspect backend claims database (Source of Truth)
        match_result = inspect_and_match_claims(
            user_request=request.user_request,
            policy_info=request.policy_info,
            existing_claims=request.existing_claims
        )

        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Inspected Backend Claims Registry",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={
                    "claim_exists": match_result.claim_exists,
                    "matched_claim_id": match_result.matched_claim_id,
                    "matched_status": match_result.matched_claim_status
                }
            )
        )

        # STEP 2: Deterministic Tool — Coverage Estimation if bill amount available
        coverage_calc: Optional[dict] = None
        estimated_bill = 0.0
        if request.document_details and "estimated_bill_inr" in request.document_details:
            estimated_bill = float(request.document_details["estimated_bill_inr"])
        elif request.policy_info and "cost" in request.user_request.lower():
            estimated_bill = 100000.0  # Default evaluation bill for query

        if estimated_bill > 0 and request.policy_info:
            hospital_name = None
            if match_result.matched_claim_data:
                hospital_name = match_result.matched_claim_data.hospital_name
            coverage_calc = calculate_coverage_estimate(
                policy_info=request.policy_info,
                estimated_bill_inr=estimated_bill,
                hospital_name=hospital_name
            )

        # STEP 3: Determine assistance type
        if match_result.claim_exists:
            assistance_type = "EXISTING_CLAIM_STATUS"
            next_step = f"Track claim '{match_result.matched_claim_id}' status updates via Backend notification."
        elif request.policy_info and request.policy_info.pre_authorization_required:
            assistance_type = "PRE_AUTH_ASSISTANCE"
            next_step = "Submit Pre-Authorization form with TPA hospital desk for cashless approval."
        else:
            assistance_type = "NEW_CLAIM_FILING_GUIDANCE"
            next_step = "Upload discharge summary and hospital bills to initiate claim submission."

        # STEP 4: AI Reasoning over tool output
        decision = f"Insurance analysis completed for policy '{request.policy_info.policy_id if request.policy_info else 'N/A'}'."
        reasoning = match_result.match_explanation
        confidence = match_result.match_confidence

        if featherless_client.is_available:
            try:
                prompt = (
                    f"User Request: {request.user_request}\n"
                    f"Claim Inspection Result: Claim Exists = {match_result.claim_exists}, Matched ID = {match_result.matched_claim_id}, Status = {match_result.matched_claim_status}\n"
                    f"Match Explanation: {match_result.match_explanation}\n"
                    f"Policy Details: {request.policy_info.model_dump() if request.policy_info else 'Not provided'}\n"
                    f"Coverage Calculation: {coverage_calc or 'Not applicable'}\n"
                )

                ai_res = featherless_client.generate_structured_json(
                    prompt=prompt,
                    system_prompt=INSURANCE_AGENT_SYSTEM_PROMPT,
                    response_model=ClaimAnalysisResponse
                )

                decision = ai_res.decision
                reasoning = ai_res.reasoning
                assistance_type = ai_res.assistance_type
                next_step = ai_res.recommended_next_step
                confidence = ai_res.confidence

                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Completed Featherless AI Insurance Analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"assistance_type": assistance_type, "model": featherless_client.model}
                    )
                )

            except Exception as e:
                logger.warning(f"Featherless AI insurance analysis call failed, using rule-based output: {e}")
                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Completed Rule-Based Insurance Analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"assistance_type": assistance_type}
                    )
                )
        else:
            steps.append(
                WorkflowStepLog(
                    step_number=3,
                    step_name="Completed Rule-Based Insurance Analysis",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="completed",
                    details={"assistance_type": assistance_type}
                )
            )

        log_workflow_event("Insurance Claims", 4, "Generated Insurance Response", {"claim_exists": match_result.claim_exists})

        return ClaimAnalysisResponse(
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action=next_step,
            data_used=[
                {"backend_claim_matched": match_result.claim_exists, "matched_id": match_result.matched_claim_id},
                {"policy_id": request.policy_info.policy_id if request.policy_info else None}
            ],
            workflow_steps=steps,
            claim_exists=match_result.claim_exists,
            matched_claim_id=match_result.matched_claim_id,
            matched_claim_status=match_result.matched_claim_status,
            assistance_type=assistance_type,
            coverage_estimation=coverage_calc,
            recommended_next_step=next_step
        )


insurance_claims_agent = InsuranceClaimsAgent()
