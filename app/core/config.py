import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LifeLink AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    FIREBASE_CREDENTIALS: str = "firebase_service_account.json"
    FIREBASE_STORAGE_BUCKET: str = "lifelink-ai-hackathon.appspot.com"
    FEATHERLESS_API_KEY: Optional[str] = None
    AGENT_BASE_URL: str = "http://127.0.0.1:8000"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8001

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

