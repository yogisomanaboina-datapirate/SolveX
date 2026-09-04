from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.errors import register_error_handlers
from core.logging import logger
from core.schemas import HealthResponse
from agents.ambulance.schemas import TriageRequest, TriageResponse
from workflows.emergency import run_triage_workflow


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


@app.post("/agent/triage", response_model=TriageResponse, tags=["Emergency"])
async def triage_endpoint(request: TriageRequest):
    """
    Emergency Triage Assessment Endpoint.
    Analyzes patient symptoms and vitals to determine urgency, severity, required medical specialty, and recommended coordination action.
    """
    return run_triage_workflow(request)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.agent_host,
        port=settings.agent_port,
        reload=(settings.environment == "development")
    )
