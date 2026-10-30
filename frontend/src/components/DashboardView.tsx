import React, { useState } from 'react';
import type { Digest, OverviewMetrics } from '../types';
import { generateDigestNow } from '../api';
import { Clock, DollarSign, Rss, Layers, Play, CheckCircle2, AlertCircle, FileText } from 'lucide-react';

interface DashboardViewProps {
  overview: OverviewMetrics | null;
  latestDigest: Digest | null;
  onDigestGenerated: (digest: Digest) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ overview, latestDigest, onDigestGenerated }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await generateDigestNow();
      onDigestGenerated(res);
    } catch (err: any) {
      setError(err.message || 'Failed to synthesize daily digest');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-slate-400">Monitored Sources</p>
            <h3 className="text-2xl font-bold text-white mt-1">{overview?.active_sources_count ?? 0} Active</h3>
            <p className="text-xs text-slate-500 mt-1">RSS, Newsletters, Reddit & Web</p>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/20">
            <Rss className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-slate-400">Next Scheduled Brief</p>
            <h3 className="text-2xl font-bold text-white mt-1">06:00 AM</h3>
            <p className="text-xs text-slate-500 mt-1">Autonomous Timezone Cron</p>
          </div>
          <div className="p-3 bg-teal-500/10 rounded-xl text-teal-400 border border-teal-500/20">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-slate-400">Daily Execution Cost</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">
              ${(overview?.total_spent_usd ?? 0.0).toFixed(4)}
            </h3>
            <p className="text-xs text-slate-500 mt-1">{overview?.total_tokens_consumed ?? 0} tokens logged</p>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/20">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-slate-400">Latest Delivery</p>
            <h3 className="text-2xl font-bold text-white mt-1">
              {latestDigest ? `${latestDigest.articles_included} Stories` : 'Ready'}
            </h3>
            <p className="text-xs text-slate-500 mt-1">{latestDigest?.date_str || 'Awaiting scheduled run'}</p>
          </div>
          <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 border border-blue-500/20">
            <Layers className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Control Bar */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white">Daily Intelligence Brief Generation</h2>
          <p className="text-xs text-slate-400">
            ZERO-INBOX executes unattended every morning at 6:00 AM. You can also trigger an immediate on-demand synthesis.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/20 flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Filtering & Synthesizing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Synthesize On-Demand Brief</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Digest Viewer */}
      {latestDigest ? (
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 shadow-md space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
            <div>
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-white">{latestDigest.title}</h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Analyzed {latestDigest.total_articles_analyzed} articles • Included {latestDigest.articles_included} key developments • Read time: ~{latestDigest.estimated_read_time_minutes} min
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Delivered
              </span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-mono">
                ${latestDigest.cost_usd.toFixed(4)} USD
              </span>
            </div>
          </div>

          <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed bg-slate-950/60 p-6 rounded-xl border border-slate-800/60 font-sans whitespace-pre-wrap selection:bg-emerald-500 selection:text-black">
            {latestDigest.content_markdown}
          </div>
        </div>
      ) : (
        <div className="text-center py-16 px-4 rounded-2xl border border-dashed border-slate-800 bg-slate-900/20">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No Intelligence Brief Generated Yet</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
            Click 'Synthesize On-Demand Brief' above or add content sources in the Source Manager to receive your first automated morning briefing.
          </p>
        </div>
      )}
    </div>
  );
};

