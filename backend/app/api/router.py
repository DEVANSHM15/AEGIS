import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.api.schemas import (
    HealthResponse,
    DocumentListResponse,
    UploadDocumentResponse,
    ChatRequest,
    ChatResponse
)
from app.core.config import settings
from app.core.logging import logger
from app.services.document_processor import DocumentProcessor
from app.services.chunker import Chunker
from app.services.embeddings import get_embedding_provider
from app.services.vector_store import VectorStore
from app.services.rag import RAGPipeline

router = APIRouter()

# Global Singleton instances
vector_store = VectorStore()
chunker = Chunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)

@router.get("/health", response_model=HealthResponse)
def get_health():
    count = vector_store.collection.count()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        embedding_provider=settings.EMBEDDING_PROVIDER,
        llm_provider=settings.LLM_PROVIDER,
        vector_db_chunks=count
    )

@router.post("/api/documents", response_model=UploadDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided in upload request.")

    logger.info(f"Received file upload request: '{file.filename}'")

    try:
        content_bytes = await file.read()
        doc_id = str(uuid.uuid4())
        
        # 1. Extract text pages
        pages = DocumentProcessor.extract_text(
            filename=file.filename,
            content_bytes=content_bytes,
            document_id=doc_id
        )

        # 2. Token-aware chunking
        chunks = chunker.process_extracted_pages(pages)

        # 3. Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embedding_provider = get_embedding_provider()
        embeddings = embedding_provider.embed_documents(chunk_texts)

        # 4. Store in ChromaDB
        vector_store.add_chunks(chunks, embeddings)

        return UploadDocumentResponse(
            document_id=doc_id,
            filename=file.filename,
            extracted_pages=len(pages),
            created_chunks=len(chunks),
            message=f"Successfully ingested '{file.filename}' ({len(chunks)} chunks created)."
        )

    except ValueError as ve:
        logger.warning(f"Validation error processing '{file.filename}': {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error ingesting file '{file.filename}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/api/documents", response_model=DocumentListResponse)
def list_documents():
    try:
        docs = vector_store.list_documents()
        return DocumentListResponse(
            documents=docs,
            total_documents=len(docs)
        )
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.delete("/api/documents/{document_id}")
def delete_document(document_id: str):
    logger.info(f"Received request to delete document_id: '{document_id}'")
    try:
        vector_store.delete_document(document_id)
        return {"status": "ok", "message": f"Document '{document_id}' successfully deleted."}
    except Exception as e:
        logger.error(f"Error deleting document '{document_id}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.delete("/api/documents")
def clear_all_documents():
    logger.info("Received request to clear all documents in vector store")
    try:
        vector_store.clear()
        return {"status": "ok", "message": "All documents successfully deleted."}
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear documents: {str(e)}")

@router.post("/api/chat", response_model=ChatResponse)
def chat_query(body: ChatRequest):
    logger.info(f"Chat question endpoint called: '{body.question}'")
    try:
        pipeline = RAGPipeline(vector_store=vector_store)
        result = pipeline.query(question=body.question)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieved_chunks=result["retrieved_chunks"]
        )
    except ValueError as ve:
        logger.warning(f"Configuration or validation error in RAG pipeline: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG execution error: {str(e)}")
