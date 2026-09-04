from datetime import datetime, timezone
from typing import List, Optional
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from tools.bed_tools import evaluate_and_rank_bed_allocations
from agents.beds.schemas import (
    BedInventory,
    BedOptimizationRequest,
    BedOptimizationResponse,
    HospitalBedAllocation,
)

DEFAULT_BED_INVENTORIES = [
    BedInventory(
        hospital_id="HOSP-01",
        hospital_name="Apollo Emergency Hospital Jubilee Hills",
        icu_beds_total=10,
        icu_beds_occupied=6,
        er_beds_total=15,
        er_beds_occupied=8,
        general_beds_total=50,
        general_beds_occupied=30,
        specialties=["CARDIOLOGY", "NEUROLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"]
    ),
    BedInventory(
        hospital_id="HOSP-02",
        hospital_name="KIMS Trauma & Heart Institute Secunderabad",
        icu_beds_total=8,
        icu_beds_occupied=7,
        er_beds_total=12,
        er_beds_occupied=10,
        general_beds_total=40,
        general_beds_occupied=32,
        specialties=["CARDIOLOGY", "PULMONOLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"]
    ),
    BedInventory(
        hospital_id="HOSP-03",
        hospital_name="Yashoda Care Hospital Gachibowli",
        icu_beds_total=6,
        icu_beds_occupied=6,  # 0 available
        er_beds_total=10,
        er_beds_occupied=7,
        general_beds_total=35,
        general_beds_occupied=20,
        specialties=["NEUROLOGY", "PULMONOLOGY", "GENERAL_EMERGENCY"]
    )
]

BED_OPTIMIZER_SYSTEM_PROMPT = """You are LifeLink AI Bed Optimization & Capacity Agent.

YOUR MANDATE:
1. Evaluate candidate hospital bed allocation options for incoming emergency admissions.
2. Consider specialty capabilities, bed type availability, and predictive capacity surge trends.
3. Output ONLY a valid JSON object matching these exact keys:
{
  "decision": "Summary of recommended bed allocation decision",
  "reasoning": "Detailed predictive capacity and clinical allocation reasoning",
  "next_action": "RESERVE_BED_IN_BACKEND" | "INITIATE_PATIENT_TRANSFER",
  "recommended_action": "RESERVE_BED_IN_BACKEND" | "INITIATE_PATIENT_TRANSFER",
  "confidence": 0.94
}
"""


