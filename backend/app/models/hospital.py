from pydantic import BaseModel, Field
from typing import List, Dict, Any

class HospitalLocation(BaseModel):
    lat: float
    lng: float

class HospitalData(BaseModel):
    hospitalId: str = Field(..., json_schema_extra={"example": "hosp_123"})
    name: str = Field(..., json_schema_extra={"example": "City Hospital"})
    location: HospitalLocation
    specialties: List[str] = Field(..., json_schema_extra={"example": ["cardiology", "neurology", "trauma"]})
    ICU: int = Field(..., json_schema_extra={"example": 20})
    ventilator: int = Field(..., json_schema_extra={"example": 10})
    general: int = Field(..., json_schema_extra={"example": 50})

class HospitalListResponse(BaseModel):
    success: bool = True
    data: List[HospitalData]

class HospitalDetailResponse(BaseModel):
    success: bool = True
    data: HospitalData
