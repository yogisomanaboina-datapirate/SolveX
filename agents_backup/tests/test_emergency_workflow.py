from fastapi.testclient import TestClient
from main import app
from tools.ambulance_tools import evaluate_available_ambulances
from tools.hospital_tools import calculate_haversine_distance, discover_nearby_hospitals, evaluate_hospital_suitability
from agents.ambulance.schemas import (
    EmergencyWorkflowRequest,
    HospitalInfo,
    LocationSchema,
    NearbyHospitalsRequest,
)
from workflows.emergency import run_full_emergency_workflow, run_nearby_hospitals_workflow

client = TestClient(app)


def test_haversine_distance_calculation():
    # Distance between Jubilee Hills (17.4325, 78.4071) and Madhapur (17.4486, 78.3908) ~2.4 km
    dist = calculate_haversine_distance(17.4486, 78.3908, 17.4325, 78.4071)
    assert 1.5 <= dist <= 3.5


def test_dynamic_hospital_availability_reevaluation():
    """
    Test requirement: System must dynamically re-evaluate when bed availability changes.
    """
    patient_lat = 17.4486
    patient_lng = 78.3908

    hospitals_input = [
        {
            "id": "HOSP-A",
            "name": "Hospital A",
            "location": {"lat": 17.4450, "lng": 78.3910},
            "specialties": ["CARDIOLOGY"],
            "icu_beds_available": 5,
            "er_beds_available": 5
        },
        {
            "id": "HOSP-B",
            "name": "Hospital B",
            "location": {"lat": 17.4460, "lng": 78.3920},
            "specialties": ["CARDIOLOGY"],
            "icu_beds_available": 2,
            "er_beds_available": 3
        }
    ]

    # Initial state: Hospital A has 5 ICU beds -> Hospital A ranked #1
    initial_eval = evaluate_hospital_suitability(
        hospitals=hospitals_input,
        required_specialty="CARDIOLOGY",
        urgency="CRITICAL",
        patient_lat=patient_lat,
        patient_lng=patient_lng
    )
    assert initial_eval[0]["hospital_id"] == "HOSP-A"

    # Changed state: Hospital A ICU beds drop to 0, ER beds drop to 0
    hospitals_input[0]["icu_beds_available"] = 0
    hospitals_input[0]["er_beds_available"] = 0

    reevaluated = evaluate_hospital_suitability(
        hospitals=hospitals_input,
        required_specialty="CARDIOLOGY",
        urgency="CRITICAL",
        patient_lat=patient_lat,
        patient_lng=patient_lng
    )
    # Re-evaluation must dynamically select Hospital B because Hospital A has no capacity!
    assert reevaluated[0]["hospital_id"] == "HOSP-B"


def test_nearby_hospital_discovery_with_gps():
    req = NearbyHospitalsRequest(
        user_location=LocationSchema(lat=17.4486, lng=78.3908, address="Madhapur, Hyderabad"),
        radius_km=15.0
    )
    nearby = run_nearby_hospitals_workflow(req)

    assert len(nearby) >= 1
    assert nearby[0].distance_km >= 0.0
    assert "https://www.google.com/maps/dir/" in nearby[0].google_maps_directions_url
    assert nearby[0].name != ""


def test_nearby_hospital_endpoint_http():
    payload = {
        "user_location": {
            "lat": 17.4486,
            "lng": 78.3908,
            "address": "Madhapur, Hyderabad"
        },
        "radius_km": 20.0
    }
    response = client.post("/agent/nearby-hospitals", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "google_maps_directions_url" in data[0]


def test_full_emergency_workflow_execution():
    request = EmergencyWorkflowRequest(
        symptoms="Severe chest pain radiating to left arm, sweating, shortness of breath",
        patient_age=60,
        patient_gender="Male",
        patient_location=LocationSchema(lat=17.4486, lng=78.3908, address="SNIST, Hyderabad")
    )
    response = run_full_emergency_workflow(request)

    assert response.triage.category == "CARDIAC_EMERGENCY"
    assert response.triage.required_specialty == "CARDIOLOGY"
    assert response.selected_hospital.hospital_id != ""
    assert response.assigned_ambulance.vehicle_number != ""
    assert response.assigned_ambulance.dispatch_status == "SIMULATED_DISPATCHED"
    assert response.hospital_notification.alert_message != ""
    assert len(response.nearby_hospitals) >= 1
    assert "direct access if feasible" in response.direct_travel_disclaimer.lower()
    assert len(response.workflow_steps) == 6


def test_emergency_endpoint_http():
    payload = {
        "symptoms": "Severe acute respiratory distress and severe shortness of breath",
        "patient_age": 45,
        "patient_location": {
            "lat": 17.4486,
            "lng": 78.3908,
            "address": "SNIST, Hyderabad"
        }
    }
    response = client.post("/agent/emergency", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["triage"]["category"] == "RESPIRATORY_DISTRESS"
    assert data["triage"]["required_specialty"] == "PULMONOLOGY"
    assert "selected_hospital" in data
    assert "assigned_ambulance" in data
    assert "hospital_notification" in data
    assert "nearby_hospitals" in data
    assert len(data["nearby_hospitals"]) >= 1
    assert "direct_travel_disclaimer" in data
    assert len(data["workflow_steps"]) == 6
