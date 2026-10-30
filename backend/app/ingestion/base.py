"""
ZERO-INBOX: Source Connector Interface
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from app.core.models import SourceConfig, RawArticle


class SourceConnector(ABC):
    """Abstract Base Class for all external source connectors."""

    @abstractmethod
    def validate_configuration(self, source: SourceConfig) -> Tuple[bool, str]:
        """Validates source URL, format, and necessary credentials."""
        pass

    @abstractmethod
    async def fetch_updates(
        self, source: SourceConfig
    ) -> Tuple[List[RawArticle], Optional[str], Optional[str]]:
        """
        Fetches new content since last sync using conditional headers where supported.
        Returns (articles, new_etag, new_last_modified).
        """
        pass

    @abstractmethod
    def get_source_metadata(self, source: SourceConfig) -> Dict[str, Any]:
        """Returns protocol-specific operational metadata."""
        pass

