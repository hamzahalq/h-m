from __future__ import annotations

import json
import os
from datetime import timedelta
from typing import Any

from utils.constraints import enforce_constraints
from utils.special_days import get_special_days_in_range


FREQUENCY_TO_INTERVAL: dict[str, int] = {
    "1x/week": 7,
    "2x/week": 4,
    "3x/week": 2,
    "daily": 1,
    "agent_decides": 2,
}


def run_strategy_and_calendar(
    campaign: dict[str, Any],
    market_data: dict[str, Any],
    research_brief: dict[str, Any],
) -> list[dict[str, Any]]:
    start_date = campaign["start_date"]
    end_date = campaign["end_date"]
    platforms = campaign["platforms"]
    products = campaign["products"]
    business_type = campaign["business_type"]
    posting_frequency = campaign.get("posting_frequency", "agent_decides")
    interval_days = FREQUENCY_TO_INTERVAL.get(posting_frequency, 2)
    special_days = (
        get_special_days_in_range(start_date, end_date)
        if campaign.get("special_days_enabled", True)
        else {}
    )
    content_pref = campaign.get("content_preference", "agent_decides")

    posts: list[dict[str, Any]] = []
    day_index = 0
    current = start_date
    while current <= end_date:
        if day_index % interval_days == 0:
            for platform in platforms:
                product = products[day_index % len(products)]
                is_b2b = business_type.upper() == "B2B"
                content_type = _pick_content_type(platform, content_pref, is_b2b)
                language = market_data["language_per_platform"].get(platform, "mixed")
                funnel = ["awareness", "consideration", "decision"][day_index % 3]
                is_special = current.isoformat() in special_days
                special_name = special_days.get(current.isoformat(), {}).get("name")

                entry = {
                    "platform": platform,
                    "date": current,
                    "time": market_data["best_times"].get(platform, "18:00"),
                    "product": product,
                    "topic": "",
                    "use_case_angle": "",
                    "content_type": content_type,
                    "language": language,
                    "funnel_stage": funnel,
                    "target_city": market_data["geo_targets"][day_index % len(market_data["geo_targets"])],
                    "age_focus": "28-45" if is_b2b else "18-30",
                    "is_special_day": is_special,
                    "special_day_name": special_name,
                    "_product": product,
                    "_is_b2b": is_b2b,
                    "_value_props": research_brief.get("value_props", []),
                    "_trending": market_data.get("trending_angles", []),
                    "_goal": campaign.get("goal", ""),
                    "_special_name": special_name,
                    "_funnel": funnel,
                    "_index": day_index,
                }
                posts.append(entry)
        current += timedelta(days=1)
        day_index += 1

    posts = enforce_constraints(posts, campaign.get("constraints", {}))

    _fill_topics_with_gpt(posts)

    for post in posts:
        for key in list(post.keys()):
            if key.startswith("_"):
                del post[key]

    return posts


def _pick_content_type(platform: str, pref: str, is_b2b: bool) -> str:
    if pref == "photos":
        return "image"
    if pref == "videos":
        return "video"
    if pref == "reels":
        return "reel"
    if platform == "linkedin":
        return "carousel"
    if platform in ("tiktok", "snapchat"):
        return "reel"
    if platform == "instagram":
        return "reel" if not is_b2b else "image"
    return "image"


def _fill_topics_with_gpt(posts: list[dict[str, Any]]) -> None:
    if not posts or not os.getenv("OPENAI_API_KEY"):
        for i, post in enumerate(posts):
            is_b2b = post.get("_is_b2b", True)
            props = post.get("_value_props", [])
            funnel = post.get("_funnel", "awareness")
            prefix = "ROI playbook" if is_b2b else "Creator tip"
            prop = props[i % len(props)] if props else "save time"
            post["topic"] = f"{prefix}: {prop}"
            product = post.get("_product", "Bith.ai")
            audience = "business teams" if is_b2b else "creators"
            post["use_case_angle"] = f"{product} for {audience} · {funnel} stage"
        return

    try:
        from openai import OpenAI
        client = OpenAI()

        post_specs = [
            {
                "index": i,
                "platform": p["platform"],
                "language": p["language"],
                "funnel": p.get("_funnel"),
                "product": p.get("_product"),
                "is_b2b": p.get("_is_b2b"),
                "special_day": p.get("_special_name"),
                "trending_angle": (p.get("_trending") or [""])[i % max(len(p.get("_trending") or [""]), 1)],
                "value_prop": (p.get("_value_props") or ["great value"])[i % max(len(p.get("_value_props") or [""]), 1)],
            }
            for i, p in enumerate(posts)
        ]

        goal = posts[0].get("_goal", "") if posts else ""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Generate content calendar topics for a marketing campaign.\n"
                    f"Campaign goal: {goal}\n"
                    f"Posts to fill: {json.dumps(post_specs)}\n\n"
                    "For each post return a specific engaging topic and use_case_angle "
                    "tailored to its platform, language, funnel stage, and value prop.\n"
                    "For special day posts, tie the theme to the occasion.\n"
                    f"Return a JSON array of exactly {len(posts)} objects with keys: "
                    "index, topic, use_case_angle"
                ),
            }],
            response_format={"type": "json_object"},
            max_tokens=200 * len(posts),
        )
        data = json.loads(resp.choices[0].message.content)
        items = data if isinstance(data, list) else data.get("posts", data.get("items", []))
        by_index = {item["index"]: item for item in items}
        for i, post in enumerate(posts):
            item = by_index.get(i, {})
            post["topic"] = item.get("topic") or post.get("topic") or "Marketing update"
            post["use_case_angle"] = item.get("use_case_angle") or post.get("use_case_angle") or ""
    except Exception:
        for i, post in enumerate(posts):
            if not post.get("topic"):
                props = post.get("_value_props", [])
                prop = props[i % len(props)] if props else "save time"
                is_b2b = post.get("_is_b2b", True)
                post["topic"] = ("ROI playbook" if is_b2b else "Creator tip") + f": {prop}"
                post["use_case_angle"] = post.get("_product", "Bith.ai") + " · " + post.get("_funnel", "awareness")
