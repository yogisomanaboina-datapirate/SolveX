from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AmbulanceLocation(BaseModel):
    lat: float
    lng: float

class AmbulanceData(BaseModel):
    ambulanceId: str = Field(..., json_schema_extra={"example": "amb_123"})
    status: str = Field(..., json_schema_extra={"example": "en_route"})
    location: AmbulanceLocation
    ETA: int = Field(..., json_schema_extra={"example": 5})
    hospitalId: str = Field(..., json_schema_extra={"example": "hosp_456"})
    hospitalName: str = Field(..., json_schema_extra={"example": "City Hospital"})
    patientId: str = Field(..., json_schema_extra={"example": "user_789"})

class AmbulanceResponse(BaseModel):
    success: bool = True
    data: AmbulanceData

class LocationUpdate(BaseModel):
    location: AmbulanceLocation

class StatusUpdate(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "arrived"})

class StandardSuccessResponse(BaseModel):
    success: bool = True
    message: str = "Success"
