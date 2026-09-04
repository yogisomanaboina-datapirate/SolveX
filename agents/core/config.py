import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    LifeLink AI Agent Configuration
    Loads configuration from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Featherless.ai Settings
    featherless_api_key: Optional[str] = None
    featherless_model: str = "Qwen/Qwen2.5-7B-Instruct"
    featherless_base_url: str = "https://api.featherless.ai/v1"
    
    # Service Configuration
    environment: str = "development"
    agent_host: str = "0.0.0.0"
    agent_port: int = 8000
    log_level: str = "INFO"
    
    # Mock Mode for Testing/Dev without API token
    use_mock_llm: bool = False

    @property
    def is_featherless_configured(self) -> bool:
        """Check if Featherless API key is present and not empty."""
        return bool(self.featherless_api_key and self.featherless_api_key.strip() and self.featherless_api_key != "your_featherless_api_key_here")


# Singleton instance
settings = Settings()
