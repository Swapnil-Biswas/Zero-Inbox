import React, { useState } from 'react';
import type { SourceConfig, SourceType } from '../types';
import { addSource, deleteSource } from '../api';
import { Plus, Trash2, Globe, Mail, Rss, MessageSquare, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SourceManagerViewProps {
  sources: SourceConfig[];
  onSourcesUpdated: () => void;
}

export const SourceManagerView: React.FC<SourceManagerViewProps> = ({ sources, onSourcesUpdated }) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [sourceType, setSourceType] = useState<SourceType>('rss');
  const [categoryHint, setCategoryHint] = useState('Technology');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !url) return;

    try {
      setLoading(true);
      setError(null);
      await addSource({
        name,
        url,
        source_type: sourceType,
        status: 'active',
        category_hint: categoryHint
      });
      setName('');
      setUrl('');
      setShowAddModal(false);
      onSourcesUpdated();
    } catch (err: any) {
      setError(err.message || 'Failed to add source');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id?: string) => {
    if (!id) return;
    if (!confirm('Are you sure you want to remove this source?')) return;
    try {
      await deleteSource(id);
      onSourcesUpdated();
    } catch (err: any) {
      alert(err.message || 'Failed to delete source');
    }
  };

  const getTypeIcon = (type: SourceType) => {
    switch (type) {
      case 'rss':
      case 'atom':
        return <Rss className="w-4 h-4 text-orange-400" />;
      case 'newsletter':
        return <Mail className="w-4 h-4 text-purple-400" />;
      case 'reddit':
        return <MessageSquare className="w-4 h-4 text-red-400" />;
      case 'web':
        return <Globe className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white">Monitored Information Feeds</h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure RSS/Atom feeds, email newsletters, Reddit discussions, and web articles.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Source</span>
        </button>
      </div>

      {showAddModal && (
        <form onSubmit={handleAdd} className="p-5 rounded-2xl bg-slate-900 border border-slate-700 shadow-xl space-y-4">
          <h3 className="text-base font-bold text-white">Register New Content Source</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Source Display Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Hacker News Frontpage"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Source Type</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value as SourceType)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="rss">RSS 2.0 / 1.0 Feed</option>
                <option value="atom">Atom Feed</option>
                <option value="newsletter">Newsletter (Forwarding / MIME)</option>
                <option value="reddit">Reddit Subreddit (r/name)</option>
                <option value="web">Public Web Article / Domain</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Feed / Destination URL</label>
            <input
              type="text"
              required
              placeholder="e.g. https://news.ycombinator.com/rss or https://reddit.com/r/technology"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          {error && <p className="text-xs text-red-400">{error}</p>}

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm"
            >
              {loading ? 'Validating...' : 'Save Source'}
            </button>
          </div>
        </form>
      )}

      {/* Sources List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((src) => (
          <div key={src.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex items-start justify-between">
            <div className="space-y-1.5 min-w-0 pr-3">
              <div className="flex items-center space-x-2">
                {getTypeIcon(src.source_type)}
                <h4 className="font-semibold text-sm text-white truncate">{src.name}</h4>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase">
                  {src.source_type}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono truncate">{src.url}</p>
              <div className="flex items-center space-x-3 text-[11px] text-slate-500 pt-1">
                <span className="flex items-center gap-1">
                  {src.error_count && src.error_count > 0 ? (
                    <AlertTriangle className="w-3 h-3 text-amber-400" />
                  ) : (
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  )}
                  {src.status}
                </span>
                {src.last_fetched_at && (
                  <span>Sync: {new Date(src.last_fetched_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                )}
              </div>
            </div>

            <button
              onClick={() => handleDelete(src.id)}
              className="p-2 text-slate-500 hover:text-red-400 transition rounded-lg hover:bg-slate-800/80"
              title="Remove source"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

