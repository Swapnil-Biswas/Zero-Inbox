"""
ZERO-INBOX: Web and Article Source Connector
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone
import re

from app.core.config import settings
from app.core.models import SourceConfig, RawArticle
from app.core.security import validate_url_safe
from app.ingestion.base import SourceConnector


class WebArticleConnector(SourceConnector):
    """Fetches and parses public web articles cleanly without bypassing authentication or paywalls."""

    def validate_configuration(self, source: SourceConfig) -> Tuple[bool, str]:
        return validate_url_safe(source.url)

    async def fetch_updates(
        self, source: SourceConfig
    ) -> Tuple[List[RawArticle], Optional[str], Optional[str]]:
        is_safe, error = self.validate_configuration(source)
        if not is_safe:
            raise ValueError(f"Security validation failed for URL: {error}")

        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True) as client:
            try:
                resp = await client.get(source.url, headers=headers)
            except Exception as e:
                raise ConnectionError(f"Failed to fetch web article: {str(e)}")

        if resp.status_code in (401, 403):
            raise PermissionError(f"Access restricted or paywalled (HTTP {resp.status_code})")
        if resp.status_code != 200:
            raise ConnectionError(f"HTTP error {resp.status_code} fetching {source.url}")

        soup = BeautifulSoup(resp.text, "html.parser")

        # Detect CAPTCHA or blocking markers
        page_title = soup.title.string.strip() if soup.title and soup.title.string else ""
        if any(marker in page_title.lower() for marker in ("just a moment...", "attention required!", "access denied")):
            raise PermissionError("Encountered automated bot challenge page; skipping.")

        # Extract title
        og_title = soup.find("meta", property="og:title")
        title = og_title["content"].strip() if (og_title and og_title.get("content")) else page_title

        # Extract author
        author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
        author = author_meta["content"].strip() if (author_meta and author_meta.get("content")) else None

        # Extract published date
        date_meta = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "date"})
        pub_date = None
        if date_meta and date_meta.get("content"):
            try:
                pub_date = datetime.fromisoformat(date_meta["content"].replace("Z", "+00:00"))
            except Exception:
                pub_date = datetime.now(timezone.utc)

        # Extract main body text
        main_body = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"content|post-body|article-body", re.I))
        if main_body:
            content_html = str(main_body)
        else:
            # Fallback to body paragraphs
            paragraphs = soup.find_all("p")
            content_html = "\n\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])

        article = RawArticle(
            source_id=source.id or "web_source",
            source_name=source.name,
            url=source.url,
            title=title or source.name,
            raw_content=content_html,
            author=author,
            published_at=pub_date or datetime.now(timezone.utc),
            retrieved_at=datetime.utcnow(),
            metadata={"source_type": "web"}
        )

        return [article], None, None

    def get_source_metadata(self, source: SourceConfig) -> Dict[str, Any]:
        return {
            "connector": "WebArticleConnector",
            "url": source.url
        }

