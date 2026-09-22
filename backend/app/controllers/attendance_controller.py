"""
Business logic for Attendance.

Attendance is typically marked once per section per day (bulk operation),
and read back either as raw records, daily/weekly/monthly reports, or a
percentage summary for the student dashboard.
"""

from typing import Optional
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.schemas.attendance import BulkAttendanceCreate, AttendanceUpdate
from app.controllers.notification_controller import create_notification
from app.models.notification import NotificationType


def mark_bulk_attendance(
    db: Session,
    payload: BulkAttendanceCreate,
    marked_by_teacher_id: int
):
    results = []

    try:
        for record in payload.records:

            student = (
                db.query(Student)
                .filter(
                    Student.student_id == record.student_id
                )
                .first()
            )

            if not student:
                raise HTTPException(
                    status_code=404,
                    detail=f"Student {record.student_id} not found"
                )

            # Student must belong to selected section
            if student.section_id != payload.section_id:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        f"Student {record.student_id} "
                        "does not belong to this section"
                    )
                )

            existing = (
                db.query(Attendance)
                .filter(
                    Attendance.student_id == record.student_id,
                    Attendance.attendance_date == payload.attendance_date,
                )
                .first()
            )

            if existing:
                existing.status = record.status
                existing.remarks = record.remarks
                existing.marked_by = marked_by_teacher_id
                existing.section_id = payload.section_id

                results.append(existing)

            else:
                new_record = Attendance(
                    student_id=record.student_id,
                    section_id=payload.section_id,
                    marked_by=marked_by_teacher_id,
                    attendance_date=payload.attendance_date,
                    status=record.status,
                    remarks=record.remarks,
                )

                db.add(new_record)
                results.append(new_record)

        db.commit()

        for record in results:
            db.refresh(record)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save attendance"
        )

    # ---------------------------------------------------------
    # Notifications
    # ---------------------------------------------------------
    for record in results:

        if record.status == AttendanceStatus.absent:

            student = (
                db.query(Student)
                .filter(
                    Student.student_id == record.student_id
                )
                .first()
            )

            if student:
                create_notification(
                    db,
                    student.user_id,
                    title="Marked Absent",
                    message=(
                        f"You were marked absent on "
                        f"{payload.attendance_date.isoformat()}"
                    ),
                    notif_type=NotificationType.attendance,
                    reference_id=record.attendance_id,
                )

    return results
def get_attendance_record(db: Session, attendance_id: int) -> Attendance:
    obj = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return obj


def update_attendance_record(db: Session, attendance_id: int, payload: AttendanceUpdate) -> Attendance:
    obj = get_attendance_record(db, attendance_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_attendance_record(db: Session, attendance_id: int):
    obj = get_attendance_record(db, attendance_id)
    db.delete(obj)
    db.commit()


# ---------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------
def get_student_summary(db: Session, student_id: int, date_from: Optional[date] = None,
                         date_to: Optional[date] = None) -> dict:
    """Overall attendance percentage for one student — powers the student dashboard widget."""
    if not db.query(Student).filter(Student.student_id == student_id).first():
        raise HTTPException(status_code=404, detail="Student not found")

    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    if date_from is not None:
        query = query.filter(Attendance.attendance_date >= date_from)
    if date_to is not None:
        query = query.filter(Attendance.attendance_date <= date_to)

    counts = dict(
        query.with_entities(Attendance.status, func.count(Attendance.attendance_id))
        .group_by(Attendance.status)
        .all()
    )

    present = counts.get(AttendanceStatus.present, 0)
    absent = counts.get(AttendanceStatus.absent, 0)
    late = counts.get(AttendanceStatus.late, 0)
    leave = counts.get(AttendanceStatus.leave, 0)
    total = present + absent + late + leave

    # "Present" and "late" both count toward attendance percentage; "leave" is excluded from the denominator
    effective_total = present + absent + late
    percentage = round(((present + late) / effective_total) * 100, 2) if effective_total > 0 else 0.0

    return {
        "total_days": total,
        "present_days": present,
        "absent_days": absent,
        "late_days": late,
        "leave_days": leave,
        "percentage": percentage,
    }


def get_section_daily_report(db: Session, section_id: int, report_date: date):
    return (
        db.query(Attendance)
        .filter(Attendance.section_id == section_id, Attendance.attendance_date == report_date)
        .all()
    )


def get_section_range_report(db: Session, section_id: int, date_from: date, date_to: Optional[date] = None):
    """Powers weekly/monthly reports — pass date_from/date_to spanning the desired range."""
    date_to = date_to or (date_from + timedelta(days=6))
    return (
        db.query(Attendance)
        .filter(
            Attendance.section_id == section_id,
            Attendance.attendance_date >= date_from,
            Attendance.attendance_date <= date_to,
        )
        .order_by(Attendance.attendance_date.asc())
        .all()
    )
