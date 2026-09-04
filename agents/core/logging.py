import logging
import sys
from typing import Any, Dict, Optional
from core.config import settings

# Configure root logger format
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("lifelink-agent")


def get_logger(name: str) -> logging.Logger:
    """Get a named sub-logger."""
    return logging.getLogger(f"lifelink-agent.{name}")


def log_workflow_event(
    workflow_name: str,
    step_number: int,
    step_name: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an observable workflow milestone step for hackathon demo tracing.
    Example output: [EMERGENCY WORKFLOW] [Step 2] Triage completed - Details: {...}
    """
    event_str = f"[{workflow_name.upper()}] [Step {step_number}] {step_name}"
    if details:
        logger.info(f"{event_str} | Data: {details}")
    else:
        logger.info(event_str)
