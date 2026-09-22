"""
Routes for Timetable.

Create/update/delete: admin, super_admin only.
Read: any authenticated user — with convenience filters for "my timetable"
(teacher's own schedule) and "my section's timetable" (student's own schedule).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.timetable import DayOfWeek
from app.controllers import timetable_controller as crud
from app.controllers.teacher_controller import get_teacher_by_user_id
from app.controllers.student_controller import get_student_by_user_id
from app.schemas.timetable import TimetableEntryCreate, TimetableEntryUpdate, TimetableEntryOut

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

ADMIN_ONLY = require_roles("admin", "super_admin")


@router.post("", response_model=TimetableEntryOut, status_code=201)
def create_timetable_entry(payload: TimetableEntryCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_timetable_entry(db, payload)


@router.get("", response_model=List[TimetableEntryOut])
def list_timetable(
    section_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    day_of_week: Optional[DayOfWeek] = Query(None),
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_timetable(db, section_id, teacher_id, day_of_week)


@router.get("/my-schedule", response_model=List[TimetableEntryOut])
def my_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convenience endpoint: teachers get their own timetable, students get their section's."""
    role = current_user.role.role_name

    if role == "teacher":
        teacher = get_teacher_by_user_id(db, current_user.user_id)
        return crud.list_timetable(db, teacher_id=teacher.teacher_id)
    elif role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        return crud.list_timetable(db, section_id=student.section_id)
    else:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is for teachers and students; use /api/timetable with filters instead",
        )


@router.get("/{timetable_id}", response_model=TimetableEntryOut)
def get_timetable_entry(timetable_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_timetable_entry(db, timetable_id)


@router.put("/{timetable_id}", response_model=TimetableEntryOut)
def update_timetable_entry(
    timetable_id: int, payload: TimetableEntryUpdate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.update_timetable_entry(db, timetable_id, payload)


@router.delete("/{timetable_id}", status_code=204)
def delete_timetable_entry(timetable_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_timetable_entry(db, timetable_id)
