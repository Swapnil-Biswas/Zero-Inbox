"""
ZERO-INBOX: Ingestion & Security Test Suite
"""

import unittest
from datetime import datetime
from app.core.models import SourceConfig, SourceType
from app.core.security import validate_url_safe, sanitize_html_content
from app.ingestion.rss import RssConnector
from app.ingestion.newsletter import NewsletterConnector
from app.ingestion.reddit import RedditConnector


class TestIngestion(unittest.TestCase):

    def test_ssrf_validation(self):
        # Disallowed private and metadata endpoints
        blocked_urls = [
            "http://127.0.0.1/admin",
            "http://localhost:8080/metrics",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.0.0.5:9000",
            "http://192.168.1.1/router",
            "ftp://example.com/file"
        ]
        for url in blocked_urls:
            safe, err = validate_url_safe(url)
            self.assertFalse(safe, f"URL should be blocked for SSRF: {url}")

    def test_html_sanitization(self):
        raw_html = """
        <div>
            <h2>Valid Title</h2>
            <script>alert('xss');</script>
            <p>This is substantive editorial text for the media intelligence digest.</p>
            <iframe src="http://evil.com"></iframe>
            <style>body { display: none; }</style>
        </div>
        """
        clean = sanitize_html_content(raw_html)
        self.assertNotIn("<script>", clean)
        self.assertNotIn("alert", clean)
        self.assertNotIn("<iframe", clean)
        self.assertIn("Valid Title", clean)
        self.assertIn("substantive editorial text", clean)

    def test_newsletter_bulk_filter(self):
        connector = NewsletterConnector()
        # Newsletter with List-Unsubscribe header
        raw_newsletter = """From: newsletter@techdaily.com
To: user@example.com
Subject: Tech Daily Issue #42
List-Unsubscribe: <https://techdaily.com/unsub>
Content-Type: text/plain

Here is what happened in AI today: major new releases from research labs.
"""
        article = connector.parse_raw_email(raw_newsletter, SourceConfig(name="Tech Daily", url="newsletter@techdaily.com"))
        self.assertIsNotNone(article)
        self.assertEqual(article.title, "Tech Daily Issue #42")

        # Personal email without bulk indicators
        raw_personal = """From: mom@family.com
To: user@example.com
Subject: Dinner on Sunday?
Content-Type: text/plain

Hey, are you free this weekend for dinner?
"""
        personal_art = connector.parse_raw_email(raw_personal, SourceConfig(name="Family", url="mom@family.com"))
        self.assertIsNone(personal_art, "Personal email must be suppressed for user privacy.")

    def test_reddit_subreddit_extraction(self):
        connector = RedditConnector()
        self.assertEqual(connector.extract_subreddit_name("https://reddit.com/r/technology"), "technology")
        self.assertEqual(connector.extract_subreddit_name("r/machinelearning"), "machinelearning")
        self.assertEqual(connector.extract_subreddit_name("artificial"), "artificial")


if __name__ == "__main__":
    unittest.main()

