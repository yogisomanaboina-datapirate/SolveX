from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class LocationSchema(BaseModel):
    """Geographic location schema."""
    lat: float = Field(default=17.4486, description="Latitude coordinate")
    lng: float = Field(default=78.3908, description="Longitude coordinate")
    address: Optional[str] = Field(default="Hyderabad, Telangana", description="Readable street/landmark address")


class HospitalInfo(BaseModel):
    """Hospital facility information supplied by Backend/dataset."""
    id: str = Field(description="Hospital unique ID", examples=["HOSP-001"])
    name: str = Field(description="Hospital facility name", examples=["Apollo Hospitals Jubilee Hills"])
    location: LocationSchema = Field(default_factory=LocationSchema)
    specialties: List[str] = Field(
        default_factory=lambda: ["CARDIOLOGY", "NEUROLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"],
        description="Supported medical specialties"
    )
    icu_beds_available: int = Field(default=5, ge=0, description="Available ICU bed capacity")
    er_beds_available: int = Field(default=10, ge=0, description="Available ER bed capacity")
    general_beds_available: int = Field(default=25, ge=0, description="Available General bed capacity")
    trauma_center_level: Optional[int] = Field(default=1, description="Trauma center accreditation level (1-3)")


class AmbulanceInfo(BaseModel):
    """Ambulance unit information supplied by Backend/dataset."""
    id: str = Field(description="Ambulance unique ID", examples=["AMB-101"])
    vehicle_number: str = Field(description="Vehicle license registration", examples=["TS-09-AMB-1001"])
    type: str = Field(default="ALS", description="Ambulance type: ALS (Advanced Life Support), BLS, CRITICAL_CARE")
    status: str = Field(default="AVAILABLE", description="Availability status: AVAILABLE, BUSY, MAINTENANCE")
    current_location: LocationSchema = Field(default_factory=LocationSchema)
    paramedic_level: str = Field(default="ADVANCED", description="Paramedic qualification level")


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
    location: Optional[LocationSchema] = Field(
        default=None,
        description="Patient current GPS coordinates or address"
    )


class TriageResponse(BaseDecisionResponse):
    """Emergency triage evaluation structured AI output."""
    urgency: str = Field(description="Triage urgency level: CRITICAL, HIGH, MEDIUM, LOW", examples=["HIGH"])
    severity: str = Field(description="Clinical severity rating: CRITICAL, HIGH, MODERATE, LOW", examples=["HIGH"])
    category: str = Field(description="Emergency classification category", examples=["CARDIAC_EMERGENCY"])
    required_specialty: str = Field(description="Required medical department at hospital", examples=["CARDIOLOGY"])
    recommended_action: str = Field(description="Immediate coordination action", examples=["IMMEDIATE_AMBULANCE_DISPATCH"])


class HospitalSelection(BaseModel):
    """Selected hospital matching recommendation details."""
    hospital_id: str
    hospital_name: str
    distance_km: float
    estimated_eta_minutes: int
    icu_beds_available: int
    er_beds_available: int
    suitability_score: float
    suitability_reason: str


class SimulatedAmbulanceDispatch(BaseModel):
    """Simulated ambulance dispatch record details."""
    dispatch_id: str
    ambulance_id: str
    vehicle_number: str
    ambulance_type: str
    hospital_id: str
    hospital_name: str
    estimated_patient_eta_minutes: int
    dispatch_status: str = "SIMULATED_DISPATCHED"
    timestamp: str


class HospitalNotificationPayload(BaseModel):
    """Emergency alert notification payload generated for target hospital ER."""
    notification_id: str
    target_hospital_id: str
    target_hospital_name: str
    patient_triage_category: str
    patient_urgency: str
    required_specialty: str
    assigned_ambulance_id: str
    estimated_arrival_minutes: int
    alert_message: str
    timestamp: str


class EmergencyWorkflowRequest(BaseModel):
    """Complete End-to-End Emergency Multi-Agent Workflow Request Payload."""
    symptoms: str = Field(description="Patient emergency symptoms or chief complaint")
    patient_age: Optional[int] = Field(default=None, description="Patient age")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    vital_signs: Optional[Dict[str, Any]] = Field(default=None, description="Patient vital signs")
    patient_location: LocationSchema = Field(default_factory=LocationSchema)
    candidate_hospitals: Optional[List[HospitalInfo]] = Field(
        default=None,
        description="Optional list of candidate hospitals provided by Backend. If omitted, default dataset is used."
    )
    available_ambulances: Optional[List[AmbulanceInfo]] = Field(
        default=None,
        description="Optional list of candidate ambulances provided by Backend. If omitted, default dataset is used."
    )


class EmergencyWorkflowResponse(BaseDecisionResponse):
    """Complete End-to-End Emergency Multi-Agent Workflow Response."""
    triage: TriageResponse
    selected_hospital: HospitalSelection
    assigned_ambulance: SimulatedAmbulanceDispatch
    hospital_notification: HospitalNotificationPayload
