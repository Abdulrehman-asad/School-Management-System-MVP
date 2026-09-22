"""
Authentication routes.

Endpoints:
  POST /api/auth/login            - login with username/email + password
  POST /api/auth/refresh           - exchange a refresh token for a new access token
  POST /api/auth/forgot-password   - request a password reset token
  POST /api/auth/reset-password    - reset password using a valid token
  POST /api/auth/change-password   - change password while logged in
  GET  /api/auth/me                - get current logged-in user's profile
"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.user import User
from app.auth.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.auth.dependencies import get_current_user
from app.utils.email_service import send_password_reset_email
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserOut,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(or_(User.username == payload.username, User.email == payload.username))
        .first()
    )

    # Same error for "no user" and "wrong password" — avoids leaking which usernames exist
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated")

    token_data = {"sub": str(user.user_id), "role": user.role.role_name}

    access_expires = timedelta(days=7) if payload.remember_me else None
    access_token = create_access_token(token_data, expires_delta=access_expires)
    refresh_token = create_refresh_token(token_data)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.role_name,
        full_name=user.full_name,
        user_id=user.user_id,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.user_id == int(decoded["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    token_data = {"sub": str(user.user_id), "role": user.role.role_name}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=user.role.role_name,
        full_name=user.full_name,
        user_id=user.user_id,
    )


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Always return a generic success message, whether or not the email exists,
    # so attackers can't use this endpoint to discover valid emails.
    generic_response = {
        "message": "If an account with that email exists, a reset link has been sent."
    }

    if not user:
        return generic_response

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    send_password_reset_email(user.email, user.full_name, reset_token)

    return generic_response


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()

    if not user or not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"message": "Password has been reset successfully"}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role.role_name,
        is_active=current_user.is_active,
    )
