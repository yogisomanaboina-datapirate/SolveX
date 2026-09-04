from fastapi.testclient import TestClient
from app.main import app
from tests.mocks import mock_agent_response, auth_headers

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_signup():
    response = client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "Test123!",
        "name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"

def test_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Test123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]

def test_me(auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "user@example.com"

def test_hospitals_list(auth_headers):
    response = client.get("/api/v1/hospitals", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

def test_hospital_detail(auth_headers):
    response = client.get("/api/v1/hospitals/hosp_1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["hospitalId"] == "hosp_1"

def test_emergency_triage_autonomous_dispatch(auth_headers):
    payload = {
        "symptoms": "chest pain, left arm numbness, sweating",
        "location": {"lat": 17.385, "lng": 78.486},
        "patientAge": 45,
        "medicalHistory": ["diabetes", "hypertension"]
    }
    response = client.post("/api/v1/triage/emergency", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["severity"] >= 4
    assert data["data"]["action"] == "ambulance_dispatched"
    assert data["data"]["ambulanceId"] is not None

def test_claims_submission(auth_headers):
    payload = {
        "patientId": "user_456",
        "insuranceProvider": "Aetna",
        "policyNumber": "POL123456",
        "claimedAmount": 5000.0
    }
    response = client.post("/api/v1/claims", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "approved"
    assert data["data"]["approvedAmount"] == 5000.0

def test_beds_query_and_update(auth_headers):
    response = client.get("/api/v1/beds/hosp_1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    update_payload = {"ICU": 10, "ventilator": 5, "general": 30}
    update_resp = client.put("/api/v1/beds/hosp_1", json=update_payload, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["ICU"] == 10

def test_medications_list(auth_headers):
    response = client.get("/api/v1/medications/user_123", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

def test_ambulance_simulate(auth_headers):
    sim_payload = {"targetLat": 17.4239, "targetLng": 78.4116, "steps": 5}
    response = client.post("/api/v1/ambulance/amb_123/simulate", json=sim_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["path"]) == 5
