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
