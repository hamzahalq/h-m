import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client
from components.calendar_grid import calendar_grid
from components.post_card import post_card
from components.platform_badge import PLATFORM_ICONS

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")

st.title("📅 Content Calendar")

# ── Load campaign ──────────────────────────────────────────────────────────

campaign_id = st.session_state.get("current_campaign_id")

if not campaign_id:
    campaigns = api_client.list_campaigns()
    if not campaigns:
        st.warning("No campaigns yet. Go to **New Campaign** to create one.")
        st.stop()
    options = {c["name"]: c["id"] for c in campaigns}
    selected_name = st.selectbox("Select a campaign", list(options.keys()))
    campaign_id = options[selected_name]
    st.session_state["current_campaign_id"] = campaign_id

campaign = api_client.get_campaign(campaign_id)
st.caption(f"Campaign: **{campaign.get('name')}** · {campaign.get('start_date')} → {campaign.get('end_date')} · {campaign.get('business_type')}")

# ── Load calendar ──────────────────────────────────────────────────────────

if "calendar" not in st.session_state or st.button("Refresh from server"):
    with st.spinner("Loading calendar..."):
        st.session_state["calendar"] = api_client.get_calendar(campaign_id)

posts = st.session_state.get("calendar", [])

if not posts:
    st.info("No posts planned yet. Run a campaign plan first.")
    st.stop()

# ── Summary stats ──────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total posts", len(posts))
with col2:
    platforms_used = list({p["platform"] for p in posts})
    st.metric("Platforms", len(platforms_used))
with col3:
    approved = sum(1 for p in posts if p["status"] == "approved")
    st.metric("Approved", approved)
with col4:
    special = sum(1 for p in posts if p.get("is_special_day"))
    st.metric("Special day posts", special)

# ── View toggle ────────────────────────────────────────────────────────────

view = st.radio("View", ["Grid", "List"], horizontal=True)

# ── Filters ────────────────────────────────────────────────────────────────

with st.expander("Filters"):
    filter_cols = st.columns(3)
    with filter_cols[0]:
        platform_filter = st.multiselect(
            "Platform",
            ["linkedin", "instagram", "tiktok", "snapchat", "x"],
            format_func=lambda p: f"{PLATFORM_ICONS.get(p,'')} {p.capitalize()}",
        )
    with filter_cols[1]:
        status_filter = st.multiselect("Status", ["draft", "approved", "generated", "published"])
    with filter_cols[2]:
        funnel_filter = st.multiselect("Funnel stage", ["awareness", "consideration", "decision"])

filtered_posts = posts
if platform_filter:
    filtered_posts = [p for p in filtered_posts if p["platform"] in platform_filter]
if status_filter:
    filtered_posts = [p for p in filtered_posts if p["status"] in status_filter]
if funnel_filter:
    filtered_posts = [p for p in filtered_posts if p["funnel_stage"] in funnel_filter]

# ── Calendar display ───────────────────────────────────────────────────────

if view == "Grid":
    calendar_grid(filtered_posts)
else:
    def _handle_update(post_id, updated):
        result = api_client.update_post(post_id, updated)
        for i, p in enumerate(st.session_state["calendar"]):
            if p["id"] == post_id:
                st.session_state["calendar"][i] = {**p, **result}
        st.success(f"Post updated.")
        st.rerun()

    def _handle_delete(post_id):
        api_client.delete_post(post_id)
        st.session_state["calendar"] = [p for p in st.session_state["calendar"] if p["id"] != post_id]
        st.success("Post deleted.")
        st.rerun()

    for post in filtered_posts:
        post_card(post, editable=True, on_update=_handle_update, on_delete=_handle_delete)

# ── Add manual post ────────────────────────────────────────────────────────

st.divider()
with st.expander("➕ Add a post manually"):
    with st.form("add_post_form"):
        a1, a2 = st.columns(2)
        with a1:
            new_platform = st.selectbox("Platform", ["linkedin", "instagram", "tiktok", "snapchat", "x"])
            new_date = st.date_input("Date")
            new_time = st.time_input("Time")
        with a2:
            new_topic = st.text_input("Topic")
            new_content_type = st.selectbox("Content type", ["image", "carousel", "video", "reel"])
            new_language = st.selectbox("Language", ["English", "Arabic", "Arabic/English mixed"])
        new_text = st.text_area("Post text (optional)")
        add_submitted = st.form_submit_button("Add post", type="primary")

    if add_submitted and new_topic:
        new_post = api_client.add_post(campaign_id, {
            "platform": new_platform,
            "date": str(new_date),
            "time": str(new_time)[:5],
            "topic": new_topic,
            "content_type": new_content_type,
            "language": new_language,
            "text_content": new_text,
            "funnel_stage": "awareness",
            "is_special_day": False,
        })
        st.session_state["calendar"].append(new_post)
        st.success("Post added.")
        st.rerun()

# ── Approve all / proceed ──────────────────────────────────────────────────

st.divider()
col_approve, col_generate = st.columns(2)
with col_approve:
    if st.button("Approve all posts", use_container_width=True):
        updated = []
        for post in st.session_state["calendar"]:
            if post["status"] == "draft":
                updated.append({**post, "status": "approved"})
            else:
                updated.append(post)
        st.session_state["calendar"] = updated
        st.success("All posts approved! Go to Generate to create visuals.")
        st.rerun()
with col_generate:
    if st.button("Generate Visuals →", type="primary", use_container_width=True):
        st.switch_page("pages/3_generate.py")
