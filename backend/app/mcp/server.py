"""
ZERO-INBOX: Model Context Protocol (MCP) Server Implementation
Using official Model Context Protocol Python SDK (mcp.server.mcpserver.MCPServer)
"""

from mcp.server.mcpserver import MCPServer
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.core.models import (
    SourceConfig, SourceType, SourceStatus, UserPreferences,
    SummaryLength, DeliveryChannel
)
from app.db.database import db
from app.scheduler.runner import run_user_digest_pipeline
from app.scheduler.engine import scheduler_engine
from app.delivery.dispatcher import delivery_dispatcher


# Initialize MCP server
mcp_server = MCPServer(settings.mcp_server_name)


# ==============================================================================
# MCP TOOLS (12 Required Tools)
# ==============================================================================

@mcp_server.tool()
async def create_digest(
    user_id: str = "default_user",
    topics: Optional[List[str]] = None,
    max_stories: int = 10,
    summary_length: str = "balanced"
) -> str:
    """
    Generate an on-demand personalized media intelligence digest from monitored sources.
    Inputs:
    - user_id: Identifier for user profile
    - topics: Optional override list of target topics
    - max_stories: Maximum number of stories to synthesize (default 10)
    - summary_length: 'concise', 'balanced', or 'detailed'
    """
    prefs = db.get_user_preferences(user_id) or UserPreferences(user_id=user_id)
    if topics:
        prefs.topics = topics
    if max_stories:
        prefs.max_stories = max_stories
    try:
        prefs.summary_length = SummaryLength(summary_length)
    except Exception:
        prefs.summary_length = SummaryLength.BALANCED

    db.save_user_preferences(prefs)
    digest = await run_user_digest_pipeline(user_id=user_id, force=True)
    if not digest:
        return json.dumps({"error": "Failed to synthesize digest; please verify sources."})

    return json.dumps({
        "digest_id": digest.id,
        "date": digest.date_str,
        "title": digest.title,
        "read_time_minutes": digest.estimated_read_time_minutes,
        "articles_included": digest.articles_included,
        "cost_usd": digest.cost_usd,
        "content_markdown": digest.content_markdown
    }, indent=2)


@mcp_server.tool()
async def get_latest_digest(user_id: str = "default_user") -> str:
    """Retrieve the most recently generated intelligence digest for a user."""
    digest = db.get_latest_digest(user_id)
    if not digest:
        return json.dumps({"status": "no_digest_found", "message": "No digest generated yet for this user."})

    return json.dumps({
        "digest_id": digest.id,
        "date": digest.date_str,
        "title": digest.title,
        "articles_analyzed": digest.total_articles_analyzed,
        "articles_included": digest.articles_included,
        "cost_usd": digest.cost_usd,
        "content_markdown": digest.content_markdown
    }, indent=2)


@mcp_server.tool()
async def add_source(
    name: str,
    url: str,
    source_type: str = "rss",
    category_hint: Optional[str] = None,
    user_id: str = "default_user"
) -> str:
    """
    Register a new RSS feed, newsletter source, Reddit community, or web publication.
    source_type can be: 'rss', 'atom', 'newsletter', 'reddit', or 'web'.
    """
    try:
        st = SourceType(source_type.lower())
    except Exception:
        st = SourceType.RSS

    src = SourceConfig(
        user_id=user_id,
        name=name,
        url=url,
        source_type=st,
        category_hint=category_hint
    )
    created = db.add_source(src)
    return json.dumps({
        "status": "success",
        "source_id": created.id,
        "name": created.name,
        "url": created.url,
        "source_type": created.source_type.value
    }, indent=2)


@mcp_server.tool()
async def remove_source(source_id: str, user_id: str = "default_user") -> str:
    """Remove a registered content source after verifying user ownership."""
    success = db.remove_source(source_id=source_id, user_id=user_id)
    if success:
        return json.dumps({"status": "success", "message": f"Source {source_id} removed."})
    return json.dumps({"status": "not_found", "message": f"Source {source_id} not found for user {user_id}."})


@mcp_server.tool()
async def list_sources(user_id: str = "default_user", status: Optional[str] = None) -> str:
    """List all registered information sources and their operational sync status."""
    sources = db.list_sources(user_id=user_id, status=status)
    results = [
        {
            "id": s.id,
            "name": s.name,
            "url": s.url,
            "type": s.source_type.value,
            "status": s.status.value,
            "error_count": s.error_count,
            "last_fetched": s.last_fetched_at.isoformat() if s.last_fetched_at else None
        }
        for s in sources
    ]
    return json.dumps({"total": len(results), "sources": results}, indent=2)


