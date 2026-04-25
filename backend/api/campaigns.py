from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from database.db import get_session
from models.campaign import Campaign, CampaignCreate


router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("")
def create_campaign(payload: CampaignCreate):
    campaign = Campaign(
        name=payload.name,
        products=json.dumps(payload.products),
        platforms=json.dumps(payload.platforms),
        business_type=payload.business_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        goal=payload.goal,
        product_description=payload.product_description,
        content_preference=payload.content_preference,
        language_preference=payload.language_preference,
        posting_frequency=payload.posting_frequency,
        constraints_json=json.dumps(payload.constraints),
        special_days_enabled=payload.special_days_enabled,
        status="created",
    )
    with get_session() as session:
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        return {"id": campaign.id, "status": campaign.status}


@router.get("")
def list_campaigns():
    with get_session() as session:
        campaigns = session.exec(select(Campaign).order_by(Campaign.created_at.desc())).all()
    return [
        {"id": c.id, "name": c.name, "status": c.status, "created_at": c.created_at}
        for c in campaigns
    ]


@router.get("/{campaign_id}")
def get_campaign(campaign_id: UUID):
    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "id": campaign.id,
        "name": campaign.name,
        "products": json.loads(campaign.products),
        "platforms": json.loads(campaign.platforms),
        "business_type": campaign.business_type,
        "start_date": campaign.start_date,
        "end_date": campaign.end_date,
        "goal": campaign.goal,
        "product_description": campaign.product_description,
        "content_preference": campaign.content_preference,
        "language_preference": campaign.language_preference,
        "posting_frequency": campaign.posting_frequency,
        "constraints": json.loads(campaign.constraints_json),
        "special_days_enabled": campaign.special_days_enabled,
        "status": campaign.status,
        "created_at": campaign.created_at,
    }
