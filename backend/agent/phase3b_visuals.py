from __future__ import annotations

from uuid import UUID


def build_mock_visual_urls(post_id: UUID, content_type: str) -> dict[str, str | None]:
    image_url = f"https://example.cdn/images/{post_id}.png"
    video_url = None
    if content_type in {"reel", "video"}:
        video_url = f"https://example.cdn/videos/{post_id}.mp4"
    return {"image_url": image_url, "video_url": video_url}