@mcp_server.tool()
async def update_preferences(
    user_id: str = "default_user",
    topics: Optional[List[str]] = None,
    max_stories: Optional[int] = None,
    summary_length: Optional[str] = None,
    timezone: Optional[str] = None,
    delivery_channel: Optional[str] = None,
    delivery_destination: Optional[str] = None
) -> str:
    """Update user digest preferences, delivery channels, and scheduled delivery times."""
    prefs = db.get_user_preferences(user_id) or UserPreferences(user_id=user_id)
    if topics is not None:
        prefs.topics = topics
    if max_stories is not None:
        prefs.max_stories = max_stories
    if summary_length is not None:
        try:
            prefs.summary_length = SummaryLength(summary_length)
        except Exception:
            pass
    if timezone is not None:
        prefs.timezone = timezone
    if delivery_channel is not None:
        try:
            prefs.delivery_channel = DeliveryChannel(delivery_channel.lower())
        except Exception:
            pass
    if delivery_destination is not None:
        prefs.delivery_destination = delivery_destination

    db.save_user_preferences(prefs)
    scheduler_engine.schedule_user_job(user_id)

    return json.dumps({
        "status": "success",
        "user_id": user_id,
        "topics": prefs.topics,
        "max_stories": prefs.max_stories,
        "summary_length": prefs.summary_length.value,
        "timezone": prefs.timezone,
        "delivery_channel": prefs.delivery_channel.value,
        "delivery_destination": prefs.delivery_destination
    }, indent=2)


@mcp_server.tool()
async def search_articles(query: str, limit: int = 15) -> str:
    """Search previously ingested articles and extracted intelligence."""
    articles = db.search_articles(query=query, limit=limit)
    items = [
        {
            "id": a.id,
            "title": a.title,
            "source": a.source_name,
            "category": a.category,
            "url": a.url,
            "summary": a.summary or a.clean_text[:200]
        }
        for a in articles
    ]
    return json.dumps({"count": len(items), "query": query, "results": items}, indent=2)


@mcp_server.tool()
async def get_article_summary(article_id: str) -> str:
    """Retrieve the full detailed summary, key takeaways, and significance of an article."""
    art = db.get_article(article_id)
    if not art:
        return json.dumps({"error": f"Article {article_id} not found."})

    return json.dumps({
        "id": art.id,
        "title": art.title,
        "source": art.source_name,
        "url": art.url,
        "category": art.category,
        "headline": art.headline,
        "summary": art.summary,
        "key_takeaways": art.key_takeaways,
        "why_it_matters": art.why_it_matters,
        "published_at": art.published_at.isoformat() if art.published_at else None
    }, indent=2)


@mcp_server.tool()
async def get_topic_trends(user_id: str = "default_user") -> str:
    """Identify topic frequency and category distribution from monitored feeds."""
    articles = db.search_articles(query="", limit=100)
    cat_counts: Dict[str, int] = {}
    for a in articles:
        cat_counts[a.category] = cat_counts.get(a.category, 0) + 1

    return json.dumps({
        "monitored_articles_sample": len(articles),
        "category_distribution": cat_counts,
        "primary_focus": max(cat_counts, key=cat_counts.get) if cat_counts else "General Technology"
    }, indent=2)


@mcp_server.tool()
async def get_digest_history(user_id: str = "default_user", limit: int = 10) -> str:
    """Retrieve historical executive digests generated for this user."""
    history = db.get_digest_history(user_id=user_id, limit=limit)
    items = [
        {
            "id": d.id,
            "date": d.date_str,
            "title": d.title,
            "articles_included": d.articles_included,
            "read_time_minutes": d.estimated_read_time_minutes,
            "cost_usd": d.cost_usd,
            "delivery_status": d.delivery_status
        }
        for d in history
    ]
    return json.dumps({"count": len(items), "history": items}, indent=2)


@mcp_server.tool()
async def send_test_notification(channel: str, destination: str) -> str:
    """Send a verification test message to a Telegram, Discord, or WhatsApp destination."""
    try:
        ch = DeliveryChannel(channel.lower())
    except Exception:
        return json.dumps({"error": f"Unsupported channel: {channel}. Choose telegram, discord, or whatsapp."})

    success, err = await delivery_dispatcher.send_test_ping(ch, destination)
    if success:
        return json.dumps({"status": "success", "message": f"Test ping successfully delivered to {destination}."})
    return json.dumps({"status": "failed", "error": err or "Failed to deliver message."})


