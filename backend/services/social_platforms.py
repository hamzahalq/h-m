from __future__ import annotations

from datetime import datetime
from typing import Any


SUPPORTED_PLATFORMS = {"linkedin", "instagram", "x", "snapchat", "tiktok"}


class SocialPlatformService:
    """
    Integration facade for all social providers.
    Replace stub implementations with real SDK/API calls per platform.
    """

    def connect_account(self, platform: str, credentials: dict[str, Any]) -> dict[str, Any]:
        self._validate_platform(platform)
        return {
            "platform": platform,
            "connected": True,
            "account_id": credentials.get("account_id", f"{platform}_account"),
            "connected_at": datetime.utcnow().isoformat(),
        }

    def publish_post(self, platform: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._validate_platform(platform)
        return {
            "platform": platform,
            "published": True,
            "provider_post_id": f"{platform}_{payload.get('post_id', 'draft')}",
            "published_at": datetime.utcnow().isoformat(),
        }

    def sync_analytics(self, platform: str, provider_post_id: str) -> dict[str, Any]:
        self._validate_platform(platform)
        return {
            "platform": platform,
            "provider_post_id": provider_post_id,
            "synced": True,
            "metrics": {
                "impressions": 1000,
                "reach": 800,
                "likes": 60,
                "comments": 8,
                "shares": 5,
                "ctr": 2.7,
            },
            "synced_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _validate_platform(platform: str) -> None:
        if platform.lower() not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
