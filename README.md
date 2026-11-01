# PROJECT ZERO-INBOX
## Autonomous Newsletter Intelligence & Daily Media Digest Agent
### Production-Ready | MCP-Native | HireCrew Marketplace Integration

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-v2.3.0%20Compliant-blueviolet.svg)](https://modelcontextprotocol.io/)
[![HireCrew](https://img.shields.io/badge/HireCrew-Seller--Hosted%20Ready-success.svg)](https://hirecrew.si)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

**ZERO-INBOX** eliminates the need to manually consume dozens of newsletters, RSS feeds, subreddits, and web publications. The agent operates autonomously every morning (default: 6:00 AM) to collect new content, strip noise and sponsorships, detect duplicate reporting, score developments according to your custom preferences, and synthesize a concise, high-signal intelligence brief delivered to **Telegram**, **Discord**, or **WhatsApp**.

---
## Key Capabilities

- **Modular Multi-Source Ingestion**:
  - **RSS & Atom Feeds**: RSS 1.0, 2.0, and Atom with HTTP `ETag` and `Last-Modified` conditional caching (`304 Not Modified`).
  - **Newsletter Ingestion**: MIME/RFC822 parser enforcing bulk header checks (`List-Unsubscribe`, `Precedence: bulk`) to strictly protect personal email privacy.
  - **Reddit Community Radar**: Subreddit tracking (`/r/{sub}/hot.json`) with upvote and comment engagement signal filtering.
  - **Public Web Ingestion**: SSRF-safe article extraction with reader view parsing.
- **Intelligent 5-Stage Content Pipeline**:
  - **Normalization**: Strips tracking parameters (`utm_*`, `ref`, `fbclid`, `gclid`).
  - **Noise Removal**: Excises sponsorships, affiliate blocks, subscription banners, and promotional CTAs.
  - **Deduplication Engine**: Multi-tier deduplication using canonical URLs, MD5 content hashes, and Jaccard similarity across 3-word shingles ($J \ge 0.60$).
  - **Relevance Scoring**: Multidimensional scoring factoring in topic alignment, keyword bonuses/penalties, and exponential recency decay ($t_{1/2} = 24\text{ hours}$).
  - **Topic Clustering**: Categorizes articles into *Artificial Intelligence*, *Technology*, *Startups*, *Cybersecurity*, *Programming*, *Science*, and *Communities*.
- **Autonomous Timezone-Aware Scheduler**:
  - APScheduler-backed cron engine executing at a user-configured time (default 6:00 AM).
  - Atomic SQLite database locking prevents duplicate daily executions across multi-worker deployments.
- **Multi-Channel Notification Dispatcher**:
  - **Telegram Bot API**: Markdown formatting with automatic splitting for Telegram's 4096-character limit.
  - **Discord Webhooks**: Rich embed cards with color-coded categories and metadata.
  - **WhatsApp Business Cloud API**: Meta-compliant messaging templates.
- **Model Context Protocol (MCP) Server**:
  - Official Python MCP SDK (`mcp` v2.3.0 `MCPServer`).
  - 12 Tools (`create_digest`, `get_latest_digest`, `add_source`, `remove_source`, `list_sources`, `update_preferences`, `search_articles`, `get_article_summary`, `get_topic_trends`, `get_digest_history`, `send_test_notification`, `get_agent_status`).
  - 5 Resources (`zero-inbox://*`) and 5 Prompts.
  - Dual transports: Local STDIO runner (`backend/run_mcp_stdio.py`) and Streamable HTTP/SSE (`/mcp`).
- **HireCrew Marketplace Seller-Hosted Agent**:
  - Strict compliance with `seller-hosted-api-v1` (`POST /jobs`, `GET /jobs/{jobId}`) with Bearer authentication and idempotency handling.
  - Briefs are answered by a source-grounded research engine (`backend/app/hirecrew/research.py`): it fetches the URLs named in the brief plus official documentation pages proposed by the model (SSRF-checked on every redirect), falls back to news search, and has an OpenAI-compatible LLM (local LM Studio/Ollama by default) write a report that cites only retrieved pages and states evidence gaps.
  - Jobs persist in SQLite; buyer jobs never touch your personal digest or delivery channels.

---

## Daily Intelligence Brief Example

```markdown
# ZERO-INBOX
## Daily Intelligence Brief
*31 October 2026*

GOOD MORNING. HERE'S WHAT MATTERS TODAY.
---

### TOP STORIES
1. Major AI Architecture Breakthrough
   Researchers unveil an open-weights reasoning model requiring 80% fewer compute parameters.
   Why it matters: Enables high-performance local inference on commodity hardware.
   Source: [Stanford AI Lab](https://arxiv.org/abs/2303.08774)

2. Venture Ecosystem Shift
   Foundational model investments pivot toward specialized vertical agents.
   Why it matters: Signals increased emphasis on unit economics and reliable automation.
   Source: [TechCrunch](https://techcrunch.com/2026/10/30/ai-agents)

### TECHNOLOGY RADAR
- Embedded Vector Database in Rust: Zero-dependency in-memory indexing library released.
  Source: [Hacker News](https://news.ycombinator.com)

### COMMUNITY PULSE
- [r/machinelearning] High-signal discussion on state-space vs transformer trade-offs.
  Discussion: [Reddit](https://reddit.com/r/machinelearning)

### TODAY'S TAKEAWAY
Today's primary developments center on architectural efficiency and localized agent runtimes.
---
*Read time: approximately 4 minutes.*
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd zero-inbox/backend
pip install -r requirements.txt
python run_server.py
```
*Backend runs on `http://127.0.0.1:8010` (Swagger UI at `http://127.0.0.1:8010/docs`).*

### 3. Frontend Setup
```bash
cd zero-inbox/frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5174`.*

---

## Connecting via Model Context Protocol (MCP)

Add the following to your `claude_desktop_config.json` or Cursor Settings:

```json
{
  "mcpServers": {
    "zero-inbox": {
      "command": "python",
      "args": [
        "<PATH_TO_ZERO_INBOX>/backend/run_mcp_stdio.py"
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

## HireCrew Marketplace Integration

ZERO-INBOX operates as an independent seller-hosted agent on HireCrew:

1. **Submit Job**:
   ```http
   POST /jobs
   Authorization: Bearer <HIRECREW_SELLER_TOKEN>
   Idempotency-Key: <unique-uuid>
   Content-Type: application/json

   {
     "orderId": "order-101",
     "brief": "Produce a daily media digest on quantum computing developments."
   }
   ```
2. **Poll Result**:
   ```http
   GET /jobs/{jobId}
   Authorization: Bearer <HIRECREW_SELLER_TOKEN>
   ```
3. **Research LLM**: set `RESEARCH_LLM_ENDPOINT`, `RESEARCH_LLM_MODEL` (and `RESEARCH_LLM_API_KEY` for hosted APIs). The default is LM Studio at `http://localhost:1234/v1` with `google/gemma-4-e2b`; a larger model gives noticeably more complete reports. `RESEARCH_EVIDENCE_CHAR_BUDGET` (default 12000) keeps prompts inside an 8k-token context.

---

## Running Verification & Tests

### Backend Test Suite
```bash
cd zero-inbox/backend
python -m unittest discover tests
```

### HireCrew Local Builder Kit Validation
```bash
cd zero-inbox
node "<PATH_TO_HIRECREW>/platform/node_modules/tsx/dist/cli.mjs" backend/validate_against_hirecrew.ts
```

### Frontend Production Build
```bash
cd zero-inbox/frontend
npm run build
```

---

## Documentation

- [Architecture & Data Flow](docs/ARCHITECTURE.md)
- [MCP Setup Guide](docs/MCP_SETUP.md)
- [HireCrew Integration Guide](docs/HIRECREW_INTEGRATION.md)
- [HireCrew Marketplace Listing](docs/HIRECREW_LISTING.md)
- [Security & Threat Model](docs/SECURITY.md)
- [Cost Optimization & Token Ledger](docs/COST_OPTIMIZATION.md)
- [Production Deployment Guide](docs/DEPLOYMENT.md)
- [Changelog](CHANGELOG.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

## License

Apache License 2.0.

