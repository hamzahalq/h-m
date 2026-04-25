from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.social_platforms import SUPPORTED_PLATFORMS, SocialPlatformService


router = APIRouter(prefix="/api/socials", tags=["socials"])
service = SocialPlatformService()


class SocialConnectRequest(BaseModel):
    credentials: dict[str, Any] = Field(default_factory=dict)


class SocialPublishRequest(BaseModel):
    post_id: str
    text_content: str
    image_url: str | None = None
    video_url: str | None = None
    scheduled_time: str | None = None


@router.get("/platforms")
def list_supported_platforms():
    return {"platforms": sorted(SUPPORTED_PLATFORMS)}


@router.post("/{platform}/connect")
def connect_platform(platform: str, payload: SocialConnectRequest):
    try:
        return service.connect_account(platform.lower(), payload.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{platform}/publish")
def publish_to_platform(platform: str, payload: SocialPublishRequest):
    try:
        return service.publish_post(platform.lower(), payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{platform}/sync-analytics")
def sync_platform_analytics(platform: str, payload: dict[str, str]):
    provider_post_id = payload.get("provider_post_id")
    if not provider_post_id:
        raise HTTPException(status_code=400, detail="provider_post_id is required")
    try:
        return service.sync_analytics(platform.lower(), provider_post_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
