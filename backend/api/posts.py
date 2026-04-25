from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from database.db import get_session
from models.post import Post, PostCreate, PostUpdate


router = APIRouter(tags=["posts"])


@router.put("/api/posts/{post_id}")
def update_post(post_id: UUID, payload: PostUpdate):
    with get_session() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


@router.delete("/api/posts/{post_id}")
def delete_post(post_id: UUID):
    with get_session() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        session.delete(post)
        session.commit()
    return {"success": True}


@router.post("/api/campaigns/{campaign_id}/posts")
def add_post(campaign_id: UUID, payload: PostCreate):
    with get_session() as session:
        post = Post(campaign_id=campaign_id, **payload.model_dump())
        session.add(post)
        session.commit()
        session.refresh(post)
    return post
