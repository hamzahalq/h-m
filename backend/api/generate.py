from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from agent.phase3_content import generate_post_text
from agent.phase3b_visuals import build_mock_visual_urls
from database.db import get_session
from models.campaign import Campaign
from models.post import Post


router = APIRouter(tags=["generate"])
JOBS: dict[str, dict] = {}


@router.post("/api/campaigns/{campaign_id}/generate")
def generate_visuals(campaign_id: UUID):
    job_id = str(uuid4())
    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        posts = session.exec(select(Post).where(Post.campaign_id == campaign_id)).all()
        results = []
        for post in posts:
            post.status = "generated"
            if not post.text_content:
                post.text_content = generate_post_text(
                    {"topic": post.topic, "use_case_angle": post.use_case_angle, "funnel_stage": post.funnel_stage},
                    campaign.goal,
                )
            visuals = build_mock_visual_urls(post.id, post.content_type)
            post.image_url = visuals["image_url"]
            post.video_url = visuals["video_url"]
            session.add(post)
            results.append({"post_id": str(post.id), **visuals})
        campaign.status = "running"
        session.add(campaign)
        session.commit()

    JOBS[job_id] = {
        "status": "done",
        "progress": 1.0,
        "results": results,
        "updated_at": datetime.utcnow().isoformat(),
    }
    return {"job_id": job_id}


@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]


@router.post("/api/posts/{post_id}/regenerate")
def regenerate_post(post_id: UUID, payload: dict):
    _feedback = payload.get("feedback", "")
    job_id = str(uuid4())
    with get_session() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        visuals = build_mock_visual_urls(post.id, post.content_type)
        post.image_url = visuals["image_url"]
        post.video_url = visuals["video_url"]
        post.status = "generated"
        session.add(post)
        session.commit()
    JOBS[job_id] = {"status": "done", "progress": 1.0, "results": [{"post_id": str(post_id), **visuals}]}
    return {"job_id": job_id}
