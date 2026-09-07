import pytest
from app.services.chunker import Chunker

def test_chunker_basic_split():
    chunker = Chunker(chunk_size=50, chunk_overlap=10)
    sample_text = "Word " * 200  # Long text
    chunks = chunker.chunk_text(sample_text)
    
    assert len(chunks) > 1
    for chunk in chunks:
        token_count = chunker.count_tokens(chunk)
        assert token_count <= 50

def test_chunker_page_metadata_preservation():
    chunker = Chunker(chunk_size=100, chunk_overlap=20)
    pages = [
        {"document_id": "doc1", "filename": "arch.pdf", "page": 1, "text": "Page 1 content about microservices Architecture."},
        {"document_id": "doc1", "filename": "arch.pdf", "page": 2, "text": "Page 2 content about PostgreSQL database."}
    ]
    
    chunks = chunker.process_extracted_pages(pages)
    
    assert len(chunks) == 2
    assert chunks[0]["page"] == 1
    assert chunks[0]["filename"] == "arch.pdf"
    assert chunks[0]["document_id"] == "doc1"
    assert "chunk_id" in chunks[0]
    
    assert chunks[1]["page"] == 2
    assert chunks[1]["filename"] == "arch.pdf"
