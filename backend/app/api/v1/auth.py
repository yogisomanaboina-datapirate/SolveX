import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import SignupRequest, LoginRequest, AuthResponse, UserMeResponse, AuthData, UserInfo
from app.api.deps import get_current_user
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
async def signup(req: SignupRequest):
    uid = f"user_{uuid.uuid4().hex[:8]}"
    email = req.email
    name = req.name

    if firebase_admin._apps:
        try:
            user_record = firebase_auth.create_user(
                email=email,
                password=req.password,
                display_name=name
            )
            uid = user_record.uid
        except Exception as e:
            logger.warning(f"Firebase user creation fallback (using generated ID): {e}")

    return AuthResponse(
        success=True,
        data=AuthData(
            token="firebase_id_token",
            user=UserInfo(
                uid=uid,
                email=email,
                name=name
            )
        )
    )

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    email = req.email
    uid = "user_123"
    name = email.split("@")[0].capitalize()

    if firebase_admin._apps:
        try:
            user_record = firebase_auth.get_user_by_email(email)
            uid = user_record.uid
            name = user_record.display_name or name
        except Exception as e:
            logger.warning(f"Firebase user lookup fallback: {e}")

    return AuthResponse(
        success=True,
        data=AuthData(
            token="firebase_id_token",
            user=UserInfo(
                uid=uid,
                email=email,
                name=name
            )
        )
    )

@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserMeResponse(
        success=True,
        data=UserInfo(
            uid=current_user.get("uid", "user_123"),
            email=current_user.get("email", "user@example.com"),
            name=current_user.get("name", "John Doe")
        )
    )
