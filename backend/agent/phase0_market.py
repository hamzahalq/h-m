from __future__ import annotations

import os
from datetime import datetime
from typing import Any


def run_market_intelligence(campaign: dict[str, Any]) -> dict[str, Any]:
    business_type = campaign["business_type"]
    platforms = campaign["platforms"]
    product = campaign["products"][0] if campaign["products"] else "Bith.ai"

    trending_angles = _fetch_trending_angles(product, business_type)

    geo_targets = (
        ["Riyadh", "Jeddah"]
        if business_type.upper() == "B2B"
        else ["Riyadh", "Jeddah", "Dammam"]
    )

    language_per_platform = {
        p: (
            "english" if p == "linkedin"
            else "arabic" if p == "snapchat"
            else "mixed"
        )
        for p in platforms
    }

    best_times = {
        p: (
            "10:00" if p == "linkedin"
            else "20:00" if p == "x"
            else "19:30"
        )
        for p in platforms
    }

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "trending_angles": trending_angles,
        "geo_targets": geo_targets,
        "language_per_platform": language_per_platform,
        "best_times": best_times,
    }


def _fetch_trending_angles(product: str, business_type: str) -> list[str]:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="ar-SA", tz=180)
        pytrends.build_payload([product], geo="SA", timeframe="now 7-d")
        related = pytrends.related_queries()

        top_queries: list[str] = []
        if product in related and related[product]["top"] is not None:
            top_queries = related[product]["top"]["query"].head(5).tolist()

        if top_queries and os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            client = OpenAI()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": (
                        f"Trending topics in Saudi Arabia this week: {top_queries}\n"
                        f"Product: {product} (targeting {business_type} customers)\n\n"
                        "Identify 3 specific campaign angles that connect these trends "
                        "to the product's value. Return exactly 3 short phrases "
                        "(max 10 words each), one per line, no numbering."
                    ),
                }],
                max_tokens=120,
            )
            lines = [
                l.strip()
                for l in resp.choices[0].message.content.strip().splitlines()
                if l.strip()
            ][:3]
            if len(lines) == 3:
                return lines
    except Exception:
        pass

    if business_type.upper() == "B2B":
        return [
            "Vision 2030 digital transformation for Saudi businesses",
            "Cut content production cost by 80% with AI tools",
            "Faster campaign turnaround in competitive KSA market",
        ]
    return [
        "Creator economy growth among Saudi youth",
        "Short-form video dominating KSA social platforms",
        "Arabic-first content outperforming English on local apps",
    ]
