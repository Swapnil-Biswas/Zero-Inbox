# Changelog

All notable changes to PROJECT ZERO-INBOX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-31

### Added
- **Source Ingestion Engine**:
  - RSS 1.0, 2.0, and Atom connectors with conditional HTTP `ETag` and `Last-Modified` caching.
  - Newsletter ingestion adapter with MIME RFC822 parser and privacy-protecting bulk mail detection.
  - Reddit community discussion connector with score and comment signal filters.
  - Public web article extractor with strict SSRF defense.
- **Intelligent Processing Pipeline**:
  - Canonical URL standardization and tracking parameter stripping.
  - Noise, ad, and sponsorship excising engine.
  - Multi-tier deduplication via exact URL, MD5 hashing, and Jaccard 3-gram shingles.
  - Multidimensional relevance scoring (topics, keywords, recency, source credibility).
  - Topic clustering and classification across 7 primary intelligence sectors.
- **Summarization & Cost Ledger**:
  - LLM provider abstraction for Google Gemini, OpenAI, Anthropic, and local endpoints.
  - Hallucination-free synthesis prompt templates.
  - Token counting and real-time USD cost calculation.
- **Autonomous Scheduling Engine**:
  - APScheduler-backed timezone-aware cron engine (default 6:00 AM).
  - Distributed SQLite locking preventing duplicate daily deliveries.
- **Delivery Channels**:
  - Telegram Bot API integration with automatic chunking.
  - Discord Webhooks with rich embed cards.
  - Meta WhatsApp Business Cloud API integration.
- **Model Context Protocol (MCP)**:
  - Official Python MCP SDK (`mcp` v2.3.0) implementation (`zero-inbox-mcp`).
  - 12 MCP tools, 5 read-only resources, and 5 prompts.
  - Local STDIO runner and remote Streamable HTTP / SSE transport (`/mcp`).
- **HireCrew Marketplace Integration**:
  - Full adherence to `seller-hosted-api-v1` (`POST /jobs`, `GET /jobs/{jobId}`).
  - Validated against private seller-local builder kit with 100% pass across all 5 benchmark cases (`research-v1`).
- **Frontend Dashboard**:
  - React 19, TypeScript, and Tailwind CSS web dashboard.
  - Views for Intelligence Radar, Source Manager, Topic Preferences, Delivery Settings, History Archive, and MCP / HireCrew settings.

