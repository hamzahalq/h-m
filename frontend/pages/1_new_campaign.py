import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client

st.set_page_config(page_title="New Campaign", page_icon="🚀", layout="wide")

st.title("🚀 New Campaign")
st.caption("Fill in the details and the agent will research, plan, and build your full content calendar.")

with st.form("campaign_form"):
    st.subheader("Campaign basics")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Campaign name *", placeholder="e.g. Ramadan Sprint, Q2 Templates Push")
        goal = st.text_input("Campaign goal *", placeholder="e.g. drive free trial signups, brand awareness in KSA")
    with col2:
        business_type = st.radio("Business type *", ["B2B", "B2C"], horizontal=True)
        product_description = st.text_area("Product description (optional)", placeholder="Extra context — agent scrapes Bith.ai if left empty", height=80)

    st.subheader("Products & platforms")
    col3, col4 = st.columns(2)
    with col3:
        products = st.multiselect(
            "Products *",
            ["Bith.ai Templates", "Bith.ai AI Shorts", "Bith.ai Studio", "Bith.ai Ads Manager"],
            default=["Bith.ai Templates"],
        )
    with col4:
        platforms = st.multiselect(
            "Platforms *",
            ["linkedin", "instagram", "tiktok", "snapchat", "x"],
            default=["linkedin", "instagram"],
            format_func=lambda p: {"linkedin": "💼 LinkedIn", "instagram": "📸 Instagram", "tiktok": "🎵 TikTok", "snapchat": "👻 Snapchat", "x": "🐦 X (Twitter)"}[p],
        )

    st.subheader("Campaign duration")
    col5, col6 = st.columns(2)
    with col5:
        start_date = st.date_input("Start date *")
    with col6:
        end_date = st.date_input("End date *")

    st.subheader("Content preferences (optional — agent decides if not set)")
    col7, col8, col9 = st.columns(3)
    with col7:
        content_preference = st.selectbox(
            "Content type preference",
            ["agent_decides", "photos", "videos", "reels", "mix"],
            format_func=lambda x: {
                "agent_decides": "🤖 Agent decides",
                "photos": "🖼️ Photos only",
                "videos": "🎬 Videos only",
                "reels": "📱 Reels only",
                "mix": "✨ Mix",
            }[x],
        )
    with col8:
        language_preference = st.selectbox(
            "Language preference",
            ["agent_decides", "arabic", "english", "mixed"],
            format_func=lambda x: {
                "agent_decides": "🤖 Agent decides",
                "arabic": "🇸🇦 Arabic",
                "english": "🇬🇧 English",
                "mixed": "🌐 Mixed",
            }[x],
        )
    with col9:
        posting_frequency = st.selectbox(
            "Posting frequency",
            ["agent_decides", "1x/week", "2x/week", "3x/week", "daily"],
            format_func=lambda x: "🤖 Agent decides" if x == "agent_decides" else x,
        )

    st.subheader("Constraints")
    col10, col11 = st.columns(2)
    with col10:
        blackout_dates_raw = st.text_input(
            "Blackout dates",
            placeholder="YYYY-MM-DD, YYYY-MM-DD (comma separated)",
        )
        blackout_times_raw = st.text_input(
            "Blackout time windows",
            placeholder="e.g. 11:30-13:30, 18:00-19:00",
            value="11:30-13:30",
        )
    with col11:
        max_posts_per_day = st.number_input("Max posts per day", min_value=1, max_value=10, value=3)
        special_days_enabled = st.toggle("Auto-detect special days (Saudi + Islamic calendar)", value=True)

    st.divider()
    submitted = st.form_submit_button("Plan Campaign →", type="primary", use_container_width=True)

if submitted:
    if not name or not goal or not products or not platforms:
        st.error("Please fill in: campaign name, goal, products, and platforms.")
        st.stop()

    if start_date >= end_date:
        st.error("End date must be after start date.")
        st.stop()

    blackout_dates = [d.strip() for d in blackout_dates_raw.split(",") if d.strip()] if blackout_dates_raw else []
    blackout_times = [t.strip() for t in blackout_times_raw.split(",") if t.strip()] if blackout_times_raw else []

    payload = {
        "name": name,
        "products": products,
        "platforms": platforms,
        "business_type": business_type,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "goal": goal,
        "product_description": product_description,
        "content_preference": content_preference,
        "language_preference": language_preference,
        "posting_frequency": posting_frequency,
        "constraints": {
            "blackout_dates": blackout_dates,
            "blackout_times": blackout_times,
            "max_posts_per_day": max_posts_per_day,
        },
        "special_days_enabled": special_days_enabled,
    }

    with st.spinner("Creating campaign..."):
        result = api_client.create_campaign(payload)

    campaign_id = result.get("id")
    st.session_state["current_campaign_id"] = campaign_id
    st.session_state["current_campaign_name"] = name

    st.success(f"Campaign created! ID: `{campaign_id}`")

    with st.spinner("Running research & strategy... (Phases 0 → 2)"):
        plan_result = api_client.plan_campaign(campaign_id)

    calendar = plan_result.get("calendar", [])
    st.session_state["calendar"] = calendar

    st.success(f"Plan ready! {len(calendar)} posts planned.")
    st.info("Go to **Calendar** to review and edit your posts, then generate visuals when ready.")

    st.subheader("Quick preview")
    for post in calendar[:3]:
        st.markdown(f"- **{post['platform'].capitalize()}** · {post['date']} {post['time']} · {post['topic']}")
    if len(calendar) > 3:
        st.caption(f"... and {len(calendar) - 3} more posts. Open the Calendar page to see all.")
