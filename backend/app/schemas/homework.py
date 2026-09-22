"""
Pydantic request/response models for Homework and Homework Submissions.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from app.models.homework import SubmissionStatus


class HomeworkCreate(BaseModel):
    section_id: int
    subject_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    attachment_path: Optional[str] = None
    assigned_date: date
    due_date: date


class HomeworkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    attachment_path: Optional[str] = None
    due_date: Optional[date] = None


class HomeworkOut(BaseModel):
    homework_id: int
    section_id: int
    subject_id: int
    teacher_id: int
    title: str
    description: Optional[str] = None
    attachment_path: Optional[str] = None
    assigned_date: date
    due_date: date

    class Config:
        from_attributes = True


class HomeworkSubmissionCreate(BaseModel):
    file_path: Optional[str] = None


class HomeworkSubmissionOut(BaseModel):
    submission_id: int
    homework_id: int
    student_id: int
    file_path: Optional[str] = None
    submitted_at: datetime
    status: SubmissionStatus
    grade_remarks: Optional[str] = None

    class Config:
        from_attributes = True


class GradeSubmissionRequest(BaseModel):
    grade_remarks: str
