"""
Business logic for the Notice Board.

Posting a notice also fans out a Notification to every user in its audience
(all / teachers / students / parents / a specific class) — this is what makes
notices show up in the notification bell for the people they're relevant to.
"""

from typing import Optional, List
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.notice import Notice, NoticeAudience
from app.models.user import User, Role
from app.models.student import Student, ParentGuardian
from app.models.teacher import Teacher
from app.controllers.notification_controller import create_notifications_bulk
from app.models.notification import NotificationType
from app.schemas.notice import NoticeCreate, NoticeUpdate


def _resolve_audience_user_ids(db: Session, audience: NoticeAudience, class_id: Optional[int]) -> List[int]:
    """Figures out which user_ids should be notified for a given audience setting."""
    if audience == NoticeAudience.teachers:
        return [t.user_id for t in db.query(Teacher).all()]

    if audience == NoticeAudience.students:
        return [s.user_id for s in db.query(Student).all()]

    if audience == NoticeAudience.parents:
        return [p.user_id for p in db.query(ParentGuardian).all()]

    if audience == NoticeAudience.specific_class:
        if class_id is None:
            return []
        students = db.query(Student).join(Student.section).filter(Student.section.has(class_id=class_id)).all()
        return [s.user_id for s in students]

    # "all"
    return [u.user_id for u in db.query(User).all()]


def create_notice(db: Session, payload: NoticeCreate, posted_by_user_id: int) -> Notice:
    if payload.audience == NoticeAudience.specific_class and payload.class_id is None:
        raise HTTPException(status_code=400, detail="class_id is required when audience is 'specific_class'")

    new_notice = Notice(
        title=payload.title,
        description=payload.description,
        posted_by=posted_by_user_id,
        audience=payload.audience,
        class_id=payload.class_id,
        attachment_path=payload.attachment_path,
        publish_date=payload.publish_date,
        expiry_date=payload.expiry_date,
    )
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)

    recipient_ids = _resolve_audience_user_ids(db, payload.audience, payload.class_id)
    if recipient_ids:
        create_notifications_bulk(
            db, recipient_ids,
            title=f"New Notice: {new_notice.title}",
            message=(new_notice.description or "")[:500],
            notif_type=NotificationType.notice,
            reference_id=new_notice.notice_id,
        )

    return new_notice


def list_notices(
    db: Session,
    audience: Optional[NoticeAudience] = None,
    class_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
) -> List[Notice]:
    query = db.query(Notice)

    if audience is not None:
        query = query.filter(Notice.audience == audience)
    if class_id is not None:
        query = query.filter(Notice.class_id == class_id)
    if active_only:
        today = date.today()
        query = query.filter(Notice.publish_date <= today).filter(
            (Notice.expiry_date.is_(None)) | (Notice.expiry_date >= today)
        )

    return query.order_by(Notice.publish_date.desc()).offset(skip).limit(limit).all()


def list_notices_for_user(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Notice]:
    """Convenience filter: returns only notices relevant to this user's role/class."""
    role = user.role.role_name
    today = date.today()

    query = db.query(Notice).filter(Notice.publish_date <= today).filter(
        (Notice.expiry_date.is_(None)) | (Notice.expiry_date >= today)
    )

    if role == "student":
        student = db.query(Student).filter(Student.user_id == user.user_id).first()
        class_id = student.section.class_id if student else None
        query = query.filter(
            (Notice.audience == NoticeAudience.all)
            | (Notice.audience == NoticeAudience.students)
            | ((Notice.audience == NoticeAudience.specific_class) & (Notice.class_id == class_id))
        )
    elif role == "teacher":
        query = query.filter((Notice.audience == NoticeAudience.all) | (Notice.audience == NoticeAudience.teachers))
    elif role == "parent":
        query = query.filter((Notice.audience == NoticeAudience.all) | (Notice.audience == NoticeAudience.parents))
    # admin/super_admin see everything (no extra filter)

    return query.order_by(Notice.publish_date.desc()).offset(skip).limit(limit).all()


def get_notice(db: Session, notice_id: int) -> Notice:
    obj = db.query(Notice).filter(Notice.notice_id == notice_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Notice not found")
    return obj


def update_notice(db: Session, notice_id: int, payload: NoticeUpdate) -> Notice:
    obj = get_notice(db, notice_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_notice(db: Session, notice_id: int):
    obj = get_notice(db, notice_id)
    db.delete(obj)
    db.commit()
