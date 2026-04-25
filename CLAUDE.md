# Bith.ai Marketing Agent — CLAUDE.md

## Who is working on this
- **Hamza** — Frontend (Streamlit) — this repo
- **Mohammad** — Backend (FastAPI) — separate repo

## What has been built (session 1 — April 25 2026)
The full Streamlit frontend is complete and working with mock data.

### Files built
```
frontend/
├── app.py                    ← Home screen, navigation
├── api_client.py             ← ALL backend calls live here. Currently USE_MOCK = True.
├── pages/
│   ├── 1_new_campaign.py     ← Campaign setup form
│   ├── 2_calendar.py         ← Calendar grid + list, edit/delete/add posts
│   ├── 3_generate.py         ← Generate visuals, progress bar, confirm campaign
│   └── 4_analytics.py        ← Metrics, AI insight cards, charts
└── components/
    ├── post_card.py           ← Reusable post card (used on pages 2, 3)
    ├── calendar_grid.py       ← Date-grouped grid view
    └── platform_badge.py      ← Colors, icons, badges for platforms/status/funnel
```

## How to run
```bash
cd /Users/hamzaalqurneh/h-m/frontend
source venv/bin/activate        # venv was created in session 1
streamlit run app.py
```

---

## What to do in the NEXT session — backend integration

**The only file that needs to change is `frontend/api_client.py`.**

### Step 1 — flip the switch
```python
# api_client.py line 6
USE_MOCK = False   # was True
```

### Step 2 — verify Mohammad's backend is running
```bash
curl http://localhost:8000/api/campaigns
```

### Step 3 — fix the known mismatches (from integration contract analysis)

These are confirmed bugs between what the frontend expects and what the backend CONTEXT.md spec says. Before connecting, confirm with Mohammad that he fixed these on his end:

#### BLOCKERS (will crash if not fixed)

**1. Calendar endpoint must return full Post object**
- `GET /api/campaigns/{id}/calendar`
- Must include: `campaign_id, product, use_case_angle, target_city, age_focus, text_content, image_url, video_url`
- Field is `use_case_angle` NOT `use_case` (the spec doc was wrong, the Pydantic model is correct)

**2. Analytics endpoint missing fields**
- `GET /api/analytics`
- Must include: `platform, date, topic` (join from Post table) + `comments, shares, profile_visits, link_clicks, saves, best_time`
- Without these, `pages/4_analytics.py` crashes with `KeyError`

**3. Insights endpoint wrong field names**
- `GET /api/analytics/insights`
- Must return: `why` (string), `platform` (string), `comparison_metric` (string e.g. "+52% link clicks vs. average")
- Must NOT return: `comparison_post_id` (frontend doesn't use it)

#### WARNINGS (won't crash, but functionality missing)

**4. `posting_frequency` field**
- Frontend sends `posting_frequency` in `POST /api/campaigns` body
- Backend Campaign model doesn't have it → silently ignored
- Mohammad should add `posting_frequency: Optional[str] = "agent_decides"` to Campaign model

**5. Job results shape**
- `GET /api/jobs/{job_id}` results array must be: `[{ post_id, image_url, video_url }]`
- Confirm this shape with Mohammad before integration

### Step 4 — add defensive normalization to api_client.py
If Mohammad can't fix everything in time, add these adapters inside api_client.py before returning data to pages:

```python
def _normalize_post(raw: dict) -> dict:
    if "use_case" in raw and "use_case_angle" not in raw:
        raw["use_case_angle"] = raw.pop("use_case")
    raw.setdefault("image_url", None)
    raw.setdefault("video_url", None)
    raw.setdefault("text_content", None)
    raw.setdefault("target_city", "")
    raw.setdefault("age_focus", "")
    return raw

def _normalize_insight(raw: dict) -> dict:
    if "comparison_post_id" in raw and "comparison_metric" not in raw:
        raw["comparison_metric"] = "see comparison post"
    raw.setdefault("why", "")
    raw.setdefault("platform", "")
    return raw
```

Apply `_normalize_post` in `get_calendar()` and `plan_campaign()`.
Apply `_normalize_insight` in `get_insights()`.

---

## Canonical data shapes (source of truth)

```json
// Post — all fields frontend expects
{
  "id": "uuid", "campaign_id": "uuid",
  "platform": "linkedin|instagram|tiktok|snapchat|x",
  "date": "YYYY-MM-DD", "time": "HH:MM",
  "product": "string", "topic": "string", "use_case_angle": "string",
  "content_type": "image|carousel|video|reel",
  "language": "string", "funnel_stage": "awareness|consideration|decision",
  "target_city": "string", "age_focus": "string",
  "is_special_day": false, "special_day_name": null,
  "text_content": null, "image_url": null, "video_url": null,
  "status": "draft|approved|generating|generated|published"
}

// Analytics row
{
  "post_id": "uuid", "platform": "string", "date": "YYYY-MM-DD", "topic": "string",
  "impressions": 0, "reach": 0, "likes": 0, "comments": 0, "shares": 0,
  "ctr": 0.0, "profile_visits": 0, "link_clicks": 0, "saves": 0,
  "age_breakdown": {"18-24": 0}, "gender_breakdown": {"male": 0, "female": 0},
  "location_breakdown": {"Riyadh": 0}, "best_time": "HH:MM"
}

// Insight
{
  "insight_text": "string", "why": "string", "recommendation": "string",
  "confidence": 90, "platform": "string", "comparison_metric": "+52% link clicks vs. average"
}
```

---

## No change needed (already matching)
- `POST /api/campaigns` body shape — Pydantic model uses `start_date`/`end_date` ✓
- `DELETE /api/posts/{id}` → `{ success: true }` ✓
- `POST /api/campaigns/{id}/confirm` → `{ confirmed, scheduled_count }` ✓
- `POST /api/campaigns/{id}/generate` → `{ job_id }` ✓
- `POST /api/posts/{id}/regenerate` → `{ job_id }` ✓
- `GET /api/campaigns` list → `[{ id, name, status, created_at }]` ✓
