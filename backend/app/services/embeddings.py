from abc import ABC, abstractmethod
from typing import List
from app.core.config import settings
from app.core.logging import logger

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

class LocalSentenceTransformerProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing Local SentenceTransformers embedding provider with model: {model_name}")
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text], convert_to_numpy=True, show_progress_bar=False)[0]
        return embedding.tolist()

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None):
        api_key = api_key or settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
        if not api_key:
            raise ValueError(
                "OpenAI Embedding API key is required when EMBEDDING_PROVIDER is 'openai'. "
                "Set EMBEDDING_API_KEY or LLM_API_KEY in environment or .env."
            )
        logger.info(f"Initializing OpenAI embedding provider with model: {model_name}")
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(input=texts, model=self.model_name)
        return [data.embedding for data in response.data]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(input=[text], model=self.model_name)
        return response.data[0].embedding

_embedding_provider_instance = None

def get_embedding_provider() -> BaseEmbeddingProvider:
    global _embedding_provider_instance
    if _embedding_provider_instance is None:
        provider_type = settings.EMBEDDING_PROVIDER.lower()
        model_name = settings.EMBEDDING_MODEL

        if provider_type == "local":
            _embedding_provider_instance = LocalSentenceTransformerProvider(model_name=model_name)
        elif provider_type == "openai":
            _embedding_provider_instance = OpenAIEmbeddingProvider(model_name=model_name)
        else:
            raise ValueError(f"Unsupported EMBEDDING_PROVIDER '{provider_type}'. Supported values: 'local', 'openai'")
    return _embedding_provider_instance
