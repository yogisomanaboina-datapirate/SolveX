import uuid
from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional
from app.core.security import db

logger = logging.getLogger(__name__)

# Fallback in-memory storage for rapid dev without Firebase credentials
_in_memory_ambulances: Dict[str, Dict[str, Any]] = {}
_in_memory_triage_logs: Dict[str, Dict[str, Any]] = {}

class AmbulanceRepository:

    @staticmethod
    def create_ambulance(
        patient_id: str,
        hospital_id: str,
        hospital_name: str,
        location: Dict[str, float],
        eta: int
    ) -> Dict[str, Any]:
        ambulance_id = f"amb_{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        doc_data = {
            "ambulanceId": ambulance_id,
            "patientId": patient_id,
            "hospitalId": hospital_id,
            "hospitalName": hospital_name,
            "status": "dispatched",
            "location": location,
            "ETA": eta,
            "timestamp": now_iso
        }

        # Try saving to Firestore
        if db:
            try:
                db.collection("ambulances").document(ambulance_id).set(doc_data)
                logger.info(f"Ambulance {ambulance_id} saved to Firestore.")
            except Exception as e:
                logger.error(f"Firestore ambulance create error: {e}")

        # Always save to in-memory fallback
        _in_memory_ambulances[ambulance_id] = doc_data
        return doc_data

    @staticmethod
    def get_ambulance_by_id(ambulance_id: str) -> Optional[Dict[str, Any]]:
        if db:
            try:
                doc = db.collection("ambulances").document(ambulance_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore ambulance fetch error: {e}")

        return _in_memory_ambulances.get(ambulance_id)

    @staticmethod
    def update_location(ambulance_id: str, location: Dict[str, float]) -> bool:
        updated = False
        if db:
            try:
                db.collection("ambulances").document(ambulance_id).update({
                    "location": location
                })
                updated = True
            except Exception as e:
                logger.error(f"Firestore location update error: {e}")

        if ambulance_id in _in_memory_ambulances:
            _in_memory_ambulances[ambulance_id]["location"] = location
            updated = True

        return updated

    @staticmethod
    def update_status(ambulance_id: str, status: str) -> bool:
        updated = False
        if db:
            try:
                db.collection("ambulances").document(ambulance_id).update({
                    "status": status
                })
                updated = True
            except Exception as e:
                logger.error(f"Firestore status update error: {e}")

        if ambulance_id in _in_memory_ambulances:
            _in_memory_ambulances[ambulance_id]["status"] = status
            updated = True

        return updated

    @staticmethod
    def save_triage_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
        triage_id = f"triage_{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        log_doc = {
            "triageId": triage_id,
            **log_data,
            "timestamp": now_iso
        }

        if db:
            try:
                db.collection("triage_logs").document(triage_id).set(log_doc)
                logger.info(f"Triage log {triage_id} saved to Firestore.")
            except Exception as e:
                logger.error(f"Firestore triage log save error: {e}")

        _in_memory_triage_logs[triage_id] = log_doc
        return log_doc
