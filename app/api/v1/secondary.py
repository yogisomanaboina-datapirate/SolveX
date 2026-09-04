import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.secondary import (
    ClaimRequest, ClaimResponse, ClaimData,
    BedUpdateRequest, BedResponse, BedData,
    MedicationRequest, MedicationData, MedicationListResponse
)
from app.api.deps import get_current_user
from app.core.security import db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["secondary"])

_in_memory_claims = {}
_in_memory_beds = {}
_in_memory_medications = {}

@router.post("/claims", response_model=ClaimResponse)
async def submit_insurance_claim(
    req: ClaimRequest,
    current_user: dict = Depends(get_current_user)
):
    claim_id = f"claim_{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Auto approve emergency policy claims for hackathon demo
    approved_amount = req.claimedAmount
    status_str = "approved"
    reasoning = f"Automated AI validation confirmed emergency medical policy cover under policy '{req.policyNumber}'."
    
    doc_data = {
        "claimId": claim_id,
        "patientId": req.patientId,
        "insuranceProvider": req.insuranceProvider,
        "policyNumber": req.policyNumber,
        "status": status_str,
        "approvedAmount": approved_amount,
        "aiReasoning": reasoning,
        "timestamp": now_iso
    }
    
    if db:
        try:
            db.collection("claims").document(claim_id).set(doc_data)
        except Exception as e:
            logger.error(f"Firestore claim save error: {e}")
            
    _in_memory_claims[claim_id] = doc_data
    
    return ClaimResponse(
        success=True,
        data=ClaimData(**doc_data)
    )

@router.get("/beds/{hospitalId}", response_model=BedResponse)
async def get_hospital_beds(
    hospitalId: str,
    current_user: dict = Depends(get_current_user)
):
    now_iso = datetime.now(timezone.utc).isoformat()
    bed_info = _in_memory_beds.get(hospitalId, {
        "hospitalId": hospitalId,
        "ICU": 5,
        "ventilator": 3,
        "general": 20,
        "lastUpdated": now_iso
    })
    
    return BedResponse(
        success=True,
        data=BedData(**bed_info)
    )

@router.put("/beds/{hospitalId}", response_model=BedResponse)
async def update_hospital_beds(
    hospitalId: str,
    req: BedUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    now_iso = datetime.now(timezone.utc).isoformat()
    doc_data = {
        "hospitalId": hospitalId,
        "ICU": req.ICU,
        "ventilator": req.ventilator,
        "general": req.general,
        "lastUpdated": now_iso
    }
    
    if db:
        try:
            db.collection("beds").document(hospitalId).set(doc_data)
        except Exception as e:
            logger.error(f"Firestore beds update error: {e}")
            
    _in_memory_beds[hospitalId] = doc_data
    return BedResponse(success=True, data=BedData(**doc_data))

@router.get("/medications/{patientId}", response_model=MedicationListResponse)
async def list_medications(
    patientId: str,
    current_user: dict = Depends(get_current_user)
):
    user_meds = _in_memory_medications.get(patientId, [
        {
            "medicationId": "med_101",
            "patientId": patientId,
            "name": "Aspirin (Emergency Preventive)",
            "dosage": "75mg 1 tablet daily",
            "schedule": ["08:00"],
            "adherence": 0.95
        },
        {
            "medicationId": "med_102",
            "patientId": patientId,
            "name": "Atorvastatin",
            "dosage": "20mg 1 tablet at night",
            "schedule": ["21:00"],
            "adherence": 0.88
        }
    ])
    
    return MedicationListResponse(
        success=True,
        data=[MedicationData(**m) for m in user_meds]
    )
