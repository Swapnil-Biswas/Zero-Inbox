# ZERO-INBOX: System Architecture & Data Flow

ZERO-INBOX is an autonomous personal media intelligence agent engineered to continuously aggregate, filter, deduplicate, score, and synthesize information from disparate communication channels into a single, high-signal executive daily brief.

---

## 1. High-Level System Architecture

```
[ External Sources ]
  ├── RSS / Atom Feeds (Conditional HTTP ETag / Last-Modified)
  ├── Newsletters (MIME RFC822 / IMAP / Webhooks with Bulk Filter)
  ├── Reddit Communities (Subreddit JSON API + Engagement Filters)
  └── Public Web Articles (SSRF-Safe Ingestion + Parser)
          │
          ▼
[ Ingestion Orchestrator ]
  └── Async Task Gathering -> RawArticle Standardizer
          │
          ▼
[ Content Processing Pipeline ]
  ├── Stage 1: Content Normalization (Canonical URL Stripping)
  ├── Stage 2: Noise Removal (Ad/Sponsor Stripper, Subscription CTAs)
  ├── Stage 3: Deduplication Engine (Exact URL, MD5 Hash, Jaccard 3-Gram)
  ├── Stage 4: Multidimensional Relevance Scorer (Topics, Recency, Keywords)
  └── Stage 5: Topic Categorization & Story Clustering
          │
          ▼
[ Summarization & Synthesis Engine ]
  ├── LLM Provider Abstraction (Gemini 1.5 Flash, OpenAI, Anthropic, Local)
  ├── Real-time Cost Tracker & Token Accounting
  └── Daily Digest Builder (Top Stories, Tech Radar, Community Pulse, Takeaway)
          │
          ▼
[ Delivery & Notification Engine ]
  ├── Telegram Bot API (Markdown Formatting, 4096-char Chunking)
  ├── Discord Webhooks (Rich Embed Cards)
  └── WhatsApp Cloud API (Meta Approved Messaging)
          │
          ▼
[ Integration Layer ]
  ├── Autonomous APScheduler (Default 6:00 AM Cron with Timezone Awareness)
  ├── Model Context Protocol (MCP) Server (12 Tools, 5 Resources, 5 Prompts)
  └── HireCrew Seller API v1 (POST /jobs, GET /jobs/{jobId}, Idempotent WAL DB)
```

---

## 2. Core Modules Description

### 2.1 Ingestion Connectors (`app/ingestion/`)
- **`RssConnector`**: Pulls RSS 1.0, 2.0, and Atom XML feeds. Issues conditional requests using HTTP `If-None-Match` and `If-Modified-Since` headers to prevent redundant downloads when feeds have not changed (`HTTP 304 Not Modified`).
- **`NewsletterConnector`**: Parses raw email streams while enforcing privacy safeguards. Evaluates `List-Unsubscribe`, `Precedence: bulk`, and sender signatures, automatically rejecting personal email correspondence.
- **`RedditConnector`**: Ingests discussions from targeted subreddits (e.g. `r/technology`, `r/machinelearning`) and filters out low-signal submissions below engagement thresholds.
- **`WebArticleConnector`**: Securely extracts public articles with strict SSRF defense (blocking private subnets, cloud metadata IPs, and loopback hosts).

### 2.2 Processing & Deduplication (`app/processing/`)
- **Noise Removal**: Strips sponsored paragraphs, affiliate blocks, subscription pitches, and boilerplate.
- **Canonicalization**: Strips tracking parameters (`utm_*`, `ref`, `fbclid`, `gclid`).
- **Deduplication**: Multi-tier pipeline utilizing canonical URL matching, MD5 hashing, and Jaccard similarity across word shingles ($J \ge 0.60$) to cluster overlapping coverage.
- **Relevance Scoring**: Evaluates topic alignment, keyword bonuses/penalties, source credibility, and exponential recency decay ($t_{1/2} = 24\text{ hours}$).

### 2.3 Summarization & Cost Tracking (`app/summarization/`)
- Abstract provider model supporting Google Gemini 1.5 Flash, OpenAI, Anthropic, or local endpoints.
- Hallucination-free prompt templates enforcing strict traceability to source content.
- Cost accounting recording exact token usage and dollar fractions per execution.

### 2.4 Autonomous Scheduling (`app/scheduler/`)
- Powered by `apscheduler.schedulers.asyncio.AsyncIOScheduler`.
- Default schedule is 6:00 AM every morning with per-user timezone support.
- Backed by atomic SQLite scheduler locks to prevent dual execution across worker processes.

