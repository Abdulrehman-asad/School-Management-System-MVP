"""
Pydantic request/response models for Attendance.

Attendance is usually marked for a whole section at once, so we support a
bulk endpoint (one row per student) alongside single-record CRUD.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

from app.models.attendance import AttendanceStatus


class AttendanceRecord(BaseModel):
    student_id: int
    status: AttendanceStatus
    remarks: Optional[str] = None


class BulkAttendanceCreate(BaseModel):
    section_id: int
    attendance_date: date
    records: List[AttendanceRecord] = Field(..., min_length=1)


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None


class AttendanceOut(BaseModel):
    attendance_id: int
    student_id: int
    section_id: int
    marked_by: int
    attendance_date: date
    status: AttendanceStatus
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Used for the student dashboard's attendance percentage widget."""
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    leave_days: int
    percentage: float
