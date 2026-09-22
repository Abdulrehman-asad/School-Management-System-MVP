"""
Routes for Results, printable result cards, and class position lists.

Enter/update/delete results: teacher, admin, super_admin.
Read: admin/super_admin/teacher can view any student; a student can view only
their own result card (needed for the Student Dashboard).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import result_controller as crud
from app.controllers.teacher_controller import get_teacher_by_user_id
from app.controllers.student_controller import get_student_by_user_id
from app.schemas.exam import (
    BulkResultCreate, ResultUpdate, ResultOut, ResultCardOut, PositionListEntry
)

router = APIRouter(prefix="/api/results", tags=["Results"])

ADMIN_ONLY = require_roles("admin", "super_admin")
STAFF = require_roles("admin", "super_admin", "teacher")


@router.post("", response_model=List[ResultOut], status_code=201)
def enter_results(
    payload: BulkResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role not in ("teacher", "admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    if role == "teacher":
        teacher = get_teacher_by_user_id(db, current_user.user_id)
        entered_by_id = teacher.teacher_id
    else:
        # Admin/super_admin entering results directly (e.g. importing marks,
        # or covering for a teacher) — not attributed to a specific teacher.
        entered_by_id = None

    return crud.enter_bulk_results(db, payload, entered_by_id)


@router.get("", response_model=List[ResultOut])
def list_results(
    schedule_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        student_id = student.student_id  # force students to only see their own results
    elif role not in ("admin", "super_admin", "teacher"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.list_results(db, schedule_id, student_id, skip, limit)


@router.put("/{result_id}", response_model=ResultOut)
def update_result(result_id: int, payload: ResultUpdate, db: Session = Depends(get_db), _=Depends(STAFF)):
    return crud.update_result(db, result_id, payload)


@router.delete("/{result_id}", status_code=204)
def delete_result(result_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_result(db, result_id)


# ---------------------------------------------------------------------
# Result cards & position lists
# ---------------------------------------------------------------------
@router.get("/report-card/{student_id}/{exam_id}", response_model=ResultCardOut)
def get_result_card(
    student_id: int, exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        if student.student_id != student_id:
            raise HTTPException(status_code=403, detail="You can only view your own result card")
    elif role not in ("admin", "super_admin", "teacher"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.get_result_card(db, student_id, exam_id)


@router.get("/position-list/{exam_id}", response_model=List[PositionListEntry])
def get_position_list(exam_id: int, db: Session = Depends(get_db), _=Depends(STAFF)):
    return crud.get_position_list(db, exam_id)
