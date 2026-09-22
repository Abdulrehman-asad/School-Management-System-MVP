"""
Routes for Exams and their per-subject schedules.

Create/update/delete: admin & super_admin only.
Read: any authenticated user (teachers/students need this to see upcoming exams).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.controllers import exam_controller as crud
from app.schemas.exam import (
    ExamCreate, ExamUpdate, ExamOut,
    ExamScheduleCreate, ExamScheduleUpdate, ExamScheduleOut,
)

router = APIRouter(prefix="/api/exams", tags=["Examinations"])

ADMIN_ONLY = require_roles("admin", "super_admin")


@router.post("", response_model=ExamOut, status_code=201)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_exam(db, payload)


@router.get("", response_model=List[ExamOut])
def list_exams(
    class_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_exams(db, class_id, skip, limit)


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_exam(db, exam_id)


@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, payload: ExamUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_exam(db, exam_id, payload)


@router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_exam(db, exam_id)


# ---------------------------------------------------------------------
# Exam subject schedules
# ---------------------------------------------------------------------
@router.post("/{exam_id}/schedule", response_model=ExamScheduleOut, status_code=201)
def create_schedule(
    exam_id: int, payload: ExamScheduleCreate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.create_schedule(db, exam_id, payload)


@router.get("/{exam_id}/schedule", response_model=List[ExamScheduleOut])
def list_schedules(exam_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.list_schedules(db, exam_id)


@router.get("/schedule/{schedule_id}", response_model=ExamScheduleOut)
def get_schedule(schedule_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_schedule(db, schedule_id)


@router.put("/schedule/{schedule_id}", response_model=ExamScheduleOut)
def update_schedule(
    schedule_id: int, payload: ExamScheduleUpdate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.update_schedule(db, schedule_id, payload)


@router.delete("/schedule/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_schedule(db, schedule_id)
