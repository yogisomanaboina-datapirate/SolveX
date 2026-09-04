from core.logging import logger
from agents.medication.scheduler_agent import medication_scheduler_agent
from agents.medication.schemas import MedicationScheduleRequest, MedicationScheduleResponse


def run_scheduler_workflow(request: MedicationScheduleRequest) -> MedicationScheduleResponse:
    """
    Execute Medication & Tablet Scheduler Workflow.
    Calculates exact intake reminder times, detects conflicts, and generates notification payloads.
    """
    logger.info("Executing Medication & Tablet Scheduler Workflow...")
    response = medication_scheduler_agent.generate_schedule(request)
    logger.info(
        f"Medication Scheduler Completed -> Generated {len(response.scheduled_reminders)} reminders. "
        f"Conflicts: {response.has_conflicts}"
    )
    return response
