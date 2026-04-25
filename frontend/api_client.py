import requests
import uuid
from datetime import datetime, date, timedelta

API_URL = "http://localhost:8000"
USE_MOCK = False  # Flip to True to use mock data without backend


# ── Normalizers ────────────────────────────────────────────────────────────

def _normalize_post(raw: dict) -> dict:
    if "use_case" in raw and "use_case_angle" not in raw:
        raw["use_case_angle"] = raw.pop("use_case")
    raw.setdefault("use_case_angle", "")
    raw.setdefault("image_url", None)
    raw.setdefault("video_url", None)
    raw.setdefault("text_content", None)
    raw.setdefault("target_city", "")
    raw.setdefault("age_focus", "")
    raw.setdefault("is_special_day", False)
    raw.setdefault("special_day_name", None)
    raw.setdefault("status", "draft")
    if "id" in raw:
        raw["id"] = str(raw["id"])
    if "campaign_id" in raw:
        raw["campaign_id"] = str(raw["campaign_id"])
    return raw


def _normalize_insight(raw: dict) -> dict:
    if "comparison_post_id" in raw and "comparison_metric" not in raw:
        raw["comparison_metric"] = "see comparison post"
    raw.setdefault("why", "")
    raw.setdefault("platform", "")
    raw.setdefault("comparison_metric", "")
    raw.setdefault("recommendation", "")
    # backend returns confidence as float 0-1 or int 0-100 — normalize to int %
    conf = raw.get("confidence", 80)
    if isinstance(conf, float) and conf <= 1.0:
        conf = int(conf * 100)
    raw["confidence"] = int(conf)
    return raw


