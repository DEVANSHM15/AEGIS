import React from 'react';
import { HelpCircle, Sparkles, FileText, Database, ShieldCheck } from 'lucide-react';

interface EmptyStateProps {
  onSelectQuestion: (question: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectQuestion }) => {
  const sampleQuestions = [
    {
      icon: <Database className="w-4 h-4 text-teal-400" />,
      title: "Architecture & Data Store",
      question: "What database systems and caching layers are used in the platform architecture?"
    },
    {
      icon: <FileText className="w-4 h-4 text-blue-400" />,
      title: "API & Ingestion Rules",
      question: "What file formats and chunking configurations are supported by the ingestion pipeline?"
    },
    {
      icon: <ShieldCheck className="w-4 h-4 text-brand-500" />,
      title: "Security & Validation",
      question: "How are file upload validation, size limits, and sanitization enforced?"
    }
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-2xl mx-auto text-center">
      <div className="w-16 h-16 rounded-2xl bg-surface-light border border-surface-border flex items-center justify-center mb-6 shadow-xl shadow-brand-500/5">
        <Sparkles className="w-8 h-8 text-brand-500" />
      </div>

      <h2 className="text-xl font-bold text-white mb-2">Aegis Knowledge Assistant</h2>
      <p className="text-sm text-gray-400 mb-8 max-w-md">
        Upload technical documents (PDF, TXT, Markdown) on the left sidebar to perform grounded vector search and grounded Q&A.
      </p>

      <div className="w-full space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
          <HelpCircle className="w-3.5 h-3.5 text-brand-500" />
          <span>Try an example question</span>
        </div>
        {sampleQuestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(item.question)}
            className="w-full p-4 rounded-xl bg-surface border border-surface-border hover:border-brand-500/50 hover:bg-surface-light/60 transition-all text-left group"
          >
            <div className="flex items-center gap-3 mb-1">
              <div className="p-1.5 rounded-lg bg-surface-light border border-surface-border group-hover:border-brand-500/30">
                {item.icon}
              </div>
              <span className="font-semibold text-xs text-gray-300 group-hover:text-brand-500 transition-colors">
                {item.title}
              </span>
            </div>
            <p className="text-sm text-gray-400 group-hover:text-gray-200 transition-colors">
              "{item.question}"
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};
