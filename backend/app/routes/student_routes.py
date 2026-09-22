"""
Routes for Student registration and management.

Create/update/delete: admin & super_admin only.
Read (list): admin, super_admin, teacher.
Read (get one): admin/super_admin/teacher can view anyone; a student can view
only their own record (needed later for the Student Dashboard).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import student_controller as crud
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/api/students", tags=["Students"])

ADMIN_ONLY = require_roles("admin", "super_admin")
STAFF_READ = require_roles("admin", "super_admin", "teacher")


@router.post("", response_model=StudentOut, status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.create_student(db, payload)


@router.get("", response_model=List[StudentOut])
def list_students(
    section_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _=Depends(STAFF_READ),
):
    return crud.list_students(db, section_id, status_filter, search, skip, limit)


@router.get("/me", response_model=StudentOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lets a logged-in student discover their own student_id and profile without
    needing it passed in from anywhere else — the Student Dashboard's entry
    point for attendance summaries, result cards, and fee status, all of which
    take student_id as a path parameter.
    """
    if current_user.role.role_name != "student":
        raise HTTPException(status_code=403, detail="This endpoint is for student accounts only")
    student = crud.get_student_by_user_id(db, current_user.user_id)
    return crud.student_to_out_dict(student)


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name

    if role in ("admin", "super_admin", "teacher"):
        student = crud.get_student(db, student_id)
    elif role == "student":
        student = crud.get_student(db, student_id)
        if student.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You can only view your own profile")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.student_to_out_dict(student)


@router.put("/{student_id}", response_model=StudentOut)
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    return crud.update_student(db, student_id, payload)


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_student(db, student_id)
