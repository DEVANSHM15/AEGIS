import React, { useRef, useState } from 'react';
import { Upload, FileText, FileCode, File, Search, RefreshCw, AlertCircle, Trash2, Loader2 } from 'lucide-react';
import { DocumentMetadata } from '../types';

interface DocumentSidebarProps {
  documents: DocumentMetadata[];
  isLoading: boolean;
  onRefresh: () => void;
  onUpload: (file: File) => Promise<void>;
  onDelete: (documentId: string) => Promise<void>;
  uploadProgress: number | null;
  uploadError: string | null;
}

export const DocumentSidebar: React.FC<DocumentSidebarProps> = ({
  documents,
  isLoading,
  onRefresh,
  onUpload,
  onDelete,
  uploadProgress,
  uploadError
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await onUpload(file);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    try {
      setDeletingId(docId);
      await onDelete(docId);
    } finally {
      setDeletingId(null);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-4 h-4 text-red-400" />;
    if (ext === 'md') return <FileCode className="w-4 h-4 text-blue-400" />;
    return <File className="w-4 h-4 text-amber-400" />;
  };

  const filteredDocs = documents.filter(d =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <aside className="w-80 border-r border-surface-border bg-surface/50 flex flex-col h-[calc(100vh-4rem)]">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-surface-border flex items-center justify-between">
        <h2 className="font-semibold text-sm text-gray-200 uppercase tracking-wider">
          Knowledge Base ({documents.length})
        </h2>
        <button
          onClick={onRefresh}
          className="p-1.5 rounded-lg hover:bg-surface-light text-gray-400 hover:text-white transition-colors"
          title="Refresh Documents"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-brand-500' : ''}`} />
        </button>
      </div>

      {/* Upload Box */}
      <div className="p-4 border-b border-surface-border">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.txt,.md"
          className="hidden"
        />
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-brand-500 bg-brand-500/10'
              : 'border-surface-border hover:border-brand-500/50 hover:bg-surface-light/40'
          }`}
        >
          <div className="w-9 h-9 rounded-lg bg-surface-light border border-surface-border flex items-center justify-center mx-auto mb-2">
            <Upload className="w-4 h-4 text-brand-500" />
          </div>
          <p className="text-xs font-medium text-gray-200">Upload Document</p>
          <p className="text-[11px] text-gray-500 mt-0.5">PDF, TXT, or Markdown (.md)</p>
        </div>

        {/* Upload Progress Bar */}
        {uploadProgress !== null && (
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-400 mb-1 font-mono">
              <span>Ingesting & Embedding...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-surface-light rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-brand-500 h-full transition-all duration-300 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Upload Error Banner */}
        {uploadError && (
          <div className="mt-3 p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Document Search Filter */}
      <div className="p-3 border-b border-surface-border/60">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search uploaded files..."
            className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-surface-light border border-surface-border text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-brand-500/50"
          />
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredDocs.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-xs">
            {searchTerm ? 'No matching documents found' : 'No documents uploaded yet.'}
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.document_id}
              className="p-3 rounded-xl bg-surface border border-surface-border hover:border-brand-500/30 transition-all group flex items-center justify-between gap-2"
            >
              <div className="flex items-start gap-2.5 min-w-0 flex-1">
                <div className="mt-0.5 shrink-0">{getFileIcon(doc.filename)}</div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xs font-medium text-gray-200 truncate group-hover:text-brand-500 transition-colors" title={doc.filename}>
                    {doc.filename}
                  </h3>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-gray-400 font-mono">
                    <span>{doc.chunk_count} chunks</span>
                    <span>•</span>
                    <span>{doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'}</span>
                  </div>
                </div>
              </div>

              {/* Delete Button */}
              <button
                onClick={(e) => handleDelete(e, doc.document_id)}
                disabled={deletingId === doc.document_id}
                title="Delete document"
                className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 opacity-70 group-hover:opacity-100 transition-all shrink-0"
              >
                {deletingId === doc.document_id ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                ) : (
                  <Trash2 className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};
