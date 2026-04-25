from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


def enforce_constraints(posts: list[dict[str, Any]], constraints: dict[str, Any]) -> list[dict[str, Any]]:
    blackout_dates = set(constraints.get("blackout_dates", []))
    max_posts_per_day = int(constraints.get("max_posts_per_day", 99))

    by_day: dict[date, int] = defaultdict(int)
    filtered: list[dict[str, Any]] = []
    for post in posts:
        post_date = post["date"]
        day_key = post_date.isoformat()
        if day_key in blackout_dates:
            continue
        if by_day[post_date] >= max_posts_per_day:
            continue
        by_day[post_date] += 1
        filtered.append(post)
    return filtered
