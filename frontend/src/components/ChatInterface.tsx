import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, User, Bot, Loader2, Sparkles, ShieldAlert } from 'lucide-react';
import { ChatMessage, SourceCitation } from '../types';
import { SourceCitationCard } from './SourceCitationCard';
import { DebugRetrievalView } from './DebugRetrievalView';
import { EmptyState } from './EmptyState';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (question: string) => Promise<void>;
  isLoading: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    const q = input.trim();
    setInput('');
    onSendMessage(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <main className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-background">
      {messages.length === 0 ? (
        <EmptyState onSelectQuestion={(q) => onSendMessage(q)} />
      ) : (
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-4 max-w-4xl mx-auto ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-surface-light border border-surface-border flex items-center justify-center text-brand-500 shrink-0 mt-1 shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-5 border ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white border-brand-500/30 rounded-tr-none shadow-lg shadow-brand-500/10'
                    : msg.isError
                    ? 'bg-red-500/10 text-red-300 border-red-500/30 rounded-tl-none'
                    : 'bg-surface text-gray-200 border-surface-border rounded-tl-none shadow-md'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <div className="space-y-4">
                    <div className="prose prose-invert prose-sm max-w-none text-gray-200 leading-relaxed">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Source Citations Section */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="pt-3 border-t border-surface-border/60">
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-brand-500" />
                          <span>Grounded Sources ({msg.sources.length})</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.sources.map((src, i) => (
                            <SourceCitationCard key={i} source={src} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Retrieval Debug View Toggle Section */}
                    {msg.retrievedChunks && msg.retrievedChunks.length > 0 && (
                      <DebugRetrievalView chunks={msg.retrievedChunks} />
                    )}
                  </div>
                ) : (
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                )}

                <div className={`mt-2 text-[10px] font-mono ${
                  msg.role === 'user' ? 'text-brand-100/70 text-right' : 'text-gray-400'
                }`}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-brand-500 flex items-center justify-center text-background shrink-0 mt-1 shadow-md">
                  <User className="w-4 h-4 font-bold" />
                </div>
              )}
            </div>
          ))}

          {/* Assistant Thinking Indicator */}
          {isLoading && (
            <div className="flex items-start gap-4 max-w-4xl mx-auto">
              <div className="w-8 h-8 rounded-xl bg-surface-light border border-surface-border flex items-center justify-center text-brand-500 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl rounded-tl-none bg-surface border border-surface-border flex items-center gap-3 text-sm text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin text-brand-500" />
                <span>Searching vector database & generating answer...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-surface-border bg-surface/50">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a technical question about uploaded documents... (Shift+Enter for new line)"
            className="w-full pl-4 pr-14 py-3.5 rounded-xl bg-surface-light border border-surface-border text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-brand-500/50 resize-none max-h-32"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2.5 p-2 rounded-lg bg-brand-500 text-background hover:bg-brand-600 disabled:opacity-30 disabled:hover:bg-brand-500 transition-all shadow-md shadow-brand-500/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </main>
  );
};
