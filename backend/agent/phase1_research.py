from __future__ import annotations

import json
import os
from typing import Any


def run_product_research(campaign: dict[str, Any]) -> dict[str, Any]:
    product = campaign["products"][0] if campaign["products"] else "Bith.ai Product"
    description = campaign.get("product_description") or ""

    if not description:
        description = _scrape_bith_ai()

    summary, value_props, competitor_gap = _extract_with_gpt(
        product, description, campaign.get("goal", "")
    )

    return {
        "product": product,
        "summary": summary,
        "value_props": value_props,
        "competitor_gap": competitor_gap,
    }


def _scrape_bith_ai() -> str:
    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get("https://bith.ai", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception:
        return ""


def _extract_with_gpt(
    product: str, description: str, goal: str
) -> tuple[str, list[str], str]:
    default_summary = f"{product} helps teams create high-converting content quickly."
    default_props = [
        "Reduces production cost by 80%",
        "Accelerates content iteration speed",
        "Supports multi-platform publishing",
    ]
    default_gap = "Competitors focus on isolated tools — Bith.ai owns the end-to-end campaign workflow."

    if not os.getenv("OPENAI_API_KEY") or not description:
        return default_summary, default_props, default_gap

    try:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Extract product marketing info.\n"
                    f"Product: {product}\n"
                    f"Campaign goal: {goal}\n"
                    f"Source text: {description[:2000]}\n\n"
                    "Return JSON with keys: summary (one sentence), "
                    "value_props (list of 3 short strings), competitor_gap (one sentence)."
                ),
            }],
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        data = json.loads(resp.choices[0].message.content)
        return (
            data.get("summary", default_summary),
            data.get("value_props", default_props)[:3],
            data.get("competitor_gap", default_gap),
        )
    except Exception:
        return default_summary, default_props, default_gap
