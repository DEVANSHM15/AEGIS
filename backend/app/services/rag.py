from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.services.embeddings import get_embedding_provider, BaseEmbeddingProvider
from app.services.vector_store import VectorStore
from app.services.llm import get_llm_provider, BaseLLMProvider

FALLBACK_ANSWER = "I couldn't find enough information in the uploaded documents to answer this."

SYSTEM_PROMPT_TEMPLATE = """You are Aegis, an authoritative AI Engineering Knowledge & Incident Intelligence assistant.

CRITICAL INSTRUCTIONS:
1. Answer the user's question strictly using ONLY the provided Document Context Chunks below.
2. If the answer cannot be directly derived from the provided context chunks, respond EXACTLY with the text:
"{fallback_text}"
3. Do NOT use outside knowledge or hallucinate facts not present in the context.
4. Keep the answer clear, technical, concise, and accurate.

DOCUMENT CONTEXT CHUNKS:
{context_block}
"""

class RAGPipeline:
    def __init__(
        self,
        vector_store: VectorStore = None,
        embedding_provider: BaseEmbeddingProvider = None,
        llm_provider: BaseLLMProvider = None
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.llm_provider = llm_provider or get_llm_provider()

    def query(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """
        Executes the Basic RAG Pipeline:
        1. Embed user question
        2. Retrieve Top-K relevant chunks from Vector DB
        3. Check context availability
        4. Generate grounded LLM response
        5. Extract source citations & retrieval debug information
        """
        k = top_k or settings.TOP_K
        logger.info(f"RAG Pipeline query received: '{question}' (top_k={k})")

        # Step 1: Generate Query Embedding
        query_embedding = self.embedding_provider.embed_query(question)
        logger.info("Generated query embedding vector")

        # Step 2: Similarity Search in Vector DB
        retrieved_chunks = self.vector_store.search(query_embedding, top_k=k)
        logger.info(f"Retrieved {len(retrieved_chunks)} candidate chunks from ChromaDB")

        # Step 3: Handle empty vector DB or no context retrieved
        if not retrieved_chunks:
            logger.info("No context retrieved. Returning standard fallback answer.")
            return {
                "answer": FALLBACK_ANSWER,
                "sources": [],
                "retrieved_chunks": []
            }

        # Format Context Block
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            page_info = f" (Page {chunk['page']})" if chunk.get('page') else ""
            context_parts.append(
                f"[Chunk {i} | File: {chunk['filename']}{page_info}]\n{chunk['text']}"
            )

        context_block = "\n\n".join(context_parts)

        # Step 4: Construct System & User Prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            fallback_text=FALLBACK_ANSWER,
            context_block=context_block
        )
        user_prompt = f"Question: {question}"

        # Step 5: Generate Answer via LLM
        try:
            raw_answer = self.llm_provider.generate_answer(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM Generation failed: {str(e)}")
            raise e

        # Step 6: Deduplicate Sources
        seen_sources = set()
        sources = []
        for chunk in retrieved_chunks:
            source_key = (chunk["filename"], chunk["page"], chunk["chunk_id"])
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append({
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                })

        # Debug Chunks Output
        debug_chunks = [
            {
                "chunk_id": c["chunk_id"],
                "filename": c["filename"],
                "page": c["page"],
                "score": c["score"],
                "text": c["text"]
            }
            for c in retrieved_chunks
        ]

        logger.info(f"RAG Pipeline completed. Generated answer length: {len(raw_answer)} chars")
        return {
            "answer": raw_answer,
            "sources": sources,
            "retrieved_chunks": debug_chunks
        }
