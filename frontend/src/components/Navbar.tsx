import React from 'react';
import { Newspaper, Rss, Sliders, Send, History, Cpu, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  statusOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, statusOnline }) => {
  const navItems = [
    { id: 'dashboard', label: 'Intelligence Radar', icon: Newspaper },
    { id: 'sources', label: 'Source Manager', icon: Rss },
    { id: 'preferences', label: 'Topics & Filtering', icon: Sliders },
    { id: 'delivery', label: 'Delivery Channels', icon: Send },
    { id: 'history', label: 'Digest History', icon: History },
    { id: 'mcp', label: 'MCP & Market', icon: Cpu },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-black font-black text-xl shadow-lg shadow-emerald-500/20">
              0
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-300">
                  ZERO-INBOX
                </span>
                <span className="text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5" /> AUTONOMOUS
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">Personal Media Intelligence Agent</p>
            </div>
          </div>

          <nav className="flex items-center space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className={`w-2 h-2 rounded-full ${statusOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="text-slate-300 font-mono hidden sm:inline">{statusOnline ? '6:00 AM Cron Ready' : 'Connecting'}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

