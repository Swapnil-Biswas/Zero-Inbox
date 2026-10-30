"""
ZERO-INBOX: LLM Provider Factory
"""

from typing import Optional
from app.core.config import settings
from app.summarization.providers.base import LLMProvider
from app.summarization.providers.local_llm import LocalLLMProvider
from app.summarization.providers.gemini import GeminiProvider


def get_llm_provider(name: Optional[str] = None) -> LLMProvider:
    provider_name = (name or settings.default_llm_provider).lower()

    if provider_name == "gemini" and settings.gemini_api_key:
        return GeminiProvider(settings.gemini_api_key)

    # Defaults to LocalLLMProvider (which handles OpenAI-compatible endpoints or local extraction)
    return LocalLLMProvider()

