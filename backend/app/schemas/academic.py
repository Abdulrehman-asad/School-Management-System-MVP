"""
Pydantic request/response models for Classes, Sections, and Subjects.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------
# Class
# ---------------------------------------------------------------------
class ClassCreate(BaseModel):
    class_name: str = Field(..., max_length=50, examples=["Class 9"])
    class_order: int = 0


class ClassUpdate(BaseModel):
    class_name: Optional[str] = Field(None, max_length=50)
    class_order: Optional[int] = None


class ClassOut(BaseModel):
    class_id: int
    class_name: str
    class_order: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------
class SectionCreate(BaseModel):
    class_id: int
    section_name: str = Field(..., max_length=20, examples=["A"])
    room_number: Optional[str] = None
    capacity: int = 40
    class_teacher_id: Optional[int] = None


class SectionUpdate(BaseModel):
    section_name: Optional[str] = Field(None, max_length=20)
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    class_teacher_id: Optional[int] = None


class SectionOut(BaseModel):
    section_id: int
    class_id: int
    section_name: str
    room_number: Optional[str] = None
    capacity: int
    class_teacher_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Subject
# ---------------------------------------------------------------------
class SubjectCreate(BaseModel):
    subject_name: str = Field(..., max_length=100, examples=["Mathematics"])
    subject_code: Optional[str] = Field(None, max_length=20)
    class_id: int
    is_optional: bool = False


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = Field(None, max_length=100)
    subject_code: Optional[str] = Field(None, max_length=20)
    is_optional: Optional[bool] = None


class SubjectOut(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    class_id: int
    is_optional: bool

    class Config:
        from_attributes = True
