"""
ZERO-INBOX: Delivery Dispatcher & Multi-Channel Router
"""

from typing import Tuple, Optional, Dict
from app.core.models import Digest, DeliveryChannel, DeliveryLog, UserPreferences
from app.db.database import db
from app.delivery.base import NotificationProvider
from app.delivery.telegram import TelegramProvider
from app.delivery.discord import DiscordProvider
from app.delivery.whatsapp import WhatsAppProvider


class DeliveryDispatcher:
    """Routes generated digests to user-configured notification providers."""

    def __init__(self):
        self.providers: Dict[DeliveryChannel, NotificationProvider] = {
            DeliveryChannel.TELEGRAM: TelegramProvider(),
            DeliveryChannel.DISCORD: DiscordProvider(),
            DeliveryChannel.WHATSAPP: WhatsAppProvider()
        }

    async def dispatch_digest(self, digest: Digest, prefs: UserPreferences) -> Tuple[bool, Optional[str]]:
        channel = prefs.delivery_channel
        if channel == DeliveryChannel.NONE or not prefs.delivery_destination:
            # Marked as skipped / internal storage only
            db.log_delivery(
                DeliveryLog(
                    digest_id=digest.id,
                    channel=channel,
                    destination=prefs.delivery_destination or "none",
                    status="skipped",
                    error_message=None
                )
            )
            return True, None

        provider = self.providers.get(channel)
        if not provider:
            err = f"Unsupported delivery channel: {channel}"
            db.log_delivery(
                DeliveryLog(
                    digest_id=digest.id,
                    channel=channel,
                    destination=prefs.delivery_destination,
                    status="failed",
                    error_message=err
                )
            )
            return False, err

        success, err = await provider.send_digest(digest, prefs.delivery_destination)
        status = "success" if success else "failed"

        db.log_delivery(
            DeliveryLog(
                digest_id=digest.id,
                channel=channel,
                destination=prefs.delivery_destination,
                status=status,
                error_message=err
            )
        )

        if success:
            digest.delivery_status = "delivered"
            db.save_digest(digest)

        return success, err

    async def send_test_ping(self, channel: DeliveryChannel, destination: str) -> Tuple[bool, Optional[str]]:
        provider = self.providers.get(channel)
        if not provider:
            return False, f"Unsupported channel: {channel}"
        return await provider.send_test_message(destination)


delivery_dispatcher = DeliveryDispatcher()

