from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter
from sqlmodel import select

from database.db import get_session
from models.analytics import AnalyticsRow
from models.post import Post


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
def get_analytics(campaign_id: UUID | None = None, platform: str | None = None):
    with get_session() as session:
        query = select(AnalyticsRow)
        if campaign_id:
            query = query.where(AnalyticsRow.campaign_id == campaign_id)
        if platform:
            query = query.where(AnalyticsRow.platform == platform)
        rows = session.exec(query).all()

        results = []
        for row in rows:
            post = session.get(Post, row.post_id)
            results.append({
                "post_id": str(row.post_id),
                "platform": row.platform,
                "date": post.date.isoformat() if post else None,
                "topic": post.topic if post else None,
                "impressions": row.impressions,
                "reach": row.reach,
                "likes": row.likes,
                "comments": row.comments,
                "shares": row.shares,
                "ctr": row.ctr,
                "profile_visits": row.profile_visits,
                "link_clicks": row.link_clicks,
                "saves": row.saves,
                "best_time": row.best_time,
                "age_breakdown": json.loads(row.age_breakdown),
                "gender_breakdown": json.loads(row.gender_breakdown),
                "location_breakdown": json.loads(row.location_breakdown),
            })
    return results


@router.get("/insights")
def get_insights(campaign_id: UUID | None = None):
    _ = campaign_id
    return [
        {
            "insight_text": "LinkedIn ROI posts performed 30% better than average at 10:00 KSA.",
            "why": "Posted during peak KSA business hours on Tuesday. Used a cost-saving ROI angle (reduces $5000/month to $200).",
            "recommendation": "Repeat ROI narrative with a clear numeric before/after on Tuesday mornings.",
            "confidence": 0.81,
            "platform": "linkedin",
            "comparison_metric": "+30% reactions vs. campaign average",
        },
        {
            "insight_text": "Instagram mixed-language reels outperformed Arabic-only posts by 18%.",
            "why": "Mixed Arabic/English copy resonates with bilingual KSA audience aged 18-28 who consume both languages daily.",
            "recommendation": "Keep mixed copy for Reels. Use Arabic-only captions for Snapchat only.",
            "confidence": 0.73,
            "platform": "instagram",
            "comparison_metric": "+18% reach vs. Arabic-only posts",
        },
        {
            "insight_text": "TikTok posts at 19:30 got 52% more link clicks than morning posts.",
            "why": "Evening slot aligns with post-Asr downtime for young Saudi users browsing entertainment content.",
            "recommendation": "Lock TikTok posting time to 19:00-20:00 window across all campaigns.",
            "confidence": 0.88,
            "platform": "tiktok",
            "comparison_metric": "+52% link clicks vs. morning posts",
        },
    ]


@router.post("/seed")
def seed_analytics(campaign_id: UUID):
    """Seed realistic mock analytics for all posts in a campaign."""
    import random
    with get_session() as session:
        posts = session.exec(select(Post).where(Post.campaign_id == campaign_id)).all()
        if not posts:
            return {"seeded": 0}
        for post in posts:
            existing = session.exec(
                select(AnalyticsRow).where(AnalyticsRow.post_id == post.id)
            ).first()
            if existing:
                continue
            impressions = random.randint(800, 8000)
            reach = int(impressions * random.uniform(0.6, 0.9))
            likes = int(reach * random.uniform(0.03, 0.12))
            row = AnalyticsRow(
                campaign_id=campaign_id,
                post_id=post.id,
                platform=post.platform,
                impressions=impressions,
                reach=reach,
                likes=likes,
                comments=random.randint(2, likes // 4 + 1),
                shares=random.randint(1, likes // 6 + 1),
                ctr=round(random.uniform(1.2, 6.5), 2),
                profile_visits=random.randint(10, 200),
                link_clicks=random.randint(5, 150),
                saves=random.randint(2, 80),
                best_time=post.time,
                age_breakdown=json.dumps({"18-24": 30, "25-34": 45, "35-44": 20, "45+": 5}),
                gender_breakdown=json.dumps({"male": 58, "female": 42}),
                location_breakdown=json.dumps({"Riyadh": 45, "Jeddah": 30, "Dammam": 15, "Other": 10}),
            )
            session.add(row)
        session.commit()
    return {"seeded": len(posts)}
