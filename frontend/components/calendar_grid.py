import streamlit as st
from collections import defaultdict
from components.platform_badge import PLATFORM_ICONS, PLATFORM_COLORS, STATUS_COLORS


def calendar_grid(posts: list):
    if not posts:
        st.info("No posts planned yet.")
        return

    by_date = defaultdict(list)
    for post in posts:
        by_date[post["date"]].append(post)

    sorted_dates = sorted(by_date.keys())

    for date_str in sorted_dates:
        day_posts = sorted(by_date[date_str], key=lambda p: p.get("time", ""))
        date_label = _format_date(date_str)

        st.markdown(f"### {date_label}")

        cols = st.columns(min(len(day_posts), 3))
        for i, post in enumerate(day_posts):
            col = cols[i % 3]
            with col:
                _mini_card(post)

        st.divider()


def _mini_card(post: dict):
    platform = post.get("platform", "")
    icon = PLATFORM_ICONS.get(platform, "📢")
    color = PLATFORM_COLORS.get(platform, "#666")
    status = post.get("status", "draft")
    status_color = STATUS_COLORS.get(status, "#666")
    content_type = post.get("content_type", "")

    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            padding: 10px 14px;
            border-radius: 8px;
            background: #1a1a2e;
            margin-bottom: 8px;
        ">
            <div style="font-size:13px;font-weight:700;color:{color}">{icon} {platform.capitalize()}</div>
            <div style="font-size:11px;color:#aaa;margin-top:2px">{post.get("time")} · {content_type}</div>
            <div style="font-size:13px;margin-top:6px;color:#eee;line-height:1.4">{post.get("topic","")[:60]}{"…" if len(post.get("topic",""))>60 else ""}</div>
            <div style="margin-top:6px">
                <span style="background:{status_color};color:#fff;font-size:10px;padding:2px 7px;border-radius:8px;font-weight:600">{status.upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_date(date_str: str) -> str:
    from datetime import datetime
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%A, %B %d %Y")
    except Exception:
        return date_str
