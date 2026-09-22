"""
Notice model — admin/teacher-posted announcements for the notice board.
Creating a notice fans out Notification rows to the relevant audience
(see app/controllers/notice_controller.py).
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class NoticeAudience(str, enum.Enum):
    all = "all"
    teachers = "teachers"
    students = "students"
    parents = "parents"
    specific_class = "specific_class"


class Notice(Base):
    __tablename__ = "notices"

    notice_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    posted_by = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    audience = Column(Enum(NoticeAudience), default=NoticeAudience.all)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="SET NULL"), nullable=True)
    attachment_path = Column(String(255))
    publish_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    posted_by_user = relationship("User")
    school_class = relationship("SchoolClass")
