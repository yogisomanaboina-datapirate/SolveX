import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.hospital import (
    HospitalListResponse,
    HospitalDetailResponse,
    HospitalData
)
from app.api.deps import get_current_user
from app.repositories.hospital_repo import HospitalRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("", response_model=HospitalListResponse)
async def list_hospitals(current_user: dict = Depends(get_current_user)):
    hospitals_raw = HospitalRepository.get_all_hospitals()
    hospitals_data = [HospitalData(**h) for h in hospitals_raw]

    return HospitalListResponse(
        success=True,
        data=hospitals_data
    )

@router.get("/{hospitalId}", response_model=HospitalDetailResponse)
async def get_hospital_detail(
    hospitalId: str,
    current_user: dict = Depends(get_current_user)
):
    hospital = HospitalRepository.get_hospital_by_id(hospitalId)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "HOSPITAL_NOT_FOUND",
                    "message": f"Hospital with ID '{hospitalId}' not found"
                }
            }
        )

    return HospitalDetailResponse(
        success=True,
        data=HospitalData(**hospital)
    )
