import math
from typing import Any, Dict, List, Optional


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate geodesic distance between two points in kilometers using Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def estimate_eta_minutes(distance_km: float, average_speed_kmh: float = 40.0) -> int:
    """
    Estimate travel time in minutes based on distance and average urban emergency travel speed.
    """
    if distance_km <= 0:
        return 2
    time_hours = distance_km / average_speed_kmh
    minutes = int(math.ceil(time_hours * 60))
    return max(minutes, 2)


def evaluate_hospital_suitability(
    hospitals: List[Dict[str, Any]],
    required_specialty: str,
    urgency: str,
    patient_lat: float,
    patient_lng: float
) -> List[Dict[str, Any]]:
    """
    Dynamically evaluate and rank candidate hospitals based on specialty match,
    bed capacity (ICU/ER), distance, and clinical urgency.
    """
    evaluated = []

    for h in hospitals:
        h_lat = h.get("location", {}).get("lat", patient_lat)
        h_lng = h.get("location", {}).get("lng", patient_lng)
        distance = calculate_haversine_distance(patient_lat, patient_lng, h_lat, h_lng)
        eta = estimate_eta_minutes(distance)

        specialties = [s.upper() for s in h.get("specialties", [])]
        specialty_match = (required_specialty.upper() in specialties) or ("GENERAL_EMERGENCY" in specialties)

        icu_beds = h.get("icu_beds_available", 0)
        er_beds = h.get("er_beds_available", 0)
        total_relevant_beds = icu_beds + er_beds

        # Suitability Score formula (0-100)
        score = 100.0

        # Specialty match is critical
        if not specialty_match:
            score -= 40.0

        # Bed availability factor
        if urgency in ["CRITICAL", "HIGH"]:
            if icu_beds == 0 and er_beds == 0:
                score -= 50.0  # Heavy penalty if no emergency/ICU beds available
            elif icu_beds > 0:
                score += min(icu_beds * 5, 20)

        # Distance penalty (-2 points per km)
        score -= min(distance * 2.0, 30.0)

        score = max(round(score, 1), 0.0)

        evaluated.append({
            "hospital_id": h.get("id", "HOSP_UNKNOWN"),
            "hospital_name": h.get("name", "Unknown Hospital"),
            "distance_km": distance,
            "estimated_eta_minutes": eta,
            "icu_beds_available": icu_beds,
            "er_beds_available": er_beds,
            "specialty_match": specialty_match,
            "suitability_score": score,
            "raw_data": h
        })

    # Sort descending by suitability score, then ascending by distance
    evaluated.sort(key=lambda x: (x["suitability_score"], -x["distance_km"]), reverse=True)
    return evaluated
