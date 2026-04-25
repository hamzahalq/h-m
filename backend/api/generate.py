from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlmodel import select

from agent.phase3_content import generate_post_text
from agent.phase3b_visuals import generate_visuals_for_post
from agent.phase4_verify import rewrite_if_needed
from database.db import get_session
from models.campaign import Campaign
from models.post import Post


router = APIRouter(tags=["generate"])
JOBS: dict[str, dict] = {}


@router.post("/api/campaigns/{campaign_id}/generate")
def generate_visuals(campaign_id: UUID, background_tasks: BackgroundTasks):
    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        campaign_data = {
            "id": str(campaign.id),
            "business_type": campaign.business_type,
            "goal": campaign.goal,
        }
        posts = session.exec(select(Post).where(Post.campaign_id == campaign_id)).all()
        post_ids = [str(p.id) for p in posts]

    job_id = str(uuid4())
    JOBS[job_id] = {
        "status": "running",
        "progress": 0.0,
        "results": [],
        "total": len(post_ids),
        "started_at": datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(_run_generation, campaign_id, campaign_data, post_ids, job_id)
    return {"job_id": job_id}


def _run_generation(
    campaign_id: UUID,
    campaign_data: dict,
    post_ids: list[str],
    job_id: str,
) -> None:
    total = len(post_ids)
    results = []

    for i, post_id_str in enumerate(post_ids):
        try:
            with get_session() as session:
                post = session.get(Post, UUID(post_id_str))
                if not post:
                    continue

                if not post.text_content:
                    text = generate_post_text(
                        {
                            "platform": post.platform,
                            "topic": post.topic,
                            "use_case_angle": post.use_case_angle,
                            "funnel_stage": post.funnel_stage,
                            "product": post.product,
                            "language": post.language,
                        },
                        campaign_data.get("goal", ""),
                    )
                    post.text_content = rewrite_if_needed(
                        {**post.__dict__, "text_content": text},
                        campaign_data.get("goal", ""),
                    )

                visuals = generate_visuals_for_post(post, campaign_data)
                post.image_url = visuals["image_url"]
                post.video_url = visuals["video_url"]
                post.status = "generated"
                session.add(post)
                session.commit()

            entry = {"post_id": post_id_str, **visuals}
            results.append(entry)
        except Exception:
            results.append({"post_id": post_id_str, "image_url": None, "video_url": None})

        JOBS[job_id]["results"] = results
        JOBS[job_id]["progress"] = (i + 1) / total

    with get_session() as session:
        campaign = session.get(Campaign, campaign_id)
        if campaign:
            campaign.status = "running"
            session.add(campaign)
            session.commit()

    JOBS[job_id]["status"] = "done"
    JOBS[job_id]["progress"] = 1.0
    JOBS[job_id]["updated_at"] = datetime.utcnow().isoformat()


@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]


@router.post("/api/posts/{post_id}/regenerate")
def regenerate_post(post_id: UUID, payload: dict, background_tasks: BackgroundTasks):
    with get_session() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        campaign = session.get(Campaign, post.campaign_id)
        campaign_data = {
            "business_type": campaign.business_type if campaign else "B2B",
            "goal": campaign.goal if campaign else "",
        }

    job_id = str(uuid4())
    JOBS[job_id] = {"status": "running", "progress": 0.0, "results": []}
    background_tasks.add_task(
        _run_regenerate, post_id, campaign_data, payload.get("feedback", ""), job_id
    )
    return {"job_id": job_id}


def _run_regenerate(
    post_id: UUID, campaign_data: dict, feedback: str, job_id: str
) -> None:
    try:
        with get_session() as session:
            post = session.get(Post, post_id)
            if not post:
                JOBS[job_id] = {"status": "done", "progress": 1.0, "results": []}
                return

            if feedback:
                new_text = generate_post_text(
                    {
                        "platform": post.platform,
                        "topic": f"{post.topic} ({feedback})",
                        "use_case_angle": post.use_case_angle,
                        "funnel_stage": post.funnel_stage,
                        "product": post.product,
                        "language": post.language,
                    },
                    campaign_data.get("goal", ""),
                )
                post.text_content = new_text

            visuals = generate_visuals_for_post(post, campaign_data)
            post.image_url = visuals["image_url"]
            post.video_url = visuals["video_url"]
            post.status = "generated"
            session.add(post)
            session.commit()

        JOBS[job_id] = {
            "status": "done",
            "progress": 1.0,
            "results": [{"post_id": str(post_id), **visuals}],
        }
    except Exception:
        JOBS[job_id] = {"status": "error", "progress": 1.0, "results": []}
