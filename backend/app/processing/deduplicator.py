"""
ZERO-INBOX: Multi-tier Deduplication & Near-Duplicate Detection Engine
"""

import hashlib
import re
from typing import List, Set, Dict, Tuple
from app.core.models import ProcessedArticle
from app.db.database import db


def compute_content_hash(text: str) -> str:
    """Computes an MD5 hash over lowercase alphanumeric characters."""
    alphanumeric = re.sub(r"[^a-z0-9]", "", text.lower())
    return hashlib.md5(alphanumeric.encode("utf-8")).hexdigest()


def extract_word_shingles(text: str, k: int = 3) -> Set[Tuple[str, ...]]:
    """Extracts k-word shingles for Jaccard near-duplicate computation."""
    words = re.findall(r"\b[a-z0-9]{3,}\b", text.lower())
    if len(words) < k:
        return {tuple(words)}
    return {tuple(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard_similarity(set_a: Set[Tuple[str, ...]], set_b: Set[Tuple[str, ...]]) -> float:
    """Computes Jaccard index between two shingle sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / float(union) if union > 0 else 0.0


class Deduplicator:
    """Identifies exact and near-duplicate stories to avoid redundant digest entries."""

    def __init__(self, near_duplicate_threshold: float = 0.60):
        self.threshold = near_duplicate_threshold

    def deduplicate_batch(self, articles: List[ProcessedArticle]) -> List[ProcessedArticle]:
        """
        Processes a batch of articles:
        1. Checks DB for previously ingested canonical URLs.
        2. Detects intra-batch identical canonical URLs and content hashes.
        3. Identifies near-duplicate stories via Jaccard n-gram similarity.
        """
        seen_urls: Set[str] = set()
        seen_hashes: Dict[str, str] = {}  # hash -> article_id
        lead_shingles: Dict[str, Set[Tuple[str, ...]]] = {}  # article_id -> shingles

        results: List[ProcessedArticle] = []

        for art in articles:
            # 1. Check against DB
            if db.is_canonical_url_present(art.canonical_url):
                art.is_duplicate = True
                results.append(art)
                continue

            # 2. Check intra-batch canonical URL
            if art.canonical_url in seen_urls:
                art.is_duplicate = True
                results.append(art)
                continue

            # 3. Check exact content hash
            chash = compute_content_hash(art.title + art.clean_text[:500])
            if chash in seen_hashes:
                art.is_duplicate = True
                art.duplicate_of_id = seen_hashes[chash]
                results.append(art)
                continue

            # 4. Check near-duplicate Jaccard similarity against existing lead stories
            art_shingles = extract_word_shingles(art.title + " " + art.clean_text[:600])
            is_near_dup = False

            for lead_id, shingles in lead_shingles.items():
                sim = jaccard_similarity(art_shingles, shingles)
                if sim >= self.threshold:
                    art.is_duplicate = True
                    art.duplicate_of_id = lead_id
                    is_near_dup = True
                    break

            if not is_near_dup:
                seen_urls.add(art.canonical_url)
                seen_hashes[chash] = art.id
                lead_shingles[art.id] = art_shingles
                art.is_duplicate = False

            results.append(art)

        return results


deduplicator = Deduplicator()
