"""
ZERO-INBOX: Topic Categorization & Story Clustering Engine
"""

from typing import List, Dict
import re
from app.core.models import ProcessedArticle, ArticleCluster


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Artificial Intelligence": [
        "ai", "llm", "gpt", "gemini", "claude", "neural", "deep learning", "machine learning",
        "transformer", "anthropic", "openai", "agent", "model", "inference", "fine-tuning"
    ],
    "Startups & Venture": [
        "startup", "funding", "seed round", "series a", "venture capital", "vc", "founder",
        "valuation", "acquisition", "ipo", "investors", "accelerator"
    ],
    "Cybersecurity": [
        "security", "vulnerability", "malware", "ransomware", "cve", "breach", "zero-day",
        "hacker", "exploit", "patch", "encryption", "firewall", "phishing"
    ],
    "Programming & DevOps": [
        "python", "rust", "typescript", "javascript", "golang", "kubernetes", "docker",
        "linux", "database", "sql", "api", "framework", "git", "compiler", "backend", "frontend"
    ],
    "Science & Research": [
        "research", "paper", "arxiv", "quantum", "physics", "biology", "astronomy", "climate",
        "study", "scientists", "experiment", "breakthrough"
    ],
    "Communities & Discussions": [
        "reddit", "discussion", "community", "hacker news", "forum", "ask hn", "r/"
    ]
}


class TopicClusterer:
    """Classifies articles into major intelligence radar categories and clusters overlapping developments."""

    def assign_category(self, article: ProcessedArticle) -> str:
        text = (article.title + " " + article.clean_text[:500]).lower()

        # Check Reddit first if it's from a subreddit
        if "reddit.com" in article.url or article.title.startswith("[r/"):
            return "Communities & Discussions"

        best_cat = "Technology"
        max_matches = 0

        for cat, keywords in CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
            if matches > max_matches:
                max_matches = matches
                best_cat = cat

        article.category = best_cat
        return best_cat

    def cluster_articles(self, articles: List[ProcessedArticle]) -> List[ArticleCluster]:
        """Groups articles into topic clusters with a designated lead story and supporting references."""
        clusters: List[ArticleCluster] = []

        # Categorize all articles first
        for art in articles:
            self.assign_category(art)

        # Group by category
        grouped: Dict[str, List[ProcessedArticle]] = {}
        for art in articles:
            grouped.setdefault(art.category, []).append(art)

        for cat, cat_articles in grouped.items():
            # Sort by relevance
            cat_articles.sort(key=lambda a: a.relevance_score, reverse=True)
            for idx, art in enumerate(cat_articles):
                cluster = ArticleCluster(
                    cluster_id=f"cluster_{art.id}",
                    topic_name=art.title,
                    category=cat,
                    lead_article=art,
                    supporting_articles=[],
                    combined_score=art.relevance_score
                )
                clusters.append(cluster)

        return clusters


topic_clusterer = TopicClusterer()
