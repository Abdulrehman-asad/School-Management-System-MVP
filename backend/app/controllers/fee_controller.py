"""
Business logic for Fee Structures and Fee Challans.

Challan numbers are auto-generated as CH-<YYYYMM>-<sequence>, e.g. CH-202608-00001.
"""

from typing import Optional, List
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.models.fee import FeeStructure, FeeChallan, ChallanStatus
from app.models.student import Student
from app.schemas.fee import (
    FeeStructureCreate, FeeStructureUpdate,
    ChallanGenerateForStudent, ChallanGenerateForClass, ChallanPayRequest, FeeChallanUpdate,
    FeeCollectionSummary,
)
from app.controllers.notification_controller import create_notification, create_notifications_bulk
from app.models.notification import NotificationType


# ---------------------------------------------------------------------
# Fee Structures
# ---------------------------------------------------------------------
def create_fee_structure(db: Session, payload: FeeStructureCreate) -> FeeStructure:
    new_structure = FeeStructure(**payload.model_dump())
    db.add(new_structure)
    db.commit()
    db.refresh(new_structure)
    return new_structure


def list_fee_structures(db: Session, class_id: Optional[int] = None) -> List[FeeStructure]:
    query = db.query(FeeStructure)
    if class_id is not None:
        query = query.filter(FeeStructure.class_id == class_id)
    return query.all()


