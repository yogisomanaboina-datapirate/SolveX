from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserInfo(BaseModel):
    uid: str
    email: str
    name: str

class AuthData(BaseModel):
    token: str
    user: UserInfo

class AuthResponse(BaseModel):
    success: bool = True
    data: AuthData

class UserMeResponse(BaseModel):
    success: bool = True
    data: UserInfo
