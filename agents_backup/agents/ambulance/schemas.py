from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
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


class NearbyHospitalInfo(BaseModel):
    """Nearby hospital facility info discovered around user GPS coordinates."""
    id: str = Field(description="Hospital ID", examples=["HOSP-01"])
    name: str = Field(description="Hospital name", examples=["Apollo Emergency Hospital Jubilee Hills"])
    distance_km: float = Field(description="Distance from user GPS in kilometers", examples=[3.2])
    address: str = Field(description="Street address or location", examples=["Jubilee Hills, Hyderabad"])
    location: LocationSchema = Field(description="GPS coordinates of hospital")
    google_maps_directions_url: str = Field(
        description="Clickable Google Maps navigation link",
        examples=["https://www.google.com/maps/dir/?api=1&destination=17.4325,78.4071"]
    )
    specialties: List[str] = Field(default_factory=list, description="Medical specialties available")
    icu_beds_available: Optional[int] = Field(default=None, description="ICU beds available")
    er_beds_available: Optional[int] = Field(default=None, description="ER beds available")


class NearbyHospitalsRequest(BaseModel):
    """Request payload for standalone nearby hospital search."""
    user_location: LocationSchema = Field(default_factory=LocationSchema)
    radius_km: float = Field(default=25.0, description="Search radius in kilometers")
    candidate_hospitals: Optional[List[HospitalInfo]] = Field(default=None)


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
    decision: str = Field(
        default="Emergency triage completed based on clinical symptoms.",
        validation_alias=AliasChoices("decision", "summary_decision", "summary"),
        description="Primary summary decision reached by the agent"
    )
    reasoning: str = Field(
        default="Patient symptoms evaluated against emergency triage protocols.",
        validation_alias=AliasChoices("reasoning", "clinical_reasoning", "rationale"),
        description="Step-by-step rationale explaining how the decision was reached"
    )
    confidence: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("confidence", "confidence_score", "score"),
        description="Confidence score in the coordination recommendation (0.0 to 1.0)"
    )
    next_action: str = Field(
        default="HOSPITAL_MATCHING",
        validation_alias=AliasChoices("next_action", "recommended_next_step"),
        description="Recommended next workflow or backend execution action"
    )
    urgency: str = Field(
        validation_alias=AliasChoices("urgency", "clinical_urgency", "urgency_level"),
        description="Triage urgency level: CRITICAL, HIGH, MEDIUM, LOW",
        examples=["HIGH"]
    )
    severity: str = Field(
        validation_alias=AliasChoices("severity", "clinical_severity", "severity_level"),
        description="Clinical severity rating: CRITICAL, HIGH, MODERATE, LOW",
        examples=["HIGH"]
    )
    category: str = Field(
        validation_alias=AliasChoices("category", "emergency_category", "triage_category"),
        description="Emergency classification category",
        examples=["CARDIAC_EMERGENCY"]
    )
    required_specialty: str = Field(
        validation_alias=AliasChoices("required_specialty", "specialty", "needed_specialty"),
        description="Required medical department at hospital",
        examples=["CARDIOLOGY"]
    )
    recommended_action: str = Field(
        validation_alias=AliasChoices("recommended_action", "coordination_action", "action"),
        description="Immediate coordination action",
        examples=["IMMEDIATE_AMBULANCE_DISPATCH"]
    )


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
    nearby_radius_km: float = Field(default=25.0, description="Radius in km for nearby real hospital discovery")


class EmergencyWorkflowResponse(BaseDecisionResponse):
    """Complete End-to-End Emergency Multi-Agent Workflow Response."""
    triage: TriageResponse
    selected_hospital: HospitalSelection
    assigned_ambulance: SimulatedAmbulanceDispatch
    hospital_notification: HospitalNotificationPayload
    nearby_hospitals: List[NearbyHospitalInfo] = Field(
        default_factory=list,
        description="Discovered nearby hospitals around user GPS coordinates for direct access option"
    )
    direct_travel_disclaimer: str = Field(
        default="Nearby hospitals are shown for direct access if feasible. For serious emergencies, follow appropriate emergency medical guidance.",
        description="Safety guidance wording regarding self-travel vs ambulance"
    )
