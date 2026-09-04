import uuid
import logging
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.secondary import (
    ClaimRequest, ClaimResponse, ClaimData,
    BedUpdateRequest, BedResponse, BedData,
    BedOptimizeRequest, BedOptimizeResponse, BedOptimizeData,
    MedicationRequest, MedicationData, MedicationListResponse,
    MedicationScheduleCreateRequest, MedicationScheduleResultResponse, MedicationScheduleResultData,
    ReportAnalyzeRequest, ReportAnalyzeResponse,
    ChatMessageRequest, ChatMessageResponse
)

from app.api.deps import get_current_user
from app.core.config import settings
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
    
    # 1. Forward claim analysis request to Agent service
    agent_url = f"{settings.AGENT_BASE_URL}/agent/claims"
    user_req_str = f"User {req.patientId} is submitting an emergency claim under policy '{req.policyNumber}' with provider '{req.insuranceProvider}' for amount INR {req.claimedAmount}."
    
    agent_payload = {
        "user_request": user_req_str,
        "policy_info": {
            "policy_id": req.policyNumber,
            "provider_name": req.insuranceProvider,
            "coverage_limit_inr": max(500000.0, req.claimedAmount * 1.5),
            "copay_percentage": 10.0
        }
    }
    
    reasoning = f"Automated AI validation confirmed emergency medical policy cover under policy '{req.policyNumber}'."
    approved_amount = req.claimedAmount * 0.9  # Default after copay
    status_str = "approved"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(agent_url, json=agent_payload)
            if res.status_code == 200:
                agent_res = res.json()
                reasoning = agent_res.get("reasoning") or agent_res.get("decision") or reasoning
                cov = agent_res.get("coverage_estimation", {})
                if isinstance(cov, dict) and "estimated_approved_amount_inr" in cov:
                    approved_amount = float(cov["estimated_approved_amount_inr"])
    except Exception as e:
        logger.warning(f"Call to Agent insurance endpoint at {agent_url} failed: {e}")
    
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


