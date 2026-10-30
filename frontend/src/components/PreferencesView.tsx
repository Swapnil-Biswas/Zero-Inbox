import React, { useState } from 'react';
import type { UserPreferences, SummaryLength } from '../types';
import { savePreferences } from '../api';
import { Sliders, Save, Check, Tag, ShieldCheck } from 'lucide-react';

interface PreferencesViewProps {
  preferences: UserPreferences | null;
  onPreferencesSaved: (prefs: UserPreferences) => void;
}

const AVAILABLE_TOPICS = [
  'Artificial Intelligence', 'Technology', 'Startups', 'Programming',
  'Cybersecurity', 'Science', 'Research', 'Communities', 'Crypto & Web3', 'Biotech'
];

export const PreferencesView: React.FC<PreferencesViewProps> = ({ preferences, onPreferencesSaved }) => {
  const [topics, setTopics] = useState<string[]>(preferences?.topics || ['Artificial Intelligence', 'Technology']);
  const [summaryLength, setSummaryLength] = useState<SummaryLength>(preferences?.summary_length || 'balanced');
  const [maxStories, setMaxStories] = useState<number>(preferences?.max_stories || 10);
  const [trackKeywords, setTrackKeywords] = useState<string>(preferences?.track_keywords?.join(', ') || '');
  const [excludeKeywords, setExcludeKeywords] = useState<string>(preferences?.exclude_keywords?.join(', ') || '');
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleTopic = (topic: string) => {
    if (topics.includes(topic)) {
      setTopics(topics.filter(t => t !== topic));
    } else {
      setTopics([...topics, topic]);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!preferences) return;

    try {
      setLoading(true);
      const updated: UserPreferences = {
        ...preferences,
        topics,
        summary_length: summaryLength,
        max_stories: maxStories,
        track_keywords: trackKeywords.split(',').map(k => k.trim()).filter(Boolean),
        exclude_keywords: excludeKeywords.split(',').map(k => k.trim()).filter(Boolean),
      };
      const res = await savePreferences(updated);
      onPreferencesSaved(res);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err: any) {
      alert(err.message || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b border-slate-800">
        <h2 className="text-xl font-bold text-white">Personalization & Topic Preferences</h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure what information ZERO-INBOX prioritizes and filters out during daily intelligence synthesis.
        </p>
      </div>

      {/* Topics */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <label className="block text-sm font-semibold text-white flex items-center gap-2">
          <Tag className="w-4 h-4 text-emerald-400" />
          Topics of Interest
        </label>
        <p className="text-xs text-slate-400">Click topics to include or exclude them from your daily radar:</p>
        <div className="flex flex-wrap gap-2 pt-1">
          {AVAILABLE_TOPICS.map((topic) => {
            const isSelected = topics.includes(topic);
            return (
              <button
                type="button"
                key={topic}
                onClick={() => toggleTopic(topic)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                  isSelected
                    ? 'bg-emerald-500 text-slate-950 font-bold shadow-sm shadow-emerald-500/20'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {topic}
              </button>
            );
          })}
        </div>
      </div>

      {/* Synthesis Depth & Max Stories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <label className="block text-sm font-semibold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-400" />
            Summary Depth
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(['concise', 'balanced', 'detailed'] as SummaryLength[]).map((len) => (
              <button
                type="button"
                key={len}
                onClick={() => setSummaryLength(len)}
                className={`py-2 rounded-xl text-xs font-semibold capitalize transition ${
                  summaryLength === len
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {len}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-500">
            {summaryLength === 'concise' && '1-2 sentence quick updates.'}
            {summaryLength === 'balanced' && 'Executive overview with bulleted takeaways and significance.'}
            {summaryLength === 'detailed' && 'Deep forensic briefing with comprehensive context and metrics.'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex justify-between items-center">
            <label className="text-sm font-semibold text-white">Maximum Stories per Brief</label>
            <span className="font-mono text-emerald-400 text-sm font-bold">{maxStories}</span>
          </div>
          <input
            type="range"
            min={3}
            max={25}
            value={maxStories}
            onChange={(e) => setMaxStories(Number(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
          <p className="text-[11px] text-slate-500">Limits length to prevent information overload.</p>
        </div>
      </div>

      {/* Custom Keyword Filters */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div>
          <label className="block text-xs font-mono text-emerald-400 mb-1">Priority Keywords to Track (+0.25 Score Bonus)</label>
          <input
            type="text"
            placeholder="e.g. Anthropic, Mamba, DeepSeek, Quantum, Rust"
            value={trackKeywords}
            onChange={(e) => setTrackKeywords(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500"
          />
          <p className="text-[11px] text-slate-500 mt-1">Comma-separated terms that elevate story priority.</p>
        </div>

        <div>
          <label className="block text-xs font-mono text-red-400 mb-1">Negative Keywords to Exclude (-0.50 Penalty)</label>
          <input
            type="text"
            placeholder="e.g. Rumor, Celebrity, Gossip, Sponsored"
            value={excludeKeywords}
            onChange={(e) => setExcludeKeywords(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-red-500"
          />
          <p className="text-[11px] text-slate-500 mt-1">Comma-separated terms that suppress or penalize stories.</p>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-3">
        {saved && (
          <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold">
            <Check className="w-4 h-4" /> Preferences Saved
          </span>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/20 flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>{loading ? 'Saving...' : 'Save Preferences'}</span>
        </button>
      </div>
    </form>
  );
};
