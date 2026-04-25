import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client
from components.post_card import post_card
from components.platform_badge import PLATFORM_ICONS, CONTENT_TYPE_ICONS

st.set_page_config(page_title="Generate Visuals", page_icon="🎨", layout="wide")

st.title("🎨 Generate Visuals")

# ── Load campaign ──────────────────────────────────────────────────────────

campaign_id = st.session_state.get("current_campaign_id")
if not campaign_id:
    st.warning("No active campaign. Go to **New Campaign** first.")
    st.stop()

campaign = api_client.get_campaign(campaign_id)
posts = st.session_state.get("calendar", [])

if not posts:
    with st.spinner("Loading posts..."):
        posts = api_client.get_calendar(campaign_id)
        st.session_state["calendar"] = posts

# ── Stats ──────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total posts", len(posts))
with col2:
    approved = sum(1 for p in posts if p["status"] in ("approved", "generated"))
    st.metric("Ready to generate", approved)
with col3:
    generated = sum(1 for p in posts if p["status"] == "generated")
    st.metric("Generated", generated)
with col4:
    images_count = sum(1 for p in posts if p.get("image_url"))
    videos_count = sum(1 for p in posts if p.get("video_url"))
    st.metric("Visuals ready", images_count + videos_count)

# ── Generate all button ────────────────────────────────────────────────────

st.divider()

if "generation_complete" not in st.session_state:
    st.session_state["generation_complete"] = False

if not st.session_state["generation_complete"]:
    generate_cols = st.columns([2, 1])
    with generate_cols[0]:
        st.info(f"Ready to generate visuals for **{approved}** posts. Images via DALL-E 3, videos via fal.ai Kling.")
    with generate_cols[1]:
        if st.button("🎬 Generate All Visuals", type="primary", use_container_width=True, disabled=approved == 0):
            with st.spinner("Starting generation job..."):
                job = api_client.generate_visuals(campaign_id)
                job_id = job.get("job_id")
                st.session_state["job_id"] = job_id

            progress_bar = st.progress(0, text="Generating visuals...")
            status_placeholder = st.empty()

            for i in range(10):
                time.sleep(0.3)
                progress = (i + 1) / 10
                progress_bar.progress(progress, text=f"Generating... {int(progress * 100)}%")

            status_placeholder.empty()
            job_result = api_client.get_job_status(job_id)

            if job_result.get("status") == "done":
                results_map = {r["post_id"]: r for r in job_result.get("results", [])}
                updated_posts = []
                for post in posts:
                    result = results_map.get(post["id"])
                    if result:
                        updated_posts.append({
                            **post,
                            "status": "generated",
                            "image_url": result.get("image_url"),
                            "video_url": result.get("video_url"),
                        })
                    else:
                        updated_posts.append(post)
                st.session_state["calendar"] = updated_posts
                posts = updated_posts
                st.session_state["generation_complete"] = True
                progress_bar.progress(1.0, text="Generation complete!")
                st.success(f"All visuals generated! Review below and confirm when ready.")
                st.rerun()
            else:
                st.error("Generation failed. Please try again.")
else:
    st.success("Visuals generated. Review below and confirm the campaign when ready.")
    if st.button("Re-generate all", type="secondary"):
        st.session_state["generation_complete"] = False
        st.rerun()

# ── Post cards with visuals ────────────────────────────────────────────────

st.subheader("Review generated content")

posts = st.session_state.get("calendar", [])

def _handle_regenerate(post_id: str, feedback: str):
    with st.spinner(f"Regenerating post {post_id}..."):
        job = api_client.regenerate_post(post_id, feedback)
    st.success("Regeneration started. Refresh the page in a moment.")

tab_all, tab_images, tab_videos = st.tabs(["All", "Images", "Videos"])

with tab_all:
    for post in posts:
        post_card(post, show_visual=True, on_regenerate=_handle_regenerate)

with tab_images:
    image_posts = [p for p in posts if p.get("content_type") in ("image", "carousel")]
    if not image_posts:
        st.caption("No image posts.")
    for post in image_posts:
        post_card(post, show_visual=True, on_regenerate=_handle_regenerate)

with tab_videos:
    video_posts = [p for p in posts if p.get("content_type") in ("video", "reel")]
    if not video_posts:
        st.caption("No video posts.")
    for post in video_posts:
        post_card(post, show_visual=True, on_regenerate=_handle_regenerate)

# ── Confirm campaign ───────────────────────────────────────────────────────

st.divider()
st.subheader("Confirm & schedule")

if st.session_state.get("generation_complete"):
    st.info("Once confirmed, posts will be scheduled on their planned dates and the team will receive an email on each publish.")

    confirm_col, _ = st.columns([1, 2])
    with confirm_col:
        if st.button("Confirm Campaign ✅", type="primary", use_container_width=True):
            with st.spinner("Confirming and scheduling..."):
                result = api_client.confirm_campaign(campaign_id)
            confirmed = result.get("confirmed")
            scheduled_count = result.get("scheduled_count", 0)
            if confirmed:
                st.success(f"Campaign confirmed! {scheduled_count} posts scheduled. Team will receive email notifications on each publish.")
                st.balloons()
                st.info("View performance in the **Analytics** tab after posts go live.")
            else:
                st.error("Something went wrong. Please try again.")
else:
    st.warning("Generate visuals first before confirming the campaign.")
