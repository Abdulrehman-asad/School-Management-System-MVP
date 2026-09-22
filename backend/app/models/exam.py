"""
Examination module models: Exam (e.g. "Mid Term"), the per-subject schedule
within that exam, and the Results recorded against that schedule.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, Time, DateTime, Numeric,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(100), nullable=False)          # e.g. "Mid Term", "Final Term"
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    academic_year = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    school_class = relationship("SchoolClass")
    schedules = relationship("ExamSubjectSchedule", back_populates="exam", cascade="all, delete-orphan")


class ExamSubjectSchedule(Base):
    """One row per (exam, subject): when it's held and how it's graded."""
    __tablename__ = "exam_subject_schedule"

    schedule_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    exam_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    total_marks = Column(Integer, default=100)
    passing_marks = Column(Integer, default=40)

    exam = relationship("Exam", back_populates="schedules")
    subject = relationship("Subject")
    results = relationship("Result", back_populates="schedule", cascade="all, delete-orphan")


class Result(Base):
    __tablename__ = "results"
    __table_args__ = (UniqueConstraint("student_id", "schedule_id", name="uq_student_schedule"),)

    result_id = Column(BigInteger, primary_key=True, index=True)
    student_id = Column(BigInteger, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("exam_subject_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
    marks_obtained = Column(Numeric(5, 2), nullable=False)
    grade = Column(String(5))
    remarks = Column(String(255))
    entered_by = Column(BigInteger, ForeignKey("teachers.teacher_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    student = relationship("Student")
    schedule = relationship("ExamSubjectSchedule", back_populates="results")
    entered_by_teacher = relationship("Teacher")
