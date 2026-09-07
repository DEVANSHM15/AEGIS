from pydantic import BaseModel, Field
from typing import List, Optional

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    embedding_provider: str
    llm_provider: str
    vector_db_chunks: int

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    total_pages: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_documents: int

class UploadDocumentResponse(BaseModel):
    document_id: str
    filename: str
    extracted_pages: int
    created_chunks: int
    message: str

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to answer via RAG")

class SourceCitation(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_id: str

class RetrievedChunkDebug(BaseModel):
    chunk_id: str
    filename: str
    page: Optional[int] = None
    score: float
    text: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    retrieved_chunks: List[RetrievedChunkDebug]
