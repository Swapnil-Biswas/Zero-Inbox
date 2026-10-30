# ZERO-INBOX: Cost Optimization & Token Accounting

Operating autonomous media agents can become costly if full web articles are processed blindly. ZERO-INBOX applies rigorous cost-control strategies to keep daily operations under fractions of a cent.

---

## 1. Multi-Stage Cost Optimization Funnel

```
[ Ingested Articles (e.g. 150 items) ]
                  │
                  ▼
   1. Conditional HTTP 304 Caching  ──> Eliminates unchanged feeds (Zero download bandwidth)
                  │
                  ▼
   2. Deduplication & Canonical URLs ──> Discards 40-60% of redundant stories before LLM
                  │
                  ▼
   3. Noise & Ad Stripping         ──> Strips 20-35% of token volume from article bodies
                  │
                  ▼
   4. Multidimensional Relevance   ──> Selects only top N high-signal stories (e.g. top 10)
                  │
                  ▼
[ LLM Summarization Batch (Only 10 articles) ]
```

---

## 2. Supported Provider Pricing Table

| Model Provider | Model ID | Prompt Cost / 1M Tokens | Completion Cost / 1M Tokens | Typical Cost per Daily Brief |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | `gemini-1.5-flash` | $0.075 | $0.300 | **$0.001 - $0.003** |
| **OpenAI** | `gpt-4o-mini` | $0.150 | $0.600 | **$0.003 - $0.006** |
| **Anthropic** | `claude-3-5-haiku` | $0.800 | $4.000 | **$0.015 - $0.030** |
| **Local Fallback** | `llama3.2 / heuristic`| $0.000 | $0.000 | **$0.000 (Free)** |

---

## 3. Real-Time Token Ledger

Every execution logs prompt tokens, completion tokens, model names, and total USD costs into the `cost_records` database table. The live cost metrics can be queried via:
- REST API: `GET /api/v1/analytics/costs`
- MCP Tool: `get_agent_status`
- Web Dashboard: Cost Analytics Card
