import pytest

@pytest.fixture
def mock_agent_response():
    return {
        "success": True,
        "data": {
            "severity": 4,
            "condition": "cardiac",
            "hospitalId": "hosp_456",
            "hospitalName": "City Hospital",
            "ETA": 8,
            "firstAid": "Chew 300mg aspirin, sit down",
            "aiReasoning": "Severity 4/5 indicates cardiac emergency...",
            "confidence": 0.92
        }
    }

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer dev_token_user_123"}
