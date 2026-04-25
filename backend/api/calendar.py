from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import delete, select

from agent.phase0_market import run_market_intelligence
from agent.phase1_research import run_product_research
from agent.phase2_strategy import run_strategy_and_calendar
from database.db import get_session
from models.campaign import Campaign
from models.post import Post


router = APIRouter(tags=["calendar"])


@router.post("/api/campaigns/{campaign_id}/plan")
def plan_campaign(campaign_id: UUID):
    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        campaign_data = {
            "id": str(campaign.id),
            "name": campaign.name,
            "products": json.loads(campaign.products),
            "platforms": json.loads(campaign.platforms),
            "business_type": campaign.business_type,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "goal": campaign.goal,
            "product_description": campaign.product_description,
            "content_preference": campaign.content_preference,
            "posting_frequency": campaign.posting_frequency,
            "constraints": json.loads(campaign.constraints_json),
            "special_days_enabled": campaign.special_days_enabled,
        }

        market_data = run_market_intelligence(campaign_data)
        research_brief = run_product_research(campaign_data)
        calendar_posts = run_strategy_and_calendar(campaign_data, market_data, research_brief)

        session.exec(delete(Post).where(Post.campaign_id == campaign.id))
        for p in calendar_posts:
            session.add(Post(campaign_id=campaign.id, **p))
        campaign.status = "planned"
        session.add(campaign)
        session.commit()

        posts = session.exec(select(Post).where(Post.campaign_id == campaign.id)).all()
    return {"calendar": posts, "market_data": market_data, "research_brief": research_brief}


@router.get("/api/campaigns/{campaign_id}/calendar")
def get_calendar(campaign_id: UUID):
    with get_session() as session:
        posts = session.exec(
            select(Post).where(Post.campaign_id == campaign_id).order_by(Post.date, Post.time)
        ).all()
    return posts


@router.post("/api/campaigns/{campaign_id}/confirm")
def confirm_campaign(campaign_id: UUID):
    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        posts = session.exec(select(Post).where(Post.campaign_id == campaign_id)).all()
        for post in posts:
            post.status = "published"
            session.add(post)
        campaign.status = "confirmed"
        session.add(campaign)
        session.commit()
    return {"confirmed": True, "scheduled_count": len(posts)}
