import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class VectorStore:
    def __init__(self, db_path: str = None, collection_name: str = "aegis_chunks"):
        self.db_path = db_path or settings.VECTOR_DB_PATH
        os.makedirs(self.db_path, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB client at: {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Use cosine distance space
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Stores chunks in ChromaDB adhering strictly to schema:
        - ids: chunk_id
        - documents: text
        - embeddings: vector
        - metadatas: {document_id, filename, page, chunk_id} (No text duplication)
        """
        if not chunks or not embeddings:
            return

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "document_id": c["document_id"],
                "filename": c["filename"],
                "page": c["page"] if c["page"] is not None else -1,
                "chunk_id": c["chunk_id"]
            }
            for c in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Upserted {len(chunks)} chunks into ChromaDB collection '{self.collection.name}'")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs similarity search.
        Returns list of dicts with chunk details + similarity score:
        [
          {
            "chunk_id": "...",
            "document_id": "...",
            "filename": "...",
            "page": 4 or None,
            "text": "...",
            "score": 0.87
          }
        ]
        """
        count = self.collection.count()
        if count == 0:
            logger.info("Vector DB is empty. Returning 0 search results.")
            return []

        actual_top_k = min(top_k, count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_top_k,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            ids_list = results["ids"][0]
            docs_list = results["documents"][0]
            metas_list = results["metadatas"][0]
            distances_list = results["distances"][0]

            for chunk_id, doc_text, meta, dist in zip(ids_list, docs_list, metas_list, distances_list):
                # Cosine distance to similarity conversion: score = max(0.0, 1.0 - dist)
                score = round(max(0.0, 1.0 - float(dist)), 4)
                page_val = meta.get("page")
                page_num = page_val if (page_val is not None and page_val != -1) else None

                search_results.append({
                    "chunk_id": chunk_id,
                    "document_id": meta.get("document_id"),
                    "filename": meta.get("filename"),
                    "page": page_num,
                    "text": doc_text,
                    "score": score
                })

        logger.info(f"Retrieved top {len(search_results)} relevant chunks from ChromaDB")
        return search_results

    def list_documents(self) -> List[Dict[str, Any]]:
        """List distinct uploaded documents with metadata summary."""
        count = self.collection.count()
        if count == 0:
            return []

        # Fetch all metadatas
        all_records = self.collection.get(include=["metadatas"])
        metas = all_records.get("metadatas", [])

        doc_summary: Dict[str, Dict[str, Any]] = {}

        for meta in metas:
            doc_id = meta.get("document_id")
            if not doc_id:
                continue

            filename = meta.get("filename", "unknown")
            page_val = meta.get("page")

            if doc_id not in doc_summary:
                doc_summary[doc_id] = {
                    "document_id": doc_id,
                    "filename": filename,
                    "chunk_count": 0,
                    "pages": set()
                }

            doc_summary[doc_id]["chunk_count"] += 1
            if page_val is not None and page_val != -1:
                doc_summary[doc_id]["pages"].add(page_val)

        res = []
        for doc_id, data in doc_summary.items():
            page_list = sorted(list(data["pages"]))
            res.append({
                "document_id": doc_id,
                "filename": data["filename"],
                "chunk_count": data["chunk_count"],
                "total_pages": len(page_list) if page_list else 1
            })

        return sorted(res, key=lambda x: x["filename"])

    def delete_document(self, document_id: str) -> bool:
        """Deletes all chunks belonging to a specific document_id."""
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted all chunks for document_id '{document_id}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting document '{document_id}': {str(e)}")
            raise e

    def clear(self):
        """Clears all records in collection (useful for testing)."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
