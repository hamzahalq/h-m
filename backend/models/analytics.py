from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AnalyticsRow(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: UUID = Field(index=True)
    post_id: UUID = Field(index=True)
    platform: str
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    ctr: float = 0.0
    profile_visits: int = 0
    link_clicks: int = 0
    saves: int = 0
    best_time: Optional[str] = None
    age_breakdown: str = "{}"
    location_breakdown: str = "{}"
    gender_breakdown: str = "{}"
    created_at: datetime = Field(default_factory=datetime.utcnow)
