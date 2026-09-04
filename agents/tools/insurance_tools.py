from typing import Any, Dict, List, Optional
from agents.insurance.schemas import ClaimMatchResult, ExistingClaimData, PolicyInfo


def inspect_and_match_claims(
    user_request: str,
    policy_info: Optional[PolicyInfo],
    existing_claims: List[ExistingClaimData]
) -> ClaimMatchResult:
    """
    Deterministic Tool: Match user query against backend-supplied existing claims.
    CRITICAL CONSTRAINT: The LLM is NOT the source of truth for whether a claim exists.
    This tool strictly inspects backend records to prevent claim hallucination.
    """
    if not existing_claims:
        return ClaimMatchResult(
            claim_exists=False,
            matched_claim_id=None,
            matched_claim_status=None,
            matched_claim_data=None,
            match_confidence=1.0,
            match_explanation="Backend claim registry contains zero existing claims for this user. No claim found."
        )

    req_lower = user_request.lower()
    target_policy_id = policy_info.policy_id.lower() if policy_info else ""

    best_match: Optional[ExistingClaimData] = None
    highest_score = 0.0

    for claim in existing_claims:
        score = 0.0

        # Exact claim ID match in prompt
        if claim.claim_id.lower() in req_lower:
            score += 0.9

        # Policy ID match
        if claim.policy_id.lower() == target_policy_id or claim.policy_id.lower() in req_lower:
            score += 0.4

        # Hospital name match
        if claim.hospital_name.lower() in req_lower:
            score += 0.3

        # Treatment type match
        if claim.treatment_type.lower() in req_lower:
            score += 0.2

        if score > highest_score:
            highest_score = score
            best_match = claim

    if best_match and highest_score >= 0.4:
        return ClaimMatchResult(
            claim_exists=True,
            matched_claim_id=best_match.claim_id,
            matched_claim_status=best_match.status,
            matched_claim_data=best_match,
            match_confidence=min(highest_score, 0.99),
            match_explanation=f"Found existing claim '{best_match.claim_id}' under policy '{best_match.policy_id}' at {best_match.hospital_name} with status '{best_match.status}'."
        )
    else:
        # Fallback to the first existing claim under the same policy if present
        policy_claims = [c for c in existing_claims if policy_info and c.policy_id == policy_info.policy_id]
        if policy_claims:
            matched = policy_claims[0]
            return ClaimMatchResult(
                claim_exists=True,
                matched_claim_id=matched.claim_id,
                matched_claim_status=matched.status,
                matched_claim_data=matched,
                match_confidence=0.85,
                match_explanation=f"Identified existing active claim '{matched.claim_id}' under policy '{matched.policy_id}'."
            )

        return ClaimMatchResult(
            claim_exists=False,
            matched_claim_id=None,
            matched_claim_status=None,
            matched_claim_data=None,
            match_confidence=0.9,
            match_explanation="No matching existing claim records found in backend database for the provided query."
        )


def calculate_coverage_estimate(
    policy_info: Optional[PolicyInfo],
    estimated_bill_inr: float,
    hospital_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deterministic Tool: Calculate financial coverage estimation based on policy terms.
    """
    if not policy_info:
        return {
            "estimated_bill_inr": estimated_bill_inr,
            "policy_provided": False,
            "message": "No policy details provided for coverage calculation."
        }

    is_network = False
    if hospital_name:
        is_network = any(
            net.lower() in hospital_name.lower() or hospital_name.lower() in net.lower()
            for net in policy_info.network_hospitals
        )

    copay_rate = policy_info.copay_percentage / 100.0
    patient_copay_amount = round(estimated_bill_inr * copay_rate, 2)
    insurer_payable_amount = round(estimated_bill_inr * (1.0 - copay_rate), 2)

    # Cap by max policy coverage limit
    capped_insurer_payment = min(insurer_payable_amount, policy_info.coverage_limit_inr)

    return {
        "policy_id": policy_info.policy_id,
        "provider_name": policy_info.provider_name,
        "estimated_bill_inr": estimated_bill_inr,
        "is_network_cashless_hospital": is_network,
        "policy_limit_inr": policy_info.coverage_limit_inr,
        "copay_percentage": policy_info.copay_percentage,
        "estimated_patient_copay_inr": patient_copay_amount,
        "estimated_insurer_payable_inr": capped_insurer_payment,
        "pre_authorization_required": policy_info.pre_authorization_required,
        "claim_mode": "CASHLESS_NETWORK" if is_network else "REIMBURSEMENT_CLAIM"
    }
