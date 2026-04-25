# Bith.ai Marketing Agent — Project Context
> Team H&M · The Agent Lab Hackathon · April 25, 2026  
> Mohammad (GitHub Copilot in Cursor) · Hamza (Claude Code CLI)

---

## What we are building

A marketing automation agent built specifically for the Bith.ai marketing team. It replaces manual content planning and creation with an intelligent pipeline that researches the market, plans a full campaign calendar, generates platform-specific content with visuals and video, verifies quality, and learns from past performance to give data-driven recommendations.

This is the marketing team's primary tool for running campaigns — not a one-off script.

---

## Core user flow

```
1. Marketing team opens the app
2. Creates a new campaign → fills in the form
3. Agent runs research + strategy → shows the full calendar (no media yet)
4. Team reviews, edits individual posts, adjusts timing
5. Team clicks "Generate All" → agent generates photos/videos/reels
6. Team reviews visuals, requests edits on specific posts if needed
7. Team confirms the full plan
8. Posts go live on scheduled dates → email sent to team on each publish
9. Analytics tab shows performance of past posts with AI insights
```

---

## Campaign setup form — what the team fills in

### Required fields
| Field | Description |
|---|---|
| Campaign name | e.g. "Ramadan Sprint", "Q2 Templates Push" |
| Product(s) | Select one or more from the product list |
| Platform(s) | LinkedIn, Instagram, X, Snapchat, TikTok — select any combination |
| Campaign duration | Start date → End date |
| Campaign goal | e.g. "drive free trial signups", "brand awareness in KSA" |
| Business type | B2B or B2C — this changes everything about tone, visuals, targeting |

### Optional fields (agent decides if not filled)
| Field | Description | Default if empty |
|---|---|---|
| Product description | Extra context about the product | Agent scrapes Bith.ai |
| Content type preference | Photos / Videos / Reels / Mix / Agent decides | Agent decides best per platform |
| Posting frequency | How many posts per week per platform | Agent decides based on platform norms |
| Language preference | Arabic / English / Mixed | Agent decides per platform + market |
| Target audience details | Extra persona hints | Agent derives from market intelligence |

### Constraints
| Field | Description |
|---|---|
| Blackout dates | Days the agent must NOT schedule posts |
| Blackout times | Time windows to avoid (e.g. prayer times, school hours) |
| Max posts per day | Hard cap across all platforms |

### Special days (agent must know these)
The agent automatically recognises and can create themed content around:

**Saudi national days:**
- Saudi National Day — September 23
- Saudi Founding Day — February 22
- Flag Day (يوم العلم) — March 11

**Islamic occasions (dates shift yearly — agent calculates):**
- Eid Al-Fitr (عيد الفطر)
- Eid Al-Adha (عيد الأضحى)
- Ramadan start
- Prophet's Birthday (المولد النبوي)

**Regional/business events:**
- UAE National Day — December 2
- Jordan Independence Day — May 25
- LEAP Tech Conference (Riyadh — February)
- GITEX (Dubai — October)

The agent checks if any special day falls within the campaign window and suggests themed posts for those days.

---

## B2B vs B2C product classification

This is critical. Content, tone, visuals, and targeting are completely different.

| | B2B | B2C |
|---|---|---|
| Example Bith.ai product | Bith.ai Templates (for business owners who make ads) | Bith.ai AI Shorts (for creators making personal videos) |
| Target | Business owners, marketing managers, agencies | Individual creators, influencers, young users |
| Tone | Professional, ROI-focused, outcome-driven | Fun, casual, relatable, fast |
| Platform priority | LinkedIn, X | TikTok, Instagram, Snapchat |
| CTA | "Book a demo", "Start free trial for your team" | "Try it free", "Make your first video now" |
| Visuals | Clean, modern, business setting | Energetic, colorful, personal |
| KSA targeting example | Store owners in Salla and Riyadh city centre with physical or online shops | Young Saudis aged 18-28 in Riyadh and Jeddah |

The agent must ask B2B or B2C at campaign setup and use it to shape every decision.

---

## Market & geospatial intelligence (Phase 0)

The agent does this automatically before building the calendar:

1. **Trend analysis** — fetches what is trending in KSA (and secondary markets) this week using pytrends. Identifies 3 angles the campaign can attach to.

2. **Geospatial analysis** — for B2B: finds which cities/areas have highest concentration of the target business type (e.g. areas in Riyadh/Jeddah with high store density). For B2C: finds where target age group is most active online.

3. **Demographic profiling** — age range, gender split, device type, online behaviour patterns for the product type in the target market.

