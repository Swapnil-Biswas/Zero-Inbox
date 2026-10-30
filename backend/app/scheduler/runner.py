"""
ZERO-INBOX: Autonomous Daily Pipeline Runner
"""

from typing import Optional, List
from datetime import datetime, timezone
from app.core.models import Digest, ProcessedArticle, UserPreferences
from app.db.database import db
from app.ingestion.manager import ingestion_manager
from app.processing.normalizer import normalize_article
from app.processing.cleaner import clean_article_noise
from app.processing.deduplicator import deduplicator
from app.processing.scorer import relevance_scorer
from app.summarization.digest_builder import digest_builder
from app.delivery.dispatcher import delivery_dispatcher
from app.scheduler.lock import scheduler_lock


async def run_user_digest_pipeline(user_id: str = "default_user", force: bool = False) -> Optional[Digest]:
    """
    Executes the autonomous zero-inbox daily intelligence pipeline:
    Ingestion -> Cleaning -> Deduplication -> Relevance Scoring -> LLM Synthesis -> Delivery.
    Enforces atomic locks to guarantee zero duplicate daily deliveries.
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lock_key = f"digest_run_{user_id}_{today_str}"

    if not force:
        # Check if already generated today
        existing = db.get_latest_digest(user_id)
        if existing and existing.created_at.strftime("%Y-%m-%d") == today_str:
            return existing

        acquired = scheduler_lock.acquire_lock(lock_key, lease_seconds=600)
        if not acquired:
            # Another worker is actively generating the digest
            return None

    try:
        # 1. Load preferences
        prefs = db.get_user_preferences(user_id)
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.save_user_preferences(prefs)

        # 2. Ingest active sources
        raw_articles = await ingestion_manager.ingest_all_active_sources(user_id)

        # If no external articles fetched (e.g. initial setup without feeds), create informative fallback items
        if not raw_articles:
            from app.core.models import RawArticle
            raw_articles = [
                RawArticle(
                    source_id="sys_welcome",
                    source_name="ZERO-INBOX Welcome Monitor",
                    url="https://github.com/Swapnil-Biswas/zero-inbox",
                    title="ZERO-INBOX Initial Intelligence System Online",
                    raw_content="ZERO-INBOX autonomous media agent initialized. Ready to ingest RSS feeds, newsletters, Reddit discussions, and public web articles according to your custom preferences.",
                    published_at=datetime.now(timezone.utc)
                )
            ]

        # 3. Normalize
        normalized = [normalize_article(raw) for raw in raw_articles]

        # 4. Clean noise, ads & sponsorships
        for art in normalized:
            art.clean_text = clean_article_noise(art.clean_text)
            art.clean_length = len(art.clean_text)

        # 5. Deduplicate
        deduped = deduplicator.deduplicate_batch(normalized)

        # 6. Score & Rank
        ranked = relevance_scorer.rank_articles(deduped, prefs)
        if not ranked:
            # If all were below threshold, take top scoring non-duplicate anyway
            ranked = [a for a in deduped if not a.is_duplicate][:5]

        # 7. Synthesize Digest
        digest = await digest_builder.build_digest(ranked, prefs)

        # 8. Dispatch notification
        await delivery_dispatcher.dispatch_digest(digest, prefs)

        return digest

    finally:
        if not force:
            scheduler_lock.release_lock(lock_key)
