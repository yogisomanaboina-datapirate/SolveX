from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.errors import register_error_handlers
from core.logging import logger
from core.schemas import HealthResponse
from core.featherless import featherless_client
from agents.ambulance.schemas import (
    EmergencyWorkflowRequest,
    EmergencyWorkflowResponse,
    TriageRequest,
    TriageResponse,
)
from agents.beds.schemas import BedOptimizationRequest, BedOptimizationResponse
from agents.insurance.schemas import ClaimAnalysisRequest, ClaimAnalysisResponse
from agents.medication.schemas import MedicationScheduleRequest, MedicationScheduleResponse
from workflows.beds import run_bed_optimizer_workflow
from workflows.emergency import run_full_emergency_workflow, run_triage_workflow
from workflows.insurance import run_claims_workflow
from workflows.medication import run_scheduler_workflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting LifeLink AI Agent Service...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Featherless Configured: {settings.is_featherless_configured}")
    yield
    logger.info("Shutting down LifeLink AI Agent Service...")


app = FastAPI(
    title="LifeLink AI Agent",
    description="Autonomous AI Agent & Workflow Engine for Healthcare Coordination",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom error handling
register_error_handlers(app)


@app.get("/", tags=["General"])
async def root():
    """Root endpoint redirecting to service info."""
    return {
        "service": "lifelink-agent",
        "status": "online",
        "health_check": "/health",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Service health check endpoint.
    Expected output: {"status": "healthy", "service": "lifelink-agent", "featherless_configured": bool}
    """
    return HealthResponse(
        status="healthy",
        service="lifelink-agent",
        featherless_configured=settings.is_featherless_configured
    )


@app.get("/agent/test-featherless", tags=["Development"])
async def test_featherless_endpoint():
    """
    Development-only Featherless API connectivity test endpoint.
    Performs 1 real chat completion call to Featherless API when credentials are set.
    """
    return featherless_client.test_connection()


@app.post("/agent/triage", response_model=TriageResponse, tags=["Emergency"])
async def triage_endpoint(request: TriageRequest):
    """
    Emergency Triage Assessment Endpoint.
    Analyzes patient symptoms and vitals to determine urgency, severity, required medical specialty, and recommended coordination action.
    """
    return run_triage_workflow(request)


@app.post("/agent/emergency", response_model=EmergencyWorkflowResponse, tags=["Emergency"])
async def emergency_workflow_endpoint(request: EmergencyWorkflowRequest):
    """
    Full End-to-End Autonomous Emergency Response Multi-Agent Workflow Endpoint.
    Executes Triage -> Hospital Matching -> Ambulance Dispatch -> Hospital Notification.
    """
    return run_full_emergency_workflow(request)


@app.post("/agent/claims", response_model=ClaimAnalysisResponse, tags=["Insurance"])
async def claims_endpoint(request: ClaimAnalysisRequest):
    """
    Insurance Claim & Policy Assistance Endpoint.
    Analyzes insurance queries, verifies backend claim records, calculates coverage estimates, and provides guided claim assistance.
    """
    return run_claims_workflow(request)


@app.post("/agent/bed-optimizer", response_model=BedOptimizationResponse, tags=["Beds"])
async def bed_optimizer_endpoint(request: BedOptimizationRequest):
    """
    Bed Optimization & Capacity Scheduling Endpoint.
    Evaluates real-time hospital bed inventories, predictive capacity surges, and specialty alignment to recommend optimal bed allocations.
    """
    return run_bed_optimizer_workflow(request)


@app.post("/agent/scheduler", response_model=MedicationScheduleResponse, tags=["Medication"])
async def scheduler_endpoint(request: MedicationScheduleRequest):
    """
    Medication & Tablet Reminder Scheduler Endpoint.
    Parses doctor-prescribed medication instructions, generates daily intake reminder times, detects conflicts, and outputs notification payloads for Backend scheduling.
    """
    return run_scheduler_workflow(request)








if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.agent_host,
        port=settings.agent_port,
        reload=(settings.environment == "development")
    )
