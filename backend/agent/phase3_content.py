from __future__ import annotations

from typing import Any


def generate_post_text(post: dict[str, Any], goal: str) -> str:
    return (
        f"{post['topic']}\n"
        f"Use case: {post['use_case_angle']}\n"
        f"Goal: {goal}\n"
        f"CTA: {'Start your team free trial' if post['funnel_stage'] != 'awareness' else 'Learn how Bith.ai works'}"
    )
