"""
ZERO-INBOX: Real-time Cost Tracker & Token Accounting
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings, ProviderPricing
from app.core.models import CostRecord


class CostTracker:
    """Tracks token consumption and calculates exact USD costs across models."""

    def __init__(self):
        self.pricing: Dict[str, ProviderPricing] = settings.pricing_table

    def estimate_tokens(self, text: str) -> int:
        """Approximates token count based on whitespace and character length (~4 chars/token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def calculate_cost(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        user_id: str = "default_user",
        digest_id: Optional[str] = None
    ) -> CostRecord:
        """Calculates exact dollar cost according to model pricing schedules."""
        pricing_rule = self.pricing.get(model) or self.pricing.get(provider) or self.pricing["local_fallback"]

        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing_rule.prompt_price_per_m
        completion_cost = (completion_tokens / 1_000_000.0) * pricing_rule.completion_price_per_m
        total_cost = round(prompt_cost + completion_cost, 6)

        return CostRecord(
            user_id=user_id,
            digest_id=digest_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost_usd=total_cost,
            created_at=datetime.utcnow()
        )

    def format_cost_summary(self, record: CostRecord) -> str:
        """Returns human-readable cost summary."""
        return (
            f"Provider: {record.provider} ({record.model}) | "
            f"Tokens: {record.prompt_tokens + record.completion_tokens} "
            f"(Prompt: {record.prompt_tokens}, Completion: {record.completion_tokens}) | "
            f"Cost: ${record.total_cost_usd:.6f} USD"
        )


cost_tracker = CostTracker()