class BedOptimizerAgent:
    """
    AI Agent responsible for evaluating bed inventory, predicting surge capacity, and optimizing bed allocation.
    """

    def optimize_bed_allocation(self, request: BedOptimizationRequest) -> BedOptimizationResponse:
        """
        Evaluate hospital bed inventories and recommend optimal allocation.
        """
        logger.info(f"BedOptimizerAgent optimizing allocation for {request.required_bed_type} bed ({request.required_specialty})")
        log_workflow_event(
            workflow_name="Bed Optimization",
            step_number=1,
            step_name="Received Bed Allocation Request",
            details={"bed_type": request.required_bed_type, "specialty": request.required_specialty, "surge_factor": request.expected_surge_factor}
        )

        steps = [
            WorkflowStepLog(
                step_number=1,
                step_name="Received Bed Allocation Request",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"bed_type": request.required_bed_type, "specialty": request.required_specialty}
            )
        ]

        inventories = request.available_hospital_inventories or DEFAULT_BED_INVENTORIES

        # STEP 1: Deterministic Tool — Evaluate & rank allocations
        ranked_allocations = evaluate_and_rank_bed_allocations(
            inventories=inventories,
            required_bed_type=request.required_bed_type,
            required_specialty=request.required_specialty,
            patient_urgency=request.patient_urgency,
            surge_factor=request.expected_surge_factor
        )

        top_allocation = ranked_allocations[0]
        alternatives = ranked_allocations[1:]

        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Evaluated Bed Capacity & Ranked Allocations",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={
                    "recommended_hospital": top_allocation.recommended_hospital_name,
                    "available_beds": top_allocation.beds_available_before_allocation,
                    "projected_occupancy_pct": top_allocation.projected_occupancy_after_allocation_pct
                }
            )
        )

        # STEP 2: Surge Warning Generation
        surge_warning: Optional[str] = None
        if top_allocation.projected_occupancy_after_allocation_pct >= 85.0:
            surge_warning = (
                f"HIGH CAPACITY ALERT: {top_allocation.recommended_hospital_name} {request.required_bed_type} occupancy "
                f"is projected at {top_allocation.projected_occupancy_after_allocation_pct}%. Pre-allocating overflow capacity."
            )
        elif request.expected_surge_factor > 1.2:
            surge_warning = f"SURGE DEMAND MULTIPLIER ({request.expected_surge_factor}x) IN EFFECT: Monitoring secondary hospital reserves."

        # STEP 3: AI Reasoning over tool results
        decision = (
            f"Recommend allocating {request.required_bed_type} bed at {top_allocation.recommended_hospital_name} "
            f"({top_allocation.beds_available_before_allocation} beds available)."
        )
        reasoning = top_allocation.allocation_rationale
        recommended_action = "RESERVE_BED_IN_BACKEND"
        confidence = 0.92

        if featherless_client.is_available:
            try:
                summary_text = "\n".join([
                    f"- {a.recommended_hospital_name}: {a.beds_available_before_allocation} {a.allocated_bed_type} available, "
                    f"Post-Allocation Occupancy: {a.projected_occupancy_after_allocation_pct}%, Score: {a.allocation_score}"
                    for a in ranked_allocations
                ])
                prompt = (
                    f"Patient Urgency: {request.patient_urgency}, Required Bed: {request.required_bed_type}, Required Specialty: {request.required_specialty}\n"
                    f"Surge Multiplier: {request.expected_surge_factor}x\n"
                    f"Ranked Hospital Bed Options:\n{summary_text}\n\n"
                    f"Selected Recommendation: {top_allocation.recommended_hospital_name}\n"
                    "Explain why this bed allocation optimizes capacity and patient safety."
                )

                ai_res = featherless_client.generate_structured_json(
                    prompt=prompt,
                    system_prompt=BED_OPTIMIZER_SYSTEM_PROMPT,
                    response_model=BedOptimizationResponse
                )

                decision = ai_res.decision
                reasoning = ai_res.reasoning
                recommended_action = ai_res.recommended_action
                confidence = ai_res.confidence

                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Completed Featherless AI Bed Optimization Analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"recommended_hospital": top_allocation.recommended_hospital_name, "model": featherless_client.model}
                    )
                )

            except Exception as e:
                logger.warning(f"Featherless AI bed optimizer call failed, using rule-based reasoning: {e}")
                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Completed Deterministic Bed Optimization Analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"recommended_hospital": top_allocation.recommended_hospital_name}
                    )
                )
        else:
            steps.append(
                WorkflowStepLog(
                    step_number=3,
                    step_name="Completed Deterministic Bed Optimization Analysis",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="completed",
                    details={"recommended_hospital": top_allocation.recommended_hospital_name}
                )
            )

        log_workflow_event(
            workflow_name="Bed Optimization",
            step_number=4,
            step_name="Bed Allocation Recommendation Finalized",
            details={"hospital": top_allocation.recommended_hospital_name, "bed_type": request.required_bed_type}
        )

        return BedOptimizationResponse(
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action=recommended_action,
            recommended_allocation=top_allocation,
            alternative_allocations=alternatives,
            surge_warning=surge_warning,
            recommended_action=recommended_action,
            data_used=[
                {"total_inventories_evaluated": len(inventories)},
                {"selected_hospital": top_allocation.recommended_hospital_name, "beds_available": top_allocation.beds_available_before_allocation}
            ],
            workflow_steps=steps
        )


bed_optimizer_agent = BedOptimizerAgent()
