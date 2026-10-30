-- ZERO-INBOX Relational Schema

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'rss',
    status TEXT NOT NULL DEFAULT 'active',
    category_hint TEXT,
    etag TEXT,
    last_modified TEXT,
    last_fetched_at TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    url TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    title TEXT NOT NULL,
    clean_text TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT DEFAULT 'Technology',
    relevance_score REAL DEFAULT 0.5,
    novelty_score REAL DEFAULT 1.0,
    is_duplicate INTEGER DEFAULT 0,
    duplicate_of_id TEXT,
    headline TEXT,
    summary TEXT,
    key_takeaways_json TEXT DEFAULT '[]',
    why_it_matters TEXT,
    FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(canonical_url);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT PRIMARY KEY,
    topics_json TEXT DEFAULT '["Artificial Intelligence", "Technology", "Startups", "Programming", "Science", "Cybersecurity"]',
    preferred_sources_json TEXT DEFAULT '[]',
    blocked_sources_json TEXT DEFAULT '[]',
    priority_sources_json TEXT DEFAULT '[]',
    summary_length TEXT DEFAULT 'balanced',
    max_stories INTEGER DEFAULT 10,
    preferred_language TEXT DEFAULT 'en',
    delivery_time_hour INTEGER DEFAULT 6,
    delivery_time_minute INTEGER DEFAULT 0,
    timezone TEXT DEFAULT 'UTC',
    delivery_channel TEXT DEFAULT 'none',
    delivery_destination TEXT,
    importance_threshold REAL DEFAULT 0.4,
    track_keywords_json TEXT DEFAULT '[]',
    exclude_keywords_json TEXT DEFAULT '[]',
    feedback_weights_json TEXT DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS digests (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date_str TEXT NOT NULL,
    title TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    categories_json TEXT DEFAULT '[]',
    total_articles_analyzed INTEGER DEFAULT 0,
    articles_included INTEGER DEFAULT 0,
    estimated_read_time_minutes INTEGER DEFAULT 5,
    cost_usd REAL DEFAULT 0.0,
    delivery_status TEXT DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_digests_user_date ON digests(user_id, date_str);

CREATE TABLE IF NOT EXISTS delivery_logs (
    id TEXT PRIMARY KEY,
    digest_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    destination TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(digest_id) REFERENCES digests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cost_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    digest_id TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_cost_usd REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scheduler_locks (
    lock_name TEXT PRIMARY KEY,
    locked_by TEXT NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
