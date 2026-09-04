from core.logging import logger
from agents.insurance.claims_agent import insurance_claims_agent
from agents.insurance.schemas import ClaimAnalysisRequest, ClaimAnalysisResponse


def run_claims_workflow(request: ClaimAnalysisRequest) -> ClaimAnalysisResponse:
    """
    Execute Insurance Claims Assistance Workflow.
    Receives user inquiry, policy details, and backend claims source of truth.
    Produces structured claim analysis, status matching, and coverage guidance.
    """
    logger.info("Executing Insurance Claims Assistance Workflow...")
    response = insurance_claims_agent.analyze_claim_request(request)
    logger.info(f"Claims Workflow Completed -> Claim Exists: {response.claim_exists}, Matched ID: {response.matched_claim_id}")
    return response
