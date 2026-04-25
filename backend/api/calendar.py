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


def _serialize_post(post: Post) -> dict:
    return {
        "id": str(post.id),
        "campaign_id": str(post.campaign_id),
        "platform": post.platform,
        "date": post.date.isoformat() if post.date else None,
        "time": post.time,
        "product": post.product,
        "topic": post.topic,
        "use_case_angle": post.use_case_angle,
        "content_type": post.content_type,
        "language": post.language,
        "funnel_stage": post.funnel_stage,
        "target_city": post.target_city or "",
        "age_focus": post.age_focus or "",
        "is_special_day": post.is_special_day,
        "special_day_name": post.special_day_name,
        "text_content": post.text_content,
        "image_url": post.image_url,
        "video_url": post.video_url,
        "status": post.status,
    }


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
            "language_preference": campaign.language_preference,
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

        posts = session.exec(
            select(Post).where(Post.campaign_id == campaign.id).order_by(Post.date, Post.time)
        ).all()
        serialized = [_serialize_post(p) for p in posts]

    return {"calendar": serialized, "market_data": market_data, "research_brief": research_brief}


@router.get("/api/campaigns/{campaign_id}/calendar")
def get_calendar(campaign_id: UUID):
    with get_session() as session:
        posts = session.exec(
            select(Post).where(Post.campaign_id == campaign_id).order_by(Post.date, Post.time)
        ).all()
    return [_serialize_post(p) for p in posts]


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

        _send_confirmation_emails(campaign, posts)

    return {"confirmed": True, "scheduled_count": len(posts)}


def _send_confirmation_emails(campaign: Campaign, posts: list[Post]) -> None:
    import os
    team_email = os.getenv("MARKETING_TEAM_EMAIL")
    if not team_email or not os.getenv("RESEND_API_KEY"):
        return
    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")
        for post in posts:
            visual_html = ""
            if post.image_url:
                visual_html = f'<img src="{post.image_url}" style="max-width:400px"><br>'
            if post.video_url:
                visual_html += f'<p><a href="{post.video_url}">▶ Watch video</a></p>'
            resend.Emails.send({
                "from": "agent@bith.ai",
                "to": [team_email],
                "subject": f"[Bith.ai] Post scheduled — {campaign.name} · {post.platform} · {post.date}",
                "html": (
                    f"<h2>{campaign.name}</h2>"
                    f"<p><b>Platform:</b> {post.platform} | <b>Date:</b> {post.date} {post.time}</p>"
                    f"<p><b>Topic:</b> {post.topic}</p>"
                    f"<p>{post.text_content or ''}</p>"
                    f"{visual_html}"
                ),
            })
    except Exception:
        pass
