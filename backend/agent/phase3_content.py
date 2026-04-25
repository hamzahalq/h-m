from __future__ import annotations

import os
from typing import Any


_PLATFORM_TONE = {
    "linkedin": "professional, ROI-focused, data-driven, suitable for business decision-makers",
    "instagram": "visual, aspirational, casual, use relevant emojis",
    "tiktok": "energetic, casual, conversational, use relevant emojis, trending hooks",
    "snapchat": "fun, short, direct, youthful, Arabic preferred",
    "x": "punchy, concise, debate-starting, under 250 chars",
}

_FUNNEL_CTA = {
    "awareness": "Learn how it works",
    "consideration": "Start your free trial",
    "decision": "Book a demo today",
}

_B2B_CTA = {
    "awareness": "See how it works for your team",
    "consideration": "Start a free team trial",
    "decision": "Book a 15-min demo",
}


def generate_post_text(post: dict[str, Any], goal: str) -> str:
    if os.getenv("OPENAI_API_KEY"):
        result = _gpt_generate(post, goal)
        if result:
            return result
    return _fallback_generate(post, goal)


def _gpt_generate(post: dict[str, Any], goal: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI()

        platform = post.get("platform", "instagram")
        language = post.get("language", "english")
        is_b2b = str(post.get("funnel_stage", "")).lower() in ("consideration", "decision")
        cta_map = _B2B_CTA if is_b2b else _FUNNEL_CTA
        cta = cta_map.get(post.get("funnel_stage", "awareness"), "Try it free")
        tone = _PLATFORM_TONE.get(platform, "engaging, clear")

        char_limit = ""
        if platform == "x":
            char_limit = "Keep under 250 characters."
        elif platform == "snapchat":
            char_limit = "Keep under 120 characters."

        lang_instruction = {
            "arabic": "Write entirely in Arabic.",
            "english": "Write entirely in English.",
            "mixed": "Write primarily in Arabic with key English terms for the product name.",
        }.get(language.lower(), "Write in English.")

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Write a {platform} marketing post.\n"
                    f"Product: {post.get('product', 'Bith.ai')}\n"
                    f"Topic: {post.get('topic', '')}\n"
                    f"Angle: {post.get('use_case_angle', '')}\n"
                    f"Funnel stage: {post.get('funnel_stage', 'awareness')}\n"
                    f"Campaign goal: {goal}\n"
                    f"Tone: {tone}\n"
                    f"Language: {lang_instruction}\n"
                    f"CTA to include: {cta}\n"
                    f"{char_limit}\n\n"
                    "Return only the post text, ready to publish."
                ),
            }],
            max_tokens=350,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


def _fallback_generate(post: dict[str, Any], goal: str) -> str:
    funnel = post.get("funnel_stage", "awareness")
    cta = _FUNNEL_CTA.get(funnel, "Try it free")
    return (
        f"{post.get('topic', '')}\n"
        f"{post.get('use_case_angle', '')}\n"
        f"Goal: {goal}\n"
        f"→ {cta}"
    )
