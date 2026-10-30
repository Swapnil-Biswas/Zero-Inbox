"""
ZERO-INBOX: Summarization, Cost Tracker & Digest Synthesis Test Suite
"""

import unittest
import asyncio
from datetime import datetime, timezone
from app.core.models import ProcessedArticle, UserPreferences
from app.core.cost_tracker import cost_tracker
from app.summarization.digest_builder import digest_builder
from app.summarization.providers.local_llm import LocalLLMProvider


class TestSummarizationAndDigest(unittest.TestCase):

    def test_cost_calculation(self):
        rec = cost_tracker.calculate_cost(
            provider="gemini",
            model="gemini-1.5-flash",
            prompt_tokens=10000,
            completion_tokens=2000
        )
        # prompt: 10000 / 1M * 0.075 = $0.00075
        # completion: 2000 / 1M * 0.30 = $0.0006
        # total: $0.00135
        self.assertAlmostEqual(rec.total_cost_usd, 0.00135, places=5)

    def test_local_summarizer(self):
        provider = LocalLLMProvider()
        title = "Open Source Framework Accelerates Agentic Workflows"
        body = (
            "A consortium of distributed systems engineers has unveiled an asynchronous execution runtime. "
            "The new engine handles state persistence, message queuing, and tool routing seamlessly. "
            "Early telemetry shows a 4x reduction in context memory overhead across long-running tasks."
        )
        loop = asyncio.new_event_loop()
        hl, summ, takeaways, why, p_tok, c_tok = loop.run_until_complete(
            provider.summarize_article(title, body)
        )
        loop.close()

        self.assertEqual(hl, title)
        self.assertTrue(len(summ) > 20)
        self.assertTrue(len(takeaways) >= 1)
        self.assertTrue(len(why) > 10)
        self.assertGreater(p_tok, 0)
        self.assertGreater(c_tok, 0)

    def test_digest_builder(self):
        articles = [
            ProcessedArticle(
                id="art_1",
                source_id="src_1",
                source_name="MIT Technology Review",
                url="https://technologyreview.com/story-1",
                canonical_url="https://technologyreview.com/story-1",
                title="Breakthrough in Quantum Error Mitigation",
                clean_text="Physicists at MIT have demonstrated scalable error mitigation using topological qubits.",
                clean_length=80,
                published_at=datetime.now(timezone.utc),
                relevance_score=0.92
            ),
            ProcessedArticle(
                id="art_2",
                source_id="src_2",
                source_name="Hacker News",
                url="https://news.ycombinator.com/item?id=9999",
                canonical_url="https://news.ycombinator.com/item?id=9999",
                title="Show HN: Lightweight In-Memory Vector Store",
                clean_text="We built an embedded vector index in Rust with zero external dependencies.",
                clean_length=75,
                published_at=datetime.now(timezone.utc),
                relevance_score=0.85
            )
        ]
        prefs = UserPreferences(user_id="test_user", max_stories=5)

        loop = asyncio.new_event_loop()
        digest = loop.run_until_complete(
            digest_builder.build_digest(articles, prefs)
        )
        loop.close()

        self.assertIsNotNone(digest)
        self.assertIn("ZERO-INBOX", digest.content_markdown)
        self.assertIn("TOP STORIES", digest.content_markdown)
        self.assertIn("TODAY'S TAKEAWAY", digest.content_markdown)
        self.assertEqual(digest.articles_included, 2)


if __name__ == "__main__":
    unittest.main()
