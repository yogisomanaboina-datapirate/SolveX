from fastapi.testclient import TestClient
from main import app
from agents.ambulance.schemas import TriageRequest
from agents.ambulance.triage import triage_agent

client = TestClient(app)


def test_triage_agent_cardiac_heuristic():
    request = TriageRequest(
        symptoms="Severe crushing chest pain radiating to jaw and left arm, accompanied by sweating.",
        patient_age=58,
        patient_gender="Male",
        vital_signs={"heart_rate": 110, "blood_pressure": "150/95"}
    )
    result = triage_agent.evaluate_triage(request)

    assert result.urgency in ["HIGH", "CRITICAL"]
    assert result.category in ["CARDIAC_EMERGENCY", "CARDIAC"]
    assert result.required_specialty == "CARDIOLOGY"
    assert result.recommended_action == "IMMEDIATE_AMBULANCE_DISPATCH"
    assert result.confidence > 0.8
    assert len(result.workflow_steps) >= 2


def test_triage_agent_respiratory_heuristic():
    request = TriageRequest(
        symptoms="Severe asthma attack, struggling for breath, wheezing uncontrollably.",
        patient_age=34
    )
    result = triage_agent.evaluate_triage(request)

    assert result.category == "RESPIRATORY_DISTRESS"
    assert result.required_specialty == "PULMONOLOGY"
    assert result.urgency == "HIGH"


def test_triage_endpoint_http():
    payload = {
        "symptoms": "Sudden onset weakness on left side of face and arm, slurred speech.",
        "patient_age": 65,
        "patient_gender": "Female"
    }
    response = client.post("/agent/triage", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["category"] == "NEUROLOGICAL_STROKE"
    assert data["required_specialty"] == "NEUROLOGY"
    assert data["urgency"] == "CRITICAL"
    assert "disclaimer" in data
    assert len(data["workflow_steps"]) >= 2
