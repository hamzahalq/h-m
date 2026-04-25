import streamlit as st
from components.platform_badge import (
    platform_badge, status_badge, funnel_badge,
    PLATFORM_ICONS, CONTENT_TYPE_ICONS,
)


def post_card(post: dict, editable: bool = False, show_visual: bool = False, on_update=None, on_delete=None, on_regenerate=None):
    platform = post.get("platform", "")
    icon = PLATFORM_ICONS.get(platform, "📢")
    content_icon = CONTENT_TYPE_ICONS.get(post.get("content_type", ""), "")

    with st.container(border=True):
        col_header, col_status = st.columns([3, 1])
        with col_header:
            st.markdown(
                f"{icon} **{platform.capitalize()}** · {post.get('date')} at {post.get('time')} · {content_icon} {post.get('content_type', '').capitalize()}",
                unsafe_allow_html=True,
            )
        with col_status:
            st.markdown(status_badge(post.get("status", "draft")), unsafe_allow_html=True)

        st.markdown(
            f"**{post.get('topic', '')}**  \n"
            f"<small style='color:#888'>{post.get('use_case_angle', '')}</small>",
            unsafe_allow_html=True,
        )

        meta_cols = st.columns(4)
        with meta_cols[0]:
            st.caption(f"🌍 {post.get('target_city', '—')}")
        with meta_cols[1]:
            st.caption(f"👥 {post.get('age_focus', '—')}")
        with meta_cols[2]:
            st.caption(f"🗣️ {post.get('language', '—')}")
        with meta_cols[3]:
            st.markdown(funnel_badge(post.get("funnel_stage", "")), unsafe_allow_html=True)

        if post.get("is_special_day"):
            st.info(f"🎉 Special day: **{post.get('special_day_name')}**")

        with st.expander("Post text"):
            st.write(post.get("text_content", "—"))

        if show_visual:
            if post.get("image_url"):
                st.image(post["image_url"], use_container_width=True)
            elif post.get("video_url"):
                st.video(post["video_url"])
            else:
                st.caption("No visual generated yet.")

            if on_regenerate and post.get("status") in ("generated", "approved"):
                with st.expander("Request regeneration"):
                    feedback = st.text_input("Feedback", key=f"regen_feedback_{post['id']}", placeholder="e.g. make it more professional")
                    if st.button("Regenerate", key=f"regen_btn_{post['id']}"):
                        if on_regenerate:
                            on_regenerate(post["id"], feedback)

        if editable:
            with st.expander("Edit post"):
                new_topic = st.text_input("Topic", value=post.get("topic", ""), key=f"topic_{post['id']}")
                new_date = st.text_input("Date (YYYY-MM-DD)", value=post.get("date", ""), key=f"date_{post['id']}")
                new_time = st.text_input("Time (HH:MM)", value=post.get("time", ""), key=f"time_{post['id']}")
                new_content_type = st.selectbox(
                    "Content type",
                    ["image", "carousel", "video", "reel"],
                    index=["image", "carousel", "video", "reel"].index(post.get("content_type", "image")),
                    key=f"ctype_{post['id']}",
                )
                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("Save changes", key=f"save_{post['id']}"):
                        if on_update:
                            on_update(post["id"], {
                                **post,
                                "topic": new_topic,
                                "date": new_date,
                                "time": new_time,
                                "content_type": new_content_type,
                            })
                with col_del:
                    if st.button("Delete post", key=f"del_{post['id']}", type="secondary"):
                        if on_delete:
                            on_delete(post["id"])
