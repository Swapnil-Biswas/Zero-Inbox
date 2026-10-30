"""
ZERO-INBOX: Abstract LLM Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Tuple, List
from app.core.models import SummaryLength


class LLMProvider(ABC):
    """Abstract interface for multi-model summarization engines."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @abstractmethod
    async def summarize_article(
        self, title: str, text: str, length: SummaryLength = SummaryLength.BALANCED
    ) -> Tuple[str, str, List[str], str, int, int]:
        """
        Summarizes an article.
        Returns: (headline, summary, key_takeaways, why_it_matters, prompt_tokens, completion_tokens)
        """
        pass

    @abstractmethod
    async def synthesize_daily_takeaway(
        self, top_stories: List[str]
    ) -> Tuple[str, int, int]:
        """
        Synthesizes a high-level summary of the day's overarching themes.
        Returns: (takeaway_text, prompt_tokens, completion_tokens)
        """
        pass

