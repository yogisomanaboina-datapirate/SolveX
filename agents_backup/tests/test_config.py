from core.config import Settings


def test_settings_default_values():
    settings = Settings(
        featherless_api_key=None,
        use_mock_llm=True
    )
    assert settings.agent_port == 8000
    assert settings.featherless_base_url == "https://api.featherless.ai/v1"
    assert settings.is_featherless_configured is False
    assert settings.use_mock_llm is True


def test_featherless_configured_property():
    valid_settings = Settings(featherless_api_key="valid_test_key_123")
    assert valid_settings.is_featherless_configured is True

    placeholder_settings = Settings(featherless_api_key="your_featherless_api_key_here")
    assert placeholder_settings.is_featherless_configured is False