4. **Language per platform** — decides Arabic / English / mixed per platform based on the market and business type. Snapchat KSA → Arabic. LinkedIn → English. TikTok → mixed.

5. **Posting time optimisation** — best time per platform for KSA audience. Accounts for Fri-Sat weekend, prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha), Ramadan schedule shifts.

6. **Competitor gap analysis** — what competitors are NOT talking about that Bith.ai can own.

---

## The pipeline phases

```
Phase 0 — Market Intelligence    → market_data.json
Phase 1 — Product Research       → research_brief.json
Phase 2 — Strategy + Calendar    → content_calendar.json  (SHOWN TO TEAM FOR REVIEW)
Phase 3 — Content Generation     → post text files
Phase 3b — Visual Generation     → images + videos  (TRIGGERED BY TEAM AFTER REVIEW)
Phase 4 — Verification           → verification_report.json
Phase 5 — Scheduling + Email     → posts scheduled, email sent on publish
```

**Important:** Phase 3b (visual generation) is separated from Phase 3 (text). The team reviews and approves the text plan before any images or videos are generated. This saves API cost and gives the team control.

---

## Calendar view — what it shows before generation

Each post in the calendar shows:
- Date and exact scheduled time
- Platform
- Content type (will be image / carousel / video / reel)
- Product being promoted
- Post topic / angle
- Use case story behind the post
- Target audience for this post
- Funnel stage (awareness / consideration / decision)
- Language
- Is it a special day themed post
- Status: draft / approved / generated / published

The team can:
- Edit any field on any post
- Move a post to a different day/time
- Delete a post
- Add a post manually
- Reorder posts
- Then click "Generate All Visuals" when happy with the plan

---

## Visual generation options per post

After the team approves the calendar, they click Generate All. For each post the agent generates based on what was planned:

| Content type | What gets generated | Tool |
|---|---|---|
| Image | 1 image matching the post | DALL-E 3 |
| Carousel | N slides with image + headline + body per slide | DALL-E 3 × N |
| Video | Multi-scene video stitched together | fal.ai Kling |
| Reel | Vertical 9:16 short video with script | fal.ai Kling |
| Mix | Agent decides best format per post | Both |

**Video durations by platform:**
- TikTok: 20 seconds (2 clips × 10s)
- Instagram Reels: 30 seconds (3 clips × 10s)
- Snapchat: 10 seconds (1 clip)
- LinkedIn: carousel preferred over video
- X: single image preferred, video optional

After generation, the team can:
- Approve a post visual
- Request a regeneration with specific feedback ("make it more professional", "change the scene")
- The agent regenerates that specific post only

---

## Analytics and AI insights (Phase 5)

The agent reads stored analytics data for past posts and generates insights.

**Data tracked per post:**
- Impressions
- Reach
- Likes / reactions
- Comments
- Shares / reposts
- CTR (click-through rate) %
- Profile visits from post
- Link clicks
- Saves / bookmarks
- Age breakdown of engagers
- Gender breakdown
- Location breakdown (city level)
- Device type
- Best performing time

**AI insight example:**
> "Your LinkedIn post about Bith.ai Templates on March 3 (Tuesday, 10am) got 40% more reactions than your average post. Key reasons: posted during peak KSA business hours, used a cost-saving ROI angle (reduces $5000/month to $200), and connected to the Vision 2030 SMB growth trend that was peaking that week. Recommendation: replicate this angle in your next campaign with the same posting time and a similar ROI hook."

**Analytics are stored in the database** — populated either from real social API connections (future) or manually entered by the team (MVP).

---

## Email notifications

On each post publish, the system sends an email to the marketing team containing:
- Post content (text)
- Visual (image URL or video URL)
- Platform
- Scheduled time
- Campaign name
- Quick link to view analytics later

**Email service:** use `smtplib` with Gmail SMTP or Resend API (simpler).

---

## Tech stack

| Layer | Technology | Owner |
|---|---|---|
| Backend API | FastAPI (Python) | Mohammad |
| Agent pipeline | Python (GPT-4o mini + fal.ai) | Mohammad |
| Database | SQLite + SQLModel | Mohammad |
| Frontend | Streamlit multi-page | Hamza |
| Email | Resend API or smtplib | Mohammad |
| Video generation | fal.ai Kling | Mohammad |
| Image generation | DALL-E 3 (OpenAI) | Mohammad |
| Market intelligence | pytrends + GPT-4o mini | Mohammad |

---

## Folder structure

