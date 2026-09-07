import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.embeddings import BaseEmbeddingProvider

class DummyTestEmbeddingProvider(BaseEmbeddingProvider):
    def embed_documents(self, texts):
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, text):
        return [0.1] * 384

@pytest.fixture(autouse=True)
def mock_embedding_provider():
    with patch("app.api.router.get_embedding_provider", return_value=DummyTestEmbeddingProvider()):
        with patch("app.services.rag.get_embedding_provider", return_value=DummyTestEmbeddingProvider()):
            yield

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "embedding_provider" in data
    assert "llm_provider" in data

def test_list_documents_empty():
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_documents" in data

def test_upload_txt_document_and_chat():
    sample_content = (
        "# Aegis Architecture Specification\n\n"
        "Aegis uses ChromaDB as its embedded vector database for fast similarity retrieval. "
        "The primary backend language is Python 3.11 with FastAPI frameworks."
    )
    
    files = {
        "file": ("architecture_spec.md", sample_content.encode("utf-8"), "text/markdown")
    }

    # Upload document
    upload_res = client.post("/api/documents", files=files)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert upload_data["filename"] == "architecture_spec.md"
    assert upload_data["created_chunks"] > 0

    # Query chat endpoint
    chat_payload = {"question": "What database does Aegis use?"}
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()

    assert "answer" in chat_data
    assert "sources" in chat_data
    assert "retrieved_chunks" in chat_data
    assert len(chat_data["sources"]) > 0
    assert chat_data["sources"][0]["filename"] == "architecture_spec.md"
    assert len(chat_data["retrieved_chunks"]) > 0
    assert "score" in chat_data["retrieved_chunks"][0]

def test_unsupported_file_upload():
    files = {
        "file": ("binary.exe", b"executable_data", "application/octet-stream")
    }
    response = client.post("/api/documents", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
