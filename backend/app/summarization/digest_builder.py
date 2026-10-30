"""
ZERO-INBOX: Daily Intelligence Digest Builder
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from app.core.models import Digest, ProcessedArticle, UserPreferences
from app.core.cost_tracker import cost_tracker
from app.db.database import db
from app.summarization.providers.factory import get_llm_provider
from app.processing.clusterer import topic_clusterer


class DigestBuilder:
    """Assembles and synthesizes normalized, deduplicated articles into a structured executive brief."""

    async def build_digest(
        self,
        articles: List[ProcessedArticle],
        prefs: UserPreferences,
        provider_name: Optional[str] = None
    ) -> Digest:
        provider = get_llm_provider(provider_name)
        digest_id = f"dig_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%d %B %Y")

        total_analyzed = len(articles)
        # Select top stories up to max_stories limit
        selected_articles = articles[:prefs.max_stories]
        articles_included = len(selected_articles)

        total_prompt_tokens = 0
        total_completion_tokens = 0

        # Summarize each article
        summarized_articles: List[ProcessedArticle] = []
        for art in selected_articles:
            try:
                hl, summ, takeaways, why, p_tok, c_tok = await provider.summarize_article(
                    art.title, art.clean_text, prefs.summary_length
                )
                art.headline = hl
                art.summary = summ
                art.key_takeaways = takeaways
                art.why_it_matters = why
                total_prompt_tokens += p_tok
                total_completion_tokens += c_tok
            except Exception as e:
                art.headline = art.title
                art.summary = art.clean_text[:250] + "..."
                art.key_takeaways = [art.clean_text[:120]]
                art.why_it_matters = "Monitored item in today's news cycle."
            summarized_articles.append(art)
            db.save_article(art)

        # Categorize
        for art in summarized_articles:
            topic_clusterer.assign_category(art)

        # Partition into sections:
        # 1. Top Stories (Highest relevance)
        # 2. Technology Radar (Tech, AI, Programming, Startups)
        # 3. Community Pulse (Discussions, Reddit)
        top_stories = summarized_articles[:3]
        community_stories = [a for a in summarized_articles if a.category == "Communities & Discussions"]
        radar_stories = [a for a in summarized_articles if a not in top_stories and a not in community_stories]

        # Synthesize Daily Takeaway
        top_headlines = [a.headline or a.title for a in top_stories]
        daily_takeaway, syn_p_tok, syn_c_tok = await provider.synthesize_daily_takeaway(top_headlines)
        total_prompt_tokens += syn_p_tok
        total_completion_tokens += syn_c_tok

        # Calculate exact cost
        cost_rec = cost_tracker.calculate_cost(
            provider=provider.provider_name,
            model=provider.default_model,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            user_id=prefs.user_id,
            digest_id=digest_id
        )
        db.record_cost(cost_rec)

        # Build Markdown content
        lines: List[str] = []
        lines.append("# ZERO-INBOX")
        lines.append("## Daily Intelligence Brief")
        lines.append(f"*{date_str}*\n")
        lines.append("GOOD MORNING. HERE'S WHAT MATTERS TODAY.\n")
        lines.append("---\n")

        # Section: TOP STORIES
        lines.append("### TOP STORIES\n")
        for idx, art in enumerate(top_stories, 1):
            lines.append(f"**{idx}. {art.headline or art.title}**")
            lines.append(f"{art.summary}\n")
            if art.why_it_matters:
                lines.append(f"*Why it matters:* {art.why_it_matters}\n")
            lines.append(f"**Source:** [{art.source_name}]({art.url})\n")

        # Section: TECHNOLOGY RADAR
        if radar_stories:
            lines.append("### TECHNOLOGY RADAR\n")
            for art in radar_stories:
                lines.append(f"- **{art.headline or art.title}**: {art.summary}")
                lines.append(f"  *Source: [{art.source_name}]({art.url})*\n")

        # Section: COMMUNITY PULSE
        if community_stories:
            lines.append("### COMMUNITY PULSE\n")
            for art in community_stories:
                lines.append(f"- **{art.headline or art.title}**: {art.summary}")
                lines.append(f"  *Discussion: [{art.source_name}]({art.url})*\n")

        # Section: TODAY'S TAKEAWAY
        lines.append("### TODAY'S TAKEAWAY\n")
        lines.append(f"{daily_takeaway}\n")

        # Estimated Read Time
        total_words = sum(len(line.split()) for line in lines)
        read_time = max(1, total_words // 200)
        lines.append(f"---\n*Read time: approximately {read_time} minute{'s' if read_time > 1 else ''}.*")

        markdown_body = "\n".join(lines)
        distinct_categories = list(set(a.category for a in summarized_articles))

        digest = Digest(
            id=digest_id,
            user_id=prefs.user_id,
            date_str=date_str,
            title=f"Daily Intelligence Brief - {date_str}",
            content_markdown=markdown_body,
            categories=distinct_categories,
            total_articles_analyzed=total_analyzed,
            articles_included=articles_included,
            estimated_read_time_minutes=read_time,
            cost_usd=cost_rec.total_cost_usd,
            delivery_status="generated",
            created_at=now
        )

        db.save_digest(digest)
        return digest


digest_builder = DigestBuilder()
