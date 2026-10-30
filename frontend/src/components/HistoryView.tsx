import React, { useState, useEffect } from 'react';
import type { Digest } from '../types';
import { fetchDigestHistory } from '../api';
import { History, FileText, CheckCircle2, ChevronRight } from 'lucide-react';

export const HistoryView: React.FC = () => {
  const [history, setHistory] = useState<Digest[]>([]);
  const [selectedDigest, setSelectedDigest] = useState<Digest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDigestHistory()
      .then((data) => {
        setHistory(data);
        if (data.length > 0) setSelectedDigest(data[0]);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h2 className="text-xl font-bold text-white">Digest Archive & History</h2>
        <p className="text-xs text-slate-400 mt-1">
          Review previously synthesized daily media briefs and audit operational logs.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Digest List */}
        <div className="space-y-2">
          {history.length === 0 && !loading && (
            <p className="text-xs text-slate-500 py-6 text-center">No historical digests stored yet.</p>
          )}

          {history.map((d) => {
            const isSelected = selectedDigest?.id === d.id;
            return (
              <button
                key={d.id}
                onClick={() => setSelectedDigest(d)}
                className={`w-full text-left p-4 rounded-xl border transition flex items-center justify-between ${
                  isSelected
                    ? 'bg-slate-900 border-emerald-500/50 shadow-md'
                    : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1 min-w-0 pr-2">
                  <h4 className="text-sm font-semibold text-white truncate">{d.title}</h4>
                  <p className="text-xs text-slate-400 font-mono">{d.date_str}</p>
                  <div className="flex items-center space-x-2 text-[10px] text-slate-500">
                    <span>{d.articles_included} stories</span>
                    <span>•</span>
                    <span>~{d.estimated_read_time_minutes} min read</span>
                    <span>•</span>
                    <span className="text-emerald-400">${d.cost_usd.toFixed(4)}</span>
                  </div>
                </div>
                <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-emerald-400' : 'text-slate-600'}`} />
              </button>
            );
          })}
        </div>

        {/* Selected Digest Detail */}
        <div className="lg:col-span-2">
          {selectedDigest ? (
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedDigest.title}</h3>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{selectedDigest.date_str}</p>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 font-mono">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Delivered
                </span>
              </div>

              <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed bg-slate-950/60 p-6 rounded-xl border border-slate-800/60 font-sans whitespace-pre-wrap">
                {selectedDigest.content_markdown}
              </div>
            </div>
          ) : (
            <div className="p-12 text-center rounded-2xl border border-slate-800 bg-slate-900/20 text-slate-500">
              <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-xs">Select a digest from the archive to inspect its contents.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
