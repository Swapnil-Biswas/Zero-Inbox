"""
ZERO-INBOX: Core Domain Models & Schemas
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    RSS = "rss"
    ATOM = "atom"
    NEWSLETTER = "newsletter"
    REDDIT = "reddit"
    WEB = "web"


class SourceStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class DeliveryChannel(str, Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    NONE = "none"


class SummaryLength(str, Enum):
    CONCISE = "concise"     # 1-2 sentences
    BALANCED = "balanced"   # 3-4 sentences + bullets
    DETAILED = "detailed"   # comprehensive paragraph + bullets + stats


class SourceConfig(BaseModel):
    id: Optional[str] = None
    user_id: str = "default_user"
    name: str
    url: str
    source_type: SourceType = SourceType.RSS
    status: SourceStatus = SourceStatus.ACTIVE
    category_hint: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    last_fetched_at: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RawArticle(BaseModel):
    source_id: str
    source_name: str
    url: str
    title: str
    raw_content: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessedArticle(BaseModel):
    id: str
    source_id: str
    source_name: str
    url: str
    canonical_url: str
    title: str
    clean_text: str
    clean_length: int
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    category: str = "Technology"
    relevance_score: float = 0.5
    novelty_score: float = 1.0
    is_duplicate: bool = False
    duplicate_of_id: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    key_takeaways: List[str] = Field(default_factory=list)
    why_it_matters: Optional[str] = None


class ArticleCluster(BaseModel):
    cluster_id: str
    topic_name: str
    category: str
    lead_article: ProcessedArticle
    supporting_articles: List[ProcessedArticle] = Field(default_factory=list)
    combined_score: float = 0.0


class UserPreferences(BaseModel):
    user_id: str = "default_user"
    topics: List[str] = Field(default_factory=lambda: [
        "Artificial Intelligence", "Technology", "Startups", "Programming", "Science", "Cybersecurity"
    ])
    preferred_sources: List[str] = Field(default_factory=list)
    blocked_sources: List[str] = Field(default_factory=list)
    priority_sources: List[str] = Field(default_factory=list)
    summary_length: SummaryLength = SummaryLength.BALANCED
    max_stories: int = 10
    preferred_language: str = "en"
    delivery_time_hour: int = 6
    delivery_time_minute: int = 0
    timezone: str = "UTC"
    delivery_channel: DeliveryChannel = DeliveryChannel.NONE
    delivery_destination: Optional[str] = None
    importance_threshold: float = 0.4
    track_keywords: List[str] = Field(default_factory=list)
    exclude_keywords: List[str] = Field(default_factory=list)
    feedback_weights: Dict[str, float] = Field(default_factory=dict)  # topic -> multiplier


class Digest(BaseModel):
    id: str
    user_id: str
    date_str: str
    title: str
    content_markdown: str
    categories: List[str] = Field(default_factory=list)
    total_articles_analyzed: int = 0
    articles_included: int = 0
    estimated_read_time_minutes: int = 5
    cost_usd: float = 0.0
    delivery_status: str = "generated"  # generated | delivered | delivery_failed
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostRecord(BaseModel):
    id: Optional[str] = None
    user_id: str
    digest_id: Optional[str] = None
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_cost_usd: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeliveryLog(BaseModel):
    id: Optional[str] = None
    digest_id: str
    channel: DeliveryChannel
    destination: str
    status: str  # success | failed | skipped
    error_message: Optional[str] = None
    sent_at: datetime = Field(default_factory=datetime.utcnow)

