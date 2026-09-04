import logging
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.services.notifications import (
    register_user_fcm_token,
    send_push_notification,
    add_scheduled_reminder,
    _scheduled_reminders_db
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

class RegisterTokenRequest(BaseModel):
    fcmToken: str = Field(description="Firebase Cloud Messaging device registration token")

class TestNotificationRequest(BaseModel):
    title: Optional[str] = "LifeLink AI Medication Reminder"
    body: Optional[str] = "Time to take your scheduled medication (Amoxicillin 500mg)."

class TestReminderRequest(BaseModel):
    medicationName: Optional[str] = "Amoxicillin"
    dosage: Optional[str] = "500mg"
    delaySeconds: Optional[int] = 60

@router.post("/register")
async def register_notification_token(
    req: RegisterTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Registers the authenticated user's Web FCM device token for browser push notifications.
    """
    user_id = current_user.get("uid", "user_123")
    success = register_user_fcm_token(user_id, req.fcmToken)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register FCM token")
    
    return {
        "success": True,
        "message": "FCM device registration token successfully associated with user.",
        "data": {
            "userId": user_id,
            "tokenPreview": f"{req.fcmToken[:15]}..."
        }
    }

@router.post("/test-send")
async def send_test_notification(
    req: TestNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Sends an immediate test push notification via FCM to the authenticated user's device.
    """
    user_id = current_user.get("uid", "user_123")
    sent = send_push_notification(
        user_id=user_id,
        title=req.title,
        body=req.body,
        data={"type": "TEST_NOTIFICATION", "route": "/medications"}
    )
    
    return {
        "success": True,
        "message": "Test push notification dispatched.",
        "delivered": sent
    }

@router.post("/test-reminder")
async def schedule_demo_test_reminder(
    req: TestReminderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    HACKATHON DEMO MODE: Schedules a real medication reminder ~1 minute in the future.
    Flow: Background APScheduler -> FCM Push -> Browser Notification.
    """
    user_id = current_user.get("uid", "user_123")
    delay = req.delaySeconds or 60
    due_dt = datetime.now(timezone.utc) + timedelta(seconds=delay)
    due_iso = due_dt.isoformat()
    
    med_name = req.medicationName or "Amoxicillin (Demo)"
    dosage = req.dosage or "500mg"
    
    reminder = add_scheduled_reminder(
        user_id=user_id,
        medication_name=med_name,
        dosage=dosage,
        due_time_iso=due_iso
    )
    
    return {
        "success": True,
        "message": f"Demo reminder scheduled for '{med_name}' in {delay} seconds.",
        "data": {
            "reminderId": reminder.get("reminder_id"),
            "dueTime": due_iso,
            "delaySeconds": delay
        }
    }
