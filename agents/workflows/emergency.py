from core.logging import logger, log_workflow_event
from agents.ambulance.schemas import TriageRequest, TriageResponse
from agents.ambulance.triage import triage_agent


def run_triage_workflow(request: TriageRequest) -> TriageResponse:
    """
    Execute standalone Triage workflow step.
    Receives user emergency symptoms/vitals and produces structured triage assessment.
    """
    logger.info("Executing Emergency Triage Workflow...")
    response = triage_agent.evaluate_triage(request)
    logger.info(f"Triage Workflow Completed -> Urgency: {response.urgency}, Specialty: {response.required_specialty}")
    return response
