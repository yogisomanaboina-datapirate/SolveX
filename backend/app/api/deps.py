from typing import Dict, Any
from fastapi import Depends
from app.core.security import verify_firebase_token

async def get_current_user(current_user: Dict[str, Any] = Depends(verify_firebase_token)) -> Dict[str, Any]:
    return current_user
