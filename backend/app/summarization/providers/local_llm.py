"""
ZERO-INBOX: Local LLM & Heuristic Extraction Provider
"""

import httpx
import re
from typing import Tuple, List
from app.core.config import settings
from app.core.models import SummaryLength
from app.core.cost_tracker import cost_tracker
from app.summarization.providers.base import LLMProvider


class LocalLLMProvider(LLMProvider):
    """
    Connects to local OpenAI-compatible endpoints (Ollama, LM Studio)
    or falls back to deterministic extractive summarization if local server is unreachable.
    """

    def __init__(self, endpoint: str = settings.local_llm_endpoint):
        self.endpoint = endpoint

    @property
    def provider_name(self) -> str:
        return "local_fallback"

    @property
    def default_model(self) -> str:
        return "heuristic-local-v1"

    async def summarize_article(
        self, title: str, text: str, length: SummaryLength = SummaryLength.BALANCED
    ) -> Tuple[str, str, List[str], str, int, int]:
        # Try calling local LLM endpoint if available
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(
                    f"{self.endpoint}/chat/completions",
                    json={
                        "model": "llama3.2",
                        "messages": [
                            {"role": "system", "content": "You are a concise forensic media analyst. Return only clear factual summaries."},
                            {"role": "user", "content": f"Title: {title}\n\nContent:\n{text[:2000]}\n\nSummarize concisely."}
                        ]
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    p_tok = cost_tracker.estimate_tokens(title + text[:2000])
                    c_tok = cost_tracker.estimate_tokens(content)
                    return title, content.strip(), [content[:120]], "Relevant development in current coverage.", p_tok, c_tok
        except Exception:
            pass  # Fallback to local heuristic extractor

        # Deterministic Extractive Fallback
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        summary_body = paragraphs[0] if paragraphs else text[:300]

        # Extract salient sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 25 and not s.startswith("http")]

        takeaways = clean_sentences[:3] if len(clean_sentences) >= 3 else [summary_body[:150]]
        why_it_matters = clean_sentences[3] if len(clean_sentences) > 3 else "Provides key context for today's industry landscape."

        prompt_tokens = cost_tracker.estimate_tokens(title + text[:1500])
        completion_tokens = cost_tracker.estimate_tokens(summary_body + " ".join(takeaways) + why_it_matters)

        return title, summary_body, takeaways, why_it_matters, prompt_tokens, completion_tokens

    async def synthesize_daily_takeaway(
        self, top_stories: List[str]
    ) -> Tuple[str, int, int]:
        if not top_stories:
            return "Quiet news cycle with steady incremental progress across monitored sectors.", 10, 15

        joined = "; ".join(top_stories[:3])
        takeaway = (
            f"Today's primary developments center on {joined}. "
            f"The overarching trend highlights rapid technical maturation and focused execution."
        )
        p_tok = cost_tracker.estimate_tokens(joined)
        c_tok = cost_tracker.estimate_tokens(takeaway)
        return takeaway, p_tok, c_tok

