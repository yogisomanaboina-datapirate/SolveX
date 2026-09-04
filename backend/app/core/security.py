import os
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth, firestore

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

db = None
firebase_app = None

def init_firebase():
    global firebase_app, db
    if firebase_admin._apps:
        firebase_app = firebase_admin.get_app()
        db = firestore.client()
        return db

    cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_service_account.json")
    if os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_app = firebase_admin.initialize_app(cred)
            db = firestore.client()
            logger.info("Firebase Admin SDK initialized successfully with service account.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase with credential file: {e}")
            db = None
    else:
        logger.warning(
            f"Firebase service account file not found at '{cred_path}'. "
            "Running with mock fallback database mode."
        )
        try:
            firebase_app = firebase_admin.initialize_app()
            db = firestore.client()
        except Exception as e:
            logger.warning(f"Default Firebase initialization skipped: {e}")
            db = None
    return db

# Initialize Firebase on import
init_firebase()

async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": "Authorization header missing or invalid format"
                }
            }
        )

    token = credentials.credentials

    # Hackathon dev token bypass for local endpoint testing
    if token in ["firebase_id_token", "mock_token", "dev_token_user_123"] or token.startswith("dev_"):
        return {
            "uid": "user_123",
            "email": "user@example.com",
            "name": "John Doe"
        }

    try:
        if firebase_admin._apps:
            decoded_token = auth.verify_id_token(token)
            return {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name", "User")
            }
        else:
            return {
                "uid": "user_123",
                "email": "user@example.com",
                "name": "John Doe"
            }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired Firebase authentication token"
                }
            }
        )
