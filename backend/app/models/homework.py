"""
Homework models: the assignment itself, plus (future-facing) student submissions.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Date, DateTime, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class Homework(Base):
    __tablename__ = "homework"

    homework_id = Column(BigInteger, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(BigInteger, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    attachment_path = Column(String(255))
    assigned_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    section = relationship("Section")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    submissions = relationship("HomeworkSubmission", back_populates="homework", cascade="all, delete-orphan")


class SubmissionStatus(str, enum.Enum):
    submitted = "submitted"
    late = "late"
    graded = "graded"


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"
    __table_args__ = (UniqueConstraint("homework_id", "student_id", name="uq_homework_student"),)

    submission_id = Column(BigInteger, primary_key=True, index=True)
    homework_id = Column(BigInteger, ForeignKey("homework.homework_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(255))
    submitted_at = Column(DateTime, server_default=func.now())
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.submitted)
    grade_remarks = Column(String(255))

    homework = relationship("Homework", back_populates="submissions")
    student = relationship("Student")
