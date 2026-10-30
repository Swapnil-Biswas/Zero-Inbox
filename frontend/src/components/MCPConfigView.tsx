import React from 'react';
import { Cpu, Terminal, CheckCircle2, Shield, ExternalLink, Code } from 'lucide-react';

export const MCPConfigView: React.FC = () => {
  const mcpConfigCode = JSON.stringify({
    mcpServers: {
      "zero-inbox": {
        command: "python",
        args: [
          "<PATH_TO_ZERO_INBOX>/backend/run_mcp_stdio.py"
        ],
        env: {
          PYTHONUNBUFFERED: "1",
          ZERO_INBOX_ENV: "development"
        }
      }
    }
  }, null, 2);

  const tools = [
    { name: "create_digest", desc: "Generate an on-demand personalized media intelligence brief." },
    { name: "get_latest_digest", desc: "Retrieve the most recently generated intelligence brief." },
    { name: "add_source", desc: "Register an RSS, newsletter, Reddit, or web source." },
    { name: "remove_source", desc: "Remove a monitored information source with verification." },
    { name: "list_sources", desc: "List all active feeds and operational sync status." },
    { name: "update_preferences", desc: "Configure topic weights, delivery channels, and schedules." },
    { name: "search_articles", desc: "Full-text search across previously ingested news articles." },
    { name: "get_article_summary", desc: "Retrieve detailed summary, takeaways, and significance." },
    { name: "get_topic_trends", desc: "Analyze category frequency distributions across sources." },
    { name: "get_digest_history", desc: "Retrieve historical intelligence briefs." },
    { name: "send_test_notification", desc: "Send verification pings to Telegram, Discord, or WhatsApp." },
    { name: "get_agent_status", desc: "Return operational health, cron status, and cost metrics." }
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b border-slate-800">
        <h2 className="text-xl font-bold text-white">Model Context Protocol (MCP) & HireCrew Marketplace</h2>
        <p className="text-xs text-slate-400 mt-1">
          ZERO-INBOX exposes an official MCP server (SDK v2.3.0) and implements the HireCrew seller-hosted API v1 contract.
        </p>
      </div>

      {/* HireCrew Marketplace Status Card */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/30 via-slate-900 to-slate-900 border border-emerald-500/30 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white">HireCrew Seller Marketplace Ready</h3>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono font-bold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> 5/5 Benchmark Pass
          </span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The seller adapter implements <code className="bg-slate-800 px-1.5 py-0.5 rounded text-emerald-300 font-mono">POST /jobs</code> and <code className="bg-slate-800 px-1.5 py-0.5 rounded text-emerald-300 font-mono">GET /jobs/&#123;jobId&#125;</code> with Bearer authentication and idempotent state persistence. All 5 frozen research-v1 benchmarks have achieved <span className="text-emerald-400 font-semibold">STRUCTURAL PASS</span> against the local builder kit.
        </p>
        <div className="flex items-center space-x-4 pt-1 text-xs">
          <a
            href="https://hirecrew.si/developers"
            target="_blank"
            rel="noreferrer"
            className="text-emerald-400 hover:text-emerald-300 underline flex items-center gap-1"
          >
            HireCrew Developer Docs <ExternalLink className="w-3 h-3" />
          </a>
          <span className="text-slate-600">•</span>
          <span className="text-slate-400">Endpoint: <span className="font-mono text-slate-300">/jobs</span></span>
        </div>
      </div>

      {/* MCP Client Setup */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Claude Desktop / Cursor MCP Configuration</h3>
        </div>
        <p className="text-xs text-slate-400">
          Add the following block to your <code className="text-slate-300 font-mono">claude_desktop_config.json</code> or Cursor MCP settings to allow external agents to invoke ZERO-INBOX:
        </p>
        <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 overflow-x-auto">
          {mcpConfigCode}
        </pre>
      </div>

      {/* 12 MCP Tools */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
        <div className="flex items-center space-x-2">
          <Code className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Exposed MCP Tools (12 Tools)</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          {tools.map((t) => (
            <div key={t.name} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
              <span className="text-xs font-mono font-bold text-emerald-400">{t.name}</span>
              <p className="text-xs text-slate-400 mt-0.5">{t.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

