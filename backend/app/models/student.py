"""
Parent and Student models.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.session import Base


class ParentGuardian(Base):
    __tablename__ = "parents"

    parent_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    cnic = Column(String(20))
    occupation = Column(String(100))
    address = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    children = relationship("Student", back_populates="parent")


class GenderEnum(str, enum.Enum):
    female = "female"
    male = "male"
    other = "other"


class StudentStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    graduated = "graduated"
    expelled = "expelled"


class Student(Base):
    __tablename__ = "students"

    student_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    registration_no = Column(String(30), unique=True, nullable=False)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("parents.parent_id", ondelete="SET NULL"), nullable=True)
    date_of_birth = Column(Date)
    gender = Column(Enum(GenderEnum), default=GenderEnum.female)
    admission_date = Column(Date)
    address = Column(String(255))
    blood_group = Column(String(5))
    status = Column(Enum(StudentStatus), default=StudentStatus.active)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    section = relationship("Section", back_populates="students")
    parent = relationship("ParentGuardian", back_populates="children")
