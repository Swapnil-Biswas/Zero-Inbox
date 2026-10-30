"""
ZERO-INBOX: Content Processing & Deduplication Test Suite
"""

import unittest
from datetime import datetime, timezone, timedelta
from app.core.models import ProcessedArticle, UserPreferences, RawArticle
from app.processing.normalizer import normalize_canonical_url, normalize_article
from app.processing.cleaner import clean_article_noise
from app.processing.deduplicator import deduplicator
from app.processing.scorer import relevance_scorer
from app.processing.clusterer import topic_clusterer


class TestProcessing(unittest.TestCase):

    def test_canonical_url_normalization(self):
        dirty_url = "https://techcrunch.com/2026/10/30/ai-agent/?utm_source=twitter&utm_medium=social&fbclid=12345#comments"
        expected = "https://techcrunch.com/2026/10/30/ai-agent"
        self.assertEqual(normalize_canonical_url(dirty_url), expected)

    def test_noise_and_sponsorship_removal(self):
        text_with_noise = """
        Researchers at Stanford unveiled an open-source reasoning model capable of mathematical synthesis.
        
        This issue is brought to you by CloudHost Inc. Get 50% off servers today!
        
        The model achieves 92% on competition benchmarks while requiring 80% fewer compute parameters.
        
        Subscribe now to our daily newsletter or upgrade to paid for full access.
        Share this post with your team.
        """
        cleaned = clean_article_noise(text_with_noise)
        self.assertNotIn("CloudHost Inc", cleaned)
        self.assertNotIn("Subscribe now", cleaned)
        self.assertNotIn("Share this post", cleaned)
        self.assertIn("Stanford unveiled an open-source reasoning model", cleaned)
        self.assertIn("competition benchmarks", cleaned)

    def test_deduplication(self):
        art1 = ProcessedArticle(
            id="art_1",
            source_id="src_1",
            source_name="News A",
            url="https://example.com/story1?utm_source=news",
            canonical_url="https://example.com/story1",
            title="OpenAI Releases New Frontier Model",
            clean_text="OpenAI has released a new frontier model with multimodal tool capabilities.",
            clean_length=70
        )
        # Duplicate with same canonical URL
        art2 = ProcessedArticle(
            id="art_2",
            source_id="src_2",
            source_name="News B",
            url="https://example.com/story1?utm_medium=email",
            canonical_url="https://example.com/story1",
            title="OpenAI Releases New Frontier Model",
            clean_text="OpenAI has released a new frontier model with multimodal tool capabilities.",
            clean_length=70
        )
        batch = deduplicator.deduplicate_batch([art1, art2])
        self.assertFalse(batch[0].is_duplicate)
        self.assertTrue(batch[1].is_duplicate)

    def test_relevance_scoring(self):
        prefs = UserPreferences(
            topics=["Artificial Intelligence", "Startups"],
            priority_sources=["TechCrunch"],
            blocked_sources=["ClickbaitDaily"],
            track_keywords=["Anthropic"],
            exclude_keywords=["Celebrity"]
        )

        art_ai = ProcessedArticle(
            id="art_ai",
            source_id="src_1",
            source_name="TechCrunch",
            url="https://techcrunch.com/anthropic-funding",
            canonical_url="https://techcrunch.com/anthropic-funding",
            title="Anthropic Secures Major AI Funding Round",
            clean_text="Anthropic announced a new financing round for their frontier artificial intelligence research.",
            clean_length=90,
            published_at=datetime.now(timezone.utc)
        )
        score = relevance_scorer.score_article(art_ai, prefs)
        self.assertGreater(score, 0.65, "Target AI story from priority source should score high.")

        art_blocked = ProcessedArticle(
            id="art_block",
            source_id="src_2",
            source_name="ClickbaitDaily",
            url="https://clickbaitdaily.com/ai-shock",
            canonical_url="https://clickbaitdaily.com/ai-shock",
            title="Shocking AI development",
            clean_text="You will not believe this new AI announcement.",
            clean_length=50
        )
        self.assertEqual(relevance_scorer.score_article(art_blocked, prefs), 0.0, "Blocked source must yield 0.0.")

    def test_topic_categorization(self):
        art_cyber = ProcessedArticle(
            id="art_sec",
            source_id="src_sec",
            source_name="BleepingComputer",
            url="https://bleepingcomputer.com/cve-2026",
            canonical_url="https://bleepingcomputer.com/cve-2026",
            title="Critical Zero-Day Vulnerability Discovered in Linux Kernel",
            clean_text="Security researchers published an advisory for a high-severity privilege escalation exploit.",
            clean_length=95
        )
        cat = topic_clusterer.assign_category(art_cyber)
        self.assertEqual(cat, "Cybersecurity")


if __name__ == "__main__":
    unittest.main()
