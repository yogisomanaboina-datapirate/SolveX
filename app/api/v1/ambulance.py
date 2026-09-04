import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.ambulance import (
    AmbulanceResponse,
    AmbulanceData,
    LocationUpdate,
    StatusUpdate,
    StandardSuccessResponse
)
from app.models.secondary import SimulationRequest, SimulationResponse
from app.api.deps import get_current_user
from app.repositories.ambulance_repo import AmbulanceRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ambulance", tags=["ambulance"])

@router.get("/{ambulanceId}", response_model=AmbulanceResponse)
async def get_ambulance_status(
    ambulanceId: str,
    current_user: dict = Depends(get_current_user)
):
    ambulance = AmbulanceRepository.get_ambulance_by_id(ambulanceId)
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "AMBULANCE_NOT_FOUND",
                    "message": f"Ambulance with ID '{ambulanceId}' not found"
                }
            }
        )

    return AmbulanceResponse(
        success=True,
        data=AmbulanceData(
            ambulanceId=ambulance["ambulanceId"],
            status=ambulance.get("status", "dispatched"),
            location=ambulance["location"],
            ETA=ambulance.get("ETA", 5),
            hospitalId=ambulance.get("hospitalId", "hosp_1"),
            hospitalName=ambulance.get("hospitalName", "City Hospital"),
            patientId=ambulance.get("patientId", current_user.get("uid", "user_123"))
        )
    )

@router.put("/{ambulanceId}/location", response_model=StandardSuccessResponse)
async def update_ambulance_location(
    ambulanceId: str,
    req: LocationUpdate,
    current_user: dict = Depends(get_current_user)
):
    success = AmbulanceRepository.update_location(ambulanceId, req.location.model_dump())
    if not success:
        # Create or update in memory fallback
        AmbulanceRepository.update_location(ambulanceId, req.location.model_dump())

    return StandardSuccessResponse(
        success=True,
        message="Location updated"
    )

@router.put("/{ambulanceId}/status", response_model=StandardSuccessResponse)
async def update_ambulance_status(
    ambulanceId: str,
    req: StatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    success = AmbulanceRepository.update_status(ambulanceId, req.status)
    if not success:
        AmbulanceRepository.update_status(ambulanceId, req.status)

    return StandardSuccessResponse(
        success=True,
        message="Status updated"
    )

@router.post("/{ambulanceId}/simulate", response_model=SimulationResponse)
async def simulate_ambulance_movement(
    ambulanceId: str,
    req: SimulationRequest,
    current_user: dict = Depends(get_current_user)
):
    ambulance = AmbulanceRepository.get_ambulance_by_id(ambulanceId)
    start_lat = ambulance["location"]["lat"] if ambulance else 17.385
    start_lng = ambulance["location"]["lng"] if ambulance else 78.486
    
    steps = max(1, req.steps)
    path = []
    
    for i in range(1, steps + 1):
        ratio = i / float(steps)
        lat = start_lat + (req.targetLat - start_lat) * ratio
        lng = start_lng + (req.targetLng - start_lng) * ratio
        path.append({"lat": round(lat, 6), "lng": round(lng, 6)})
        
    final_location = path[-1]
    AmbulanceRepository.update_location(ambulanceId, final_location)
    
    return SimulationResponse(
        success=True,
        message=f"Simulated {steps} movement steps for ambulance '{ambulanceId}'",
        path=path
    )
