"""
Business logic for Homework and Homework Submissions.
"""

from typing import Optional
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.homework import Homework, HomeworkSubmission, SubmissionStatus
from app.models.student import Student
from app.schemas.homework import HomeworkCreate, HomeworkUpdate, HomeworkSubmissionCreate
from app.controllers.notification_controller import create_notifications_bulk
from app.models.notification import NotificationType


def create_homework(db: Session, payload: HomeworkCreate, teacher_id: int) -> Homework:
    if payload.due_date < payload.assigned_date:
        raise HTTPException(status_code=400, detail="due_date cannot be before assigned_date")

    new_homework = Homework(
        section_id=payload.section_id,
        subject_id=payload.subject_id,
        teacher_id=teacher_id,
        title=payload.title,
        description=payload.description,
        attachment_path=payload.attachment_path,
        assigned_date=payload.assigned_date,
        due_date=payload.due_date,
    )
    db.add(new_homework)
    db.commit()
    db.refresh(new_homework)

    # Notify every student in the section that new homework has been assigned
    student_user_ids = [
        s.user_id for s in db.query(Student).filter(Student.section_id == payload.section_id).all()
    ]
    if student_user_ids:
        create_notifications_bulk(
            db, student_user_ids,
            title=f"New Homework: {new_homework.title}",
            message=f"Due on {new_homework.due_date.isoformat()}",
            notif_type=NotificationType.homework,
            reference_id=new_homework.homework_id,
        )

    return new_homework


def list_homework(
    db: Session,
    section_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Homework)
    if section_id is not None:
        query = query.filter(Homework.section_id == section_id)
    if subject_id is not None:
        query = query.filter(Homework.subject_id == subject_id)
    if teacher_id is not None:
        query = query.filter(Homework.teacher_id == teacher_id)

    return query.order_by(Homework.due_date.desc()).offset(skip).limit(limit).all()


def get_homework(db: Session, homework_id: int) -> Homework:
    obj = db.query(Homework).filter(Homework.homework_id == homework_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Homework not found")
    return obj


def update_homework(db: Session, homework_id: int, payload: HomeworkUpdate, teacher_id: int) -> Homework:
    obj = get_homework(db, homework_id)
    if obj.teacher_id != teacher_id:
        raise HTTPException(status_code=403, detail="You can only edit homework you assigned")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_homework(db: Session, homework_id: int, teacher_id: int):
    obj = get_homework(db, homework_id)
    if obj.teacher_id != teacher_id:
        raise HTTPException(status_code=403, detail="You can only delete homework you assigned")
    db.delete(obj)
    db.commit()


# ---------------------------------------------------------------------
# Submissions (future-facing, per the spec)
# ---------------------------------------------------------------------
def submit_homework(db: Session, homework_id: int, student_id: int, payload: HomeworkSubmissionCreate):
    homework = get_homework(db, homework_id)

    existing = (
        db.query(HomeworkSubmission)
        .filter(
            HomeworkSubmission.homework_id == homework_id,
            HomeworkSubmission.student_id == student_id,
        )
        .first()
    )
    is_late = date.today() > homework.due_date
    status_value = SubmissionStatus.late if is_late else SubmissionStatus.submitted

    if existing:
        existing.file_path = payload.file_path
        existing.status = status_value
        existing.submitted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    submission = HomeworkSubmission(
        homework_id=homework_id,
        student_id=student_id,
        file_path=payload.file_path,
        status=status_value,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_submissions(db: Session, homework_id: int):
    get_homework(db, homework_id)  # 404 if missing
    return (
        db.query(HomeworkSubmission)
        .filter(HomeworkSubmission.homework_id == homework_id)
        .all()
    )


def grade_submission(db: Session, submission_id: int, grade_remarks: str) -> HomeworkSubmission:
    obj = db.query(HomeworkSubmission).filter(HomeworkSubmission.submission_id == submission_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Submission not found")
    obj.grade_remarks = grade_remarks
    obj.status = SubmissionStatus.graded
    db.commit()
    db.refresh(obj)
    return obj
