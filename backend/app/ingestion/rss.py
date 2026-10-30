"""
ZERO-INBOX: RSS and Atom Feed Connector with Conditional ETag/Last-Modified Caching
"""

import httpx
import feedparser
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone
import time

from app.core.config import settings
from app.core.models import SourceConfig, RawArticle
from app.core.security import validate_url_safe
from app.ingestion.base import SourceConnector


class RssConnector(SourceConnector):
    """Parses RSS 1.0, 2.0 and Atom feeds with conditional caching to prevent redundant bandwidth usage."""

    def validate_configuration(self, source: SourceConfig) -> Tuple[bool, str]:
        is_safe, error = validate_url_safe(source.url)
        if not is_safe:
            return False, error
        return True, ""

    async def fetch_updates(
        self, source: SourceConfig
    ) -> Tuple[List[RawArticle], Optional[str], Optional[str]]:
        is_valid, err = self.validate_configuration(source)
        if not is_valid:
            raise ValueError(f"Invalid RSS feed URL: {err}")

        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8"
        }
        if source.etag:
            headers["If-None-Match"] = source.etag
        if source.last_modified:
            headers["If-Modified-Since"] = source.last_modified

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True) as client:
            try:
                resp = await client.get(source.url, headers=headers)
            except Exception as e:
                raise ConnectionError(f"HTTP fetch failed for {source.url}: {str(e)}")

        # 304 Not Modified -> No new articles
        if resp.status_code == 304:
            return [], source.etag, source.last_modified

        if resp.status_code != 200:
            raise ConnectionError(f"Unexpected HTTP status {resp.status_code} from {source.url}")

        new_etag = resp.headers.get("etag")
        new_last_modified = resp.headers.get("last-modified")

        # Parse XML feed
        parsed = feedparser.parse(resp.text)
        if parsed.bozo and not parsed.entries:
            raise ValueError(f"Failed to parse XML feed from {source.url}: {getattr(parsed, 'bozo_exception', 'Malformed feed')}")

        raw_articles: List[RawArticle] = []
        for entry in parsed.entries[:settings.max_articles_per_feed]:
            link = getattr(entry, "link", "")
            title = getattr(entry, "title", "Untitled")

            # Content extraction: check content, summary, or description
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].value
            elif hasattr(entry, "summary") and entry.summary:
                content = entry.summary
            elif hasattr(entry, "description") and entry.description:
                content = entry.description

            # Publication date parsing
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
                except Exception:
                    pub_date = None
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
                except Exception:
                    pub_date = None

            author = getattr(entry, "author", None)

            raw_articles.append(
                RawArticle(
                    source_id=source.id or "unknown_source",
                    source_name=source.name,
                    url=link or f"{source.url}#{hash(title)}",
                    title=title,
                    raw_content=content,
                    author=author,
                    published_at=pub_date,
                    retrieved_at=datetime.utcnow(),
                    metadata={
                        "guid": getattr(entry, "id", link),
                        "feed_type": parsed.version or "rss"
                    }
                )
            )

        return raw_articles, new_etag, new_last_modified

    def get_source_metadata(self, source: SourceConfig) -> Dict[str, Any]:
        return {
            "connector": "RssConnector",
            "url": source.url,
            "supports_conditional_etag": True,
            "cached_etag": source.etag,
            "cached_last_modified": source.last_modified
        }

