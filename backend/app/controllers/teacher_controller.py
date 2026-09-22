"""
Business logic for the Teacher module.

Registering a teacher is a two-table operation (users + teachers) that must
succeed or fail together, so it's wrapped in a single DB transaction.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.user import User, Role
from app.models.teacher import Teacher, TeacherSubjectAssignment
from app.models.academic import Subject, Section, SchoolClass
from app.auth.security import hash_password
from app.schemas.teacher import TeacherCreate, TeacherUpdate, SubjectAssignmentCreate

def assign_teacher_section(
    db: Session,
    teacher_id: int,
    section_id: int
):
    teacher = get_teacher(db, teacher_id)

    section = (
        db.query(Section)
        .filter(Section.section_id == section_id)
        .first()
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    # Check whether this section is already assigned
    # to another teacher.
    if (
        section.class_teacher_id is not None
        and section.class_teacher_id != teacher_id
    ):
        raise HTTPException(
            status_code=409,
            detail="This section is already assigned to another teacher"
        )

    # Check whether this teacher already has
    # another section assigned.
    existing_section = (
        db.query(Section)
        .filter(
            Section.class_teacher_id == teacher_id,
            Section.section_id != section_id
        )
        .first()
    )

    if existing_section:
        raise HTTPException(
            status_code=409,
            detail=(
                f"This teacher is already assigned to "
                f"section {existing_section.section_id}"
            )
        )

    section.class_teacher_id = teacher_id

    db.commit()
    db.refresh(section)

    return section

def teacher_to_out_dict(teacher: Teacher) -> dict:
    """Flattens the Teacher + related User row into the shape TeacherOut expects."""
    return {
        "teacher_id": teacher.teacher_id,
        "user_id": teacher.user_id,
        "full_name": teacher.user.full_name,
        "email": teacher.user.email,
        "phone": teacher.user.phone,
        "username": teacher.user.username,
        "employee_code": teacher.employee_code,
        "qualification": teacher.qualification,
        "specialization": teacher.specialization,
        "joining_date": teacher.joining_date,
        "address": teacher.address,
        "salary": teacher.salary,
        "status": teacher.status,
        "is_active": teacher.user.is_active,
        "profile_image": teacher.user.profile_image,
    }




def create_teacher(db: Session, payload: TeacherCreate) -> dict:
    """Create User + Teacher atomically, with optional section assignment."""
    teacher_role = (
        db.query(Role)
        .filter(Role.role_name == "teacher")
        .first()
    )
    if not teacher_role:
        raise HTTPException(
            status_code=500,
            detail="Teacher role missing from database. Run schema.sql first.",
        )

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        new_user = User(
            role_id=teacher_role.role_id,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            username=payload.username,
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        db.add(new_user)
        db.flush()

        new_teacher = Teacher(
            user_id=new_user.user_id,
            employee_code=payload.employee_code,
            qualification=payload.qualification,
            specialization=payload.specialization,
            joining_date=payload.joining_date,
            cnic=payload.cnic,
            address=payload.address,
            salary=payload.salary,
        )
        db.add(new_teacher)
        db.flush()

        section_id = getattr(payload, "section_id", None)

        if section_id is not None:
            section = (
                db.query(Section)
                .filter(Section.section_id == section_id)
                .first()
            )

            if not section:
                db.rollback()
                raise HTTPException(status_code=404, detail="Section not found")

            if section.class_teacher_id is not None:
                db.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="This section is already assigned to another teacher",
                )

            section.class_teacher_id = new_teacher.teacher_id

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee code, CNIC, username, or email already exists",
        )

    db.refresh(new_teacher)
    db.refresh(new_user)
    return teacher_to_out_dict(new_teacher)

def list_teachers(db: Session, status_filter: Optional[str] = None, search: Optional[str] = None,
                   skip: int = 0, limit: int = 100):
    query = db.query(Teacher).options(joinedload(Teacher.user))

    if status_filter:
        query = query.filter(Teacher.status == status_filter)
    if search:
        query = query.join(User).filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    teachers = query.offset(skip).limit(limit).all()
    return [teacher_to_out_dict(t) for t in teachers]


def get_teacher_by_user_id(db: Session, user_id: int) -> Teacher:
    """Used by attendance/homework/timetable routes to resolve 'the logged-in teacher'."""
    obj = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No teacher profile linked to this account")
    return obj


def get_teacher(db: Session, teacher_id: int) -> Teacher:
    obj = (
        db.query(Teacher)
        .options(joinedload(Teacher.user))
        .filter(Teacher.teacher_id == teacher_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return obj


def update_teacher(db: Session, teacher_id: int, payload: TeacherUpdate) -> dict:
    teacher = get_teacher(db, teacher_id)

    data = payload.model_dump(exclude_unset=True)

    # ---------------------------------------------------------
    # Section Assignment
    # ---------------------------------------------------------

    if "section_id" in data:
        new_section_id = data.pop("section_id")

        # Remove current section assignment
        if new_section_id is None:

            current_section = (
                db.query(Section)
                .filter(
                    Section.class_teacher_id == teacher_id
                )
                .first()
            )

            if current_section:
                current_section.class_teacher_id = None

        else:

            # Find new section
            new_section = (
                db.query(Section)
                .filter(
                    Section.section_id == new_section_id
                )
                .first()
            )

            if not new_section:
                raise HTTPException(
                    status_code=404,
                    detail="Section not found"
                )

            # Check whether another teacher already owns it
            if (
                new_section.class_teacher_id is not None
                and new_section.class_teacher_id != teacher_id
            ):
                raise HTTPException(
                    status_code=409,
                    detail="This section is already assigned to another teacher"
                )

            # Find teacher's current section
            current_section = (
                db.query(Section)
                .filter(
                    Section.class_teacher_id == teacher_id
                )
                .first()
            )

            # Remove old section if changing section
            if (
                current_section
                and current_section.section_id != new_section_id
            ):
                current_section.class_teacher_id = None

            # Assign new section
            new_section.class_teacher_id = teacher_id

    # ---------------------------------------------------------
    # User Table Fields
    # ---------------------------------------------------------

    for user_field in ("full_name", "phone", "is_active"):
        if user_field in data:
            setattr(
                teacher.user,
                user_field,
                data.pop(user_field)
            )

    # ---------------------------------------------------------
    # Teacher Table Fields
    # ---------------------------------------------------------

    for field, value in data.items():
        setattr(teacher, field, value)

    # ---------------------------------------------------------
    # Save Everything Together
    # ---------------------------------------------------------

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Unable to update teacher"
        )

    db.refresh(teacher)
    db.refresh(teacher.user)

    return teacher_to_out_dict(teacher)


def delete_teacher(db: Session, teacher_id: int):
    teacher = get_teacher(db, teacher_id)
    user = teacher.user
    db.delete(teacher)  # deleting the user cascades, but explicit teacher delete first is safer with FKs pointing to it
    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete teacher: still assigned as a class teacher or has linked records",
        )


# ---------------------------------------------------------------------
# Subject assignments (which teacher teaches which subject/section)
# ---------------------------------------------------------------------
def assign_subject(db: Session, teacher_id: int, payload: SubjectAssignmentCreate) -> TeacherSubjectAssignment:
    get_teacher(db, teacher_id)  # 404 if missing

    if not db.query(Subject).filter(Subject.subject_id == payload.subject_id).first():
        raise HTTPException(status_code=404, detail="Subject not found")
    if not db.query(Section).filter(Section.section_id == payload.section_id).first():
        raise HTTPException(status_code=404, detail="Section not found")

    assignment = TeacherSubjectAssignment(
        teacher_id=teacher_id, subject_id=payload.subject_id, section_id=payload.section_id
    )
    db.add(assignment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This teacher is already assigned to this subject/section")
    db.refresh(assignment)
    return assignment


def list_teacher_assignments(db: Session, teacher_id: int):
    get_teacher(db, teacher_id)  # 404 if missing
    return (
        db.query(TeacherSubjectAssignment)
        .filter(TeacherSubjectAssignment.teacher_id == teacher_id)
        .all()
    )


def remove_assignment(db: Session, teacher_id: int, assignment_id: int):
    assignment = (
        db.query(TeacherSubjectAssignment)
        .filter(
            TeacherSubjectAssignment.assignment_id == assignment_id,
            TeacherSubjectAssignment.teacher_id == teacher_id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
def get_teacher_section(db: Session, teacher_id: int):
    section = (
        db.query(Section)
        .filter(Section.class_teacher_id == teacher_id)
        .first()
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail="No class/section assigned to this teacher"
        )

    school_class = (
        db.query(SchoolClass)
        .filter(SchoolClass.class_id == section.class_id)
        .first()
    )

    if not school_class:
        raise HTTPException(
            status_code=404,
            detail="Class not found for this section"
        )

    return {
        "teacher_id": teacher_id,
        "section_id": section.section_id,
        "class_id": school_class.class_id,
        "class_name": school_class.class_name,
        "section_name": section.section_name,
    }