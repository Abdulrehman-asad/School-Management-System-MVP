"""
Pydantic request/response models for Notifications.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    notification_id: int
    user_id: int
    title: str
    message: Optional[str] = None
    type: NotificationType
    reference_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UnreadCountOut(BaseModel):
    unread_count: int


class MarkAllReadOut(BaseModel):
    marked_count: int
