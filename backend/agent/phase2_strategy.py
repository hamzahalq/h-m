from __future__ import annotations

from datetime import timedelta
from typing import Any

from utils.constraints import enforce_constraints
from utils.special_days import get_special_days_in_range


FREQUENCY_TO_INTERVAL: dict[str, int] = {
    "1x/week": 7,
    "2x/week": 4,
    "3x/week": 2,
    "daily": 1,
    "agent_decides": 1,
}


def run_strategy_and_calendar(
    campaign: dict[str, Any], market_data: dict[str, Any], research_brief: dict[str, Any]
) -> list[dict[str, Any]]:
    start_date = campaign["start_date"]
    end_date = campaign["end_date"]
    platforms = campaign["platforms"]
    products = campaign["products"]
    business_type = campaign["business_type"]
    posting_frequency = campaign.get("posting_frequency", "agent_decides")
    interval_days = FREQUENCY_TO_INTERVAL.get(posting_frequency, 1)
    special_days = get_special_days_in_range(start_date, end_date) if campaign["special_days_enabled"] else {}

    posts: list[dict[str, Any]] = []
    day_index = 0
    current = start_date
    while current <= end_date:
        if day_index % interval_days == 0:
            for platform in platforms:
                product = products[day_index % len(products)]
                is_b2b = business_type.upper() == "B2B"
                topic_prefix = "ROI playbook" if is_b2b else "Creator growth hack"
                entry = {
                    "platform": platform,
                    "date": current,
                    "time": market_data["best_times"].get(platform, "18:00"),
                    "product": product,
                    "topic": f"{topic_prefix}: {research_brief['value_props'][day_index % 3]}",
                    "use_case_angle": f"{product} for {'business teams' if is_b2b else 'creators'} in {market_data['geo_targets'][0]}",
                    "content_type": "carousel" if platform == "linkedin" else "reel",
                    "language": market_data["language_per_platform"].get(platform, "mixed"),
                    "funnel_stage": ["awareness", "consideration", "decision"][day_index % 3],
                    "target_city": market_data["geo_targets"][day_index % len(market_data["geo_targets"])],
                    "age_focus": "28-40" if is_b2b else "18-28",
                    "is_special_day": current.isoformat() in special_days,
                    "special_day_name": special_days.get(current.isoformat(), {}).get("name"),
                }
                posts.append(entry)
        current += timedelta(days=1)
        day_index += 1

    return enforce_constraints(posts, campaign.get("constraints", {}))
