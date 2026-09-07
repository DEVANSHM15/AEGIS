import pytest
import os
import shutil
from app.services.vector_store import VectorStore

@pytest.fixture
def temp_vector_store(tmp_path):
    db_path = str(tmp_path / "test_chroma")
    vs = VectorStore(db_path=db_path, collection_name="test_collection")
    yield vs
    vs.clear()
    if os.path.exists(db_path):
        shutil.rmtree(db_path, ignore_errors=True)

def test_vector_store_add_and_search(temp_vector_store):
    chunks = [
        {
            "chunk_id": "chunk_1",
            "document_id": "doc_1",
            "filename": "database.md",
            "page": None,
            "text": "Aegis platform utilizes PostgreSQL database for metadata storage."
        },
        {
            "chunk_id": "chunk_2",
            "document_id": "doc_1",
            "filename": "database.md",
            "page": None,
            "text": "Redis is used for caching session state and rate limiting."
        }
    ]
    # Simple 3D dummy vector embeddings for testing
    embeddings = [
        [0.1, 0.2, 0.9],
        [0.8, 0.1, 0.1]
    ]

    temp_vector_store.add_chunks(chunks, embeddings)

    # Query close to chunk_1 vector
    query_vector = [0.1, 0.2, 0.85]
    results = temp_vector_store.search(query_vector, top_k=2)

    assert len(results) == 2
    top_result = results[0]
    assert top_result["chunk_id"] == "chunk_1"
    assert top_result["filename"] == "database.md"
    assert "PostgreSQL" in top_result["text"]
    assert "score" in top_result
    assert top_result["score"] > 0.8

def test_vector_store_list_documents(temp_vector_store):
    chunks = [
        {
            "chunk_id": "c1",
            "document_id": "doc_A",
            "filename": "api_spec.pdf",
            "page": 1,
            "text": "API section 1"
        },
        {
            "chunk_id": "c2",
            "document_id": "doc_A",
            "filename": "api_spec.pdf",
            "page": 2,
            "text": "API section 2"
        }
    ]
    embeddings = [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]]
    temp_vector_store.add_chunks(chunks, embeddings)

    docs = temp_vector_store.list_documents()
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc_A"
    assert docs[0]["filename"] == "api_spec.pdf"
    assert docs[0]["chunk_count"] == 2

def test_vector_store_delete_document(temp_vector_store):
    chunks = [
        {
            "chunk_id": "c1",
            "document_id": "doc_to_delete",
            "filename": "old_file.pdf",
            "page": 1,
            "text": "old content"
        },
        {
            "chunk_id": "c2",
            "document_id": "doc_to_keep",
            "filename": "keep_file.pdf",
            "page": 1,
            "text": "kept content"
        }
    ]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    temp_vector_store.add_chunks(chunks, embeddings)

    assert len(temp_vector_store.list_documents()) == 2
    temp_vector_store.delete_document("doc_to_delete")

    remaining_docs = temp_vector_store.list_documents()
    assert len(remaining_docs) == 1
    assert remaining_docs[0]["document_id"] == "doc_to_keep"
