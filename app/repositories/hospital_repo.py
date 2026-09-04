import logging
from typing import List, Dict, Any, Optional
from app.core.security import db

logger = logging.getLogger(__name__)

# Sample hospital seed data for fallback / initial setup
DEFAULT_HOSPITALS = [
    {
        "hospitalId": "hosp_1",
        "name": "Apollo Hospitals, Jubilee Hills",
        "location": {"lat": 17.4239, "lng": 78.4116},
        "specialties": ["cardiology", "neurology", "trauma", "emergency"],
        "ICU": 25,
        "ventilator": 12,
        "general": 80
    },
    {
        "hospitalId": "hosp_2",
        "name": "Care Hospitals, Banjara Hills",
        "location": {"lat": 17.4156, "lng": 78.4487},
        "specialties": ["cardiology", "orthopedics", "nephrology"],
        "ICU": 18,
        "ventilator": 8,
        "general": 60
    },
    {
        "hospitalId": "hosp_3",
        "name": "KIMS Hospitals, Secunderabad",
        "location": {"lat": 17.4375, "lng": 78.4983},
        "specialties": ["trauma", "emergency", "pulmonology"],
        "ICU": 30,
        "ventilator": 15,
        "general": 100
    },
    {
        "hospitalId": "hosp_4",
        "name": "Yashoda Hospitals, Somajiguda",
        "location": {"lat": 17.4258, "lng": 78.4597},
        "specialties": ["oncology", "gastroenterology", "emergency"],
        "ICU": 20,
        "ventilator": 10,
        "general": 75
    },
    {
        "hospitalId": "hosp_5",
        "name": "Continental Hospitals, Gachibowli",
        "location": {"lat": 17.4204, "lng": 78.3488},
        "specialties": ["cardiology", "neurology", "trauma", "pediatrics"],
        "ICU": 22,
        "ventilator": 11,
        "general": 90
    }
]

_in_memory_hospitals: Dict[str, Dict[str, Any]] = {
    h["hospitalId"]: h for h in DEFAULT_HOSPITALS
}

class HospitalRepository:

    @staticmethod
    def get_all_hospitals() -> List[Dict[str, Any]]:
        hospitals_list = []
        if db:
            try:
                docs = db.collection("hospitals").stream()
                for doc in docs:
                    hospitals_list.append(doc.to_dict())
                if hospitals_list:
                    return hospitals_list
            except Exception as e:
                logger.error(f"Firestore hospitals fetch error: {e}")

        return list(_in_memory_hospitals.values())

    @staticmethod
    def get_hospital_by_id(hospital_id: str) -> Optional[Dict[str, Any]]:
        if db:
            try:
                doc = db.collection("hospitals").document(hospital_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore hospital detail fetch error: {e}")

        return _in_memory_hospitals.get(hospital_id)
