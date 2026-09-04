from core.logging import logger
from agents.beds.bed_agent import bed_optimizer_agent
from agents.beds.schemas import BedOptimizationRequest, BedOptimizationResponse


def run_bed_optimizer_workflow(request: BedOptimizationRequest) -> BedOptimizationResponse:
    """
    Execute Bed Optimization & Capacity Scheduling Workflow.
    Evaluates real-time hospital bed inventories, predictive capacity surges, and specialty alignment.
    Produces structured bed allocation decision.
    """
    logger.info("Executing Bed Optimization & Scheduling Workflow...")
    response = bed_optimizer_agent.optimize_bed_allocation(request)
    logger.info(
        f"Bed Optimization Completed -> Hospital: {response.recommended_allocation.recommended_hospital_name}, "
        f"Beds Available: {response.recommended_allocation.beds_available_before_allocation}"
    )
    return response
