"""
Pydantic request/response models for the Notice Board.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date

from app.models.notice import NoticeAudience


class NoticeCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    audience: NoticeAudience = NoticeAudience.all
    class_id: Optional[int] = None
    attachment_path: Optional[str] = None
    publish_date: date
    expiry_date: Optional[date] = None

    @model_validator(mode="after")
    def check_class_id(self):
        if self.audience == NoticeAudience.specific_class and self.class_id is None:
            raise ValueError("class_id is required when audience is 'specific_class'")
        if self.expiry_date and self.expiry_date < self.publish_date:
            raise ValueError("expiry_date cannot be before publish_date")
        return self


class NoticeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    attachment_path: Optional[str] = None
    publish_date: Optional[date] = None
    expiry_date: Optional[date] = None


class NoticeOut(BaseModel):
    notice_id: int
    title: str
    description: Optional[str] = None
    posted_by: int
    audience: NoticeAudience
    class_id: Optional[int] = None
    attachment_path: Optional[str] = None
    publish_date: date
    expiry_date: Optional[date] = None

    class Config:
        from_attributes = True