@mcp_server.tool()
async def get_agent_status() -> str:
    """Return operational health, autonomous schedule status, active sources, and cost metrics."""
    sources = db.list_sources()
    cost_summary = db.get_cost_summary()
    sched_info = scheduler_engine.get_job_info("default_user")

    return json.dumps({
        "status": "operational",
        "agent_name": settings.app_name,
        "version": settings.version,
        "active_sources": len([s for s in sources if s.status == SourceStatus.ACTIVE]),
        "total_sources": len(sources),
        "scheduler": sched_info or {"status": "inactive"},
        "costs": cost_summary
    }, indent=2)


# ==============================================================================
# MCP RESOURCES (5 Required Resources)
# ==============================================================================

@mcp_server.resource("zero-inbox://capabilities")
def get_capabilities_resource() -> str:
    return json.dumps({
        "name": settings.app_name,
        "version": settings.version,
        "supported_sources": ["rss", "atom", "newsletter_mime", "reddit", "web_article"],
        "delivery_channels": ["telegram", "discord", "whatsapp", "in_app"],
        "noise_removal": ["sponsorships", "affiliates", "subscription_prompts", "tracking_params"],
        "deduplication": ["canonical_url", "md5_hash", "jaccard_ngram_shingles"],
        "supported_llm_providers": ["gemini", "openai", "anthropic", "local_fallback"]
    }, indent=2)


@mcp_server.resource("zero-inbox://methodology")
def get_methodology_resource() -> str:
    return (
        "# ZERO-INBOX Forensic Media Intelligence Methodology\n\n"
        "1. Ingestion: Pulls updates using HTTP conditional headers (ETag, Last-Modified) to eliminate bandwidth waste.\n"
        "2. Sanitization: Strips tracking params (UTM, ref), malicious scripts (SSRF/XSS protection), and marketing boilerplate.\n"
        "3. Deduplication: Multi-tier canonicalization, MD5 fingerprinting, and Jaccard n-gram shingle clustering.\n"
        "4. Relevance Ranking: Multi-factor scoring weighting topic relevance, keyword tracks/excludes, and exponential recency decay.\n"
        "5. Hallucination-Free Synthesis: Strict prompt guidelines requiring direct traceability to source content."
    )


@mcp_server.resource("zero-inbox://supported-sources")
def get_supported_sources_resource() -> str:
    return json.dumps({
        "rss_atom": "Full RSS 1.0, 2.0, and Atom support with conditional ETag caching.",
        "newsletters": "MIME RFC822 parser with privacy guard filtering out personal mail.",
        "reddit": "Subreddit hot discussion tracker with upvote/comment signal filters.",
        "web_articles": "Public article scraper with SSRF safeguards and reader extraction."
    }, indent=2)


@mcp_server.resource("zero-inbox://delivery-channels")
def get_delivery_channels_resource() -> str:
    return json.dumps({
        "telegram": "Telegram Bot API with automatic message splitting for 4096-character limit.",
        "discord": "Discord Webhook & Bot integration with rich embed cards.",
        "whatsapp": "Meta WhatsApp Cloud API with template compliance."
    }, indent=2)


@mcp_server.resource("zero-inbox://agent-status")
def get_agent_status_resource() -> str:
    cost_summary = db.get_cost_summary()
    sources = db.list_sources()
    return json.dumps({
        "health": "healthy",
        "active_sources": len([s for s in sources if s.status == SourceStatus.ACTIVE]),
        "total_spent_usd": cost_summary.get("total_spent_usd", 0.0),
        "timestamp": datetime.utcnow().isoformat()
    }, indent=2)


# ==============================================================================
# MCP PROMPTS (5 Required Prompts)
# ==============================================================================

@mcp_server.prompt()
def morning_intelligence_brief() -> str:
    return (
        "Generate a high-level executive morning brief from the latest monitored sources. "
        "Highlight the top 3 critical developments, the technology radar, and the overarching daily takeaway. "
        "Ensure all summaries are factual, strictly source-grounded, and concise."
    )


@mcp_server.prompt()
def technology_news_digest() -> str:
    return (
        "Synthesize a focused Technology News Digest filtering out all promotional fluff and advertisements. "
        "Group stories into Artificial Intelligence, Programming & DevOps, and Cybersecurity."
    )


@mcp_server.prompt()
def research_digest() -> str:
    return (
        "Compile a Research & Science Digest highlighting recent papers, breakthrough experiments, "
        "and empirical findings. Focus on methodology, key statistics, and why it matters."
    )


@mcp_server.prompt()
def startup_intelligence() -> str:
    return (
        "Analyze the latest venture capital, founder developments, seed/Series A funding announcements, "
        "and product launches. Summarize market signals and ecosystem shifts."
    )


@mcp_server.prompt()
def personalized_media_summary() -> str:
    return (
        "Review the user's configured topic preferences and generate an aligned media summary. "
        "Prioritize user priority sources, respect exclude keywords, and highlight actionable insights."
    )
