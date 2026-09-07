import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DocumentSidebar } from './components/DocumentSidebar';
import { ChatInterface } from './components/ChatInterface';
import { apiService } from './services/api';
import { HealthStatus, DocumentMetadata, ChatMessage } from './types';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isDocsLoading, setIsDocsLoading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchHealth = async () => {
    try {
      const data = await apiService.getHealth();
      setHealth(data);
    } catch (e) {
      console.error('Failed to fetch health check', e);
    }
  };

  const fetchDocuments = async () => {
    setIsDocsLoading(true);
    try {
      const data = await apiService.getDocuments();
      setDocuments(data.documents);
    } catch (e) {
      console.error('Failed to fetch documents list', e);
    } finally {
      setIsDocsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchDocuments();
  }, []);

  const handleUpload = async (file: File) => {
    setUploadError(null);
    setUploadProgress(0);
    try {
      await apiService.uploadDocument(file, (percent) => {
        setUploadProgress(percent);
      });
      await fetchDocuments();
      await fetchHealth();
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Document upload failed.';
      setUploadError(msg);
    } finally {
      setUploadProgress(null);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await apiService.deleteDocument(documentId);
      await fetchDocuments();
      await fetchHealth();
    } catch (err: any) {
      console.error('Failed to delete document', err);
      alert('Failed to delete document: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSendMessage = async (question: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);

    try {
      const res = await apiService.sendChatMessage(question);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        retrievedChunks: res.retrieved_chunks,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || err.message || 'An error occurred during query execution.';
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `**Error**: ${errorDetail}`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans">
      <Navbar health={health} />
      <div className="flex flex-1 overflow-hidden">
        <DocumentSidebar
          documents={documents}
          isLoading={isDocsLoading}
          onRefresh={fetchDocuments}
          onUpload={handleUpload}
          onDelete={handleDeleteDocument}
          uploadProgress={uploadProgress}
          uploadError={uploadError}
        />
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isChatLoading}
        />
      </div>
    </div>
  );
};

export default App;
