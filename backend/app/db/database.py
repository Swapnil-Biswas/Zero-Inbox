"""
ZERO-INBOX: SQLite WAL Database Layer & Model Mappers
"""

import sqlite3
import json
import uuid
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from app.core.config import settings
from app.core.models import (
    SourceConfig, SourceType, SourceStatus, ProcessedArticle,
    UserPreferences, Digest, DeliveryLog, CostRecord, DeliveryChannel, SummaryLength
)


class Database:
    """Thread-safe SQLite manager with WAL journal mode and typed persistence helpers."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            # Enable WAL mode for high concurrency
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables from schema.sql."""
        schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
        self._ensure_default_user_preferences()

    def _ensure_default_user_preferences(self, user_id: str = "default_user"):
        """Seeds default user preferences if not already present."""
        prefs = self.get_user_preferences(user_id)
        if not prefs:
            default_prefs = UserPreferences(user_id=user_id)
            self.save_user_preferences(default_prefs)

    # --- Sources CRUD ---
    def add_source(self, source: SourceConfig) -> SourceConfig:
        if not source.id:
            source.id = f"src_{uuid.uuid4().hex[:12]}"
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sources (id, user_id, name, url, source_type, status, category_hint, etag, last_modified, last_fetched_at, error_count, last_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source.id, source.user_id, source.name, source.url,
                    source.source_type.value, source.status.value, source.category_hint,
                    source.etag, source.last_modified,
                    source.last_fetched_at.isoformat() if source.last_fetched_at else None,
                    source.error_count, source.last_error
                )
            )
        return source

    def get_source(self, source_id: str) -> Optional[SourceConfig]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
            if not row:
                return None
            return self._row_to_source(row)

    def list_sources(self, user_id: str = "default_user", status: Optional[str] = None) -> List[SourceConfig]:
        with self.get_connection() as conn:
            query = "SELECT * FROM sources WHERE user_id = ?"
            params = [user_id]
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_source(r) for r in rows]

    def update_source_sync(self, source_id: str, etag: Optional[str], last_modified: Optional[str], error: Optional[str] = None):
        with self.get_connection() as conn:
            now = datetime.utcnow().isoformat()
            if error:
                conn.execute(
                    "UPDATE sources SET error_count = error_count + 1, last_error = ?, last_fetched_at = ? WHERE id = ?",
                    (error, now, source_id)
                )
            else:
                conn.execute(
                    "UPDATE sources SET etag = ?, last_modified = ?, error_count = 0, last_error = NULL, last_fetched_at = ? WHERE id = ?",
                    (etag, last_modified, now, source_id)
                )

    def remove_source(self, source_id: str, user_id: str = "default_user") -> bool:
        with self.get_connection() as conn:
            cur = conn.execute("DELETE FROM sources WHERE id = ? AND user_id = ?", (source_id, user_id))
            return cur.rowcount > 0

    def _row_to_source(self, row: sqlite3.Row) -> SourceConfig:
        return SourceConfig(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            url=row["url"],
            source_type=SourceType(row["source_type"]),
            status=SourceStatus(row["status"]),
            category_hint=row["category_hint"],
            etag=row["etag"],
            last_modified=row["last_modified"],
            last_fetched_at=datetime.fromisoformat(row["last_fetched_at"]) if row["last_fetched_at"] else None,
            error_count=row["error_count"],
            last_error=row["last_error"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow()
        )

    # --- Articles CRUD ---
    def save_article(self, article: ProcessedArticle):
        with self.get_connection() as conn:
            # Ensure referenced source exists to satisfy relational integrity
            if article.source_id:
                src_check = conn.execute("SELECT 1 FROM sources WHERE id = ?", (article.source_id,)).fetchone()
                if not src_check:
                    conn.execute(
                        "INSERT OR IGNORE INTO sources (id, user_id, name, url, source_type, status) VALUES (?, ?, ?, ?, ?, ?)",
                        (article.source_id, "default_user", article.source_name or "Direct Source", article.url, "web", "active")
                    )
            conn.execute(
                """
                INSERT OR REPLACE INTO articles (
                    id, source_id, source_name, url, canonical_url, title, clean_text,
                    author, published_at, category, relevance_score, novelty_score,
                    is_duplicate, duplicate_of_id, headline, summary, key_takeaways_json, why_it_matters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article.id, article.source_id, article.source_name, article.url,
                    article.canonical_url, article.title, article.clean_text,
                    article.author,
                    article.published_at.isoformat() if article.published_at else None,
                    article.category, article.relevance_score, article.novelty_score,
                    1 if article.is_duplicate else 0, article.duplicate_of_id,
                    article.headline, article.summary,
                    json.dumps(article.key_takeaways), article.why_it_matters
                )
            )

    def is_canonical_url_present(self, canonical_url: str) -> bool:
        with self.get_connection() as conn:
            row = conn.execute("SELECT 1 FROM articles WHERE canonical_url = ? LIMIT 1", (canonical_url,)).fetchone()
            return row is not None

    def search_articles(self, query: str, limit: int = 20) -> List[ProcessedArticle]:
        with self.get_connection() as conn:
            like_query = f"%{query}%"
            rows = conn.execute(
                """
                SELECT * FROM articles
                WHERE title LIKE ? OR clean_text LIKE ? OR summary LIKE ?
                ORDER BY published_at DESC LIMIT ?
                """,
                (like_query, like_query, like_query, limit)
            ).fetchall()
            return [self._row_to_article(r) for r in rows]

    def get_article(self, article_id: str) -> Optional[ProcessedArticle]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
            if not row:
                return None
            return self._row_to_article(row)

    def _row_to_article(self, row: sqlite3.Row) -> ProcessedArticle:
        takeaways = []
        if row["key_takeaways_json"]:
            try:
                takeaways = json.loads(row["key_takeaways_json"])
            except Exception:
                takeaways = []
        return ProcessedArticle(
            id=row["id"],
            source_id=row["source_id"],
            source_name=row["source_name"],
            url=row["url"],
            canonical_url=row["canonical_url"],
            title=row["title"],
            clean_text=row["clean_text"],
            clean_length=len(row["clean_text"]),
            author=row["author"],
            published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
            category=row["category"],
            relevance_score=row["relevance_score"],
            novelty_score=row["novelty_score"],
            is_duplicate=bool(row["is_duplicate"]),
            duplicate_of_id=row["duplicate_of_id"],
            headline=row["headline"],
            summary=row["summary"],
            key_takeaways=takeaways,
            why_it_matters=row["why_it_matters"]
        )

    # --- User Preferences CRUD ---
    def get_user_preferences(self, user_id: str = "default_user") -> Optional[UserPreferences]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
            if not row:
                return None
            return UserPreferences(
                user_id=row["user_id"],
                topics=json.loads(row["topics_json"]),
                preferred_sources=json.loads(row["preferred_sources_json"]),
                blocked_sources=json.loads(row["blocked_sources_json"]),
                priority_sources=json.loads(row["priority_sources_json"]),
                summary_length=SummaryLength(row["summary_length"]),
                max_stories=row["max_stories"],
                preferred_language=row["preferred_language"],
                delivery_time_hour=row["delivery_time_hour"],
                delivery_time_minute=row["delivery_time_minute"],
                timezone=row["timezone"],
                delivery_channel=DeliveryChannel(row["delivery_channel"]),
                delivery_destination=row["delivery_destination"],
                importance_threshold=row["importance_threshold"],
                track_keywords=json.loads(row["track_keywords_json"]),
                exclude_keywords=json.loads(row["exclude_keywords_json"]),
                feedback_weights=json.loads(row["feedback_weights_json"])
            )

    def save_user_preferences(self, prefs: UserPreferences):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO user_preferences (
                    user_id, topics_json, preferred_sources_json, blocked_sources_json,
                    priority_sources_json, summary_length, max_stories, preferred_language,
                    delivery_time_hour, delivery_time_minute, timezone, delivery_channel,
                    delivery_destination, importance_threshold, track_keywords_json,
                    exclude_keywords_json, feedback_weights_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prefs.user_id,
                    json.dumps(prefs.topics),
                    json.dumps(prefs.preferred_sources),
                    json.dumps(prefs.blocked_sources),
                    json.dumps(prefs.priority_sources),
                    prefs.summary_length.value,
                    prefs.max_stories,
                    prefs.preferred_language,
                    prefs.delivery_time_hour,
                    prefs.delivery_time_minute,
                    prefs.timezone,
                    prefs.delivery_channel.value,
                    prefs.delivery_destination,
                    prefs.importance_threshold,
                    json.dumps(prefs.track_keywords),
                    json.dumps(prefs.exclude_keywords),
                    json.dumps(prefs.feedback_weights),
                    datetime.utcnow().isoformat()
                )
            )

    # --- Digests CRUD ---
    def save_digest(self, digest: Digest):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO digests (
                    id, user_id, date_str, title, content_markdown, categories_json,
                    total_articles_analyzed, articles_included, estimated_read_time_minutes,
                    cost_usd, delivery_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    digest.id, digest.user_id, digest.date_str, digest.title,
                    digest.content_markdown, json.dumps(digest.categories),
                    digest.total_articles_analyzed, digest.articles_included,
                    digest.estimated_read_time_minutes, digest.cost_usd,
                    digest.delivery_status, digest.created_at.isoformat()
                )
            )

    def get_latest_digest(self, user_id: str = "default_user") -> Optional[Digest]:
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM digests WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_digest(row)

    def get_digest_history(self, user_id: str = "default_user", limit: int = 15) -> List[Digest]:
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM digests WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [self._row_to_digest(r) for r in rows]

    def _row_to_digest(self, row: sqlite3.Row) -> Digest:
        return Digest(
            id=row["id"],
            user_id=row["user_id"],
            date_str=row["date_str"],
            title=row["title"],
            content_markdown=row["content_markdown"],
            categories=json.loads(row["categories_json"]),
            total_articles_analyzed=row["total_articles_analyzed"],
            articles_included=row["articles_included"],
            estimated_read_time_minutes=row["estimated_read_time_minutes"],
            cost_usd=row["cost_usd"],
            delivery_status=row["delivery_status"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow()
        )

    # --- Delivery Logs ---
    def log_delivery(self, log: DeliveryLog):
        if not log.id:
            log.id = f"del_{uuid.uuid4().hex[:12]}"
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO delivery_logs (id, digest_id, channel, destination, status, error_message, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (log.id, log.digest_id, log.channel.value, log.destination, log.status, log.error_message, log.sent_at.isoformat())
            )

    # --- Cost Records ---
    def record_cost(self, record: CostRecord):
        if not record.id:
            record.id = f"cst_{uuid.uuid4().hex[:12]}"
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO cost_records (id, user_id, digest_id, provider, model, prompt_tokens, completion_tokens, total_cost_usd, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id, record.user_id, record.digest_id, record.provider,
                    record.model, record.prompt_tokens, record.completion_tokens,
                    record.total_cost_usd, record.created_at.isoformat()
                )
            )

    def get_cost_summary(self, user_id: str = "default_user") -> Dict[str, Any]:
        with self.get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total_calls,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    SUM(total_cost_usd) as total_spent_usd
                FROM cost_records
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()
            return {
                "total_calls": row["total_calls"] or 0,
                "total_prompt_tokens": row["total_prompt_tokens"] or 0,
                "total_completion_tokens": row["total_completion_tokens"] or 0,
                "total_tokens": (row["total_prompt_tokens"] or 0) + (row["total_completion_tokens"] or 0),
                "total_spent_usd": round(row["total_spent_usd"] or 0.0, 6)
            }


db = Database()
