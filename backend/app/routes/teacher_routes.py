"""
Routes for Teacher registration and management.

Create/update/delete/assign: admin & super_admin only.
Read (list/get): admin, super_admin, and the teacher's own account can view.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import teacher_controller as crud
from app.schemas.teacher import (
    TeacherCreate, TeacherUpdate, TeacherOut, SubjectAssignmentCreate, SubjectAssignmentOut , TeacherSectionAssign,
TeacherSectionOut
)

router = APIRouter(prefix="/api/teachers", tags=["Teachers"])

ADMIN_ONLY = require_roles("admin", "super_admin")
STAFF_READ = require_roles("admin", "super_admin", "teacher")


@router.post("", response_model=TeacherOut, status_code=201)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_teacher(db, payload)


@router.get("", response_model=List[TeacherOut])
def list_teachers(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(STAFF_READ),
):
    return crud.list_teachers(db, status_filter, search, skip, limit)


# ---------------------------------------------------------------------
# Class / Section assignment
# ---------------------------------------------------------------------

@router.post(
    "/{teacher_id}/section",
    response_model=TeacherSectionOut
)
def assign_teacher_section(
    teacher_id: int,
    payload: TeacherSectionAssign,
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    section = crud.assign_teacher_section(
        db,
        teacher_id,
        payload.section_id
    )

    return crud.get_teacher_section(
        db,
        teacher_id
    )


@router.get(
    "/me/section",
    response_model=TeacherSectionOut
)
def get_my_section(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.role_name != "teacher":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is for teacher accounts only"
        )

    teacher = crud.get_teacher_by_user_id(
        db,
        current_user.user_id
    )

    return crud.get_teacher_section(
        db,
        teacher.teacher_id
    )

@router.get("/me", response_model=TeacherOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lets a logged-in teacher discover their own teacher_id and profile —
    the Teacher Dashboard's entry point for "my assignments"
    (/api/teachers/{teacher_id}/assignments), which takes teacher_id as a
    path parameter.
    """
    if current_user.role.role_name != "teacher":
        raise HTTPException(status_code=403, detail="This endpoint is for teacher accounts only")
    teacher = crud.get_teacher_by_user_id(db, current_user.user_id)
    return crud.teacher_to_out_dict(teacher)


@router.get("/{teacher_id}", response_model=TeacherOut)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Admins/super_admins can view anyone; a teacher can only view their own record
    if current_user.role.role_name == "teacher":
        teacher = crud.get_teacher(db, teacher_id)
        if teacher.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only view your own profile")
        return crud.teacher_to_out_dict(teacher)
    elif current_user.role.role_name not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = crud.get_teacher(db, teacher_id)
    return crud.teacher_to_out_dict(teacher)


@router.put("/{teacher_id}", response_model=TeacherOut)
def update_teacher(teacher_id: int, payload: TeacherUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_teacher(db, teacher_id, payload)


@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_teacher(db, teacher_id)


# ---------------------------------------------------------------------
# Subject assignments
# ---------------------------------------------------------------------
@router.post("/{teacher_id}/assignments", response_model=SubjectAssignmentOut, status_code=201)
def assign_subject(
    teacher_id: int, payload: SubjectAssignmentCreate,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    return crud.assign_subject(db, teacher_id, payload)


@router.get("/{teacher_id}/assignments", response_model=List[SubjectAssignmentOut])
def list_assignments(teacher_id: int, db: Session = Depends(get_db), _=Depends(STAFF_READ)):
    return crud.list_teacher_assignments(db, teacher_id)


@router.delete("/{teacher_id}/assignments/{assignment_id}", status_code=204)
def remove_assignment(
    teacher_id: int, assignment_id: int,
    db: Session = Depends(get_db), _=Depends(ADMIN_ONLY),
):
    crud.remove_assignment(db, teacher_id, assignment_id)
