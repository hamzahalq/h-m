from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    campaign_id: UUID = Field(index=True)
    platform: str
    date: date
    time: str
    product: str
    topic: str
    use_case_angle: str
    content_type: str
    language: str
    funnel_stage: str
    target_city: Optional[str] = None
    age_focus: Optional[str] = None
    is_special_day: bool = False
    special_day_name: Optional[str] = None
    text_content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PostUpdate(SQLModel):
    platform: Optional[str] = None
    date: Optional[date] = None
    time: Optional[str] = None
    product: Optional[str] = None
    topic: Optional[str] = None
    use_case_angle: Optional[str] = None
    content_type: Optional[str] = None
    language: Optional[str] = None
    funnel_stage: Optional[str] = None
    target_city: Optional[str] = None
    age_focus: Optional[str] = None
    is_special_day: Optional[bool] = None
    special_day_name: Optional[str] = None
    text_content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    status: Optional[str] = None


class PostCreate(SQLModel):
    platform: str
    date: date
    time: str
    product: str
    topic: str
    use_case_angle: str
    content_type: str
    language: str
    funnel_stage: str
    target_city: Optional[str] = None
    age_focus: Optional[str] = None
    is_special_day: bool = False
    special_day_name: Optional[str] = None
    text_content: Optional[str] = None
