import React, { useState, useEffect } from 'react';
import type { SourceConfig, UserPreferences, Digest, OverviewMetrics } from './types';
import { fetchOverview, fetchSources, fetchPreferences, fetchLatestDigest } from './api';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { SourceManagerView } from './components/SourceManagerView';
import { PreferencesView } from './components/PreferencesView';
import { DeliverySettingsView } from './components/DeliverySettingsView';
import { HistoryView } from './components/HistoryView';
import { MCPConfigView } from './components/MCPConfigView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [overview, setOverview] = useState<OverviewMetrics | null>(null);
  const [sources, setSources] = useState<SourceConfig[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [latestDigest, setLatestDigest] = useState<Digest | null>(null);
  const [statusOnline, setStatusOnline] = useState(true);

  const reloadData = async () => {
    try {
      const [ov, src, pref, dig] = await Promise.allSettled([
        fetchOverview(),
        fetchSources(),
        fetchPreferences(),
        fetchLatestDigest()
      ]);

      if (ov.status === 'fulfilled') setOverview(ov.value);
      if (src.status === 'fulfilled') setSources(src.value);
      if (pref.status === 'fulfilled') setPreferences(pref.value);
      if (dig.status === 'fulfilled') setLatestDigest(dig.value);
      setStatusOnline(true);
    } catch {
      setStatusOnline(false);
    }
  };

  useEffect(() => {
    reloadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} statusOnline={statusOnline} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <DashboardView
            overview={overview}
            latestDigest={latestDigest}
            onDigestGenerated={(d) => {
              setLatestDigest(d);
              reloadData();
            }}
          />
        )}

        {activeTab === 'sources' && (
          <SourceManagerView sources={sources} onSourcesUpdated={reloadData} />
        )}

        {activeTab === 'preferences' && (
          <PreferencesView
            preferences={preferences}
            onPreferencesSaved={(p) => {
              setPreferences(p);
              reloadData();
            }}
          />
        )}

        {activeTab === 'delivery' && (
          <DeliverySettingsView
            preferences={preferences}
            onPreferencesSaved={(p) => {
              setPreferences(p);
              reloadData();
            }}
          />
        )}

        {activeTab === 'history' && <HistoryView />}

        {activeTab === 'mcp' && <MCPConfigView />}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500 font-mono">
        ZERO-INBOX • Autonomous Media Intelligence & Daily Digest Agent • HireCrew & MCP Compatible
      </footer>
    </div>
  );
};

export default App;
