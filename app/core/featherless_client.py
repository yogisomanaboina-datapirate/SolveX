import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

api_key = settings.FEATHERLESS_API_KEY or os.getenv("FEATHERLESS_API_KEY")

try:
    from featherless import FeatherlessClient
    client = FeatherlessClient(api_key=api_key) if api_key else None
except ImportError:
    client = None
    logger.info("featherless library not directly imported; calls will route via AI Agent service.")
