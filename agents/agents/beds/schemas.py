from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class BedInventory(BaseModel):
    """Hospital bed capacity and occupancy inventory."""
    hospital_id: str = Field(description="Hospital unique ID", examples=["HOSP-001"])
    hospital_name: str = Field(description="Hospital facility name", examples=["Apollo Emergency Hospital Jubilee Hills"])
    icu_beds_total: int = Field(default=10, ge=0)
    icu_beds_occupied: int = Field(default=6, ge=0)
    er_beds_total: int = Field(default=15, ge=0)
    er_beds_occupied: int = Field(default=10, ge=0)
    general_beds_total: int = Field(default=50, ge=0)
    general_beds_occupied: int = Field(default=35, ge=0)
    pediatric_beds_total: int = Field(default=10, ge=0)
    pediatric_beds_occupied: int = Field(default=4, ge=0)
    surgical_beds_total: int = Field(default=10, ge=0)
    surgical_beds_occupied: int = Field(default=5, ge=0)
    specialties: List[str] = Field(
        default_factory=lambda: ["CARDIOLOGY", "NEUROLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"]
    )


class BedOptimizationRequest(BaseModel):
    """Bed optimization and scheduling recommendation request payload."""
    patient_id: Optional[str] = Field(default=None, description="Patient reference ID")
    required_bed_type: str = Field(
        default="ICU",
        description="Required bed category: ICU, ER, GENERAL, PEDIATRIC, SURGICAL",
        examples=["ICU"]
    )
    required_specialty: str = Field(
        default="CARDIOLOGY",
        description="Medical specialty requirement",
        examples=["CARDIOLOGY"]
    )
    patient_urgency: str = Field(
        default="HIGH",
        description="Clinical urgency: CRITICAL, HIGH, MEDIUM, LOW",
        examples=["HIGH"]
    )
    target_hospital_id: Optional[str] = Field(default=None, description="Preferred target hospital ID if specified")
    available_hospital_inventories: List[BedInventory] = Field(
        default_factory=list,
        description="Backend-supplied hospital bed inventories dataset"
    )
    expected_surge_factor: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Demand multiplier for predictive optimization (1.0 = normal, 1.5 = 50% surge)"
    )


class HospitalBedAllocation(BaseModel):
    """Bed allocation recommendation for a specific hospital."""
    recommended_hospital_id: str
    recommended_hospital_name: str
    allocated_bed_type: str
    beds_available_before_allocation: int
    projected_occupancy_after_allocation_pct: float
    allocation_score: float
    allocation_rationale: str


class BedOptimizationResponse(BaseDecisionResponse):
    """Structured Bed Optimization AI Decision Output."""
    decision: str = Field(
        default="Recommend allocating bed based on inventory and urgency.",
        validation_alias=AliasChoices("decision", "summary"),
        description="Summary bed allocation recommendation"
    )
    reasoning: str = Field(
        default="Bed allocation optimized based on capacity and urgency.",
        validation_alias=AliasChoices("reasoning", "rationale"),
        description="Detailed predictive and clinical reasoning"
    )
    confidence: float = Field(default=0.92, description="Recommendation confidence score")
    recommended_allocation: Optional[HospitalBedAllocation] = Field(
        default=None,
        description="Optimal hospital bed allocation recommendation"
    )
    alternative_allocations: List[HospitalBedAllocation] = Field(
        default_factory=list,
        description="Ranked alternative hospital bed options"
    )
    surge_warning: Optional[str] = Field(default=None, description="Warning if capacity is near critical threshold")
    recommended_action: str = Field(
        default="RESERVE_BED_IN_BACKEND",
        description="Recommended action for Backend execution"
    )
