# ZERO-INBOX: Model Context Protocol (MCP) Setup Guide

ZERO-INBOX includes a native Model Context Protocol (MCP) server built with the official Python SDK (`mcp` v2.3.0 `MCPServer`). It allows AI assistants like Claude Desktop, Cursor, and custom agentic frameworks to interact with your media intelligence pipeline.

---

## 1. Quick Setup for Claude Desktop & Cursor

### STDIO Client Configuration
Add the following block to your `claude_desktop_config.json` or Cursor Settings:

```json
{
  "mcpServers": {
    "zero-inbox": {
      "command": "python",
      "args": [
        "c:/Users/swapn/OneDrive/Desktop/agent/zero-inbox/backend/run_mcp_stdio.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "ZERO_INBOX_ENV": "development"
      }
    }
  }
}
```

---

## 2. Remote Streamable HTTP / SSE Transport

The MCP server is also mounted directly on the FastAPI application:
```http
http://127.0.0.1:8010/mcp
```
Remote MCP clients can connect over Server-Sent Events (SSE) to query tools and resources remotely.

---

## 3. Exposed MCP Tools

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `create_digest` | `user_id`, `topics`, `max_stories`, `summary_length` | Generates an on-demand personalized media brief. |
| `get_latest_digest` | `user_id` | Retrieves the most recently synthesized intelligence brief. |
| `add_source` | `name`, `url`, `source_type`, `category_hint`, `user_id` | Registers an RSS, newsletter, Reddit, or web source. |
| `remove_source` | `source_id`, `user_id` | Removes a registered source after ownership validation. |
| `list_sources` | `user_id`, `status` | Returns all active feeds and sync status. |
| `update_preferences` | `user_id`, `topics`, `max_stories`, `summary_length`, `timezone`, `delivery_channel`, `delivery_destination` | Updates user preferences and cron delivery time. |
| `search_articles` | `query`, `limit` | Full-text searches across previously ingested articles. |
| `get_article_summary`| `article_id` | Retrieves deep summary, key takeaways, and significance. |
| `get_topic_trends` | `user_id` | Analyzes topic category distribution across active feeds. |
| `get_digest_history` | `user_id`, `limit` | Returns archived historical daily briefs. |
| `send_test_notification` | `channel`, `destination` | Sends test notification to Telegram, Discord, or WhatsApp. |
| `get_agent_status` | *(none)* | Returns operational health, next cron execution, and costs. |

---

## 4. MCP Resources

- `zero-inbox://capabilities`: JSON schema of supported formats, channels, and LLMs.
- `zero-inbox://methodology`: Architectural explanation of ingestion, deduplication, and scoring.
- `zero-inbox://supported-sources`: Detailed specifications for RSS, MIME, Reddit, and web sources.
- `zero-inbox://delivery-channels`: Delivery channel specs and payload requirements.
- `zero-inbox://agent-status`: Real-time operational health and token expenditures.

---

## 5. MCP Prompts

- `morning_intelligence_brief`: Guides an AI agent to request an executive morning brief.
- `technology_news_digest`: Tailors queries to software, hardware, and engineering developments.
- `research_digest`: Synthesizes scientific papers and breakthrough experiments.
- `startup_intelligence`: Focuses on funding, venture shifts, and founder announcements.
- `personalized_media_summary`: Interacts with the user to craft custom media summaries.
