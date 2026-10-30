"""
ZERO-INBOX: Telegram Bot Delivery Provider
"""

import httpx
from typing import Tuple, Optional, List
from app.core.config import settings
from app.core.models import Digest
from app.delivery.base import NotificationProvider


class TelegramProvider(NotificationProvider):
    """Delivers digests via Telegram Bot API with chunking support for messages >4096 chars."""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.telegram_bot_token

    def validate_configuration(self) -> Tuple[bool, str]:
        if not self.bot_token:
            return False, "Telegram Bot Token is not configured."
        return True, ""

    def _split_markdown_chunks(self, text: str, max_chars: int = 4000) -> List[str]:
        chunks: List[str] = []
        lines = text.split("\n")
        curr = ""
        for line in lines:
            if len(curr) + len(line) + 1 > max_chars:
                chunks.append(curr)
                curr = line + "\n"
            else:
                curr += line + "\n"
        if curr:
            chunks.append(curr)
        return chunks

    async def send_digest(self, digest: Digest, destination: str) -> Tuple[bool, Optional[str]]:
        is_valid, err = self.validate_configuration()
        if not is_valid:
            return False, err

        chunks = self._split_markdown_chunks(digest.content_markdown)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        async with httpx.AsyncClient(timeout=15.0) as client:
            for idx, chunk in enumerate(chunks):
                payload = {
                    "chat_id": destination,
                    "text": chunk,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                try:
                    resp = await client.post(url, json=payload)
                    # If Markdown parsing fails, retry without parse_mode
                    if resp.status_code == 400:
                        payload.pop("parse_mode", None)
                        resp = await client.post(url, json=payload)

                    if resp.status_code != 200:
                        return False, f"Telegram API error {resp.status_code}: {resp.text}"
                except Exception as e:
                    return False, f"HTTP exception sending Telegram message: {str(e)}"

        return True, None

    async def send_test_message(self, destination: str) -> Tuple[bool, Optional[str]]:
        is_valid, err = self.validate_configuration()
        if not is_valid:
            return False, err

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": destination,
            "text": "🔔 *ZERO-INBOX Verification*: Your Telegram notifications are successfully configured!",
            "parse_mode": "Markdown"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    return True, None
                return False, f"Telegram status {resp.status_code}: {resp.text}"
            except Exception as e:
                return False, str(e)
