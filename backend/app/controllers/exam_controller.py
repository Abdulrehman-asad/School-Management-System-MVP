"""
Business logic for Exams and their per-subject schedules.
"""

from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.exam import Exam, ExamSubjectSchedule
from app.models.academic import Subject
from app.models.student import Student
from app.schemas.exam import ExamCreate, ExamUpdate, ExamScheduleCreate, ExamScheduleUpdate
from app.controllers.notification_controller import create_notifications_bulk
from app.models.notification import NotificationType


# ---------------------------------------------------------------------
# Exams
# ---------------------------------------------------------------------
def create_exam(db: Session, payload: ExamCreate) -> Exam:
    if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")

    new_exam = Exam(**payload.model_dump())
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam


def list_exams(db: Session, class_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Exam]:
    query = db.query(Exam)
    if class_id is not None:
        query = query.filter(Exam.class_id == class_id)
    return query.order_by(Exam.start_date.desc()).offset(skip).limit(limit).all()


def get_exam(db: Session, exam_id: int) -> Exam:
    obj = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Exam not found")
    return obj


def update_exam(db: Session, exam_id: int, payload: ExamUpdate) -> Exam:
    obj = get_exam(db, exam_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_exam(db: Session, exam_id: int):
    obj = get_exam(db, exam_id)
    db.delete(obj)
    db.commit()


# ---------------------------------------------------------------------
# Exam Subject Schedule
# ---------------------------------------------------------------------
def create_schedule(db: Session, exam_id: int, payload: ExamScheduleCreate) -> ExamSubjectSchedule:
    get_exam(db, exam_id)  # 404 if missing

    if not db.query(Subject).filter(Subject.subject_id == payload.subject_id).first():
        raise HTTPException(status_code=404, detail="Subject not found")

    existing = (
        db.query(ExamSubjectSchedule)
        .filter(ExamSubjectSchedule.exam_id == exam_id, ExamSubjectSchedule.subject_id == payload.subject_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="This subject is already scheduled for this exam")

    new_schedule = ExamSubjectSchedule(exam_id=exam_id, **payload.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # Notify every student in this exam's class that a subject exam has been scheduled
    exam = get_exam(db, exam_id)
    subject = db.query(Subject).filter(Subject.subject_id == payload.subject_id).first()
    students = db.query(Student).join(Student.section).filter(Student.section.has(class_id=exam.class_id)).all()
    student_user_ids = [s.user_id for s in students]
    if student_user_ids:
        date_str = payload.exam_date.isoformat() if payload.exam_date else "TBA"
        create_notifications_bulk(
            db, student_user_ids,
            title=f"{exam.exam_name}: {subject.subject_name} Scheduled",
            message=f"Exam date: {date_str}",
            notif_type=NotificationType.exam,
            reference_id=new_schedule.schedule_id,
        )

    return new_schedule


def list_schedules(db: Session, exam_id: int) -> List[ExamSubjectSchedule]:
    get_exam(db, exam_id)  # 404 if missing
    return (
        db.query(ExamSubjectSchedule)
        .filter(ExamSubjectSchedule.exam_id == exam_id)
        .order_by(ExamSubjectSchedule.exam_date.asc())
        .all()
    )


def get_schedule(db: Session, schedule_id: int) -> ExamSubjectSchedule:
    obj = db.query(ExamSubjectSchedule).filter(ExamSubjectSchedule.schedule_id == schedule_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Exam schedule not found")
    return obj


def update_schedule(db: Session, schedule_id: int, payload: ExamScheduleUpdate) -> ExamSubjectSchedule:
    obj = get_schedule(db, schedule_id)
    data = payload.model_dump(exclude_unset=True)

    new_start = data.get("start_time", obj.start_time)
    new_end = data.get("end_time", obj.end_time)
    if new_start and new_end and new_end <= new_start:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    new_total = data.get("total_marks", obj.total_marks)
    new_passing = data.get("passing_marks", obj.passing_marks)
    if new_passing > new_total:
        raise HTTPException(status_code=400, detail="passing_marks cannot exceed total_marks")

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_schedule(db: Session, schedule_id: int):
    obj = get_schedule(db, schedule_id)
    db.delete(obj)
    db.commit()
