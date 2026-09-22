"""
Pydantic request/response models for the authentication module.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username, email, or registration number")
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: Optional[str] = None
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
