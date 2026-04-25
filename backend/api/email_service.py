from __future__ import annotations

import os

from fastapi import APIRouter


router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/publish")
def send_publish_email(payload: dict):
    to = payload.get("to") or os.getenv("MARKETING_TEAM_EMAIL")
    campaign_name = payload.get("campaign_name", "Campaign")
    subject = f"[Bith.ai] Post published: {campaign_name}"

    if not to:
        return {"sent": False, "reason": "No recipient"}

    if not os.getenv("RESEND_API_KEY"):
        return {"sent": False, "reason": "RESEND_API_KEY not set"}

    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")

        visual_html = ""
        if payload.get("image_url"):
            visual_html += f'<img src="{payload["image_url"]}" style="max-width:480px;border-radius:8px"><br>'
        if payload.get("video_url"):
            visual_html += f'<p><a href="{payload["video_url"]}">▶ Watch video</a></p>'

        html = (
            f"<h2 style='font-family:sans-serif'>{campaign_name}</h2>"
            f"<p><b>Platform:</b> {payload.get('platform', '')} · "
            f"<b>Scheduled:</b> {payload.get('date', '')} {payload.get('time', '')}</p>"
            f"<p><b>Topic:</b> {payload.get('topic', '')}</p>"
            f"<p style='white-space:pre-wrap'>{payload.get('text_content', '')}</p>"
            f"{visual_html}"
        )

        resend.Emails.send({
            "from": "agent@bith.ai",
            "to": [to],
            "subject": subject,
            "html": html,
        })
        return {"sent": True, "to": to, "subject": subject}
    except Exception as e:
        return {"sent": False, "reason": str(e)}
