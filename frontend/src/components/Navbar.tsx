import React from 'react';
import { Shield, Database, Cpu, Activity } from 'lucide-react';
import { HealthStatus } from '../types';

interface NavbarProps {
  health: HealthStatus | null;
}

export const Navbar: React.FC<NavbarProps> = ({ health }) => {
  return (
    <header className="h-16 border-b border-surface-border bg-surface/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-500 to-teal-400 p-[1px] shadow-lg shadow-brand-500/20">
          <div className="w-full h-full bg-background rounded-[11px] flex items-center justify-center">
            <Shield className="w-5 h-5 text-brand-500" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold text-lg tracking-wider text-white">AEGIS</h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-500 border border-brand-500/20">
              Phase 1 RAG
            </span>
          </div>
          <p className="text-xs text-gray-400">AI Engineering Knowledge & Incident Intelligence Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs font-mono">
        {health ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-light border border-surface-border text-gray-300">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              <span>Embed: <strong className="text-white">{health.embedding_provider}</strong></span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-light border border-surface-border text-gray-300">
              <Activity className="w-3.5 h-3.5 text-brand-500" />
              <span>LLM: <strong className="text-white">{health.llm_provider}</strong></span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-500">
              <Database className="w-3.5 h-3.5" />
              <span>{health.vector_db_chunks} Chunks</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-gray-500">
            <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span>Connecting to Aegis Engine...</span>
          </div>
        )}
      </div>
    </header>
  );
};
