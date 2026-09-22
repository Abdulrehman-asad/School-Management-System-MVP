"""
Business logic for Results, GPA calculation, printable result cards, and
class position lists.
"""

from typing import Optional, List
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.exam import Exam, ExamSubjectSchedule, Result
from app.models.student import Student
from app.utils.grading import calculate_grade
from app.schemas.exam import (
    BulkResultCreate, ResultUpdate, ResultCardOut, SubjectResultLine, PositionListEntry
)


def enter_bulk_results(db: Session, payload: BulkResultCreate, entered_by_teacher_id: Optional[int]) -> List[Result]:
    schedule = db.query(ExamSubjectSchedule).filter(
        ExamSubjectSchedule.schedule_id == payload.schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Exam schedule not found")

    results = []
    for entry in payload.results:
        if entry.marks_obtained > schedule.total_marks:
            raise HTTPException(
                status_code=400,
                detail=f"Marks for student {entry.student_id} exceed total_marks ({schedule.total_marks})",
            )

        grade, _ = calculate_grade(float(entry.marks_obtained), float(schedule.total_marks))

        existing = (
            db.query(Result)
            .filter(Result.student_id == entry.student_id, Result.schedule_id == payload.schedule_id)
            .first()
        )
        if existing:
            existing.marks_obtained = entry.marks_obtained
            existing.grade = grade
            existing.remarks = entry.remarks
            existing.entered_by = entered_by_teacher_id
            results.append(existing)
        else:
            new_result = Result(
                student_id=entry.student_id,
                schedule_id=payload.schedule_id,
                marks_obtained=entry.marks_obtained,
                grade=grade,
                remarks=entry.remarks,
                entered_by=entered_by_teacher_id,
            )
            db.add(new_result)
            results.append(new_result)

    db.commit()
    for r in results:
        db.refresh(r)
    return results


def list_results(db: Session, schedule_id: Optional[int] = None, student_id: Optional[int] = None,
                  skip: int = 0, limit: int = 200) -> List[Result]:
    query = db.query(Result)
    if schedule_id is not None:
        query = query.filter(Result.schedule_id == schedule_id)
    if student_id is not None:
        query = query.filter(Result.student_id == student_id)
    return query.offset(skip).limit(limit).all()


def get_result(db: Session, result_id: int) -> Result:
    obj = db.query(Result).filter(Result.result_id == result_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Result not found")
    return obj


def update_result(db: Session, result_id: int, payload: ResultUpdate) -> Result:
    obj = get_result(db, result_id)
    data = payload.model_dump(exclude_unset=True)

    if "marks_obtained" in data:
        schedule = obj.schedule
        if data["marks_obtained"] > schedule.total_marks:
            raise HTTPException(
                status_code=400, detail=f"Marks cannot exceed total_marks ({schedule.total_marks})"
            )
        grade, _ = calculate_grade(float(data["marks_obtained"]), float(schedule.total_marks))
        obj.grade = grade

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_result(db: Session, result_id: int):
    obj = get_result(db, result_id)
    db.delete(obj)
    db.commit()


# ---------------------------------------------------------------------
# Report card (subject-wise marks + overall GPA) for one student in one exam
# ---------------------------------------------------------------------
def _build_result_card(db: Session, student: Student, exam: Exam) -> ResultCardOut:
    schedules = (
        db.query(ExamSubjectSchedule)
        .options(joinedload(ExamSubjectSchedule.subject))
        .filter(ExamSubjectSchedule.exam_id == exam.exam_id)
        .all()
    )
    if not schedules:
        raise HTTPException(status_code=404, detail="No subjects have been scheduled for this exam yet")

    subject_lines = []
    total_obtained = Decimal("0")
    total_possible = 0
    gpa_points_sum = 0.0
    graded_subject_count = 0

    for schedule in schedules:
        result = (
            db.query(Result)
            .filter(Result.student_id == student.student_id, Result.schedule_id == schedule.schedule_id)
            .first()
        )
        if result is None:
            continue  # subject not yet graded for this student — skip from the card

        _, gpa_points = calculate_grade(float(result.marks_obtained), float(schedule.total_marks))

        subject_lines.append(SubjectResultLine(
            subject_id=schedule.subject_id,
            subject_name=schedule.subject.subject_name,
            marks_obtained=result.marks_obtained,
            total_marks=schedule.total_marks,
            passing_marks=schedule.passing_marks,
            grade=result.grade or "N/A",
            is_pass=result.marks_obtained >= schedule.passing_marks,
        ))
        total_obtained += result.marks_obtained
        total_possible += schedule.total_marks
        gpa_points_sum += gpa_points
        graded_subject_count += 1

    if graded_subject_count == 0:
        raise HTTPException(status_code=404, detail="No results have been entered for this student yet")

    overall_percentage = round((float(total_obtained) / total_possible) * 100, 2) if total_possible else 0.0
    overall_grade, _ = calculate_grade(float(total_obtained), float(total_possible))
    gpa = round(gpa_points_sum / graded_subject_count, 2)

    return ResultCardOut(
        student_id=student.student_id,
        student_name=student.user.full_name,
        registration_no=student.registration_no,
        exam_id=exam.exam_id,
        exam_name=exam.exam_name,
        subjects=subject_lines,
        total_marks_obtained=total_obtained,
        total_marks_possible=total_possible,
        overall_percentage=overall_percentage,
        overall_grade=overall_grade,
        gpa=gpa,
    )


def get_result_card(db: Session, student_id: int, exam_id: int) -> ResultCardOut:
    student = db.query(Student).options(joinedload(Student.user)).filter(
        Student.student_id == student_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    card = _build_result_card(db, student, exam)

    # Attach the student's class position for this exam (computed via the position list)
    position_list = _compute_position_list(db, exam)
    for entry in position_list:
        if entry.student_id == student_id:
            card.position = entry.position
            break

    return card


# ---------------------------------------------------------------------
# Position list (class ranking for a given exam)
# ---------------------------------------------------------------------
def _compute_position_list(db: Session, exam: Exam) -> List[PositionListEntry]:
    students = (
        db.query(Student)
        .options(joinedload(Student.user), joinedload(Student.section))
        .join(Student.section)
        .filter(Student.section.has(class_id=exam.class_id))
        .all()
    )

    raw_entries = []
    for student in students:
        try:
            card = _build_result_card(db, student, exam)
        except HTTPException:
            continue  # student has no results yet for this exam — excluded from ranking
        raw_entries.append((student, card))

    # Rank by total marks obtained, descending; ties share the same position (standard competition ranking)
    raw_entries.sort(key=lambda pair: pair[1].total_marks_obtained, reverse=True)

    position_list = []
    previous_marks = None
    current_position = 0
    for idx, (student, card) in enumerate(raw_entries, start=1):
        if card.total_marks_obtained != previous_marks:
            current_position = idx
            previous_marks = card.total_marks_obtained

        position_list.append(PositionListEntry(
            student_id=student.student_id,
            student_name=student.user.full_name,
            registration_no=student.registration_no,
            total_marks_obtained=card.total_marks_obtained,
            overall_percentage=card.overall_percentage,
            gpa=card.gpa,
            position=current_position,
        ))

    return position_list


def get_position_list(db: Session, exam_id: int) -> List[PositionListEntry]:
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return _compute_position_list(db, exam)
