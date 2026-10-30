"""
ZERO-INBOX: Reddit Community Discussions Connector
"""

import httpx
import re
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings
from app.core.models import SourceConfig, RawArticle
from app.ingestion.base import SourceConnector


class RedditConnector(SourceConnector):
    """Fetches high-signal community discussions from Reddit subreddits."""

    def __init__(self, min_score: int = 15, min_comments: int = 3):
        self.min_score = min_score
        self.min_comments = min_comments

    def extract_subreddit_name(self, url_or_name: str) -> str:
        """Extracts clean subreddit name from r/name, /r/name, or full URL."""
        match = re.search(r"r/([a-zA-Z0-9_]+)", url_or_name)
        if match:
            return match.group(1)
        # If pure name given
        cleaned = re.sub(r"[^a-zA-Z0-9_]", "", url_or_name)
        return cleaned or "technology"

    def validate_configuration(self, source: SourceConfig) -> Tuple[bool, str]:
        sub = self.extract_subreddit_name(source.url)
        if not sub:
            return False, "Could not determine subreddit name."
        return True, ""

    async def fetch_updates(
        self, source: SourceConfig
    ) -> Tuple[List[RawArticle], Optional[str], Optional[str]]:
        sub = self.extract_subreddit_name(source.url)
        endpoint = f"https://www.reddit.com/r/{sub}/hot.json?limit=30"

        headers = {
            "User-Agent": f"ZeroInboxBot/1.0 (by /u/zeroinbox_intelligence; contact: dev@zeroinbox.local)"
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            try:
                resp = await client.get(endpoint, headers=headers)
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Reddit r/{sub}: {str(e)}")

        if resp.status_code == 429:
            raise ConnectionError(f"Reddit rate limit encountered on r/{sub}")
        if resp.status_code != 200:
            raise ConnectionError(f"Reddit API returned HTTP {resp.status_code} for r/{sub}")

        data = resp.json()
        children = data.get("data", {}).get("children", [])

        articles: List[RawArticle] = []
        for item in children:
            post = item.get("data", {})
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            score = post.get("score", 0)
            num_comments = post.get("num_comments", 0)
            permalink = f"https://reddit.com{post.get('permalink', '')}"
            author = post.get("author", "[deleted]")
            created_utc = post.get("created_utc")
            is_stickied = post.get("stickied", False)

            # Skip moderator stickied announcements
            if is_stickied:
                continue

            # Signal filter: require minimum community engagement
            if score < self.min_score and num_comments < self.min_comments:
                continue

            pub_date = datetime.fromtimestamp(created_utc, tz=timezone.utc) if created_utc else datetime.now(timezone.utc)

            body_content = f"{selftext}\n\n[Reddit Discussion: {score} upvotes, {num_comments} comments]"

            articles.append(
                RawArticle(
                    source_id=source.id or "reddit_source",
                    source_name=f"r/{sub}",
                    url=permalink,
                    title=f"[r/{sub}] {title}",
                    raw_content=body_content,
                    author=f"u/{author}",
                    published_at=pub_date,
                    retrieved_at=datetime.utcnow(),
                    metadata={
                        "score": score,
                        "num_comments": num_comments,
                        "subreddit": sub,
                        "is_self": post.get("is_self", False),
                        "external_url": post.get("url")
                    }
                )
            )

        return articles, None, None

    def get_source_metadata(self, source: SourceConfig) -> Dict[str, Any]:
        sub = self.extract_subreddit_name(source.url)
        return {
            "connector": "RedditConnector",
            "subreddit": sub,
            "min_score_filter": self.min_score,
            "min_comments_filter": self.min_comments
        }
