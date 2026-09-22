"""
Business logic for the Reports module.

Each function gathers data by reusing the existing per-module controllers
(so the numbers always match what the dashboards show), then reshapes it
into (headers, rows) — a plain list-of-dicts format that
app/utils/report_export.py can turn into either an .xlsx or .pdf file.
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.controllers import attendance_controller, student_controller, teacher_controller, fee_controller
from app.controllers.result_controller import get_position_list
from app.controllers.exam_controller import get_exam
from app.models.student import Student
from app.models.academic import Section, SchoolClass


ReportData = Tuple[List[str], List[Dict[str, Any]]]


def attendance_report(
    db: Session, section_id: int, date_from: date, date_to: Optional[date] = None
) -> ReportData:
    records = attendance_controller.get_section_range_report(db, section_id, date_from, date_to)

    headers = ["Date", "Registration No", "Student Name", "Status", "Remarks"]
    rows = []
    for r in records:
        student = db.query(Student).options(joinedload(Student.user)).filter(
            Student.student_id == r.student_id
        ).first()
        rows.append({
            "Date": r.attendance_date.isoformat(),
            "Registration No": student.registration_no if student else "",
            "Student Name": student.user.full_name if student else "",
            "Status": r.status.value if hasattr(r.status, "value") else r.status,
            "Remarks": r.remarks or "",
        })
    return headers, rows


def result_report(db: Session, exam_id: int) -> ReportData:
    get_exam(db, exam_id)  # 404 if missing
    position_list = get_position_list(db, exam_id)

    headers = ["Position", "Registration No", "Student Name", "Total Marks", "Percentage", "GPA"]
    rows = [
        {
            "Position": entry.position,
            "Registration No": entry.registration_no,
            "Student Name": entry.student_name,
            "Total Marks": str(entry.total_marks_obtained),
            "Percentage": f"{entry.overall_percentage}%",
            "GPA": entry.gpa,
        }
        for entry in position_list
    ]
    return headers, rows


def student_report(
    db: Session, section_id: Optional[int] = None, status_filter: Optional[str] = None
) -> ReportData:
    students = student_controller.list_students(db, section_id=section_id, status_filter=status_filter,
                                                 skip=0, limit=10000)

    headers = ["Registration No", "Name", "Class", "Section", "Gender", "Status", "Admission Date"]
    rows = []
    for s in students:
        section = db.query(Section).filter(Section.section_id == s["section_id"]).first()
        school_class = db.query(SchoolClass).filter(SchoolClass.class_id == section.class_id).first() if section else None
        rows.append({
            "Registration No": s["registration_no"],
            "Name": s["full_name"],
            "Class": school_class.class_name if school_class else "",
            "Section": section.section_name if section else "",
            "Gender": s["gender"].value if hasattr(s["gender"], "value") else s["gender"],
            "Status": s["status"].value if hasattr(s["status"], "value") else s["status"],
            "Admission Date": s["admission_date"].isoformat() if s["admission_date"] else "",
        })
    return headers, rows


def teacher_report(db: Session, status_filter: Optional[str] = None) -> ReportData:
    teachers = teacher_controller.list_teachers(db, status_filter=status_filter, skip=0, limit=10000)

    headers = ["Employee Code", "Name", "Email", "Phone", "Qualification", "Status"]
    rows = [
        {
            "Employee Code": t["employee_code"] or "",
            "Name": t["full_name"],
            "Email": t["email"] or "",
            "Phone": t["phone"] or "",
            "Qualification": t["qualification"] or "",
            "Status": t["status"].value if hasattr(t["status"], "value") else t["status"],
        }
        for t in teachers
    ]
    return headers, rows


def fee_report(
    db: Session, month_year: Optional[str] = None, status_filter: Optional[str] = None
) -> ReportData:
    challans = fee_controller.list_challans(db, status_filter=status_filter, month_year=month_year,
                                             skip=0, limit=10000)

    headers = ["Challan No", "Registration No", "Student Name", "Amount", "Fine", "Due Date", "Status", "Paid Date"]
    rows = []
    for c in challans:
        student = db.query(Student).options(joinedload(Student.user)).filter(
            Student.student_id == c.student_id
        ).first()
        rows.append({
            "Challan No": c.challan_no,
            "Registration No": student.registration_no if student else "",
            "Student Name": student.user.full_name if student else "",
            "Amount": str(c.amount),
            "Fine": str(c.fine_amount),
            "Due Date": c.due_date.isoformat(),
            "Status": c.status.value if hasattr(c.status, "value") else c.status,
            "Paid Date": c.paid_date.isoformat() if c.paid_date else "",
        })
    return headers, rows
