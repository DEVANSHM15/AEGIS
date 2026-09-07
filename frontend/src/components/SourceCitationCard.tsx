import React from 'react';
import { FileText, FileCode, File, Bookmark } from 'lucide-react';
import { SourceCitation } from '../types';

interface SourceCitationCardProps {
  source: SourceCitation;
  onSelect?: (source: SourceCitation) => void;
}

export const SourceCitationCard: React.FC<SourceCitationCardProps> = ({ source, onSelect }) => {
  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-3.5 h-3.5 text-red-400" />;
    if (ext === 'md') return <FileCode className="w-3.5 h-3.5 text-blue-400" />;
    return <File className="w-3.5 h-3.5 text-amber-400" />;
  };

  return (
    <div
      onClick={() => onSelect && onSelect(source)}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-light border border-surface-border hover:border-brand-500/50 hover:bg-surface-border/40 transition-all text-xs cursor-pointer group"
      title={`Chunk ID: ${source.chunk_id}`}
    >
      {getFileIcon(source.filename)}
      <span className="font-medium text-gray-200 group-hover:text-brand-500 transition-colors">
        {source.filename}
      </span>
      {source.page && (
        <span className="flex items-center gap-1 font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface border border-surface-border text-gray-400">
          <Bookmark className="w-2.5 h-2.5 text-brand-500" />
          p.{source.page}
        </span>
      )}
    </div>
  );
};
