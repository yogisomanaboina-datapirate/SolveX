from fastapi.testclient import TestClient
from main import app
from agents.chat.schemas import ChatbotRequest, PatientContextProfile
from workflows.chat import run_chatbot_workflow

client = TestClient(app)


def test_general_health_query():
    request = ChatbotRequest(
        message="What is the normal reference range for fasting blood glucose?"
    )
    response = run_chatbot_workflow(request)

    assert response.intent in ["GENERAL_HEALTH_QUERY", "MEDICATION_INQUIRY"]
    assert response.personalized_data_used is False
    assert response.message != ""
    assert "disclaimer" in response.model_dump()
    assert len(response.suggested_quick_actions) >= 1
    assert len(response.workflow_steps) == 4


def test_personalized_patient_query():
    profile = PatientContextProfile(
        patient_name="Rahul Sharma",
        patient_age=42,
        patient_gender="Male",
        active_conditions=["Hypertension", "Mild Anemia"],
        current_medications=["Tab Amlodipine 5mg", "Tab Iron Folic Acid"],
        latest_lab_results={"Hemoglobin": "11.2 g/dL"}
    )
    request = ChatbotRequest(
        message="How is my hemoglobin level doing according to my latest lab report?",
        patient_profile=profile
    )
    response = run_chatbot_workflow(request)

    assert response.personalized_data_used is True
    assert response.intent in ["PERSONALIZED_PATIENT_QUERY", "GENERAL_HEALTH_QUERY"]
    assert response.message != ""
    assert "disclaimer" in response.model_dump()


def test_emergency_guidance_query():
    request = ChatbotRequest(
        message="I have severe sudden chest pain radiating to my arm and severe shortness of breath!"
    )
    response = run_chatbot_workflow(request)

    assert response.intent == "EMERGENCY_GUIDANCE"
    assert response.next_action in ["TRIGGER_EMERGENCY_WORKFLOW", "CONTINUE_CONVERSATION"]
    assert "emergency" in response.message.lower() or "ambulance" in response.message.lower()


def test_chatbot_endpoint_http():
    payload = {
        "message": "When should I take my prescribed blood pressure medication?",
        "patient_profile": {
            "patient_name": "Priya",
            "active_conditions": ["Hypertension"],
            "current_medications": ["Tab Telmisartan 40mg"]
        }
    }
    response = client.post("/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "intent" in data
    assert data["personalized_data_used"] is True
    assert "disclaimer" in data
    assert len(data["workflow_steps"]) == 4