```
bith_agent/
├── backend/                          # Mohammad owns entirely
│   ├── main.py                       # FastAPI app entry point
│   ├── api/
│   │   ├── campaigns.py              # Campaign CRUD
│   │   ├── calendar.py               # Calendar generation
│   │   ├── generate.py               # Visual generation
│   │   ├── analytics.py              # Analytics + insights
│   │   └── email_service.py          # Email on publish
│   ├── agent/
│   │   ├── phase0_market.py          # Market intelligence
│   │   ├── phase1_research.py        # Product research
│   │   ├── phase2_strategy.py        # Strategy + calendar
│   │   ├── phase3_content.py         # Text content
│   │   ├── phase3b_visuals.py        # Image + video generation
│   │   └── phase4_verify.py          # Verification
│   ├── models/
│   │   ├── campaign.py               # Pydantic + SQLModel schemas
│   │   ├── post.py
│   │   └── analytics.py
│   ├── database/
│   │   └── db.py                     # DB connection + seed data
│   └── utils/
│       ├── special_days.py           # Saudi/Islamic calendar
│       └── constraints.py            # Blackout logic
│
├── frontend/                         # Hamza owns entirely
│   ├── app.py                        # Streamlit entry point
│   ├── pages/
│   │   ├── 1_new_campaign.py         # Campaign setup form
│   │   ├── 2_calendar.py             # Calendar review + edit
│   │   ├── 3_generate.py            # Generate + approve visuals
│   │   └── 4_analytics.py           # Analytics dashboard
│   ├── components/
│   │   ├── post_card.py              # Reusable post card
│   │   ├── calendar_grid.py          # Calendar grid component
│   │   └── platform_badge.py        # Platform icon + badge
│   └── api_client.py                 # All calls to backend API
│
├── outputs/                          # Generated content
│   ├── posts/
│   ├── images/
│   └── videos/
│
├── .env                              # API keys (never commit)
├── .env.example                      # Template (commit this)
├── requirements.txt
├── CONTEXT.md                        # This file
└── README.md
```

---

## API contracts (Mohammad builds, Hamza consumes)

Hamza uses mock responses on Day 1 and plugs in the real API when Mohammad is done.

### Campaigns

```
POST   /api/campaigns
       Body: { name, products[], platforms[], duration, goal, business_type,
               content_preference, constraints, special_days_enabled }
       Returns: { id, status: "created" }

GET    /api/campaigns
       Returns: [{ id, name, status, created_at }]

GET    /api/campaigns/{id}
       Returns: full campaign object
```

### Calendar planning

```
POST   /api/campaigns/{id}/plan
       Triggers: Phase 0 + 1 + 2 (research + strategy, no media)
       Returns: { calendar: [post objects], market_data, research_brief }

GET    /api/campaigns/{id}/calendar
       Returns: [{ id, date, time, platform, topic, use_case, content_type,
                   language, funnel_stage, status, is_special_day, special_day_name }]
```

### Post editing

```
PUT    /api/posts/{id}
       Body: any editable fields
       Returns: updated post

DELETE /api/posts/{id}
       Returns: { success: true }

POST   /api/campaigns/{id}/posts
       Body: manual post addition
       Returns: new post object
```

### Visual generation

```
POST   /api/campaigns/{id}/generate
       Triggers: Phase 3b for all approved posts
       Returns: { job_id } (async — poll for status)

GET    /api/jobs/{job_id}
       Returns: { status: "running"|"done", progress: 0.6, results: [] }

POST   /api/posts/{id}/regenerate
       Body: { feedback: "make it more professional" }
       Returns: { job_id }
```

### Confirm and schedule

```
POST   /api/campaigns/{id}/confirm
       Marks all posts as confirmed and scheduled
       Returns: { confirmed: true, scheduled_count: 7 }
```

### Analytics

```
GET    /api/analytics
       Query params: ?campaign_id=&platform=&from=&to=
       Returns: [{ post_id, impressions, reach, likes, ctr, age_breakdown,
                   location_breakdown, gender_breakdown }]

GET    /api/analytics/insights
       Query params: ?campaign_id=
       Returns: [{ insight_text, confidence, recommendation, comparison_post_id }]
```

---

## Pydantic models (shared understanding)

