import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.notifications import get_due_reminders, mark_reminder_sent, send_push_notification

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_deliver_due_reminders():
    """
    Periodic background job: Scans due medication reminders and triggers FCM push notifications.
    """
    due_reminders = get_due_reminders()
    if not due_reminders:
        return

    logger.info(f"[APScheduler] Found {len(due_reminders)} due medication reminder(s) to process.")
    for r in due_reminders:
        reminder_id = r.get("reminder_id")
        user_id = r.get("user_id")
        med_name = r.get("medication_name", "Medication")
        dosage = r.get("dosage", "1 dose")

        logger.info(f"[APScheduler] Processing due reminder '{reminder_id}' for user '{user_id}'...")

        # 1. Trigger FCM Notification
        title = "LifeLink AI Medication Reminder"
        body = f"Time to take your scheduled medication: {med_name} ({dosage})."
        data = {
          "type": "MEDICATION_REMINDER",
          "reminder_id": reminder_id,
          "medication_name": med_name,
          "route": "/medications"
        }

        success = send_push_notification(user_id=user_id, title=title, body=body, data=data)

        # 2. Mark Sent to prevent duplicate notifications (Idempotency)
        if success:
            mark_reminder_sent(reminder_id)
            logger.info(f"[APScheduler] Successfully delivered & marked reminder '{reminder_id}' as SENT.")
        else:
            logger.warning(f"[APScheduler] Failed to deliver FCM notification for reminder '{reminder_id}'.")

def start_background_scheduler():
    """
    Starts the APScheduler background worker loop.
    """
    if not scheduler.running:
        scheduler.add_job(
            check_and_deliver_due_reminders,
            'interval',
            seconds=10,
            id='medication_reminder_job',
            replace_existing=True
        )
        scheduler.start()
        logger.info("[APScheduler] Background medication reminder scheduler started (interval: 10s).")

def stop_background_scheduler():
    """
    Stops the background scheduler gracefully.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[APScheduler] Background medication reminder scheduler shut down.")
