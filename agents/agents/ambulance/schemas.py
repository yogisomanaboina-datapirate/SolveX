from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from core.schemas import BaseDecisionResponse


class TriageRequest(BaseModel):
    """Emergency triage evaluation request payload."""
    symptoms: str = Field(
        description="Patient reported emergency symptoms or chief complaint",
        examples=["Severe chest pain radiating to left arm and shortness of breath"]
    )
    patient_age: Optional[int] = Field(default=None, ge=0, le=120, description="Patient age in years")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    vital_signs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Patient vital signs if available (e.g., HR, BP, SpO2)",
        examples=[{"heart_rate": 115, "blood_pressure": "145/95", "spo2": 94}]
    )
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Patient current GPS coordinates or address",
        examples=[{"lat": 17.4486, "lng": 78.3908, "address": "SNIST, Hyderabad"}]
    )


class TriageResponse(BaseDecisionResponse):
    """Emergency triage evaluation structured AI output."""
    urgency: str = Field(
        description="Triage urgency level: CRITICAL, HIGH, MEDIUM, LOW",
        examples=["HIGH"]
    )
    severity: str = Field(
        description="Clinical severity rating: CRITICAL, HIGH, MODERATE, LOW",
        examples=["HIGH"]
    )
    category: str = Field(
        description="Emergency classification category (e.g. CARDIAC_EMERGENCY, TRAUMA, RESPIRATORY)",
        examples=["CARDIAC_EMERGENCY"]
    )
    required_specialty: str = Field(
        description="Required medical department/specialty at destination hospital",
        examples=["CARDIOLOGY"]
    )
    recommended_action: str = Field(
        description="Immediate coordination action (e.g., IMMEDIATE_AMBULANCE_DISPATCH)",
        examples=["IMMEDIATE_AMBULANCE_DISPATCH"]
    )
