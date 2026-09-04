from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List
from tools.hospital_tools import calculate_haversine_distance, estimate_eta_minutes


def evaluate_available_ambulances(
    ambulances: List[Dict[str, Any]],
    patient_lat: float,
    patient_lng: float
) -> List[Dict[str, Any]]:
    """
    Filter and rank available ambulances based on current location and estimated ETA to patient.
    """
    candidates = []

    for amb in ambulances:
        # Only evaluate available ambulances
        status = str(amb.get("status", "AVAILABLE")).upper()
        if status != "AVAILABLE":
            continue

        a_loc = amb.get("current_location", {})
        a_lat = a_loc.get("lat", patient_lat)
        a_lng = a_loc.get("lng", patient_lng)

        distance = calculate_haversine_distance(patient_lat, patient_lng, a_lat, a_lng)
        eta = estimate_eta_minutes(distance, average_speed_kmh=45.0)

        candidates.append({
            "ambulance_id": amb.get("id", "AMB_UNKNOWN"),
            "vehicle_number": amb.get("vehicle_number", "AMB-001"),
            "type": amb.get("type", "ALS"),
            "distance_km": distance,
            "estimated_eta_minutes": eta,
            "paramedic_level": amb.get("paramedic_level", "ADVANCED"),
            "raw_data": amb
        })

    # Sort by shortest ETA
    candidates.sort(key=lambda x: x["estimated_eta_minutes"])
    return candidates


def create_simulated_dispatch_event(
    ambulance: Dict[str, Any],
    hospital: Dict[str, Any],
    patient_symptoms: str,
    urgency: str
) -> Dict[str, Any]:
    """
    Generate structured simulated dispatch record for emergency response.
    """
    dispatch_id = f"DSP-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "dispatch_id": dispatch_id,
        "ambulance_id": ambulance.get("ambulance_id", "AMB-101"),
        "vehicle_number": ambulance.get("vehicle_number", "TS-09-AMB-1001"),
        "ambulance_type": ambulance.get("type", "ALS"),
        "hospital_id": hospital.get("hospital_id", "HOSP-01"),
        "hospital_name": hospital.get("hospital_name", "City Care Hospital"),
        "estimated_patient_eta_minutes": ambulance.get("estimated_eta_minutes", 8),
        "dispatch_status": "SIMULATED_DISPATCHED",
        "timestamp": timestamp,
        "patient_symptoms_summary": patient_symptoms[:100],
        "urgency_level": urgency
    }


def generate_hospital_notification_payload(
    hospital: Dict[str, Any],
    ambulance_dispatch: Dict[str, Any],
    triage_category: str,
    urgency: str,
    required_specialty: str
) -> Dict[str, Any]:
    """
    Generate incoming emergency notification payload for target hospital ER dashboard.
    """
    notification_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"

    return {
        "notification_id": notification_id,
        "target_hospital_id": hospital.get("hospital_id", "HOSP-01"),
        "target_hospital_name": hospital.get("hospital_name", "City Care Hospital"),
        "patient_triage_category": triage_category,
        "patient_urgency": urgency,
        "required_specialty": required_specialty,
        "assigned_ambulance_id": ambulance_dispatch.get("ambulance_id", "AMB-101"),
        "estimated_arrival_minutes": ambulance_dispatch.get("estimated_patient_eta_minutes", 10),
        "alert_message": (
            f"INCOMING EMERGENCY: [{urgency}] {triage_category} patient requiring {required_specialty}. "
            f"Dispatched via Ambulance {ambulance_dispatch.get('vehicle_number')}. ETA ~{ambulance_dispatch.get('estimated_patient_eta_minutes')} mins."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
