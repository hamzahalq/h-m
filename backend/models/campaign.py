from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CampaignBase(SQLModel):
    name: str
    products: str
    platforms: str
    business_type: str
    start_date: date
    end_date: date
    goal: str
    product_description: Optional[str] = None
    content_preference: str = "agent_decides"
    language_preference: str = "agent_decides"
    posting_frequency: str = "agent_decides"
    constraints_json: str = "{}"
    special_days_enabled: bool = True


class Campaign(CampaignBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CampaignCreate(SQLModel):
    name: str
    products: list[str]
    platforms: list[str]
    business_type: str
    start_date: date
    end_date: date
    goal: str
    product_description: Optional[str] = None
    content_preference: str = "agent_decides"
    language_preference: str = "agent_decides"
    posting_frequency: str = "agent_decides"
    constraints: dict = {}
    special_days_enabled: bool = True


class CampaignRead(SQLModel):
    id: UUID
    name: str
    products: list[str]
    platforms: list[str]
    business_type: str
    start_date: date
    end_date: date
    goal: str
    product_description: Optional[str]
    content_preference: str
    language_preference: str
    constraints: dict
    special_days_enabled: bool
    status: str
    created_at: datetime
