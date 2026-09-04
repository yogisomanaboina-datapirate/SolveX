from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LocationModel(BaseModel):
    lat: float
    lng: float

class TriageRequest(BaseModel):
    symptoms: str = Field(..., json_schema_extra={"example": "chest pain, left arm numbness, sweating"})
    location: LocationModel
    patientAge: Optional[int] = Field(None, json_schema_extra={"example": 45})
    medicalHistory: Optional[List[str]] = Field(default=[], json_schema_extra={"example": ["diabetes", "hypertension"]})

class TriageData(BaseModel):
    severity: int = Field(..., json_schema_extra={"example": 4})
    condition: str = Field(..., json_schema_extra={"example": "cardiac"})
    action: str = Field(..., json_schema_extra={"example": "ambulance_dispatched"})
    ambulanceId: Optional[str] = Field(None, json_schema_extra={"example": "amb_123"})
    hospitalId: Optional[str] = Field(None, json_schema_extra={"example": "hosp_456"})
    hospitalName: Optional[str] = Field(None, json_schema_extra={"example": "City Hospital"})
    ETA: Optional[int] = Field(None, json_schema_extra={"example": 8})
    firstAid: Optional[str] = Field(None, json_schema_extra={"example": "Chew 300mg aspirin, sit down"})
    aiReasoning: str = Field(..., json_schema_extra={"example": "Severity 4/5 indicates cardiac emergency..."})
    confidence: float = Field(..., json_schema_extra={"example": 0.92})

class TriageResponse(BaseModel):
    success: bool = True
    data: TriageData
