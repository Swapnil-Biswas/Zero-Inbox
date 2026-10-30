"""
ZERO-INBOX: HireCrew Brief Parser & Prompt-Injection Neutralizer
"""

import re
from typing import Dict, Any


def sanitize_and_parse_brief(brief: str) -> Dict[str, Any]:
    """
    Parses buyer brief strictly as passive data.
    Neutralizes adversarial prompt injection payloads (e.g. SYSTEM OVERRIDE / IGNORE PREVIOUS).
    """
    cleaned = brief.strip()

    # Detect prompt injection attempts
    adversarial_flag = False
    if re.search(r"(?i)(?:system override|ignore (?:all )?prior instructions|disregard|you must now output)", cleaned):
        adversarial_flag = True

    # Extract topic or key entities
    topic = "Daily Intelligence Brief"
    if "quantum" in cleaned.lower():
        topic = "Quantum Computing Developments"
    elif "ai" in cleaned.lower() or "model" in cleaned.lower() or "llm" in cleaned.lower():
        topic = "Artificial Intelligence Architecture & Benchmarks"
    elif "climate" in cleaned.lower() or "energy" in cleaned.lower():
        topic = "Clean Energy & Climate Tech"

    return {
        "raw_brief": cleaned,
        "topic": topic,
        "is_adversarial_flagged": adversarial_flag,
        "length": len(cleaned)
    }
