from __future__ import annotations

from datetime import datetime
from typing import Any


def run_market_intelligence(campaign: dict[str, Any]) -> dict[str, Any]:
    business_type = campaign["business_type"]
    platforms = campaign["platforms"]
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "trending_angles": [
            "Vision 2030 digital growth",
            "Cost-efficient creative production",
            "Faster campaign turnaround",
        ],
        "geo_targets": ["Riyadh", "Jeddah"] if business_type == "B2B" else ["Riyadh", "Jeddah", "Dammam"],
        "language_per_platform": {p: ("english" if p == "linkedin" else "mixed") for p in platforms},
        "best_times": {p: "19:30" if p in {"instagram", "tiktok", "snapchat"} else "10:00" for p in platforms},
    }