def get_fee_structure(db: Session, fee_structure_id: int) -> FeeStructure:
    obj = db.query(FeeStructure).filter(FeeStructure.fee_structure_id == fee_structure_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Fee structure not found")
    return obj


def update_fee_structure(db: Session, fee_structure_id: int, payload: FeeStructureUpdate) -> FeeStructure:
    obj = get_fee_structure(db, fee_structure_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_fee_structure(db: Session, fee_structure_id: int):
    obj = get_fee_structure(db, fee_structure_id)
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cannot delete: challans already exist against this fee structure")


# ---------------------------------------------------------------------
# Fee Challans
# ---------------------------------------------------------------------
def _generate_challan_no(db: Session, on_date: date) -> str:
    prefix = f"CH-{on_date.strftime('%Y%m')}-"
    count = db.query(func.count(FeeChallan.challan_id)).filter(
        FeeChallan.challan_no.like(f"{prefix}%")
    ).scalar()
    sequence = str(count + 1).zfill(5)
    return f"{prefix}{sequence}"


def generate_challan_for_student(db: Session, payload: ChallanGenerateForStudent) -> FeeChallan:
    student = db.query(Student).filter(Student.student_id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    structure = get_fee_structure(db, payload.fee_structure_id)

    new_challan = FeeChallan(
        student_id=payload.student_id,
        fee_structure_id=payload.fee_structure_id,
        challan_no=_generate_challan_no(db, date.today()),
        month_year=payload.month_year,
        amount=structure.amount,
        fine_amount=payload.fine_amount,
        due_date=payload.due_date,
        status=ChallanStatus.unpaid,
    )
    db.add(new_challan)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A challan with this number already exists — please retry")
    db.refresh(new_challan)

    create_notification(
        db, student.user_id,
        title=f"Fee Challan Generated: {structure.fee_title}",
        message=f"Amount due: {structure.amount} by {payload.due_date.isoformat()}",
        notif_type=NotificationType.fee,
        reference_id=new_challan.challan_id,
    )

    return new_challan


def generate_challans_for_class(db: Session, payload: ChallanGenerateForClass) -> List[FeeChallan]:
    structure = get_fee_structure(db, payload.fee_structure_id)

    students = (
        db.query(Student)
        .filter(Student.section_id == payload.section_id, Student.status == "active")
        .all()
    )
    if not students:
        raise HTTPException(status_code=404, detail="No active students found in this section")

    new_challans = []
    for student in students:
        challan = FeeChallan(
            student_id=student.student_id,
            fee_structure_id=payload.fee_structure_id,
            challan_no=_generate_challan_no(db, date.today()),
            month_year=payload.month_year,
            amount=structure.amount,
            due_date=payload.due_date,
            status=ChallanStatus.unpaid,
        )
        db.add(challan)
        new_challans.append(challan)

    db.commit()
    for c in new_challans:
        db.refresh(c)

    student_user_ids = [s.user_id for s in students]
    create_notifications_bulk(
        db, student_user_ids,
        title=f"Fee Challan Generated: {structure.fee_title}",
        message=f"Amount due: {structure.amount} by {payload.due_date.isoformat()}",
        notif_type=NotificationType.fee,
    )

    return new_challans


def list_challans(
    db: Session,
    student_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    month_year: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
) -> List[FeeChallan]:
    query = db.query(FeeChallan)
    if student_id is not None:
        query = query.filter(FeeChallan.student_id == student_id)
    if status_filter:
        query = query.filter(FeeChallan.status == status_filter)
    if month_year:
        query = query.filter(FeeChallan.month_year == month_year)

    # Auto-flag overdue challans on read, so admins always see accurate status
    all_matching = query.all()
    if _mark_overdue(all_matching):
        db.commit()

    return query.order_by(FeeChallan.due_date.desc()).offset(skip).limit(limit).all()


def _mark_overdue(challans: List[FeeChallan]):
    today = date.today()
    changed = False
    for c in challans:
        if c.status == ChallanStatus.unpaid and c.due_date < today:
            c.status = ChallanStatus.overdue
            changed = True
    return changed


def get_challan(db: Session, challan_id: int) -> FeeChallan:
    obj = db.query(FeeChallan).filter(FeeChallan.challan_id == challan_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Fee challan not found")

    if obj.status == ChallanStatus.unpaid and obj.due_date < date.today():
        obj.status = ChallanStatus.overdue
        db.commit()
        db.refresh(obj)

    return obj


def pay_challan(db: Session, challan_id: int, payload: ChallanPayRequest) -> FeeChallan:
    obj = get_challan(db, challan_id)
    if obj.status == ChallanStatus.paid:
        raise HTTPException(status_code=400, detail="This challan has already been paid")
    if obj.status == ChallanStatus.cancelled:
        raise HTTPException(status_code=400, detail="This challan has been cancelled and cannot be paid")

    obj.status = ChallanStatus.paid
    obj.payment_method = payload.payment_method
    obj.paid_date = payload.paid_date or date.today()
    db.commit()
    db.refresh(obj)
    return obj


def update_challan(db: Session, challan_id: int, payload: FeeChallanUpdate) -> FeeChallan:
    obj = get_challan(db, challan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_challan(db: Session, challan_id: int):
    obj = get_challan(db, challan_id)
    db.delete(obj)
    db.commit()


# ---------------------------------------------------------------------
# Fee collection summary (dashboard widget)
# ---------------------------------------------------------------------
def get_collection_summary(db: Session, month_year: Optional[str] = None) -> FeeCollectionSummary:
    query = db.query(FeeChallan)
    if month_year:
        query = query.filter(FeeChallan.month_year == month_year)
    challans = query.all()
    _mark_overdue(challans)
    db.commit()

    total_billed = sum((c.amount + c.fine_amount for c in challans), Decimal("0"))
    total_collected = sum((c.amount + c.fine_amount for c in challans if c.status == ChallanStatus.paid), Decimal("0"))
    total_pending = total_billed - total_collected

    return FeeCollectionSummary(
        total_challans=len(challans),
        total_amount_billed=total_billed,
        total_amount_collected=total_collected,
        total_amount_pending=total_pending,
        paid_count=sum(1 for c in challans if c.status == ChallanStatus.paid),
        unpaid_count=sum(1 for c in challans if c.status == ChallanStatus.unpaid),
        overdue_count=sum(1 for c in challans if c.status == ChallanStatus.overdue),
    )
