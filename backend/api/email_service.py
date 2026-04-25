from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/publish")
def send_publish_email(payload: dict):
    return {
        "sent": True,
        "to": payload.get("to"),
        "subject": f"Post published: {payload.get('campaign_name', 'Campaign')}",
    }
