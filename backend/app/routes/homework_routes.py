"""
Routes for Homework.

Create/update/delete: teacher (their own homework), admin, super_admin.
Read: any authenticated user (filtered appropriately on the frontend by
section/subject for students).
Submissions: students submit to their own record; teachers grade.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import homework_controller as crud
from app.controllers.teacher_controller import get_teacher_by_user_id
from app.controllers.student_controller import get_student_by_user_id
from app.schemas.homework import (
    HomeworkCreate, HomeworkUpdate, HomeworkOut,
    HomeworkSubmissionCreate, HomeworkSubmissionOut, GradeSubmissionRequest,
)

router = APIRouter(prefix="/api/homework", tags=["Homework"])

ADMIN_ONLY = require_roles("admin", "super_admin")
TEACHER_OR_ADMIN = require_roles("teacher", "admin", "super_admin")


@router.post("", response_model=HomeworkOut, status_code=201)
def create_homework(
    payload: HomeworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role not in ("teacher", "admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    if role == "teacher":
        teacher = get_teacher_by_user_id(db, current_user.user_id)
        teacher_id = teacher.teacher_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Admins should assign homework via a teacher account",
        )

    return crud.create_homework(db, payload, teacher_id)


@router.get("", response_model=List[HomeworkOut])
def list_homework(
    section_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return crud.list_homework(db, section_id, subject_id, teacher_id, skip, limit)


@router.get("/{homework_id}", response_model=HomeworkOut)
def get_homework(homework_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_homework(db, homework_id)


@router.put("/{homework_id}", response_model=HomeworkOut)
def update_homework(
    homework_id: int, payload: HomeworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "teacher":
        teacher = get_teacher_by_user_id(db, current_user.user_id)
        return crud.update_homework(db, homework_id, payload, teacher.teacher_id)
    elif role in ("admin", "super_admin"):
        # Admins can override the teacher_id ownership check
        obj = crud.get_homework(db, homework_id)
        return crud.update_homework(db, homework_id, payload, obj.teacher_id)
    raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{homework_id}", status_code=204)
def delete_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "teacher":
        teacher = get_teacher_by_user_id(db, current_user.user_id)
        crud.delete_homework(db, homework_id, teacher.teacher_id)
    elif role in ("admin", "super_admin"):
        obj = crud.get_homework(db, homework_id)
        crud.delete_homework(db, homework_id, obj.teacher_id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


# ---------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------
@router.post("/{homework_id}/submit", response_model=HomeworkSubmissionOut, status_code=201)
def submit_homework(
    homework_id: int, payload: HomeworkSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.role_name != "student":
        raise HTTPException(status_code=403, detail="Only students can submit homework")

    student = get_student_by_user_id(db, current_user.user_id)
    return crud.submit_homework(db, homework_id, student.student_id, payload)


@router.get("/{homework_id}/submissions", response_model=List[HomeworkSubmissionOut])
def list_submissions(homework_id: int, db: Session = Depends(get_db), _=Depends(TEACHER_OR_ADMIN)):
    return crud.list_submissions(db, homework_id)


@router.put("/submissions/{submission_id}/grade", response_model=HomeworkSubmissionOut)
def grade_submission(
    submission_id: int, payload: GradeSubmissionRequest,
    db: Session = Depends(get_db), _=Depends(TEACHER_OR_ADMIN),
):
    return crud.grade_submission(db, submission_id, payload.grade_remarks)
