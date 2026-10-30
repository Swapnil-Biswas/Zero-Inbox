"""
ZERO-INBOX: Delivery Notification Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from app.core.models import Digest


class NotificationProvider(ABC):
    """Abstract interface for external notification delivery channels."""

    @abstractmethod
    def validate_configuration(self) -> Tuple[bool, str]:
        """Verifies API credentials and connection endpoints."""
        pass

    @abstractmethod
    async def send_digest(self, digest: Digest, destination: str) -> Tuple[bool, Optional[str]]:
        """
        Sends the synthesized digest to the target destination (chat ID, channel, or phone number).
        Returns: (success, error_message)
        """
        pass

    @abstractmethod
    async def send_test_message(self, destination: str) -> Tuple[bool, Optional[str]]:
        """Sends a verification ping."""
        pass

