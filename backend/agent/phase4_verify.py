from __future__ import annotations

import os
from typing import Any


_CTAS = ["trial", "demo", "free", "start", "try", "sign up", "book", "learn", "discover", "join"]


def verify_text_content(post: dict[str, Any]) -> dict[str, Any]:
    text = post.get("text_content", "") or ""
    issues: list[str] = []

    if len(text) < 40:
        issues.append("Text too short (< 40 chars)")

    lower = text.lower()
    if not any(cta in lower for cta in _CTAS):
        issues.append("No call-to-action found")

    platform = post.get("platform", "")
    if platform == "x" and len(text) > 280:
        issues.append("Exceeds X/Twitter 280 char limit")
    if platform == "linkedin" and len(text) > 3000:
        issues.append("Exceeds LinkedIn 3000 char limit")

    return {"ok": len(issues) == 0, "issues": issues}


def rewrite_if_needed(post: dict[str, Any], goal: str) -> str:
    """Auto-rewrite post text if verification fails. Returns original if GPT unavailable."""
    check = verify_text_content(post)
    if check["ok"]:
        return post.get("text_content", "")

    if not os.getenv("OPENAI_API_KEY"):
        return post.get("text_content", "")

    try:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Rewrite this marketing post to fix these issues: {check['issues']}\n"
                    f"Platform: {post.get('platform')}\n"
                    f"Original text: {post.get('text_content')}\n"
                    f"Campaign goal: {goal}\n\n"
                    "Return only the rewritten post text, no explanation."
                ),
            }],
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return post.get("text_content", "")
