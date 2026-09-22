"""
Pydantic request/response models for the Examination module:
Exams, per-subject exam schedules, Results, GPA, and printable result cards.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import date, time
from decimal import Decimal


# ---------------------------------------------------------------------
# Exam
# ---------------------------------------------------------------------
class ExamCreate(BaseModel):
    exam_name: str = Field(..., max_length=100, examples=["Mid Term"])
    class_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    academic_year: Optional[str] = Field(None, max_length=20, examples=["2025-2026"])


class ExamUpdate(BaseModel):
    exam_name: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    academic_year: Optional[str] = Field(None, max_length=20)


class ExamOut(BaseModel):
    exam_id: int
    exam_name: str
    class_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    academic_year: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Exam Subject Schedule
# ---------------------------------------------------------------------
class ExamScheduleCreate(BaseModel):
    subject_id: int
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    total_marks: int = 100
    passing_marks: int = 40

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.passing_marks > self.total_marks:
            raise ValueError("passing_marks cannot exceed total_marks")
        return self


class ExamScheduleUpdate(BaseModel):
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    total_marks: Optional[int] = None
    passing_marks: Optional[int] = None


class ExamScheduleOut(BaseModel):
    schedule_id: int
    exam_id: int
    subject_id: int
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    total_marks: int
    passing_marks: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------
class ResultEntry(BaseModel):
    student_id: int
    marks_obtained: Decimal = Field(..., ge=0)
    remarks: Optional[str] = None


class BulkResultCreate(BaseModel):
    schedule_id: int
    results: List[ResultEntry] = Field(..., min_length=1)


class ResultUpdate(BaseModel):
    marks_obtained: Optional[Decimal] = Field(None, ge=0)
    remarks: Optional[str] = None


class ResultOut(BaseModel):
    result_id: int
    student_id: int
    schedule_id: int
    marks_obtained: Decimal
    grade: Optional[str] = None
    remarks: Optional[str] = None
    entered_by: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Report card / GPA / position list
# ---------------------------------------------------------------------
class SubjectResultLine(BaseModel):
    subject_id: int
    subject_name: str
    marks_obtained: Decimal
    total_marks: int
    passing_marks: int
    grade: str
    is_pass: bool


class ResultCardOut(BaseModel):
    student_id: int
    student_name: str
    registration_no: str
    exam_id: int
    exam_name: str
    subjects: List[SubjectResultLine]
    total_marks_obtained: Decimal
    total_marks_possible: int
    overall_percentage: float
    overall_grade: str
    gpa: float
    position: Optional[int] = None


class PositionListEntry(BaseModel):
    student_id: int
    student_name: str
    registration_no: str
    total_marks_obtained: Decimal
    overall_percentage: float
    gpa: float
    position: int
