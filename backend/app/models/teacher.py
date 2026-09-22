"""
Teacher model. A Teacher is always backed by a User row (for login),
plus teacher-specific fields (employee code, qualifications, salary, etc.)
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Numeric, Date, DateTime, ForeignKey,
    Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class TeacherStatus(str, enum.Enum):
    active = "active"
    on_leave = "on_leave"
    resigned = "resigned"
    terminated = "terminated"


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    employee_code = Column(String(30), unique=True, nullable=True)
    qualification = Column(String(255))
    specialization = Column(String(150))
    joining_date = Column(Date)
    cnic = Column(String(20))
    address = Column(String(255))
    salary = Column(Numeric(10, 2))
    status = Column(Enum(TeacherStatus), default=TeacherStatus.active)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    subject_assignments = relationship(
        "TeacherSubjectAssignment", back_populates="teacher", cascade="all, delete-orphan"
    )


class TeacherSubjectAssignment(Base):
    """Which teacher teaches which subject in which section."""
    __tablename__ = "teacher_subject_assignments"
    __table_args__ = (
        UniqueConstraint("teacher_id", "subject_id", "section_id", name="uq_teacher_subject_section"),
    )

    assignment_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    teacher = relationship("Teacher", back_populates="subject_assignments")
    subject = relationship("Subject")
    section = relationship("Section")
