import time
import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.triage import router as triage_router
from app.api.v1.ambulance import router as ambulance_router
from app.api.v1.hospitals import router as hospitals_router
from app.api.v1.secondary import router as secondary_router

from contextlib import asynccontextmanager
from app.api.v1.notifications import router as notifications_router
from app.services.scheduler import start_background_scheduler, stop_background_scheduler

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LifeLink AI Backend Gateway...")
    start_background_scheduler()
    yield
    logger.info("Shutting down LifeLink AI Backend Gateway...")
    stop_background_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LifeLink AI - Autonomous Emergency Healthcare System Backend API",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "auth", "description": "Authentication & User endpoints"},
        {"name": "triage", "description": "AI-powered emergency triage & autonomous ambulance dispatch"},
        {"name": "ambulance", "description": "Real-time ambulance tracking, simulation & status updates"},
        {"name": "hospitals", "description": "Hospital bed & resource query endpoints"},
        {"name": "secondary", "description": "Insurance claims, bed management & medication schedules"},
        {"name": "notifications", "description": "Firebase Cloud Messaging & Medication Push Reminders"}
    ]
)

# Request ID & Performance Timing Middleware
@app.middleware("http")
async def add_process_time_and_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4().hex[:8])
    start_time = time.time()
    logger.info(f"REQ [{request_id}] START {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    logger.info(f"REQ [{request_id}] END {request.method} {request.url.path} - Status {response.status_code} ({process_time:.4f}s)")
    return response

# CORS configuration allowing hackathon frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(triage_router, prefix=settings.API_V1_STR)
app.include_router(ambulance_router, prefix=settings.API_V1_STR)
app.include_router(hospitals_router, prefix=settings.API_V1_STR)
app.include_router(secondary_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)

# Global Exception Handler for uniform error format
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc) or "An unexpected server error occurred."
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
