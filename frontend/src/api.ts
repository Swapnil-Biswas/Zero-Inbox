import type { SourceConfig, UserPreferences, Digest, OverviewMetrics } from './types';

const BASE_URL = 'http://127.0.0.1:8010/api/v1';

export async function fetchOverview(): Promise<OverviewMetrics> {
  const res = await fetch(`${BASE_URL}/analytics/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview metrics');
  return res.json();
}

export async function fetchSources(): Promise<SourceConfig[]> {
  const res = await fetch(`${BASE_URL}/sources`);
  if (!res.ok) throw new Error('Failed to fetch sources');
  return res.json();
}

export async function addSource(source: SourceConfig): Promise<SourceConfig> {
  const res = await fetch(`${BASE_URL}/sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(source)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to add source');
  }
  return res.json();
}

export async function deleteSource(sourceId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/sources/${sourceId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete source');
}

export async function fetchPreferences(): Promise<UserPreferences> {
  const res = await fetch(`${BASE_URL}/preferences`);
  if (!res.ok) throw new Error('Failed to fetch preferences');
  return res.json();
}

export async function savePreferences(prefs: UserPreferences): Promise<UserPreferences> {
  const res = await fetch(`${BASE_URL}/preferences`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prefs)
  });
  if (!res.ok) throw new Error('Failed to save preferences');
  return res.json();
}

export async function fetchLatestDigest(): Promise<Digest | null> {
  const res = await fetch(`${BASE_URL}/digest/latest`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error('Failed to fetch latest digest');
  return res.json();
}

export async function generateDigestNow(): Promise<Digest> {
  const res = await fetch(`${BASE_URL}/digest/generate?force=true`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to generate digest');
  return res.json();
}

export async function fetchDigestHistory(): Promise<Digest[]> {
  const res = await fetch(`${BASE_URL}/digest/history`);
  if (!res.ok) throw new Error('Failed to fetch digest history');
  return res.json();
}
