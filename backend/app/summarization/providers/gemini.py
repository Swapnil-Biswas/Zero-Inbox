"""
ZERO-INBOX: Google Gemini Provider
"""

import httpx
import json
import re
from typing import Tuple, List
from app.core.config import settings
from app.core.models import SummaryLength
from app.core.cost_tracker import cost_tracker
from app.summarization.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Integrates Google Gemini 1.5 Flash for high-speed, cost-optimized summarization."""

    def __init__(self, api_key: str = settings.gemini_api_key or ""):
        self.api_key = api_key
        self.model = "gemini-1.5-flash"

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self.model

    async def summarize_article(
        self, title: str, text: str, length: SummaryLength = SummaryLength.BALANCED
    ) -> Tuple[str, str, List[str], str, int, int]:
        if not self.api_key:
            from app.summarization.providers.local_llm import LocalLLMProvider
            return await LocalLLMProvider().summarize_article(title, text, length)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"You are an executive media intelligence analyst. Summarize this article without any hallucinations.\n"
            f"Article Title: {title}\n"
            f"Article Text:\n{text[:4000]}\n\n"
            f"Return a strict JSON object with these keys:\n"
            f'{{"headline": "concise 1-line headline", "summary": "2-3 sentence overview", '
            f'"key_takeaways": ["point 1", "point 2"], "why_it_matters": "1 sentence on significance"}}'
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error: {resp.status_code} - {resp.text}")
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_text)

            p_tok = cost_tracker.estimate_tokens(prompt)
            c_tok = cost_tracker.estimate_tokens(raw_text)

            return (
                parsed.get("headline", title),
                parsed.get("summary", ""),
                parsed.get("key_takeaways", []),
                parsed.get("why_it_matters", ""),
                p_tok,
                c_tok
            )

    async def synthesize_daily_takeaway(
        self, top_stories: List[str]
    ) -> Tuple[str, int, int]:
        if not self.api_key:
            from app.summarization.providers.local_llm import LocalLLMProvider
            return await LocalLLMProvider().synthesize_daily_takeaway(top_stories)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"Synthesize the overarching theme of today's top developments in 2-3 sentences:\n"
            + "\n".join(f"- {s}" for s in top_stories)
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            takeaway = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            p_tok = cost_tracker.estimate_tokens(prompt)
            c_tok = cost_tracker.estimate_tokens(takeaway)
            return takeaway, p_tok, c_tok
