export type SourceType = 'rss' | 'atom' | 'newsletter' | 'reddit' | 'web';
export type SourceStatus = 'active' | 'paused' | 'error';
export type DeliveryChannel = 'telegram' | 'discord' | 'whatsapp' | 'none';
export type SummaryLength = 'concise' | 'balanced' | 'detailed';

export interface SourceConfig {
  id?: string;
  user_id?: string;
  name: string;
  url: string;
  source_type: SourceType;
  status: SourceStatus;
  category_hint?: string;
  error_count?: number;
  last_error?: string;
  last_fetched_at?: string;
}

export interface UserPreferences {
  user_id: string;
  topics: string[];
  preferred_sources: string[];
  blocked_sources: string[];
  priority_sources: string[];
  summary_length: SummaryLength;
  max_stories: number;
  preferred_language: string;
  delivery_time_hour: number;
  delivery_time_minute: number;
  timezone: string;
  delivery_channel: DeliveryChannel;
  delivery_destination?: string;
  importance_threshold: number;
  track_keywords: string[];
  exclude_keywords: string[];
}

export interface Digest {
  id: string;
  user_id: string;
  date_str: string;
  title: string;
  content_markdown: string;
  categories: string[];
  total_articles_analyzed: number;
  articles_included: number;
  estimated_read_time_minutes: number;
  cost_usd: number;
  delivery_status: string;
  created_at: string;
}

export interface OverviewMetrics {
  active_sources_count: number;
  total_sources_count: number;
  total_spent_usd: number;
  total_tokens_consumed: number;
  latest_digest_date?: string;
  next_scheduled_execution?: string;
}
