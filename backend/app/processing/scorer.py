"""
ZERO-INBOX: Multi-Factor Relevance & Interest Scoring Engine
"""

from typing import List
from datetime import datetime, timezone
import math
from app.core.models import ProcessedArticle, UserPreferences


class RelevanceScorer:
    """Calculates multidimensional relevance scores balancing user interests, recency, source credibility and feedback."""

    def score_article(self, article: ProcessedArticle, prefs: UserPreferences) -> float:
        # 1. Source filter: If blocked, return 0.0 immediately
        if any(b.lower() in article.source_name.lower() or b.lower() in article.url.lower() for b in prefs.blocked_sources):
            return 0.0

        score = 0.40  # Baseline prior

        text_lower = (article.title + " " + article.clean_text).lower()

        # 2. Topic Matching (+0.25 max)
        matched_topics = 0
        for topic in prefs.topics:
            t_low = topic.lower()
            if t_low in text_lower:
                matched_topics += 1
                # Check user feedback multiplier for this topic
                weight = prefs.feedback_weights.get(topic, 1.0)
                score += 0.08 * weight

        # 3. Tracked Keywords (+0.25 max)
        for kw in prefs.track_keywords:
            if kw.lower() in text_lower:
                score += 0.12

        # 4. Excluded Keywords (-0.50 max)
        for ex in prefs.exclude_keywords:
            if ex.lower() in text_lower:
                score -= 0.30

        # 5. Source Preference
        if any(p.lower() in article.source_name.lower() for p in prefs.priority_sources):
            score += 0.25
        elif any(p.lower() in article.source_name.lower() for p in prefs.preferred_sources):
            score += 0.12

        # 6. Recency Decay (Half-life = 24 hours)
        if article.published_at:
            now = datetime.now(timezone.utc)
            # Ensure timezone compatibility
            pub = article.published_at if article.published_at.tzinfo else article.published_at.replace(tzinfo=timezone.utc)
            age_hours = max(0.0, (now - pub).total_seconds() / 3600.0)
            recency_factor = math.exp(-0.693 * (age_hours / 24.0))  # 1.0 at 0h, 0.5 at 24h
            score *= (0.7 + 0.3 * recency_factor)

        # 7. Quality / Substantive Content Bonus
        word_count = len(article.clean_text.split())
        if word_count > 200:
            score += 0.05
        elif word_count < 40:
            score -= 0.15

        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, round(score, 4)))

    def rank_articles(self, articles: List[ProcessedArticle], prefs: UserPreferences) -> List[ProcessedArticle]:
        """Calculates relevance scores and sorts descending."""
        for art in articles:
            art.relevance_score = self.score_article(art, prefs)

        # Filter out duplicates and low relevance, sort descending
        valid_articles = [a for a in articles if not a.is_duplicate and a.relevance_score >= prefs.importance_threshold]
        valid_articles.sort(key=lambda a: a.relevance_score, reverse=True)
        return valid_articles


relevance_scorer = RelevanceScorer()

