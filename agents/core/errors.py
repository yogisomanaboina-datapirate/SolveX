from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.logging import logger


class AgentException(Exception):
    """Base exception for all Agent errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class FeatherlessAPIError(AgentException):
    """Error interacting with Featherless.ai LLM service."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Featherless AI Error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class ToolExecutionError(AgentException):
    """Error executing a deterministic agent tool."""
    def __init__(self, tool_name: str, message: str):
        super().__init__(
            message=f"Tool Execution Error ({tool_name}): {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"tool_name": tool_name}
        )


class InvalidInputException(AgentException):
    """Validation or malformed request payload error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


def register_error_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application."""

    @app.exception_handler(AgentException)
    async def agent_exception_handler(request: Request, exc: AgentException):
        logger.error(f"AgentException caught on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
                "service": "lifelink-agent"
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "An unexpected error occurred within the LifeLink Agent service.",
                "details": {"error_type": exc.__class__.__name__},
                "service": "lifelink-agent"
            }
        )
