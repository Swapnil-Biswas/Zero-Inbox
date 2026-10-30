"""
ZERO-INBOX: Content Normalization & Canonical URL Standardization
"""

import uuid
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from app.core.models import RawArticle, ProcessedArticle
from app.core.security import sanitize_html_content


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "ref_src", "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid"
}


def normalize_canonical_url(raw_url: str) -> str:
    """Strips query tracking parameters, hashes, and trailing slashes to compute canonical URL."""
    if not raw_url or not raw_url.startswith("http"):
        return raw_url or ""

    try:
        parsed = urlparse(raw_url)
        # Filter query params
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        clean_pairs = [(k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS]
        clean_query = urlencode(clean_pairs)

        clean_path = parsed.path.rstrip("/") if parsed.path != "/" else "/"

        canonical = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.params,
            clean_query,
            ""  # Strip fragment
        ))
        return canonical
    except Exception:
        return raw_url


def normalize_article(raw: RawArticle) -> ProcessedArticle:
    """Converts a RawArticle into a normalized ProcessedArticle."""
    canonical_url = normalize_canonical_url(raw.url)
    clean_text = sanitize_html_content(raw.raw_content)

    clean_title = re.sub(r"\s+", " ", raw.title).strip()

    return ProcessedArticle(
        id=f"art_{uuid.uuid4().hex[:12]}",
        source_id=raw.source_id,
        source_name=raw.source_name,
        url=raw.url,
        canonical_url=canonical_url,
        title=clean_title,
        clean_text=clean_text,
        clean_length=len(clean_text),
        author=raw.author,
        published_at=raw.published_at,
        category="Technology",
        relevance_score=0.5,
        novelty_score=1.0,
        is_duplicate=False
    )

