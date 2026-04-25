import streamlit as st

st.set_page_config(
    page_title="Bith.ai Marketing Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 Bith.ai Marketing Agent")
st.caption("AI-powered campaign planning, content generation, and scheduling for the Bith.ai marketing team.")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("### 🚀 New Campaign")
        st.write("Set up a new marketing campaign. Define products, platforms, goals, and constraints. The agent plans everything.")
        st.page_link("pages/1_new_campaign.py", label="Create campaign →")

with col2:
    with st.container(border=True):
        st.markdown("### 📅 Calendar")
        st.write("Review the AI-generated content calendar. Edit posts, adjust timing, add or delete posts before generating visuals.")
        st.page_link("pages/2_calendar.py", label="View calendar →")

with col3:
    with st.container(border=True):
        st.markdown("### 🎨 Generate")
        st.write("Generate images and videos for all approved posts. Review visuals, request edits, and confirm the campaign.")
        st.page_link("pages/3_generate.py", label="Generate visuals →")

with col4:
    with st.container(border=True):
        st.markdown("### 📊 Analytics")
        st.write("View performance of past posts. AI insights explain what worked and why, with recommendations for next campaigns.")
        st.page_link("pages/4_analytics.py", label="View analytics →")

st.divider()

st.subheader("How it works")
steps = [
    ("1", "Fill the campaign form", "Products, platforms, duration, goal, B2B or B2C"),
    ("2", "Agent researches & plans", "Market intelligence → strategy → full content calendar"),
    ("3", "You review & edit", "Approve the plan, edit any post, adjust timing"),
    ("4", "Generate visuals", "DALL-E 3 images + fal.ai Kling videos for every post"),
    ("5", "Confirm & schedule", "Posts go live on scheduled dates, team gets email per publish"),
    ("6", "Track performance", "Analytics tab shows insights and data-driven recommendations"),
]

for num, title, desc in steps:
    with st.container():
        c1, c2 = st.columns([1, 8])
        with c1:
            st.markdown(
                f'<div style="background:#1e3a5f;color:#60a5fa;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px">{num}</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(f"**{title}** — {desc}")
