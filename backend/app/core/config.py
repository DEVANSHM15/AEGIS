import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Aegis - AI Engineering Knowledge Platform"
    API_V1_STR: str = "/api"

    # Embeddings Configuration
    EMBEDDING_PROVIDER: str = "local"  # 'local' or 'openai'
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_API_KEY: Optional[str] = None

    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # 'mock', 'openai', 'gemini', 'ollama'
    LLM_MODEL: str = "gemini-3.6-flash"
    LLM_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Vector DB Configuration
    VECTOR_DB_PATH: str = os.path.join(os.getcwd(), "data", "chroma_db")
    TOP_K: int = 5

    # Chunking Configuration
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # System Configuration
    MAX_FILE_SIZE_MB: int = 15

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            os.path.join(os.getcwd(), ".env"),
            ".env",
            "../.env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
