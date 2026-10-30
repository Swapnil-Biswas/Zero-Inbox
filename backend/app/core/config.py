"""
ZERO-INBOX: Core Configuration Module
"""

import os
import secrets
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ProviderPricing(BaseModel):
    """Pricing in USD per 1M tokens."""
    prompt_price_per_m: float
    completion_price_per_m: float


class Settings(BaseModel):
    app_name: str = "ZERO-INBOX Autonomous Media Intelligence"
    version: str = "1.0.0"
    env: str = os.getenv("ZERO_INBOX_ENV", "development")
    debug: bool = os.getenv("ZERO_INBOX_DEBUG", "false").lower() == "true"
    host: str = os.getenv("ZERO_INBOX_HOST", "0.0.0.0")
    port: int = int(os.getenv("ZERO_INBOX_PORT", "8010"))
    secret_key: str = os.getenv("ZERO_INBOX_SECRET_KEY", "default-zero-inbox-insecure-secret-key-32b")

    # Database Path
    db_path: str = os.getenv(
        "ZERO_INBOX_DB_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "zero_inbox.db")
    )

    # Ingestion Limits
    max_articles_per_feed: int = 50
    request_timeout_seconds: float = 12.0
    user_agent: str = "ZeroInbox-IntelligenceBot/1.0 (+https://github.com/Swapnil-Biswas/zero-inbox)"

    # Scheduling Defaults
    default_schedule_hour: int = int(os.getenv("DEFAULT_SCHEDULE_HOUR", "6"))
    default_schedule_minute: int = int(os.getenv("DEFAULT_SCHEDULE_MINUTE", "0"))
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "UTC")

    # LLM Settings
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "local_fallback")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    local_llm_endpoint: str = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434/v1")

    # Pricing Table (USD per 1 Million Tokens)
    pricing_table: Dict[str, ProviderPricing] = {
        "gemini-1.5-flash": ProviderPricing(prompt_price_per_m=0.075, completion_price_per_m=0.30),
        "gpt-4o-mini": ProviderPricing(prompt_price_per_m=0.15, completion_price_per_m=0.60),
        "claude-3-5-haiku": ProviderPricing(prompt_price_per_m=0.80, completion_price_per_m=4.00),
        "local_fallback": ProviderPricing(prompt_price_per_m=0.00, completion_price_per_m=0.00),
    }

    # Delivery API Secrets
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    discord_webhook_url: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    whatsapp_phone_number_id: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_access_token: Optional[str] = os.getenv("WHATSAPP_ACCESS_TOKEN")
    whatsapp_template_name: str = os.getenv("WHATSAPP_TEMPLATE_NAME", "daily_media_digest")

    # MCP Server
    mcp_server_name: str = "zero-inbox-mcp"
    mcp_server_version: str = "1.0.0"
    mcp_auth_token: Optional[str] = os.getenv("ZERO_INBOX_MCP_AUTH_TOKEN")

    # HireCrew Marketplace
    # No published fallback: when unset, a random per-process token keeps /jobs closed.
    hirecrew_seller_token: str = os.getenv("HIRECREW_SELLER_TOKEN") or secrets.token_urlsafe(32)
    hirecrew_job_timeout_seconds: int = 300

    # Research LLM for HireCrew briefs (any OpenAI-compatible chat endpoint, e.g. LM Studio / Ollama / OpenAI)
    research_llm_endpoint: str = os.getenv("RESEARCH_LLM_ENDPOINT", "http://localhost:1234/v1")
    research_llm_model: str = os.getenv("RESEARCH_LLM_MODEL", "google/gemma-4-e2b")
    research_llm_api_key: Optional[str] = os.getenv("RESEARCH_LLM_API_KEY")
    research_llm_timeout_seconds: float = float(os.getenv("RESEARCH_LLM_TIMEOUT_SECONDS", "180"))
    # Evidence characters sent to the model; ~12k chars fits an 8k-token context with room to answer.
    research_evidence_char_budget: int = int(os.getenv("RESEARCH_EVIDENCE_CHAR_BUDGET", "12000"))


settings = Settings()

