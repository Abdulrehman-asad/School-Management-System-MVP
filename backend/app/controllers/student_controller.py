"""
Business logic for the Student module.

Registering a student is a two-table operation (users + students), wrapped in
a single transaction. Registration numbers are auto-generated as
SMGHS-<admission_year>-<sequence>, e.g. SMGHS-2026-0001, unless supplied explicitly.
"""

from typing import Optional
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.models.user import User, Role
from app.models.student import Student
from app.models.academic import Section
from app.auth.security import hash_password
from app.schemas.student import StudentCreate, StudentUpdate


def _generate_registration_no(db: Session, admission_year: int) -> str:
    prefix = f"SMGHS-{admission_year}-"
    count = (
        db.query(func.count(Student.student_id))
        .filter(Student.registration_no.like(f"{prefix}%"))
        .scalar()
    )
    sequence = str(count + 1).zfill(4)
    return f"{prefix}{sequence}"


def student_to_out_dict(student: Student) -> dict:
    return {
        "student_id": student.student_id,
        "user_id": student.user_id,
        "full_name": student.user.full_name,
        "email": student.user.email,
        "phone": student.user.phone,
        "username": student.user.username,
        "registration_no": student.registration_no,
        "section_id": student.section_id,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
        "admission_date": student.admission_date,
        "address": student.address,
        "blood_group": student.blood_group,
        "status": student.status,
        "is_active": student.user.is_active,
        "profile_image": student.user.profile_image,
    }


def create_student(db: Session, payload: StudentCreate) -> dict:
    student_role = db.query(Role).filter(Role.role_name == "student").first()
    if not student_role:
        raise HTTPException(status_code=500, detail="Student role missing from database. Run schema.sql first.")

    section = db.query(Section).filter(Section.section_id == payload.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(
        role_id=student_role.role_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(new_user)
    db.flush()  # get new_user.user_id

    admission_date = payload.admission_date or date.today()
    registration_no = payload.registration_no or _generate_registration_no(db, admission_date.year)

    new_student = Student(
        user_id=new_user.user_id,
        registration_no=registration_no,
        section_id=payload.section_id,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        admission_date=admission_date,
        address=payload.address,
        blood_group=payload.blood_group,
    )
    db.add(new_student)

    try:
     db.commit()
    except IntegrityError as e:
     db.rollback()

     print("========== STUDENT CREATE ERROR ==========")
     print(e)
     print("ORIGINAL ERROR:", e.orig)
     print("==========================================")

     raise HTTPException(
        status_code=409,
        detail=f"Database error: {str(e.orig)}"
    )
    db.refresh(new_student)
    db.refresh(new_user)
    return student_to_out_dict(new_student)


def list_students(db: Session, section_id: Optional[int] = None, status_filter: Optional[str] = None,
                   search: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(Student).options(joinedload(Student.user))

    if section_id is not None:
        query = query.filter(Student.section_id == section_id)
    if status_filter:
        query = query.filter(Student.status == status_filter)
    if search:
        query = query.join(User).filter(
            (User.full_name.ilike(f"%{search}%"))
            | (Student.registration_no.ilike(f"%{search}%"))
        )

    students = query.offset(skip).limit(limit).all()
    return [student_to_out_dict(s) for s in students]


def get_student_by_user_id(db: Session, user_id: int) -> Student:
    """Used by attendance/homework routes to resolve 'the logged-in student'."""
    obj = db.query(Student).filter(Student.user_id == user_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No student profile linked to this account")
    return obj


def get_student(db: Session, student_id: int) -> Student:
    obj = (
        db.query(Student)
        .options(joinedload(Student.user))
        .filter(Student.student_id == student_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Student not found")
    return obj


def update_student(db: Session, student_id: int, payload: StudentUpdate) -> dict:
    student = get_student(db, student_id)
    data = payload.model_dump(exclude_unset=True)

    if "section_id" in data:
        new_section = db.query(Section).filter(Section.section_id == data["section_id"]).first()
        if not new_section:
            raise HTTPException(status_code=404, detail="Section not found")

    for user_field in ("full_name", "phone", "is_active"):
        if user_field in data:
            setattr(student.user, user_field, data.pop(user_field))

    for field, value in data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    db.refresh(student.user)
    return student_to_out_dict(student)


def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    user = student.user
    db.delete(student)
    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete student: linked attendance, results, or fee records exist",
        )
