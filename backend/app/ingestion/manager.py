"""
ZERO-INBOX: Source Ingestion Orchestrator
"""

import asyncio
from typing import List, Dict, Tuple
from app.core.models import SourceConfig, SourceType, RawArticle
from app.db.database import db
from app.ingestion.base import SourceConnector
from app.ingestion.rss import RssConnector
from app.ingestion.newsletter import NewsletterConnector
from app.ingestion.reddit import RedditConnector
from app.ingestion.web import WebArticleConnector


class IngestionManager:
    """Coordinates polling and update cycles across all source connectors."""

    def __init__(self):
        self.connectors: Dict[SourceType, SourceConnector] = {
            SourceType.RSS: RssConnector(),
            SourceType.ATOM: RssConnector(),
            SourceType.NEWSLETTER: NewsletterConnector(),
            SourceType.REDDIT: RedditConnector(),
            SourceType.WEB: WebArticleConnector()
        }

    def get_connector(self, source_type: SourceType) -> SourceConnector:
        return self.connectors.get(source_type, self.connectors[SourceType.RSS])

    async def ingest_source(self, source: SourceConfig) -> List[RawArticle]:
        """Polls a single source and updates sync state in the DB."""
        connector = self.get_connector(source.source_type)
        try:
            articles, new_etag, new_last_mod = await connector.fetch_updates(source)
            if source.id:
                db.update_source_sync(source.id, etag=new_etag, last_modified=new_last_mod)
            return articles
        except Exception as e:
            err_msg = str(e)
            if source.id:
                db.update_source_sync(source.id, etag=source.etag, last_modified=source.last_modified, error=err_msg)
            return []

    async def ingest_all_active_sources(self, user_id: str = "default_user") -> List[RawArticle]:
        """Concurrently polls all active sources for a user."""
        sources = db.list_sources(user_id=user_id, status="active")
        if not sources:
            return []

        tasks = [self.ingest_source(src) for src in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_raw_articles: List[RawArticle] = []
        for res in results:
            if isinstance(res, list):
                all_raw_articles.extend(res)

        return all_raw_articles


ingestion_manager = IngestionManager()
