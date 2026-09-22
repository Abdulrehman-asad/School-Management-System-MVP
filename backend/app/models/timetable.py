"""
Timetable model: one row per (section, subject, teacher, day, time-slot).
Student and teacher timetables are both just filtered views of this table.
"""

from sqlalchemy import Column, Integer, BigInteger, Time, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"


class TimetableEntry(Base):
    __tablename__ = "timetable"

    timetable_id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    section = relationship("Section")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
