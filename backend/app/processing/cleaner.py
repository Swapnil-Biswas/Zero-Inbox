"""
ZERO-INBOX: Noise Removal & Ad/Sponsorship Stripper
"""

import re
from typing import List


# Patterns for commercial sponsorships and promotions
SPONSOR_PATTERNS = [
    r"(?is)(?:this issue|this edition|this email|today's newsletter) is (?:brought to you by|sponsored by|presented by).*?(?:\n\s*\n|\Z)",
    r"(?is)a (?:quick |special )?word from our (?:sponsor|partner).*?(?:\n\s*\n|\Z)",
    r"(?is)\[(?:sponsor|ad|promoted)\]:?.*?(?:\n\s*\n|\Z)",
    r"(?is)^thanks to our sponsor,.*?(?:\n\s*\n|\Z)",
]

# Patterns for subscription CTAs and promotional boilerplates
CTA_PATTERNS = [
    r"(?is)(?:subscribe now|upgrade to paid|become a paid subscriber|pledge your support).*?(?:\n\s*\n|\Z)",
    r"(?is)join (?:over )?[0-9,]+ (?:readers|engineers|subscribers).*?(?:\n\s*\n|\Z)",
    r"(?is)share this (?:post|newsletter|article|issue) with your (?:friends|team|colleagues).*?(?:\n\s*\n|\Z)",
    r"(?is)leave a comment|restack this post|follow us on (?:twitter|x|linkedin|threads).*?(?:\n\s*\n|\Z)",
    r"(?is)you received this email because you subscribed to.*?(?:\n\s*\n|\Z)",
    r"(?is)unsubscribe here|manage your subscription|view in browser.*?(?:\n\s*\n|\Z)",
    r"(?is)all rights reserved\b.*?(?:\n\s*\n|\Z)",
]


def clean_article_noise(text: str) -> str:
    """Removes sponsorships, advertisements, subscription prompts, and boilerplate from article body."""
    if not text:
        return ""

    # Normalize trailing line whitespace first
    cleaned = re.sub(r"[ \t]+(?=\n)", "", text)

    # Strip sponsorship blocks
    for pat in SPONSOR_PATTERNS:
        cleaned = re.sub(pat, "\n\n", cleaned)

    # Strip subscription / CTA blocks
    for pat in CTA_PATTERNS:
        cleaned = re.sub(pat, "\n\n", cleaned)

    # Collapse excess whitespace
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
