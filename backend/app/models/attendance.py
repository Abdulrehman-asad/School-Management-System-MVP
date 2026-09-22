"""
Attendance model. One row per student per day.
Marked by a teacher, scoped to a section.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, DateTime, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    leave = "leave"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "attendance_date", name="uq_student_date"),)

    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(BigInteger, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False)
    marked_by = Column(BigInteger, ForeignKey("teachers.teacher_id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    remarks = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student")
    section = relationship("Section")
    marked_by_teacher = relationship("Teacher")
