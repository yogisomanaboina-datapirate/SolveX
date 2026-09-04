from core.config import settings
from core.featherless import FeatherlessClient


def test_featherless_client_mock_mode():
    settings.use_mock_llm = True
    client = FeatherlessClient()
    assert client.is_available is True

    completion = client.generate_completion("Test prompt")
    assert "[MOCK AI RESPONSE]" in completion
