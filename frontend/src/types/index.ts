export interface DocumentMetadata {
  document_id: string;
  filename: string;
  chunk_count: number;
  total_pages: number;
}

export interface DocumentListResponse {
  documents: DocumentMetadata[];
  total_documents: number;
}

export interface UploadDocumentResponse {
  document_id: string;
  filename: string;
  extracted_pages: number;
  created_chunks: number;
  message: string;
}

export interface SourceCitation {
  filename: string;
  page?: number | null;
  chunk_id: string;
}

export interface RetrievedChunkDebug {
  chunk_id: string;
  filename: string;
  page?: number | null;
  score: number;
  text: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  retrieved_chunks: RetrievedChunkDebug[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  retrievedChunks?: RetrievedChunkDebug[];
  timestamp: Date;
  isError?: boolean;
}

export interface HealthStatus {
  status: string;
  version: string;
  embedding_provider: string;
  llm_provider: string;
  vector_db_chunks: number;
}
