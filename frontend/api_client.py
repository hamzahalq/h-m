from __future__ import annotations

import requests

API_URL = "http://localhost:8000"


def get_calendar(campaign_id: str):
    response = requests.get(f"{API_URL}/api/campaigns/{campaign_id}/calendar", timeout=30)
    response.raise_for_status()
    return response.json()
