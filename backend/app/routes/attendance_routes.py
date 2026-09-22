"""
Routes for Attendance.

Marking attendance: teacher (their own section), admin, super_admin.
Reading: admin/super_admin/teacher can view any section; a student can view
only their own attendance summary/history (needed for the Student Dashboard).
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.models.academic import Section

from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User
from app.controllers import attendance_controller as crud
from app.controllers.teacher_controller import get_teacher_by_user_id
from app.controllers.student_controller import get_student_by_user_id
from app.schemas.attendance import (
    BulkAttendanceCreate, AttendanceUpdate, AttendanceOut, AttendanceSummary
)

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

ADMIN_ONLY = require_roles("admin", "super_admin")
STAFF = require_roles("admin", "super_admin", "teacher")


@router.post("/mark", response_model=List[AttendanceOut], status_code=201)
def mark_attendance(
    payload: BulkAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name

    # ---------------------------------------------------------
    # Teacher
    # ---------------------------------------------------------
    if role == "teacher":

        teacher = get_teacher_by_user_id(
            db,
            current_user.user_id
        )

        marked_by_id = teacher.teacher_id

        # Find teacher's assigned section
        assigned_section = (
            db.query(Section)
            .filter(
                Section.class_teacher_id == teacher.teacher_id
            )
            .first()
        )

        if not assigned_section:
            raise HTTPException(
                status_code=403,
                detail="No class/section has been assigned to this teacher"
            )

        # Teacher can only mark attendance
        # for their own assigned section
        if assigned_section.section_id != payload.section_id:
            raise HTTPException(
                status_code=403,
                detail="You can only mark attendance for your assigned section"
            )

    # ---------------------------------------------------------
    # Admin / Super Admin
    # ---------------------------------------------------------
    elif role in ("admin", "super_admin"):

        # Admin does not have to be a teacher.
        # Use the section's class teacher as marked_by.
        section = (
            db.query(Section)
            .filter(
                Section.section_id == payload.section_id
            )
            .first()
        )

        if not section:
            raise HTTPException(
                status_code=404,
                detail="Section not found"
            )

        if not section.class_teacher_id:
            raise HTTPException(
                status_code=400,
                detail="This section does not have a class teacher assigned"
            )

        marked_by_id = section.class_teacher_id

    # ---------------------------------------------------------
    # Other roles
    # ---------------------------------------------------------
    else:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to mark attendance"
        )

    # ---------------------------------------------------------
    # Mark attendance
    # ---------------------------------------------------------
    return crud.mark_bulk_attendance(
        db,
        payload,
        marked_by_id
    )

@router.get("", response_model=List[AttendanceOut])
def list_attendance(
    section_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name

    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        student_id = student.student_id  # force students to only ever see their own data
    elif role not in ("admin", "super_admin", "teacher"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.list_attendance(db, section_id, student_id, date_from, date_to, skip, limit)


@router.get("/reports/daily", response_model=List[AttendanceOut])
def daily_report(
    section_id: int, report_date: date,
    db: Session = Depends(get_db), _=Depends(STAFF),
):
    return crud.get_section_daily_report(db, section_id, report_date)


@router.get("/reports/range", response_model=List[AttendanceOut])
def range_report(
    section_id: int, date_from: date, date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db), _=Depends(STAFF),
):
    """Powers weekly/monthly reports — omit date_to for a 7-day window from date_from."""
    return crud.get_section_range_report(db, section_id, date_from, date_to)


@router.get("/summary/{student_id}", response_model=AttendanceSummary)
def student_summary(
    student_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.role_name
    if role == "student":
        student = get_student_by_user_id(db, current_user.user_id)
        if student.student_id != student_id:
            raise HTTPException(status_code=403, detail="You can only view your own attendance summary")
    elif role not in ("admin", "super_admin", "teacher"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.get_student_summary(db, student_id, date_from, date_to)


@router.put("/{attendance_id}", response_model=AttendanceOut)
def update_attendance(
    attendance_id: int, payload: AttendanceUpdate,
    db: Session = Depends(get_db), _=Depends(STAFF),
):
    return crud.update_attendance_record(db, attendance_id, payload)


@router.delete("/{attendance_id}", status_code=204)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db), _=Depends(ADMIN_ONLY)):
    crud.delete_attendance_record(db, attendance_id)