```python
# Campaign
{
  "id": "uuid",
  "name": "Ramadan Sprint",
  "products": ["Bith.ai Templates"],
  "platforms": ["linkedin", "instagram", "tiktok"],
  "business_type": "B2B",   # or "B2C"
  "start_date": "2026-04-28",
  "end_date": "2026-05-05",
  "goal": "drive free trial signups",
  "product_description": "optional extra context",
  "content_preference": "mix",   # photos / videos / reels / mix / agent_decides
  "language_preference": "agent_decides",
  "constraints": {
    "blackout_dates": ["2026-05-01"],
    "blackout_times": ["11:30-13:30"],  # prayer midday window
    "max_posts_per_day": 3
  },
  "special_days_enabled": true,
  "status": "draft"   # draft / planned / generating / confirmed / running / done
}

# Post
{
  "id": "uuid",
  "campaign_id": "uuid",
  "platform": "instagram",
  "date": "2026-04-29",
  "time": "19:30",
  "product": "Bith.ai Templates",
  "topic": "Before and after: $5000 shoot vs Bith.ai template",
  "use_case_angle": "Store owner in Riyadh cuts production cost by 80%",
  "content_type": "reel",
  "language": "Arabic/English mixed",
  "funnel_stage": "awareness",
  "target_city": "Riyadh",
  "age_focus": "28-40",
  "is_special_day": false,
  "special_day_name": null,
  "text_content": "generated post text here...",
  "image_url": null,   # filled after generation
  "video_url": null,   # filled after generation
  "status": "draft"    # draft / approved / generating / generated / published
}
```

---

## Work split — Mohammad and Hamza

### Mohammad — Backend + Agent Pipeline

**Owns:** Everything in `backend/`

**Day tasks in order:**
1. Set up FastAPI app with basic routing
2. Set up SQLite database with SQLModel — Campaign and Post tables
3. Build `agent/phase0_market.py` — market intelligence with pytrends
4. Build `agent/phase1_research.py` — scrape Bith.ai + GPT extraction
5. Build `agent/phase2_strategy.py` — calendar generation with B2B/B2C awareness, special days, constraints
6. Build `agent/phase3_content.py` — text generation per platform
7. Build `agent/phase3b_visuals.py` — image (DALL-E) + video (fal.ai Kling) generation
8. Build `agent/phase4_verify.py` — quality checking + auto-rewrite
9. Wire all agent phases into `api/calendar.py` and `api/generate.py`
10. Build `api/analytics.py` — seed with sample data, GPT insight generation
11. Build `api/email_service.py` — email on publish using Resend or smtplib
12. Build `utils/special_days.py` — Saudi/Islamic holiday calendar
13. Build `utils/constraints.py` — blackout date/time logic

**Delivers to Hamza:**
- Running FastAPI server on `localhost:8000`
- All API endpoints listed above
- `.env.example` with all required key names

---

### Hamza — Frontend (Streamlit)

**Owns:** Everything in `frontend/`

**Day tasks in order:**
1. Set up `frontend/api_client.py` with mock responses for all API endpoints — this lets Hamza build the full UI without waiting for Mohammad
2. Build `pages/1_new_campaign.py` — the campaign setup form with all fields (products, platforms, B2B/B2C, duration, goal, content type, constraints, special days toggle)
3. Build `pages/2_calendar.py` — calendar grid view showing all planned posts, click to edit any post, drag to reschedule (or date picker), delete, add manual post
4. Build `pages/3_generate.py` — "Generate All Visuals" button, progress bar, post cards showing text + generated image/video side by side, regenerate button per post with feedback input, confirm button
5. Build `pages/4_analytics.py` — analytics dashboard showing past post performance as charts, AI insight cards with percentage comparisons
6. Build `components/post_card.py` — reusable card component used across pages
7. Build `components/calendar_grid.py` — calendar grid with day/time slots
8. Swap `api_client.py` mock responses for real API calls once Mohammad's backend is running

**Mock response format for api_client.py:**
```python
# Use this structure so the real swap is just changing the HTTP calls

def get_calendar(campaign_id):
    # Mohammad not done yet — return mock data
    return [
        {
            "id": "post_001",
            "platform": "instagram",
            "date": "2026-04-29",
            "time": "19:30",
            "topic": "Before and after: $5000 shoot vs Bith.ai",
            "content_type": "reel",
            "status": "draft"
        }
        # ... more posts
    ]
    # When Mohammad is done, replace with:
    # return requests.get(f"{API_URL}/api/campaigns/{campaign_id}/calendar").json()
```

---

## How to not block each other

**The contract is the API spec above.** Mohammad and Hamza both read it once and build to it independently.

| Situation | What to do |
|---|---|
| Hamza needs data Mohammad hasn't built yet | Use mock data in api_client.py |
| Mohammad changes an API response shape | Update CONTEXT.md, tell Hamza the change |
| Both need to update CONTEXT.md | Commit separately, merge manually — it's just docs |
| Integration time | Hamza swaps api_client.py mock to real HTTP calls, test together |

