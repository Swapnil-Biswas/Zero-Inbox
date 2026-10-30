"""
ZERO-INBOX: Discord Webhook & Bot Delivery Provider
"""

import httpx
from typing import Tuple, Optional
from app.core.config import settings
from app.core.models import Digest
from app.delivery.base import NotificationProvider


class DiscordProvider(NotificationProvider):
    """Delivers formatted executive digests to Discord channels using webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or settings.discord_webhook_url

    def validate_configuration(self) -> Tuple[bool, str]:
        if not self.webhook_url or not self.webhook_url.startswith("https://discord.com/api/webhooks/"):
            return False, "Invalid or missing Discord Webhook URL."
        return True, ""

    async def send_digest(self, digest: Digest, destination: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        url = destination or self.webhook_url
        if not url or not url.startswith("https://discord.com/"):
            return False, "Invalid Discord webhook endpoint."

        # Discord embeds have a 4096 char description limit
        desc = digest.content_markdown[:4000]

        payload = {
            "username": "ZERO-INBOX Intelligence",
            "avatar_url": "https://raw.githubusercontent.com/Swapnil-Biswas/zero-inbox/main/docs/logo.png",
            "embeds": [
                {
                    "title": f"📰 {digest.title}",
                    "description": desc,
                    "color": 3447003,  # Blue
                    "footer": {
                        "text": f"Analyzed {digest.total_articles_analyzed} articles • Read time: ~{digest.estimated_read_time_minutes} min • Cost: ${digest.cost_usd:.4f}"
                    }
                }
            ]
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code in (200, 204):
                    return True, None
                return False, f"Discord webhook error {resp.status_code}: {resp.text}"
            except Exception as e:
                return False, f"Failed to send Discord webhook: {str(e)}"

    async def send_test_message(self, destination: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        url = destination or self.webhook_url
        if not url:
            return False, "Missing Discord webhook URL."

        payload = {
            "content": "🔔 **ZERO-INBOX Verification**: Your Discord delivery channel is successfully connected!"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code in (200, 204):
                    return True, None
                return False, f"Discord error {resp.status_code}: {resp.text}"
            except Exception as e:
                return False, str(e)

