from fastapi.testclient import TestClient
from main import app
from core.config import settings
from core.featherless import FeatherlessClient

client = TestClient(app)


def test_featherless_client_mock_mode():
    settings.use_mock_llm = True
    client = FeatherlessClient()
    assert client.is_available is True

    completion = client.generate_completion("Test prompt")
    assert "[MOCK AI RESPONSE]" in completion


def test_featherless_test_connection_endpoint():
    response = client.get("/agent/test-featherless")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "api_key_detected" in data
    assert "model_detected" in data
    assert "model_used" in data
    assert "error" in data