def _get(path: str, params: dict = None) -> dict | list:
    resp = requests.get(f"{API_URL}{path}", params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, payload: dict = None) -> dict | list:
    resp = requests.post(f"{API_URL}{path}", json=payload or {}, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _put(path: str, payload: dict) -> dict:
    resp = requests.put(f"{API_URL}{path}", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _delete(path: str) -> dict:
    resp = requests.delete(f"{API_URL}{path}", timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Campaigns ──────────────────────────────────────────────────────────────

def create_campaign(payload: dict) -> dict:
    if USE_MOCK:
        return {"id": str(uuid.uuid4()), "status": "created"}
    return _post("/api/campaigns", payload)


def list_campaigns() -> list:
    if USE_MOCK:
        return [
            {"id": "camp_001", "name": "Ramadan Sprint", "status": "planned", "created_at": "2026-04-25T10:00:00"},
            {"id": "camp_002", "name": "Q2 Templates Push", "status": "draft", "created_at": "2026-04-24T09:00:00"},
        ]
    return _get("/api/campaigns")


def get_campaign(campaign_id: str) -> dict:
    if USE_MOCK:
        return {
            "id": campaign_id,
            "name": "Ramadan Sprint",
            "products": ["Bith.ai Templates"],
            "platforms": ["linkedin", "instagram", "tiktok"],
            "business_type": "B2B",
            "start_date": "2026-04-28",
            "end_date": "2026-05-05",
            "goal": "drive free trial signups",
            "content_preference": "mix",
            "language_preference": "agent_decides",
            "constraints": {"blackout_dates": [], "blackout_times": ["11:30-13:30"], "max_posts_per_day": 3},
            "special_days_enabled": True,
            "status": "planned",
        }
    return _get(f"/api/campaigns/{campaign_id}")


# ── Calendar planning ──────────────────────────────────────────────────────

def plan_campaign(campaign_id: str) -> dict:
    if USE_MOCK:
        import time
        time.sleep(2)
        return {"calendar": _mock_calendar(campaign_id), "market_data": {}, "research_brief": {}}
    result = _post(f"/api/campaigns/{campaign_id}/plan")
    result["calendar"] = [_normalize_post(p) for p in result.get("calendar", [])]
    return result


def get_calendar(campaign_id: str) -> list:
    if USE_MOCK:
        return _mock_calendar(campaign_id)
    posts = _get(f"/api/campaigns/{campaign_id}/calendar")
    return [_normalize_post(p) for p in posts]


def _mock_calendar(campaign_id: str) -> list:
    base = date(2026, 4, 28)
    posts = [
        {
            "id": "post_001", "campaign_id": campaign_id, "platform": "linkedin",
            "date": str(base), "time": "09:00", "product": "Bith.ai Templates",
            "topic": "How Riyadh store owners cut content costs by 80% with Bith.ai",
            "use_case_angle": "Store owner in Riyadh cuts production cost from $5000 to $200/month",
            "content_type": "carousel", "language": "English", "funnel_stage": "awareness",
            "target_city": "Riyadh", "age_focus": "28-45", "is_special_day": False,
            "special_day_name": None,
            "text_content": "Tired of spending thousands on content? Bith.ai Templates lets you create professional marketing materials in minutes. Saudi SMBs are saving 80% on production costs. Try it free today.",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_002", "campaign_id": campaign_id, "platform": "instagram",
            "date": str(base + timedelta(days=1)), "time": "19:30", "product": "Bith.ai Templates",
            "topic": "Before & after: professional shoot vs Bith.ai template",
            "use_case_angle": "Visual transformation story for e-commerce owners",
            "content_type": "reel", "language": "Arabic/English mixed", "funnel_stage": "awareness",
            "target_city": "Jeddah", "age_focus": "22-35", "is_special_day": False,
            "special_day_name": None,
            "text_content": "شاهد الفرق! قبل وبعد استخدام Bith.ai Templates. احصل على محتوى احترافي في دقائق. جرّبه مجانًا الآن! ✨",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_003", "campaign_id": campaign_id, "platform": "tiktok",
            "date": str(base + timedelta(days=2)), "time": "20:00", "product": "Bith.ai Templates",
            "topic": "3 templates every Saudi brand needs right now",
            "use_case_angle": "Fast tips for small business owners on TikTok",
            "content_type": "video", "language": "Arabic", "funnel_stage": "consideration",
            "target_city": "Riyadh", "age_focus": "18-30", "is_special_day": False,
            "special_day_name": None,
            "text_content": "٣ تمبلتات ما يعرفها أصحاب الأعمال في السعودية! جرّب Bith.ai مجانًا 👇",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_004", "campaign_id": campaign_id, "platform": "linkedin",
            "date": str(base + timedelta(days=3)), "time": "10:00", "product": "Bith.ai Templates",
            "topic": "ROI breakdown: Bith.ai vs traditional content agency",
            "use_case_angle": "Data-driven comparison for marketing managers",
            "content_type": "carousel", "language": "English", "funnel_stage": "consideration",
            "target_city": "Riyadh", "age_focus": "30-50", "is_special_day": False,
            "special_day_name": None,
            "text_content": "The numbers don't lie. Traditional agency: $5,000/month. Bith.ai Templates: $200/month. Same quality. 10x the speed. See the full breakdown →",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_005", "campaign_id": campaign_id, "platform": "instagram",
            "date": str(base + timedelta(days=4)), "time": "18:00", "product": "Bith.ai Templates",
            "topic": "Vision 2030 is pushing Saudi SMBs online — are you ready?",
            "use_case_angle": "Riding the national digital transformation wave",
            "content_type": "image", "language": "Arabic/English mixed", "funnel_stage": "awareness",
            "target_city": "Riyadh", "age_focus": "25-45", "is_special_day": False,
            "special_day_name": None,
            "text_content": "رؤية 2030 تدفع الأعمال السعودية للرقمنة. Bith.ai Templates يجعل هذا سهلاً وسريعاً.",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_006", "campaign_id": campaign_id, "platform": "tiktok",
            "date": str(base + timedelta(days=5)), "time": "21:00", "product": "Bith.ai Templates",
            "topic": "Watch me build a full ad campaign in 5 minutes",
            "use_case_angle": "Speed demo — shock factor for business owners",
            "content_type": "video", "language": "Arabic", "funnel_stage": "decision",
            "target_city": "Jeddah", "age_focus": "20-35", "is_special_day": False,
            "special_day_name": None,
            "text_content": "شاهد كيف أبني حملة تسويقية كاملة في ٥ دقائق باستخدام Bith.ai! 🚀 جرّبه الآن مجانًا",
            "image_url": None, "video_url": None, "status": "draft",
        },
        {
            "id": "post_007", "campaign_id": campaign_id, "platform": "linkedin",
            "date": str(base + timedelta(days=6)), "time": "09:30", "product": "Bith.ai Templates",
            "topic": "Start your free trial — limited offer for KSA businesses",
            "use_case_angle": "Final CTA post — conversion push",
            "content_type": "image", "language": "English", "funnel_stage": "decision",
            "target_city": "Riyadh", "age_focus": "28-50", "is_special_day": False,
            "special_day_name": None,
            "text_content": "Ready to transform your content strategy? Start your free trial today. No credit card required.",
            "image_url": None, "video_url": None, "status": "draft",
        },
    ]
    return posts


# ── Post editing ───────────────────────────────────────────────────────────

def update_post(post_id: str, payload: dict) -> dict:
    if USE_MOCK:
        return {**payload, "id": post_id}
    return _normalize_post(_put(f"/api/posts/{post_id}", payload))


def delete_post(post_id: str) -> dict:
    if USE_MOCK:
        return {"success": True}
    return _delete(f"/api/posts/{post_id}")


def add_post(campaign_id: str, payload: dict) -> dict:
    if USE_MOCK:
        return {**payload, "id": str(uuid.uuid4()), "campaign_id": campaign_id, "status": "draft"}
    return _normalize_post(_post(f"/api/campaigns/{campaign_id}/posts", payload))


# ── Visual generation ──────────────────────────────────────────────────────

def generate_visuals(campaign_id: str) -> dict:
    if USE_MOCK:
        return {"job_id": "job_" + str(uuid.uuid4())[:8]}
    return _post(f"/api/campaigns/{campaign_id}/generate")


def get_job_status(job_id: str) -> dict:
    if USE_MOCK:
        return {
            "status": "done",
            "progress": 1.0,
            "results": [
                {"post_id": "post_001", "image_url": "https://picsum.photos/seed/post1/800/600", "video_url": None},
                {"post_id": "post_002", "image_url": None, "video_url": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"},
                {"post_id": "post_003", "image_url": None, "video_url": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"},
                {"post_id": "post_004", "image_url": "https://picsum.photos/seed/post4/800/600", "video_url": None},
                {"post_id": "post_005", "image_url": "https://picsum.photos/seed/post5/800/600", "video_url": None},
                {"post_id": "post_006", "image_url": None, "video_url": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"},
                {"post_id": "post_007", "image_url": "https://picsum.photos/seed/post7/800/600", "video_url": None},
            ],
        }
    return _get(f"/api/jobs/{job_id}")


def regenerate_post(post_id: str, feedback: str) -> dict:
    if USE_MOCK:
        return {"job_id": "job_" + str(uuid.uuid4())[:8]}
    return _post(f"/api/posts/{post_id}/regenerate", {"feedback": feedback})


def confirm_campaign(campaign_id: str) -> dict:
    if USE_MOCK:
        return {"confirmed": True, "scheduled_count": 7}
    return _post(f"/api/campaigns/{campaign_id}/confirm")


# ── Analytics ──────────────────────────────────────────────────────────────

def get_analytics(campaign_id: str = None, platform: str = None) -> list:
    if USE_MOCK:
        return _mock_analytics()
    params = {}
    if campaign_id:
        params["campaign_id"] = campaign_id
    if platform:
        params["platform"] = platform
    return _get("/api/analytics", params=params)


def get_insights(campaign_id: str = None) -> list:
    if USE_MOCK:
        return _mock_insights()
    params = {}
    if campaign_id:
        params["campaign_id"] = campaign_id
    raw = _get("/api/analytics/insights", params=params)
    return [_normalize_insight(i) for i in raw]


def _mock_analytics() -> list:
    return [
        {
            "post_id": "post_001", "platform": "linkedin", "date": "2026-04-28",
            "topic": "How Riyadh store owners cut content costs by 80%",
            "impressions": 4200, "reach": 3800, "likes": 210, "comments": 34, "shares": 58,
            "ctr": 4.8, "profile_visits": 120, "link_clicks": 195, "saves": 87,
            "age_breakdown": {"18-24": 8, "25-34": 32, "35-44": 38, "45+": 22},
            "gender_breakdown": {"male": 64, "female": 36},
            "location_breakdown": {"Riyadh": 52, "Jeddah": 24, "Dammam": 14, "Other": 10},
            "best_time": "09:00",
        },
        {
            "post_id": "post_002", "platform": "instagram", "date": "2026-04-29",
            "topic": "Before & after: professional shoot vs Bith.ai template",
            "impressions": 8900, "reach": 7600, "likes": 640, "comments": 89, "shares": 210,
            "ctr": 6.2, "profile_visits": 340, "link_clicks": 280, "saves": 430,
            "age_breakdown": {"18-24": 38, "25-34": 42, "35-44": 14, "45+": 6},
            "gender_breakdown": {"male": 45, "female": 55},
            "location_breakdown": {"Riyadh": 38, "Jeddah": 36, "Dammam": 12, "Other": 14},
            "best_time": "19:30",
        },
        {
            "post_id": "post_003", "platform": "tiktok", "date": "2026-04-30",
            "topic": "3 templates every Saudi brand needs right now",
            "impressions": 22000, "reach": 19500, "likes": 1800, "comments": 245, "shares": 890,
            "ctr": 8.1, "profile_visits": 760, "link_clicks": 490, "saves": 320,
            "age_breakdown": {"18-24": 54, "25-34": 34, "35-44": 9, "45+": 3},
            "gender_breakdown": {"male": 52, "female": 48},
            "location_breakdown": {"Riyadh": 44, "Jeddah": 30, "Dammam": 16, "Other": 10},
            "best_time": "20:00",
        },
        {
            "post_id": "post_004", "platform": "linkedin", "date": "2026-05-01",
            "topic": "ROI breakdown: Bith.ai vs traditional content agency",
            "impressions": 5800, "reach": 5100, "likes": 320, "comments": 67, "shares": 142,
            "ctr": 7.3, "profile_visits": 198, "link_clicks": 312, "saves": 156,
            "age_breakdown": {"18-24": 6, "25-34": 28, "35-44": 42, "45+": 24},
            "gender_breakdown": {"male": 68, "female": 32},
            "location_breakdown": {"Riyadh": 58, "Jeddah": 22, "Dammam": 12, "Other": 8},
            "best_time": "10:00",
        },
    ]


def _mock_insights() -> list:
    return [
        {
            "insight_text": "Your LinkedIn post about ROI breakdown (May 1, 10am) got 52% more link clicks than your average LinkedIn post.",
            "why": "Posted during peak KSA business hours, used a concrete cost comparison ($5,000 vs $200), and targeted decision-stage buyers.",
            "recommendation": "Replicate the cost-comparison angle in your next LinkedIn campaign. Use the same 10am Tuesday posting time.",
            "confidence": 92,
            "platform": "linkedin",
            "comparison_metric": "+52% link clicks vs. average",
        },
        {
            "insight_text": "Your TikTok post on April 30 (8pm) reached 22,000 impressions — 3x your TikTok average.",
            "why": "The '3 tips' format performs exceptionally well on TikTok with Saudi audiences. Posted right after Maghrib prayer when engagement spikes.",
            "recommendation": "Use numbered-list formats ('3 things', '5 mistakes') for TikTok. Always post between 8-10pm KSA time.",
            "confidence": 88,
            "platform": "tiktok",
            "comparison_metric": "+200% impressions vs. average",
        },
        {
            "insight_text": "Instagram Reels are generating 4x more saves than static posts across this campaign.",
            "why": "Reels with before/after transformations trigger save behavior — users bookmark them to revisit later.",
            "recommendation": "Prioritize Reels over static images for Instagram. Always include a before/after element.",
            "confidence": 85,
            "platform": "instagram",
            "comparison_metric": "4x saves vs. static posts",
        },
    ]
