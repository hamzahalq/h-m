from __future__ import annotations

from typing import Any


def run_product_research(campaign: dict[str, Any]) -> dict[str, Any]:
    product = campaign["products"][0] if campaign["products"] else "Bith.ai Product"
    return {
        "product": product,
        "summary": campaign.get("product_description") or f"{product} helps teams create high-converting content quickly.",
        "value_props": [
            "Reduces production cost",
            "Accelerates iteration speed",
            "Supports multi-platform publishing",
        ],
        "competitor_gap": "Most competitors focus on templates only, while Bith.ai can own the end-to-end workflow story.",
    }
