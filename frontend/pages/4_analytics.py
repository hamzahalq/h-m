import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client
from components.platform_badge import PLATFORM_COLORS, PLATFORM_ICONS

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Analytics & Insights")

# ── Load data ──────────────────────────────────────────────────────────────

campaign_id = st.session_state.get("current_campaign_id")

col_filter1, col_filter2, _ = st.columns([1, 1, 2])
with col_filter1:
    platform_filter = st.selectbox(
        "Platform",
        ["All", "linkedin", "instagram", "tiktok", "snapchat", "x"],
        format_func=lambda p: "All platforms" if p == "All" else f"{PLATFORM_ICONS.get(p,'')} {p.capitalize()}",
    )
with col_filter2:
    if st.button("Refresh data"):
        st.cache_data.clear()

analytics = api_client.get_analytics(
    campaign_id=campaign_id,
    platform=None if platform_filter == "All" else platform_filter,
)
insights = api_client.get_insights(campaign_id=campaign_id)

if not analytics:
    st.info("No analytics data yet. Data appears after posts go live.")
    st.stop()

# ── Summary metrics ────────────────────────────────────────────────────────

total_impressions = sum(a["impressions"] for a in analytics)
total_reach = sum(a["reach"] for a in analytics)
total_likes = sum(a["likes"] for a in analytics)
total_link_clicks = sum(a["link_clicks"] for a in analytics)
avg_ctr = sum(a["ctr"] for a in analytics) / len(analytics)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Impressions", f"{total_impressions:,}")
m2.metric("Total Reach", f"{total_reach:,}")
m3.metric("Total Likes", f"{total_likes:,}")
m4.metric("Link Clicks", f"{total_link_clicks:,}")
m5.metric("Avg CTR", f"{avg_ctr:.1f}%")

st.divider()

# ── AI Insights ────────────────────────────────────────────────────────────

st.subheader("🤖 AI Insights")

for insight in insights:
    platform = insight.get("platform", "")
    color = PLATFORM_COLORS.get(platform, "#666")
    icon = PLATFORM_ICONS.get(platform, "💡")

    with st.container(border=True):
        col_left, col_right = st.columns([3, 1])
        with col_left:
            st.markdown(
                f"**{icon} {insight['insight_text']}**",
            )
            st.caption(f"Why: {insight['why']}")
            st.info(f"💡 **Recommendation:** {insight['recommendation']}")
        with col_right:
            st.metric("Confidence", f"{insight['confidence']}%")
            st.markdown(
                f'<div style="background:{color}22;border:1px solid {color};color:{color};padding:6px 12px;border-radius:8px;font-size:13px;font-weight:700;text-align:center">{insight["comparison_metric"]}</div>',
                unsafe_allow_html=True,
            )

st.divider()

# ── Platform breakdown charts ──────────────────────────────────────────────

st.subheader("Platform performance")

try:
    import pandas as pd

    df = pd.DataFrame(analytics)

    tab_overview, tab_engagement, tab_audience, tab_posts = st.tabs(
        ["Overview", "Engagement", "Audience", "Post breakdown"]
    )

    with tab_overview:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Impressions by platform**")
            by_platform = df.groupby("platform")["impressions"].sum().reset_index()
            by_platform.columns = ["Platform", "Impressions"]
            st.bar_chart(by_platform.set_index("Platform"))

        with chart_col2:
            st.markdown("**Link clicks by platform**")
            by_platform_clicks = df.groupby("platform")["link_clicks"].sum().reset_index()
            by_platform_clicks.columns = ["Platform", "Link Clicks"]
            st.bar_chart(by_platform_clicks.set_index("Platform"))

    with tab_engagement:
        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.markdown("**Likes vs. Shares by post**")
            likes_shares = df[["topic", "likes", "shares"]].set_index("topic")
            st.bar_chart(likes_shares)

        with chart_col4:
            st.markdown("**CTR by platform**")
            ctr_data = df.groupby("platform")["ctr"].mean().reset_index()
            ctr_data.columns = ["Platform", "Avg CTR %"]
            st.bar_chart(ctr_data.set_index("Platform"))

    with tab_audience:
        if analytics:
            sample = analytics[0]
            aud_col1, aud_col2 = st.columns(2)
            with aud_col1:
                st.markdown("**Age breakdown (top post)**")
                age_df = pd.DataFrame(
                    list(sample["age_breakdown"].items()),
                    columns=["Age group", "Share %"],
                ).set_index("Age group")
                st.bar_chart(age_df)

            with aud_col2:
                st.markdown("**Top cities (top post)**")
                city_df = pd.DataFrame(
                    list(sample["location_breakdown"].items()),
                    columns=["City", "Share %"],
                ).set_index("City")
                st.bar_chart(city_df)

    with tab_posts:
        st.markdown("**All posts performance**")
        display_df = df[["platform", "date", "topic", "impressions", "reach", "likes", "shares", "link_clicks", "ctr", "saves"]].copy()
        display_df.columns = ["Platform", "Date", "Topic", "Impressions", "Reach", "Likes", "Shares", "Link Clicks", "CTR %", "Saves"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

except ImportError:
    st.warning("Install pandas for charts: `pip install pandas`")
    for a in analytics:
        with st.container(border=True):
            st.markdown(f"**{a['platform'].capitalize()}** · {a['date']}")
            st.write(f"Impressions: {a['impressions']:,} · Reach: {a['reach']:,} · Likes: {a['likes']:,} · CTR: {a['ctr']}%")
