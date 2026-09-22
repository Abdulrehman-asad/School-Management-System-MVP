"""
Business logic for the Timetable module.

Includes clash detection: a section can't have two classes at overlapping
times on the same day, and a teacher can't be scheduled in two places at once.
"""

from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.timetable import TimetableEntry, DayOfWeek
from app.schemas.timetable import TimetableEntryCreate, TimetableEntryUpdate


def _overlaps(existing: TimetableEntry, day_of_week, start_time, end_time) -> bool:
    return (
        existing.day_of_week == day_of_week
        and existing.start_time < end_time
        and existing.end_time > start_time
    )


def _check_conflicts(db: Session, section_id: int, teacher_id: int, day_of_week, start_time,
                      end_time, exclude_timetable_id: Optional[int] = None):
    query = db.query(TimetableEntry).filter(
        TimetableEntry.day_of_week == day_of_week,
        or_(TimetableEntry.section_id == section_id, TimetableEntry.teacher_id == teacher_id),
    )
    if exclude_timetable_id is not None:
        query = query.filter(TimetableEntry.timetable_id != exclude_timetable_id)

    for entry in query.all():
        if _overlaps(entry, day_of_week, start_time, end_time):
            if entry.section_id == section_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"This section already has a class scheduled at that time on {day_of_week.value}",
                )
            if entry.teacher_id == teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"This teacher is already teaching another class at that time on {day_of_week.value}",
                )


def create_timetable_entry(db: Session, payload: TimetableEntryCreate) -> TimetableEntry:
    _check_conflicts(
        db, payload.section_id, payload.teacher_id, payload.day_of_week,
        payload.start_time, payload.end_time,
    )

    new_entry = TimetableEntry(**payload.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def list_timetable(
    db: Session,
    section_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    day_of_week: Optional[DayOfWeek] = None,
) -> List[TimetableEntry]:
    query = db.query(TimetableEntry)
    if section_id is not None:
        query = query.filter(TimetableEntry.section_id == section_id)
    if teacher_id is not None:
        query = query.filter(TimetableEntry.teacher_id == teacher_id)
    if day_of_week is not None:
        query = query.filter(TimetableEntry.day_of_week == day_of_week)

    return query.order_by(TimetableEntry.day_of_week.asc(), TimetableEntry.start_time.asc()).all()


def get_timetable_entry(db: Session, timetable_id: int) -> TimetableEntry:
    obj = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == timetable_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return obj


def update_timetable_entry(db: Session, timetable_id: int, payload: TimetableEntryUpdate) -> TimetableEntry:
    obj = get_timetable_entry(db, timetable_id)
    data = payload.model_dump(exclude_unset=True)

    merged = {
        "section_id": obj.section_id,
        "teacher_id": data.get("teacher_id", obj.teacher_id),
        "day_of_week": data.get("day_of_week", obj.day_of_week),
        "start_time": data.get("start_time", obj.start_time),
        "end_time": data.get("end_time", obj.end_time),
    }
    if merged["end_time"] <= merged["start_time"]:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    _check_conflicts(
        db, merged["section_id"], merged["teacher_id"], merged["day_of_week"],
        merged["start_time"], merged["end_time"], exclude_timetable_id=timetable_id,
    )

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_timetable_entry(db: Session, timetable_id: int):
    obj = get_timetable_entry(db, timetable_id)
    db.delete(obj)
    db.commit()
