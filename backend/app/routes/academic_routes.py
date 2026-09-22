"""
Routes for Classes, Sections, and Subjects.

Read access: any authenticated user (teachers/students need this to render
timetables, dropdowns, etc.)
Write access: admin / super_admin only.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.controllers import academic_controller as crud
from app.schemas.academic import (
    ClassCreate, ClassUpdate, ClassOut,
    SectionCreate, SectionUpdate, SectionOut,
    SubjectCreate, SubjectUpdate, SubjectOut,
)

router = APIRouter(prefix="/api/academic", tags=["Academic Structure"])

ADMIN_ONLY = require_roles("admin", "super_admin")


# ---------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------
@router.post("/classes", response_model=ClassOut, status_code=201)
def create_class(payload: ClassCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_class(db, payload)


@router.get("/classes", response_model=List[ClassOut])
def list_classes(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_classes(db, skip, limit)


@router.get("/classes/{class_id}", response_model=ClassOut)
def get_class(class_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_class(db, class_id)


@router.put("/classes/{class_id}", response_model=ClassOut)
def update_class(class_id: int, payload: ClassUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_class(db, class_id, payload)


@router.delete("/classes/{class_id}", status_code=204)
def delete_class(class_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_class(db, class_id)


# ---------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------
@router.post("/sections", response_model=SectionOut, status_code=201)
def create_section(payload: SectionCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_section(db, payload)


@router.get("/sections", response_model=List[SectionOut])
def list_sections(
    class_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_sections(db, class_id, skip, limit)


@router.get("/sections/{section_id}", response_model=SectionOut)
def get_section(section_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_section(db, section_id)


@router.put("/sections/{section_id}", response_model=SectionOut)
def update_section(section_id: int, payload: SectionUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_section(db, section_id, payload)


@router.delete("/sections/{section_id}", status_code=204)
def delete_section(section_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_section(db, section_id)


# ---------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------
@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_subject(db, payload)


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(
    class_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_subjects(db, class_id, skip, limit)


@router.get("/subjects/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_subject(db, subject_id)


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_subject(db, subject_id, payload)


@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_subject(db, subject_id)
