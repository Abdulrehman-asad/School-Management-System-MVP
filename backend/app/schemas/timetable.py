"""
Pydantic request/response models for the Timetable module.
"""

from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import time

from app.models.timetable import DayOfWeek


class TimetableEntryCreate(BaseModel):
    section_id: int
    subject_id: int
    teacher_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class TimetableEntryUpdate(BaseModel):
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class TimetableEntryOut(BaseModel):
    timetable_id: int
    section_id: int
    subject_id: int
    teacher_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    class Config:
        from_attributes = True
