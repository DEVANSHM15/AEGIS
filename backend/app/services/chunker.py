import uuid
import re
from typing import List, Dict, Any
from app.core.logging import logger

class Chunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100, encoding_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = None

        try:
            import tiktoken
            self.encoding = tiktoken.get_encoding(encoding_name)
            logger.info(f"Initialized tiktoken encoding '{encoding_name}'")
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoding '{encoding_name}' ({str(e)}). Falling back to regex-based token estimator.")

    def count_tokens(self, text: str) -> int:
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        # Fallback estimation: ~4 chars per token or word count * 1.3
        words = len(re.findall(r'\w+', text))
        return max(1, int(words * 1.3))

    def chunk_text(self, text: str) -> List[str]:
        """Splits text into overlapping token chunks."""
        if not text or not text.strip():
            return []

        if self.encoding:
            try:
                tokens = self.encoding.encode(text)
                if len(tokens) <= self.chunk_size:
                    return [text.strip()]

                chunks = []
                start = 0
                step = self.chunk_size - self.chunk_overlap

                while start < len(tokens):
                    end = start + self.chunk_size
                    chunk_tokens = tokens[start:end]
                    chunk_str = self.encoding.decode(chunk_tokens)
                    if chunk_str.strip():
                        chunks.append(chunk_str.strip())

                    if end >= len(tokens):
                        break
                    start += step

                return chunks
            except Exception as e:
                logger.warning(f"Tiktoken encoding failed during chunking: {str(e)}. Using fallback chunker.")

        # Fallback word-based chunker (~1 token ≈ 0.75 words, 800 tokens ≈ 600 words)
        words = text.split()
        target_words = int(self.chunk_size * 0.75)
        overlap_words = int(self.chunk_overlap * 0.75)

        if len(words) <= target_words:
            return [text.strip()]

        chunks = []
        start = 0
        step = max(1, target_words - overlap_words)

        while start < len(words):
            end = start + target_words
            chunk_words = words[start:end]
            chunk_str = " ".join(chunk_words)
            if chunk_str.strip():
                chunks.append(chunk_str.strip())
            if end >= len(words):
                break
            start += step

        return chunks

    def process_extracted_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes extracted page dicts:
        [{"document_id": "...", "filename": "...", "page": 1, "text": "..."}]
        Returns chunk dicts:
        [{"chunk_id": "...", "document_id": "...", "filename": "...", "page": 1, "text": "..."}]
        """
        all_chunks: List[Dict[str, Any]] = []

        for page_info in pages:
            doc_id = page_info["document_id"]
            filename = page_info["filename"]
            page_num = page_info["page"]
            page_text = page_info["text"]

            text_chunks = self.chunk_text(page_text)
            for idx, text_chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}_p{page_num or 0}_c{idx}_{uuid.uuid4().hex[:8]}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "filename": filename,
                    "page": page_num,
                    "text": text_chunk
                })

        logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
        return all_chunks
