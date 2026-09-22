"""
Academic structure models: Class, Section, Subject.
These form the backbone that Teachers, Students, Attendance, Exams, etc. all hang off of.
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class SchoolClass(Base):
    """Represents a grade level, e.g. 'Class 9', 'Nursery'. Named SchoolClass to avoid clashing with Python's `class`."""
    __tablename__ = "classes"

    class_id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(50), nullable=False)
    class_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    sections = relationship("Section", back_populates="school_class", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="school_class", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    __table_args__ = (
        UniqueConstraint("class_id", "section_name", name="uq_class_section"),
        UniqueConstraint("class_teacher_id", name="uq_one_section_per_teacher"),
    )

    section_id = Column(Integer, primary_key=True, index=True)

    class_id = Column(
        Integer,
        ForeignKey("classes.class_id", ondelete="CASCADE"),
        nullable=False
    )

    section_name = Column(String(20), nullable=False)
    room_number = Column(String(20))
    capacity = Column(Integer, default=40)

    class_teacher_id = Column(
        BigInteger,
        ForeignKey("teachers.teacher_id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = Column(DateTime, server_default=func.now())

    school_class = relationship(
        "SchoolClass",
        back_populates="sections"
    )

    class_teacher = relationship(
        "Teacher",
        foreign_keys=[class_teacher_id]
    )

    students = relationship(
        "Student",
        back_populates="section"
    )
    section_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String(20), nullable=False)
    room_number = Column(String(20))
    capacity = Column(Integer, default=40)
    class_teacher_id = Column(BigInteger, ForeignKey("teachers.teacher_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    school_class = relationship("SchoolClass", back_populates="sections")
    class_teacher = relationship("Teacher", foreign_keys=[class_teacher_id])
    students = relationship("Student", back_populates="section")


class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    subject_code = Column(String(20), unique=True, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    school_class = relationship("SchoolClass", back_populates="subjects")
