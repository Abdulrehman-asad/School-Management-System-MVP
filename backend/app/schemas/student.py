"""
Pydantic request/response models for the Student module.

Creating a student creates a `users` row (for login) and a `students` row
(for student-specific data) in one transaction. registration_no is generated
server-side if not supplied.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

from app.models.student import GenderEnum, StudentStatus


class StudentCreate(BaseModel):
    # --- login/account fields ---
    full_name: str = Field(..., max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    username: str = Field(..., max_length=80)
    password: str = Field(..., min_length=8)

    # --- student-specific fields ---
    section_id: int
    parent_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: GenderEnum = GenderEnum.female
    admission_date: Optional[date] = None
    address: Optional[str] = None
    blood_group: Optional[str] = Field(None, max_length=5)
    registration_no: Optional[str] = Field(
        None, max_length=30, description="Auto-generated if left blank"
    )


class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    section_id: Optional[int] = None
    parent_id: Optional[int] = None
    address: Optional[str] = None
    blood_group: Optional[str] = Field(None, max_length=5)
    status: Optional[StudentStatus] = None
    is_active: Optional[bool] = None


class StudentOut(BaseModel):
    student_id: int
    user_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    username: str
    registration_no: str
    section_id: int
    parent_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: GenderEnum
    admission_date: Optional[date] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    status: StudentStatus
    is_active: bool
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True
