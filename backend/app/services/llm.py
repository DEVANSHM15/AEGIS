from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        pass

class MockLLMProvider(BaseLLMProvider):
    def __init__(self):
        logger.info("Initializing Explicit Mock LLM Provider (LLM_PROVIDER=mock)")

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "[MOCK RESPONSE] This is a simulated response generated because LLM_PROVIDER=mock is explicitly configured. "
            "The system ingested your context and processed your question successfully."
        )

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        api_key = api_key or settings.LLM_API_KEY
        if not api_key:
            raise ValueError(
                "OpenAI LLM API key is missing. Please set LLM_API_KEY in environment or .env file. "
                "The system will not silently fallback to mock mode."
            )
        logger.info(f"Initializing OpenAI LLM provider with model: {model_name}")
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gemini-3.6-flash", api_key: str = None):
        api_key = api_key or settings.LLM_API_KEY
        if not api_key:
            raise ValueError(
                "Gemini LLM API key is missing. Please set LLM_API_KEY in environment or .env file. "
                "The system will not silently fallback to mock mode."
            )
        logger.info(f"Initializing Gemini LLM provider with model: {model_name}")
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        full_prompt = f"{system_prompt}\n\nUser Question:\n{user_prompt}"
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt
        )
        return response.text.strip()

class OllamaLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "llama3", base_url: str = None):
        import httpx
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model_name = model_name or settings.LLM_MODEL
        logger.info(f"Initializing Ollama LLM provider at {self.base_url} with model: {self.model_name}")

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        import httpx
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\nQuestion: {user_prompt}",
            "stream": False
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise RuntimeError(f"Failed to communicate with Ollama endpoint at {self.base_url}: {str(e)}")

_llm_provider_instance = None

def get_llm_provider() -> BaseLLMProvider:
    global _llm_provider_instance
    if _llm_provider_instance is None:
        provider = settings.LLM_PROVIDER.lower()
        model = settings.LLM_MODEL

        if provider == "mock":
            _llm_provider_instance = MockLLMProvider()
        elif provider == "openai":
            _llm_provider_instance = OpenAILLMProvider(model_name=model)
        elif provider == "gemini":
            _llm_provider_instance = GeminiLLMProvider(model_name=model)
        elif provider == "ollama":
            _llm_provider_instance = OllamaLLMProvider(model_name=model)
        else:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{provider}'. Supported providers: 'mock', 'openai', 'gemini', 'ollama'."
            )
    return _llm_provider_instance
