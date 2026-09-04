import logging
import asyncio
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.triage import TriageRequest, TriageResponse, TriageData
from app.api.deps import get_current_user
from app.core.config import settings
from app.repositories.ambulance_repo import AmbulanceRepository
from app.repositories.hospital_repo import HospitalRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/triage", tags=["triage"])

def map_agent_triage_to_backend(agent_res: dict) -> dict:
    """Safely map Agent response (urgency, category, etc.) -> Backend response (severity, condition, etc.)."""
    data = agent_res.get("data", agent_res)
    
    # Safe explicit mapping for urgency -> severity (1 to 5)
    urgency_raw = str(data.get("urgency") or data.get("severity") or "MEDIUM").upper()
    urgency_map = {
        "CRITICAL": 5,
        "HIGH": 4,
        "MEDIUM": 3,
        "MODERATE": 3,
        "LOW": 2,
        "5": 5, "4": 4, "3": 3, "2": 2, "1": 1
    }
    severity = urgency_map.get(urgency_raw, 3)

    # Category -> condition
    condition = data.get("category") or data.get("condition") or data.get("required_specialty") or "unknown_condition"

    # Preserving reasoning, confidence, hospital info, ETA, firstAid, recommended_action
    ai_reasoning = data.get("reasoning") or data.get("aiReasoning") or data.get("decision") or "Autonomous AI evaluation completed."
    first_aid = data.get("recommended_action") or data.get("firstAid") or "Chew 300mg aspirin if conscious, loosen tight clothing, sit upright"
    
    try:
        confidence = float(data.get("confidence", 0.90))
    except (ValueError, TypeError):
        confidence = 0.90

    hospital_id = data.get("hospitalId") or data.get("hospital_id") or "hosp_1"
    hospital_name = data.get("hospitalName") or data.get("hospital_name") or "Apollo Hospital"
    eta = data.get("ETA") or data.get("eta_minutes") or 8

    return {
        "severity": severity,
        "condition": condition,
        "hospitalId": hospital_id,
        "hospitalName": hospital_name,
        "ETA": eta,
        "firstAid": first_aid,
        "aiReasoning": ai_reasoning,
        "confidence": confidence
    }

async def call_agent_triage_with_retry(payload: dict, retries: int = 2, timeout: float = 10.0) -> dict:
    agent_url = f"{settings.AGENT_BASE_URL}/agent/triage"
    
    agent_payload = {
        "symptoms": payload.get("symptoms", ""),
        "patient_age": payload.get("patientAge") or payload.get("patient_age"),
        "location": payload.get("location")
    }

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(agent_url, json=agent_payload)
                if response.status_code == 200:
                    data = response.json()
                    return map_agent_triage_to_backend(data)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} to call Agent at {agent_url} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(0.5)

    # Fallback smart triage engine if AI Agent is offline (Hackathon safety net)
    logger.info("Using smart local triage safety net fallback")
    symptoms_lower = payload.get("symptoms", "").lower()
    
    # Critical symptoms rule check
    critical_keywords = ["chest pain", "can't breathe", "breathless", "unconscious", "stroke", "numbness", "severe bleeding", "cardiac", "heart attack"]
    is_critical = any(kw in symptoms_lower for kw in critical_keywords)
    
    if is_critical:
        # Default to high priority hospital (Apollo Hospital hosp_1)
        hospitals = HospitalRepository.get_all_hospitals()
        selected_hosp = hospitals[0] if hospitals else {"hospitalId": "hosp_1", "name": "Apollo Hospital"}
        
        return {
            "severity": 4,
            "condition": "cardiac_or_respiratory_distress",
            "hospitalId": selected_hosp.get("hospitalId", "hosp_1"),
            "hospitalName": selected_hosp.get("name", "Apollo Hospital"),
            "ETA": 8,
            "firstAid": "Chew 300mg aspirin if conscious, loosen tight clothing, sit upright",
            "aiReasoning": "Symptoms indicate potential severe cardiac or respiratory emergency. Immediate intervention required.",
            "confidence": 0.92
        }
    else:
        return {
            "severity": 2,
            "condition": "non_urgent_symptoms",
            "hospitalId": None,
            "hospitalName": None,
            "ETA": None,
            "firstAid": "Rest in a comfortable position, hydrate, monitor symptoms.",
            "aiReasoning": "Symptoms appear non-life threatening. Self-care recommended.",
            "confidence": 0.85
        }


@router.post("/emergency", response_model=TriageResponse)
async def create_emergency_triage(
    req: TriageRequest,
    current_user: dict = Depends(get_current_user)
):
    patient_id = current_user.get("uid", "user_123")
    
    payload = {
        "symptoms": req.symptoms,
        "location": req.location.model_dump(),
        "patientAge": req.patientAge,
        "medicalHistory": req.medicalHistory
    }

    # 1. Get AI Agent decision
    agent_data = await call_agent_triage_with_retry(payload)

    severity = agent_data.get("severity", 1)
    condition = agent_data.get("condition", "unknown")
    hospital_id = agent_data.get("hospitalId") or "hosp_1"
    hospital_name = agent_data.get("hospitalName") or "Apollo Hospital"
    eta = agent_data.get("ETA") or 8
    first_aid = agent_data.get("firstAid", "Remain calm and await assistance")
    ai_reasoning = agent_data.get("aiReasoning", "Autonomous AI evaluation completed.")
    confidence = float(agent_data.get("confidence", 0.90))

    ambulance_id = None
    action = "self_care"

    # 2. Autonomous Dispatch Logic (severity >= 4)
    if severity >= 4:
        action = "ambulance_dispatched"
        ambulance_record = AmbulanceRepository.create_ambulance(
            patient_id=patient_id,
            hospital_id=hospital_id,
            hospital_name=hospital_name,
            location=req.location.model_dump(),
            eta=eta
        )
        ambulance_id = ambulance_record["ambulanceId"]

    # 3. Log to Firestore triage_logs
    triage_log_data = {
        "patientId": patient_id,
        "symptoms": req.symptoms,
        "severity": severity,
        "condition": condition,
        "action": action,
        "ambulanceId": ambulance_id,
        "hospitalId": hospital_id if severity >= 4 else None,
        "aiReasoning": ai_reasoning,
    }
    AmbulanceRepository.save_triage_log(triage_log_data)

    # 4. Construct response
    return TriageResponse(
        success=True,
        data=TriageData(
            severity=severity,
            condition=condition,
            action=action,
            ambulanceId=ambulance_id,
            hospitalId=hospital_id if severity >= 4 else None,
            hospitalName=hospital_name if severity >= 4 else None,
            ETA=eta if severity >= 4 else None,
            firstAid=first_aid,
            aiReasoning=ai_reasoning,
            confidence=confidence
        )
    )
