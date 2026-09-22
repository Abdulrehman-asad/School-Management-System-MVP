"""
Business logic for Classes, Sections, and Subjects.
Kept separate from routes so the same logic could be reused (e.g. by a future
bulk-import script) without going through HTTP.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.academic import SchoolClass, Section, Subject
from app.schemas.academic import (
    ClassCreate, ClassUpdate, SectionCreate, SectionUpdate, SubjectCreate, SubjectUpdate
)


# ---------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------
def create_class(db: Session, payload: ClassCreate) -> SchoolClass:
    new_class = SchoolClass(class_name=payload.class_name, class_order=payload.class_order)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


def list_classes(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(SchoolClass)
        .order_by(SchoolClass.class_order.asc(), SchoolClass.class_name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_class(db: Session, class_id: int) -> SchoolClass:
    obj = db.query(SchoolClass).filter(SchoolClass.class_id == class_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return obj


def update_class(db: Session, class_id: int, payload: ClassUpdate) -> SchoolClass:
    obj = get_class(db, class_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_class(db: Session, class_id: int):
    obj = get_class(db, class_id)
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete class: sections or subjects still reference it",
        )


# ---------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------
def create_section(db: Session, payload: SectionCreate) -> Section:
    get_class(db, payload.class_id)  # 404 if class doesn't exist

    existing = (
        db.query(Section)
        .filter(Section.class_id == payload.class_id, Section.section_name == payload.section_name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This section already exists for the selected class",
        )

    new_section = Section(**payload.model_dump())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section


def list_sections(db: Session, class_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(Section)
    if class_id is not None:
        query = query.filter(Section.class_id == class_id)
    return query.order_by(Section.section_name.asc()).offset(skip).limit(limit).all()


def get_section(db: Session, section_id: int) -> Section:
    obj = db.query(Section).filter(Section.section_id == section_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Section not found")
    return obj


def update_section(db: Session, section_id: int, payload: SectionUpdate) -> Section:
    obj = get_section(db, section_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_section(db: Session, section_id: int):
    obj = get_section(db, section_id)
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete section: students are still enrolled in it",
        )


# ---------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------
def create_subject(db: Session, payload: SubjectCreate) -> Subject:
    get_class(db, payload.class_id)  # 404 if class doesn't exist

    new_subject = Subject(**payload.model_dump())
    db.add(new_subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Subject code already exists")
    db.refresh(new_subject)
    return new_subject


def list_subjects(db: Session, class_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(Subject)
    if class_id is not None:
        query = query.filter(Subject.class_id == class_id)
    return query.order_by(Subject.subject_name.asc()).offset(skip).limit(limit).all()


def get_subject(db: Session, subject_id: int) -> Subject:
    obj = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return obj


def update_subject(db: Session, subject_id: int, payload: SubjectUpdate) -> Subject:
    obj = get_subject(db, subject_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_subject(db: Session, subject_id: int):
    obj = get_subject(db, subject_id)
    db.delete(obj)
    db.commit()
