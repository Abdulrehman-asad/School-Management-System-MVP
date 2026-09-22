"""
Routes for Reports: Attendance, Results, Students, Teachers, Fees.

Every report supports `?format=excel` (default) or `?format=pdf` and streams
the file back as a download. Admin/super_admin only, matching the spec's
"Admin Features: Reports" placement.
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import require_roles
from app.controllers import report_controller as reports
from app.utils.report_export import build_excel_report, build_pdf_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

ADMIN_ONLY = require_roles("admin", "super_admin")

EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PDF_MEDIA_TYPE = "application/pdf"


def _stream_report(title: str, headers, rows, export_format: str, filename_base: str, subtitle: str = ""):
    if export_format not in ("excel", "pdf"):
        raise HTTPException(status_code=400, detail="format must be 'excel' or 'pdf'")

    if export_format == "excel":
        buffer = build_excel_report(title, headers, rows)
        media_type = EXCEL_MEDIA_TYPE
        filename = f"{filename_base}.xlsx"
    else:
        buffer = build_pdf_report(title, headers, rows, subtitle)
        media_type = PDF_MEDIA_TYPE
        filename = f"{filename_base}.pdf"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/attendance")
def attendance_report(
    section_id: int,
    date_from: date,
    date_to: Optional[date] = Query(None),
    format: str = Query("excel"),
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    headers, rows = reports.attendance_report(db, section_id, date_from, date_to)
    subtitle = f"Section ID {section_id} | {date_from} to {date_to or date_from}"
    return _stream_report("Attendance Report", headers, rows, format, "attendance_report", subtitle)


@router.get("/results")
def result_report(
    exam_id: int,
    format: str = Query("excel"),
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    headers, rows = reports.result_report(db, exam_id)
    return _stream_report("Result Report", headers, rows, format, "result_report", f"Exam ID {exam_id}")


@router.get("/students")
def student_report(
    section_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    format: str = Query("excel"),
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    headers, rows = reports.student_report(db, section_id, status)
    return _stream_report("Student Report", headers, rows, format, "student_report")


@router.get("/teachers")
def teacher_report(
    status: Optional[str] = Query(None),
    format: str = Query("excel"),
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    headers, rows = reports.teacher_report(db, status)
    return _stream_report("Teacher Report", headers, rows, format, "teacher_report")


@router.get("/fees")
def fee_report(
    month_year: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    format: str = Query("excel"),
    db: Session = Depends(get_db),
    _=Depends(ADMIN_ONLY),
):
    headers, rows = reports.fee_report(db, month_year, status)
    subtitle = month_year or "All periods"
    return _stream_report("Fee Report", headers, rows, format, "fee_report", subtitle)