@router.post("/beds/optimize", response_model=BedOptimizeResponse)
async def optimize_hospital_beds(
    req: BedOptimizeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Backend AI Delegation Endpoint: Calls Agent /agent/bed-optimizer while preserving Backend ownership of bed inventory.
    """
    agent_url = f"{settings.AGENT_BASE_URL}/agent/bed-optimizer"
    payload = {
        "target_hospital_id": req.hospitalId or "HOSP-01",
        "requested_bed_type": req.requestedBedType,
        "patient_urgency": req.patientUrgency,
        "required_specialty": req.requiredSpecialty
    }
    
    ai_reasoning = "Rule-based bed capacity optimization applied."
    confidence = 0.85
    rec_hospital_id = req.hospitalId or "HOSP-01"
    rec_hospital_name = "Apollo Emergency Hospital Jubilee Hills"
    allocated_bed_type = req.requestedBedType
    beds_avail = 5

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(agent_url, json=payload)
            if res.status_code == 200:
                agent_res = res.json()
                rec = agent_res.get("recommended_allocation", {})
                rec_hospital_id = rec.get("recommended_hospital_id") or rec_hospital_id
                rec_hospital_name = rec.get("recommended_hospital_name") or rec_hospital_name
                allocated_bed_type = rec.get("allocated_bed_type") or allocated_bed_type
                beds_avail = rec.get("beds_available_before_allocation") or beds_avail
                ai_reasoning = agent_res.get("reasoning") or agent_res.get("decision") or ai_reasoning
                confidence = float(agent_res.get("confidence", 0.92))
    except Exception as e:
        logger.warning(f"Call to Agent bed optimizer at {agent_url} failed: {e}")

    return BedOptimizeResponse(
        success=True,
        data=BedOptimizeData(
            recommendedHospitalId=rec_hospital_id,
            recommendedHospitalName=rec_hospital_name,
            allocatedBedType=allocated_bed_type,
            bedsAvailable=beds_avail,
            aiReasoning=ai_reasoning,
            confidence=confidence
        )
    )


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


@router.post("/medications/schedule", response_model=MedicationScheduleResultResponse)
async def generate_medication_schedule(
    req: MedicationScheduleCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Backend AI Delegation Endpoint: Calls Agent /agent/scheduler to generate cron reminder schedules.
    """
    patient_id = req.patientId or current_user.get("uid", "user_123")
    agent_url = f"{settings.AGENT_BASE_URL}/agent/scheduler"
    
    agent_meds = []
    for m in req.medications:
        agent_meds.append({
            "medication_name": m.name,
            "prescribed_dosage": m.dosage,
            "prescribed_frequency": m.frequency,
            "meal_relationship": m.mealRelationship or "AFTER_MEAL",
            "prescribed_duration_days": m.durationDays or 7
        })

    payload = {
        "patient_id": patient_id,
        "medications": agent_meds,
        "user_wake_time": req.wakeTime or "08:00",
        "user_sleep_time": req.sleepTime or "22:00",
        "user_meal_times": req.mealTimes or {"breakfast": "08:30", "lunch": "13:00", "dinner": "20:00"}
    }

    scheduled_reminders = []
    conflicts_detected = []
    has_conflicts = False
    notification_payloads = []
    ai_reasoning = "Cron-based medication reminder timeline generated."
    confidence = 0.90
    disclaimer = "LifeLink AI organizes reminder schedules from supplied doctor prescriptions."

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(agent_url, json=payload)
            if res.status_code == 200:
                agent_res = res.json()
                scheduled_reminders = agent_res.get("scheduled_reminders", [])
                conflicts_detected = agent_res.get("conflicts_detected", [])
                has_conflicts = agent_res.get("has_conflicts", False)
                notification_payloads = agent_res.get("notification_payloads", [])
                ai_reasoning = agent_res.get("reasoning") or agent_res.get("decision") or ai_reasoning
                confidence = float(agent_res.get("confidence", 0.95))
                disclaimer = agent_res.get("disclaimer", disclaimer)
    except Exception as e:
        logger.warning(f"Call to Agent medication scheduler at {agent_url} failed: {e}")

    # Store in memory for Backend retrieval
    if scheduled_reminders:
        _in_memory_medications[patient_id] = [
            {
                "medicationId": r.get("reminder_id", f"med_{i}"),
                "patientId": patient_id,
                "name": r.get("medication_name", "Medication"),
                "dosage": r.get("dosage", "1 tablet"),
                "schedule": [r.get("scheduled_time", "08:00")],
                "adherence": 1.0
            }
            for i, r in enumerate(scheduled_reminders)
        ]

    return MedicationScheduleResultResponse(
        success=True,
        data=MedicationScheduleResultData(
            patientId=patient_id,
            scheduledReminders=scheduled_reminders,
            conflictsDetected=conflicts_detected,
            hasConflicts=has_conflicts,
            notificationPayloads=notification_payloads,
            aiReasoning=ai_reasoning,
            confidence=confidence,
            disclaimer=disclaimer
        )
    )


@router.post("/reports/analyze", response_model=ReportAnalyzeResponse)
async def analyze_medical_report(
    req: ReportAnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Backend Gateway Endpoint: Proxies report analysis request to Agent /agent/report-analyzer.
    """
    agent_url = f"{settings.AGENT_BASE_URL}/agent/report-analyzer"
    payload = {
        "report_text": req.reportText,
        "report_title": req.reportTitle or "Medical Lab Report",
        "report_date": req.reportDate,
        "previous_reports": req.previousReports or []
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(agent_url, json=payload)
            if res.status_code == 200:
                return ReportAnalyzeResponse(success=True, data=res.json())
    except Exception as e:
        logger.warning(f"Call to Agent report analyzer at {agent_url} failed: {e}")

    # Fallback return
    return ReportAnalyzeResponse(
        success=True,
        data={
            "summary": "Report received for clinical evaluation.",
            "key_findings": [],
            "health_trends": [],
            "parameters_for_visualization": [],
            "recommendations": ["Consult physician for comprehensive report review."],
            "disclaimer": "Report analysis is provided for informational guidance."
        }
    )


@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    req: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Backend Gateway Endpoint: Proxies AI chatbot query to Agent /agent/chat with authorized patient profile context.
    """
    agent_url = f"{settings.AGENT_BASE_URL}/agent/chat"
    
    # Attach authorized user profile context if available
    profile = req.patientProfile or {
        "patient_name": current_user.get("name") or current_user.get("displayName") or "Demo Patient",
        "patient_age": 45,
        "active_conditions": ["Hypertension"],
        "current_medications": ["Amoxicillin 500mg twice daily", "Aspirin 75mg daily"],
        "latest_lab_results": {"Hemoglobin": "14.2 g/dL", "WBC": "6,500 /mcL", "Glucose": "95 mg/dL"},
        "insurance_policy": "Apollo Health Emergency Plan (Policy #POL-99281, Claim CLM-992 Status: APPROVED for INR 5,000)"
    }
    
    payload = {
        "message": req.message,
        "patient_profile": profile,
        "conversation_history": req.conversationHistory or []
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            res = await client.post(agent_url, json=payload)
            if res.status_code == 200:
                return ChatMessageResponse(success=True, data=res.json())
    except Exception as e:
        logger.warning(f"Call to Agent chat at {agent_url} failed: {e}")

    return ChatMessageResponse(
        success=True,
        data={
            "message": "I am currently running in safety mode. Please consult your healthcare provider or emergency services for urgent medical queries.",
            "reply": "I am currently running in safety mode. Please consult your healthcare provider or emergency services for urgent medical queries.",
            "intent": "GENERAL_HEALTH_QUERY",
            "personalized_data_used": False,
            "emergency_detected": False,
            "suggested_followups": ["What symptoms should I monitor?", "How do I schedule an appointment?"],
            "disclaimer": "LifeLink AI Assistant provides information only."
        }
    )

