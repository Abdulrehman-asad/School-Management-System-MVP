"""
Notification model — one row per user per event (homework assigned, attendance
marked, exam scheduled, fee challan generated, notice posted, etc.)

Created by helper functions in app/controllers/notification_controller.py, called
from other modules (homework, fees, notices, ...) whenever something notification-
worthy happens.
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class NotificationType(str, enum.Enum):
    homework = "homework"
    attendance = "attendance"
    exam = "exam"
    fee = "fee"
    notice = "notice"
    general = "general"


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(500))
    type = Column(Enum(NotificationType), default=NotificationType.general)
    reference_id = Column(BigInteger, nullable=True)   # id of the related record (homework_id, exam_id, etc.)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