**Suggested split of the hackathon hours:**

| Time | Mohammad | Hamza |
|---|---|---|
| 11:00-11:30 | FastAPI setup + DB models | Streamlit setup + api_client.py mocks |
| 11:30-12:30 | Phase 0 + Phase 1 | Campaign form (page 1) |
| 12:30-14:00 | Phase 2 strategy + calendar API | Calendar view (page 2) |
| 14:00-16:00 | Lunch | Lunch |
| 16:00-17:00 | Phase 3 text + Phase 3b visuals | Generate + approve page (page 3) |
| 17:00-17:30 | Phase 4 verify + email | Analytics page (page 4) |
| 17:30-18:00 | Integration — connect frontend to real API | Integration |
| 18:00-19:00 | Demo polish + run full flow | Demo polish |

---

## Environment variables (.env)

```
OPENAI_API_KEY=sk-xxxxxxxx
FAL_KEY=xxxxxxxx
RESEND_API_KEY=xxxxxxxx      # for email — get from resend.com (free tier)
DATABASE_URL=sqlite:///./bith_agent.db
MARKETING_TEAM_EMAIL=team@bith.ai
```

---

## How to run

**Backend (Mohammad starts this):**
```bash
cd backend
pip install fastapi uvicorn sqlmodel openai fal-client requests beautifulsoup4 python-dotenv pytrends moviepy resend
uvicorn main:app --reload --port 8000
```

**Frontend (Hamza starts this):**
```bash
cd frontend
pip install streamlit requests
streamlit run app.py
```

Both run independently. Frontend calls backend at `http://localhost:8000`.

---

## Demo script (2 minutes)

1. Open the app in the browser
2. Click "New Campaign"
3. Fill in: Product = "Bith.ai Templates", Platform = LinkedIn + Instagram + TikTok, Type = B2B, Duration = 1 week, Goal = "free trial signups"
4. Click "Plan Campaign" — phases 0, 1, 2 run — calendar appears
5. Show the calendar — 7 posts, each with date, time, topic, platform
6. Edit one post live — change the topic or time
7. Click "Generate All Visuals" — show progress
8. Show a generated LinkedIn carousel (5 slides with images)
9. Show a generated Instagram reel video
10. Click "Confirm Campaign"
11. Open Analytics tab — show past post insights with percentage comparisons
12. Say: "Next week the team opens the app, changes the product, clicks plan — same flow"

---

## Special days utility (Mohammad builds this)

```python
# utils/special_days.py

FIXED_SPECIAL_DAYS = {
    "09-23": {"name": "Saudi National Day", "name_ar": "اليوم الوطني السعودي", "tone": "patriotic"},
    "02-22": {"name": "Saudi Founding Day", "name_ar": "يوم التأسيس", "tone": "proud"},
    "03-11": {"name": "Flag Day", "name_ar": "يوم العلم", "tone": "patriotic"},
    "12-02": {"name": "UAE National Day", "name_ar": "اليوم الوطني الإماراتي", "tone": "celebratory"},
    "05-25": {"name": "Jordan Independence Day", "name_ar": "يوم الاستقلال الأردني", "tone": "celebratory"},
}

# Islamic dates shift every year — calculate dynamically using hijri-converter
# pip install hijri-converter

def get_special_days_in_range(start_date, end_date):
    # Returns list of special days falling within the campaign window
    # Including calculated Islamic occasions for the year
    pass
```

---

## Git workflow

```bash
# Mohammad works on backend/
git checkout -b mohammad/backend

# Hamza works on frontend/
git checkout -b hamza/frontend

# Merge to main when both are done
git checkout main
git merge mohammad/backend
git merge hamza/frontend
```

Never commit `.env`. Only commit `.env.example`.

---

## What makes this win

1. **Full pipeline end to end** — research → plan → review → generate → verify → schedule → email
2. **Team control at the right moments** — they see the plan before generation, they approve visuals before confirming
3. **B2B vs B2C intelligence** — content, targeting, and tone are fundamentally different per type
4. **Special days awareness** — agent knows Saudi and Islamic calendar and creates themed content automatically
5. **Data-driven insights** — "this post type got 40% more reactions — here's why"
6. **Self-verification** — agent checks and rewrites its own output before showing the team
7. **One tool, any product** — change the product, run the campaign, get everything generated

---

*Last updated: April 25, 2026 — Team H&M*
