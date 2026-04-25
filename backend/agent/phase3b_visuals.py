from __future__ import annotations

import os
from typing import Any
from uuid import UUID


_PLATFORM_STYLE = {
    "linkedin": "clean professional business setting, modern office, neutral tones, corporate aesthetic",
    "instagram": "vibrant lifestyle photography, warm tones, aspirational, high contrast",
    "tiktok": "energetic dynamic scene, bold colors, youth culture, phone-native vertical",
    "snapchat": "fun casual scene, bright colors, youthful, vertical format",
    "x": "bold graphic design, clean minimal layout, strong visual hierarchy",
}

_ASPECT_RATIO = {
    "reel": "9:16",
    "video": "16:9",
    "image": "1:1",
    "carousel": "1:1",
}

_VIDEO_DURATION = {
    "tiktok": "5",
    "instagram": "5",
    "snapchat": "5",
    "linkedin": "5",
    "x": "5",
}


def generate_visuals_for_post(post: Any, campaign_data: dict) -> dict[str, str | None]:
    content_type = getattr(post, "content_type", None) or post.get("content_type", "image")
    is_video = content_type in ("reel", "video")

    image_url = _generate_image(post, campaign_data)
    video_url = None
    if is_video:
        video_url = _generate_video(post, campaign_data)

    return {"image_url": image_url, "video_url": video_url}


def _build_visual_prompt(post: Any, campaign_data: dict) -> str:
    platform = _attr(post, "platform") or "instagram"
    product = _attr(post, "product") or "Bith.ai"
    topic = _attr(post, "topic") or ""
    angle = _attr(post, "use_case_angle") or ""
    is_b2b = campaign_data.get("business_type", "B2B").upper() == "B2B"
    style = _PLATFORM_STYLE.get(platform, "professional marketing visual")
    audience_style = "professional business" if is_b2b else "youthful creative"

    return (
        f"Marketing visual for {product}. "
        f"Theme: {topic}. "
        f"Story: {angle}. "
        f"Style: {style}, {audience_style} audience. "
        f"Saudi Arabian market context. "
        "No text overlay. High quality commercial photography."
    )


def _generate_image(post: Any, campaign_data: dict) -> str | None:
    if not os.getenv("OPENAI_API_KEY"):
        return _placeholder_image(post)
    try:
        from openai import OpenAI
        client = OpenAI()
        prompt = _build_visual_prompt(post, campaign_data)
        resp = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return resp.data[0].url
    except Exception:
        return _placeholder_image(post)


def _generate_video(post: Any, campaign_data: dict) -> str | None:
    if not os.getenv("FAL_KEY"):
        return None
    try:
        import fal_client
        platform = _attr(post, "platform") or "instagram"
        prompt = _build_visual_prompt(post, campaign_data)
        result = fal_client.run(
            "fal-ai/kling-video/v1.6/standard/text-to-video",
            arguments={
                "prompt": prompt,
                "duration": _VIDEO_DURATION.get(platform, "5"),
                "aspect_ratio": _ASPECT_RATIO.get(_attr(post, "content_type") or "reel", "9:16"),
            },
        )
        return result.get("video", {}).get("url")
    except Exception:
        return None


def _placeholder_image(post: Any) -> str:
    post_id = _attr(post, "id") or "placeholder"
    return f"https://picsum.photos/seed/{post_id}/800/600"


def _attr(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)
