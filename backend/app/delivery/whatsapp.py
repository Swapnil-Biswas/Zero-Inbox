"""
ZERO-INBOX: WhatsApp Business Cloud API Delivery Provider
"""

import httpx
from typing import Tuple, Optional
from app.core.config import settings
from app.core.models import Digest
from app.delivery.base import NotificationProvider


class WhatsAppProvider(NotificationProvider):
    """Integrates official Meta WhatsApp Cloud API for executive digest broadcast."""

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        template_name: Optional[str] = None
    ):
        self.phone_number_id = phone_number_id or settings.whatsapp_phone_number_id
        self.access_token = access_token or settings.whatsapp_access_token
        self.template_name = template_name or settings.whatsapp_template_name

    def validate_configuration(self) -> Tuple[bool, str]:
        if not self.phone_number_id or not self.access_token:
            return False, "WhatsApp Phone Number ID or Access Token is missing."
        return True, ""

    async def send_digest(self, digest: Digest, destination: str) -> Tuple[bool, Optional[str]]:
        is_valid, err = self.validate_configuration()
        if not is_valid:
            return False, err

        # Clean recipient phone number (E.164 without '+')
        recipient = destination.replace("+", "").replace("-", "").replace(" ", "").strip()
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Format concise text (WhatsApp text body has 4096 char limit)
        body_text = f"📰 *{digest.title}*\n\n{digest.content_markdown[:3800]}"

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": True, "body": body_text}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    return True, None
                return False, f"WhatsApp Cloud API error {resp.status_code}: {resp.text}"
            except Exception as e:
                return False, f"WhatsApp delivery failed: {str(e)}"

    async def send_test_message(self, destination: str) -> Tuple[bool, Optional[str]]:
        is_valid, err = self.validate_configuration()
        if not is_valid:
            return False, err

        recipient = destination.replace("+", "").replace("-", "").replace(" ", "").strip()
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": "🔔 *ZERO-INBOX Verification*: WhatsApp delivery channel is active!"}
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    return True, None
                return False, f"WhatsApp status {resp.status_code}: {resp.text}"
            except Exception as e:
                return False, str(e)

