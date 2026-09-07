import io
import uuid
import re
from typing import List, Dict, Any
from pypdf import PdfReader
from app.core.logging import logger

class DocumentProcessor:
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal and remove dangerous characters."""
        filename = re.sub(r'[^\w\s\.-]', '', filename).strip()
        return filename or "document"

    @classmethod
    def validate_file(cls, filename: str, content_bytes: bytes, max_size_mb: int = 15):
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: PDF, TXT, Markdown (.md)")
        
        file_size_mb = len(content_bytes) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size of {max_size_mb} MB")

        if len(content_bytes) == 0:
            raise ValueError("Uploaded file is empty.")

    @classmethod
    def extract_text(cls, filename: str, content_bytes: bytes, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Extract text from file.
        Returns a list of page objects:
        [
          {"document_id": doc_id, "filename": filename, "page": page_num, "text": page_text}
        ]
        """
        doc_id = document_id or str(uuid.uuid4())
        clean_filename = cls.sanitize_filename(filename)
        cls.validate_file(clean_filename, content_bytes)
        ext = "." + clean_filename.rsplit(".", 1)[-1].lower()

        extracted_pages: List[Dict[str, Any]] = []

        if ext == ".pdf":
            logger.info(f"Extracting text from PDF: {clean_filename}")
            pdf_stream = io.BytesIO(content_bytes)
            reader = PdfReader(pdf_stream)

            if len(reader.pages) == 0:
                raise ValueError(f"PDF file '{clean_filename}' contains no readable pages.")

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                page_number = i + 1
                if page_text.strip():
                    extracted_pages.append({
                        "document_id": doc_id,
                        "filename": clean_filename,
                        "page": page_number,
                        "text": page_text.strip()
                    })

            logger.info(f"Extracted {len(extracted_pages)} non-empty pages from PDF '{clean_filename}'")

        elif ext in [".txt", ".md"]:
            logger.info(f"Extracting text from text/markdown file: {clean_filename}")
            try:
                raw_text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = content_bytes.decode("latin-1", errors="ignore")

            if not raw_text.strip():
                raise ValueError(f"File '{clean_filename}' contains no readable text.")

            extracted_pages.append({
                "document_id": doc_id,
                "filename": clean_filename,
                "page": None,
                "text": raw_text.strip()
            })

        return extracted_pages
