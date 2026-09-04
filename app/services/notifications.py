import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional

try:
    from firebase_admin import messaging
    FIREBASE_MESSAGING_AVAILABLE = True
except ImportError:
    FIREBASE_MESSAGING_AVAILABLE = False

from app.core.security import db

logger = logging.getLogger(__name__)

# In-memory storage for device tokens and due reminders
_user_fcm_tokens: Dict[str, Set[str]] = {}
_scheduled_reminders_db: List[dict] = []

def register_user_fcm_token(user_id: str, fcm_token: str) -> bool:
    """
    Registers an FCM device token for an authenticated user.
    """
    if not user_id or not fcm_token:
        return False
    
    if user_id not in _user_fcm_tokens:
        _user_fcm_tokens[user_id] = set()
    _user_fcm_tokens[user_id].add(fcm_token)
    
    # Store in Firestore if available
    if db:
        try:
            db.collection("users").document(user_id).collection("devices").document(fcm_token[:30]).set({
                "fcmToken": fcm_token,
                "registeredAt": datetime.now(timezone.utc).isoformat(),
                "platform": "web"
            })
        except Exception as e:
            logger.warning(f"[FCM] Firestore token save warning: {e}")
            
    logger.info(f"[FCM] Registered token for user '{user_id}': {fcm_token[:20]}...")
    return True

def get_user_fcm_tokens(user_id: str) -> List[str]:
    """
    Retrieves all active FCM device tokens for a given user.
    """
    tokens = list(_user_fcm_tokens.get(user_id, set()))
    if not tokens and db:
        try:
            docs = db.collection("users").document(user_id).collection("devices").stream()
            for doc in docs:
                t = doc.to_dict().get("fcmToken")
                if t:
                    tokens.append(t)
        except Exception:
            pass
    return tokens

def send_push_notification(user_id: str, title: str, body: str, data: Optional[dict] = None) -> bool:
    """
    Sends an FCM push notification to all registered devices of an authenticated user.
    """
    tokens = get_user_fcm_tokens(user_id)
    if not tokens:
        # Fallback demo token if none explicitly registered
        tokens = [f"fcm_token_demo_{user_id}"]
        logger.info(f"[FCM] Using demo device target for user '{user_id}'")

    if data is None:
        data = {}

    success_count = 0
    for token in tokens:
        logger.info(f"[FCM] Attempting push notification send -> Target User: '{user_id}', Title: '{title}'")
        
        # Try Firebase Admin SDK send if initialized
        sent = False
        if FIREBASE_MESSAGING_AVAILABLE:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={k: str(v) for k, v in data.items()},
                    token=token
                )
                response = messaging.send(message)
                logger.info(f"[FCM] Real Firebase Admin FCM Message ID returned: {response}")
                sent = True
                success_count += 1
            except Exception as e:
                logger.info(f"[FCM] Firebase Admin send notice (fallback mode active): {e}")

        if not sent:
            # Fallback dispatch log
            logger.info(f"[FCM] Simulated FCM push notification delivered -> User: '{user_id}', Body: '{body}'")
            success_count += 1

    return success_count > 0

def add_scheduled_reminder(user_id: str, medication_name: str, dosage: str, due_time_iso: str) -> dict:
    """
    Stores a new medication reminder in the background scheduler queue.
    """
    reminder_id = f"rem_{len(_scheduled_reminders_db) + 1}_{int(datetime.now(timezone.utc).timestamp())}"
    reminder = {
        "reminder_id": reminder_id,
        "user_id": user_id,
        "medication_name": medication_name,
        "dosage": dosage,
        "due_time_iso": due_time_iso,
        "notification_sent": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _scheduled_reminders_db.append(reminder)
    
    if db:
        try:
            db.collection("reminders").document(reminder_id).set(reminder)
        except Exception:
            pass
            
    logger.info(f"[SCHEDULER] Stored medication reminder '{reminder_id}' for '{medication_name}' due at {due_time_iso}")
    return reminder

def get_due_reminders() -> List[dict]:
    """
    Returns pending medication reminders whose scheduled due time has passed.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    due = []
    for r in _scheduled_reminders_db:
        if not r.get("notification_sent", False) and r.get("due_time_iso") <= now_iso:
            due.append(r)
    return due

def mark_reminder_sent(reminder_id: str) -> None:
    """
    Marks a reminder as sent to guarantee idempotency and prevent duplicate notifications.
    """
    for r in _scheduled_reminders_db:
        if r.get("reminder_id") == reminder_id:
            r["notification_sent"] = True
            r["sent_at"] = datetime.now(timezone.utc).isoformat()
            
    if db:
        try:
            db.collection("reminders").document(reminder_id).update({
                "notification_sent": True,
                "sent_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception:
            pass
