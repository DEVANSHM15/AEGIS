import axios from 'axios';
import { HealthStatus, DocumentListResponse, UploadDocumentResponse, ChatResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  async getHealth(): Promise<HealthStatus> {
    const res = await client.get<HealthStatus>('/health');
    return res.data;
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await client.get<DocumentListResponse>('/api/documents');
    return res.data;
  },

  async uploadDocument(file: File, onProgress?: (percent: number) => void): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await client.post<UploadDocumentResponse>('/api/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });
    return res.data;
  },

  async deleteDocument(documentId: string): Promise<{ status: string; message: string }> {
    const res = await client.delete<{ status: string; message: string }>(`/api/documents/${documentId}`);
    return res.data;
  },

  async clearAllDocuments(): Promise<{ status: string; message: string }> {
    const res = await client.delete<{ status: string; message: string }>('/api/documents');
    return res.data;
  },

  async sendChatMessage(question: string): Promise<ChatResponse> {
    const res = await client.post<ChatResponse>('/api/chat', { question });
    return res.data;
  },
};
