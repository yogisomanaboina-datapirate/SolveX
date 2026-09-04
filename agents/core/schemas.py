from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check endpoint response schema."""
    status: str = Field(default="healthy", description="Status of the agent service")
    service: str = Field(default="lifelink-agent", description="Service identifier")
    featherless_configured: bool = Field(default=False, description="Whether Featherless API key is loaded")


class WorkflowStepLog(BaseModel):
    """Log entry for an observable workflow execution step."""
    step_number: int
    step_name: str
    timestamp: str
    status: str = "completed"
    details: Optional[Dict[str, Any]] = None


class BaseDecisionResponse(BaseModel):
    """
    Standardized base response schema for all major Agent decisions.
    Safety constraint: confidence represents AI decision clarity, NOT medical diagnostic certainty.
    """
    decision: str = Field(description="Primary summary decision reached by the agent")
    reasoning: str = Field(description="Step-by-step rationale explaining how the decision was reached")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score in the coordination recommendation (0.0 to 1.0)"
    )
    next_action: str = Field(description="Recommended next workflow or backend execution action")
    data_used: List[Any] = Field(default_factory=list, description="Summary of tools, datasets, or inputs evaluated")
    workflow_steps: List[WorkflowStepLog] = Field(
        default_factory=list,
        description="Chronological step execution trace for observability"
    )
    disclaimer: str = Field(
        default="LifeLink AI is a healthcare coordination assistant and does not provide medical diagnoses or prescriptions.",
        description="Mandatory medical safety disclaimer"
    )
