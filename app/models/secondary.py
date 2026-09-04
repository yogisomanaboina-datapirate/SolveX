from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ClaimRequest(BaseModel):
    patientId: str = Field(..., json_schema_extra={"example": "user_456"})
    insuranceProvider: str = Field(..., json_schema_extra={"example": "Aetna"})
    policyNumber: str = Field(..., json_schema_extra={"example": "POL123456"})
    claimedAmount: float = Field(..., json_schema_extra={"example": 5000.0})
    fileUrl: Optional[str] = Field(None, json_schema_extra={"example": "gs://bucket/claim.pdf"})

class ClaimData(BaseModel):
    claimId: str = Field(..., json_schema_extra={"example": "claim_123"})
    patientId: str
    insuranceProvider: str
    policyNumber: str
    status: str = Field(..., json_schema_extra={"example": "approved"})
    approvedAmount: float = Field(..., json_schema_extra={"example": 5000.0})
    aiReasoning: str = Field(..., json_schema_extra={"example": "Policy covers emergency cardiac procedures."})
    timestamp: str

class ClaimResponse(BaseModel):
    success: bool = True
    data: ClaimData

class BedUpdateRequest(BaseModel):
    ICU: int = Field(..., json_schema_extra={"example": 5})
    ventilator: int = Field(..., json_schema_extra={"example": 3})
    general: int = Field(..., json_schema_extra={"example": 20})

class BedData(BaseModel):
    hospitalId: str
    ICU: int
    ventilator: int
    general: int
    lastUpdated: str

class BedResponse(BaseModel):
    success: bool = True
    data: BedData

class MedicationRequest(BaseModel):
    patientId: str
    name: str = Field(..., json_schema_extra={"example": "Aspirin"})
    dosage: str = Field(..., json_schema_extra={"example": "1 tablet daily"})
    schedule: List[str] = Field(..., json_schema_extra={"example": ["08:00"]})

class MedicationData(BaseModel):
    medicationId: str
    patientId: str
    name: str
    dosage: str
    schedule: List[str]
    adherence: float = Field(..., json_schema_extra={"example": 0.85})

class MedicationListResponse(BaseModel):
    success: bool = True
    data: List[MedicationData]

class SimulationRequest(BaseModel):
    targetLat: float = Field(..., json_schema_extra={"example": 17.4239})
    targetLng: float = Field(..., json_schema_extra={"example": 78.4116})
    steps: int = Field(5, json_schema_extra={"example": 5})

class SimulationResponse(BaseModel):
    success: bool = True
    message: str
    path: List[Dict[str, float]]

# Bed Optimization Models
class BedOptimizeRequest(BaseModel):
    hospitalId: Optional[str] = Field(None, json_schema_extra={"example": "hosp_1"})
    requestedBedType: str = Field("ICU", json_schema_extra={"example": "ICU"})
    patientUrgency: str = Field("HIGH", json_schema_extra={"example": "HIGH"})
    requiredSpecialty: str = Field("CARDIOLOGY", json_schema_extra={"example": "CARDIOLOGY"})

class BedOptimizeData(BaseModel):
    recommendedHospitalId: str
    recommendedHospitalName: str
    allocatedBedType: str
    bedsAvailable: int
    aiReasoning: str
    confidence: float

class BedOptimizeResponse(BaseModel):
    success: bool = True
    data: BedOptimizeData

# Medication Scheduling Models
class PrescriptionMedicationInput(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Amoxicillin"})
    dosage: str = Field(..., json_schema_extra={"example": "500mg"})
    frequency: str = Field("Twice daily", json_schema_extra={"example": "Twice daily"})
    mealRelationship: Optional[str] = Field("AFTER_MEAL", json_schema_extra={"example": "AFTER_MEAL"})
    durationDays: Optional[int] = Field(7, json_schema_extra={"example": 7})

class MedicationScheduleCreateRequest(BaseModel):
    patientId: Optional[str] = Field(None, json_schema_extra={"example": "user_123"})
    medications: List[PrescriptionMedicationInput]
    wakeTime: Optional[str] = Field("08:00", json_schema_extra={"example": "08:00"})
    sleepTime: Optional[str] = Field("22:00", json_schema_extra={"example": "22:00"})
    mealTimes: Optional[Dict[str, str]] = Field(default_factory=lambda: {"breakfast": "08:30", "lunch": "13:00", "dinner": "20:00"})

class MedicationScheduleResultData(BaseModel):
    patientId: str
    scheduledReminders: List[Dict[str, Any]]
    conflictsDetected: List[Dict[str, Any]]
    hasConflicts: bool
    notificationPayloads: List[Dict[str, Any]]
    aiReasoning: str
    confidence: float
    disclaimer: str

class MedicationScheduleResultResponse(BaseModel):
    success: bool = True
    data: MedicationScheduleResultData

# Medical Report Analyzer Models
class ReportAnalyzeRequest(BaseModel):
    reportText: str = Field(..., json_schema_extra={"example": "CBC Report: Hemoglobin 14.2 g/dL, WBC 6500"})
    reportTitle: Optional[str] = Field("Medical Lab Report", json_schema_extra={"example": "Annual CBC"})
    reportDate: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-10"})
    previousReports: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class ReportAnalyzeResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]

# Chat Assistant Models
class ChatMessageRequest(BaseModel):
    message: str = Field(..., json_schema_extra={"example": "What is hemoglobin?"})
    patientProfile: Optional[Dict[str, Any]] = Field(default=None)
    conversationHistory: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class ChatMessageResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


