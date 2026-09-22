"""
Business logic for Notifications.

`create_notification` and `create_notifications_bulk` are meant to be called
from OTHER modules (homework, fees, exams, notices, ...) whenever something
notification-worthy happens — they're the "fan-out" helpers referenced in the
spec's Notifications section (Homework, Attendance, Exams, Fees, Notices).
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.utils.ws_manager import manager


def _push(notification: Notification):
    payload = {
        "notification_id": notification.notification_id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type.value if hasattr(notification.type, "value") else notification.type,
        "reference_id": notification.reference_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }
    manager.push_to_user_threadsafe(notification.user_id, payload)


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notif_type: NotificationType = NotificationType.general,
    reference_id: Optional[int] = None,
    commit: bool = True,
) -> Notification:
    notification = Notification(
        user_id=user_id, title=title, message=message,
        type=notif_type, reference_id=reference_id,
    )
    db.add(notification)
    if commit:
        db.commit()
        db.refresh(notification)
        _push(notification)
    return notification


def create_notifications_bulk(
    db: Session,
    user_ids: List[int],
    title: str,
    message: str,
    notif_type: NotificationType = NotificationType.general,
    reference_id: Optional[int] = None,
) -> List[Notification]:
    """Same notification fanned out to many users at once (e.g. a whole section, or 'all')."""
    notifications = [
        Notification(user_id=uid, title=title, message=message, type=notif_type, reference_id=reference_id)
        for uid in user_ids
    ]
    db.add_all(notifications)
    db.commit()
    for n in notifications:
        db.refresh(n)
        _push(n)
    return notifications


# ---------------------------------------------------------------------
# Reading / managing notifications (used by the notification bell UI)
# ---------------------------------------------------------------------
def list_notifications(db: Session, user_id: int, unread_only: bool = False,
                        skip: int = 0, limit: int = 50) -> List[Notification]:
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .count()
    )


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
    obj = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Notification not found")
    obj.is_read = True
    db.commit()
    db.refresh(obj)
    return obj


def mark_all_as_read(db: Session, user_id: int) -> int:
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .update({"is_read": True})
    )
    db.commit()
    return updated


def delete_notification(db: Session, notification_id: int, user_id: int):
    obj = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(obj)
    db.commit()
