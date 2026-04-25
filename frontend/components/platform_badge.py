PLATFORM_COLORS = {
    "linkedin": "#0A66C2",
    "instagram": "#E1306C",
    "tiktok": "#010101",
    "snapchat": "#FFFC00",
    "x": "#1DA1F2",
}

PLATFORM_ICONS = {
    "linkedin": "💼",
    "instagram": "📸",
    "tiktok": "🎵",
    "snapchat": "👻",
    "x": "🐦",
}

CONTENT_TYPE_ICONS = {
    "image": "🖼️",
    "carousel": "📑",
    "video": "🎬",
    "reel": "📱",
    "mix": "✨",
}

FUNNEL_COLORS = {
    "awareness": "#3B82F6",
    "consideration": "#F59E0B",
    "decision": "#10B981",
}

STATUS_COLORS = {
    "draft": "#6B7280",
    "approved": "#3B82F6",
    "generating": "#F59E0B",
    "generated": "#8B5CF6",
    "published": "#10B981",
}


def platform_badge(platform: str) -> str:
    icon = PLATFORM_ICONS.get(platform, "📢")
    color = PLATFORM_COLORS.get(platform, "#666")
    label = platform.capitalize()
    return f'<span style="background:{color};color:{"#000" if platform=="snapchat" else "#fff"};padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600">{icon} {label}</span>'


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#666")
    return f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase">{status}</span>'


def funnel_badge(stage: str) -> str:
    color = FUNNEL_COLORS.get(stage, "#999")
    return f'<span style="background:{color}22;color:{color};border:1px solid {color};padding:2px 8px;border-radius:8px;font-size:11px;font-weight:600">{stage.upper()}</span>'
