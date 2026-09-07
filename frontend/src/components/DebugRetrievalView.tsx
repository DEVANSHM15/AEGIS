import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Terminal, BarChart2 } from 'lucide-react';
import { RetrievedChunkDebug } from '../types';

interface DebugRetrievalViewProps {
  chunks: RetrievedChunkDebug[];
}

export const DebugRetrievalView: React.FC<DebugRetrievalViewProps> = ({ chunks }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!chunks || chunks.length === 0) return null;

  return (
    <div className="mt-3 border border-surface-border/60 rounded-xl bg-surface/40 overflow-hidden font-mono text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2.5 flex items-center justify-between bg-surface-light/50 hover:bg-surface-light text-gray-300 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-brand-500" />
          <span className="font-semibold text-gray-200">Show Retrieval Details</span>
          <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-500 text-[10px]">
            {chunks.length} Top-K Chunks
          </span>
        </div>
        <div className="flex items-center gap-1 text-gray-400">
          <span className="text-[11px]">{isOpen ? 'Hide' : 'Inspect'}</span>
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 space-y-3 bg-background/60 divide-y divide-surface-border/40">
          {chunks.map((chunk, idx) => (
            <div key={chunk.chunk_id} className={idx > 0 ? 'pt-3' : ''}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-brand-500">#{idx + 1}</span>
                  <span className="text-white font-medium">{chunk.filename}</span>
                  {chunk.page && (
                    <span className="text-gray-400 text-[11px]">(Page {chunk.page})</span>
                  )}
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[11px]">
                  <BarChart2 className="w-3 h-3" />
                  <span>Score: {chunk.score.toFixed(4)}</span>
                </div>
              </div>
              <div className="text-[10px] text-gray-500 mb-1">
                Chunk ID: <span className="text-gray-400">{chunk.chunk_id}</span>
              </div>
              <pre className="p-2.5 rounded bg-surface-light border border-surface-border text-gray-300 whitespace-pre-wrap text-[11px] leading-relaxed max-h-40 overflow-y-auto">
                {chunk.text}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
