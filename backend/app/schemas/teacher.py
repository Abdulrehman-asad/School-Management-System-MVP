"""
Pydantic request/response models for the Teacher module.

Creating a teacher creates BOTH a `users` row (for login) and a `teachers` row
(for teacher-specific data) in one transaction.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from decimal import Decimal

from app.models.teacher import TeacherStatus


class TeacherCreate(BaseModel):
    # --- login/account fields ---
    full_name: str = Field(..., max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    username: str = Field(..., max_length=80)
    password: str = Field(..., min_length=8)

    # --- teacher-specific fields ---
    employee_code: Optional[str] = Field(None, max_length=30)
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    joining_date: Optional[date] = None
    cnic: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    salary: Optional[Decimal] = None
    section_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    address: Optional[str] = None
    salary: Optional[Decimal] = None
    status: Optional[TeacherStatus] = None
    is_active: Optional[bool] = None


class TeacherOut(BaseModel):
    teacher_id: int
    user_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    username: str
    employee_code: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    joining_date: Optional[date] = None
    address: Optional[str] = None
    salary: Optional[Decimal] = None
    status: TeacherStatus
    is_active: bool
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectAssignmentCreate(BaseModel):
    subject_id: int
    section_id: int


class SubjectAssignmentOut(BaseModel):
    assignment_id: int
    teacher_id: int
    subject_id: int
    section_id: int

    class Config:
        from_attributes = True



class TeacherSectionAssign(BaseModel):
    section_id: int


class TeacherSectionOut(BaseModel):
    teacher_id: int
    section_id: int
    class_id: int
    class_name: str
    section_name: str