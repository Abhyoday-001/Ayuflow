from app.core.config import settings
from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider

class LLMRouter:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.ollama = OllamaProvider()

    async def generate_structured(self, prompt: str, schema: dict) -> dict:
        if settings.LLM_PROVIDER == "gemini" and self.gemini.is_available():
            try:
                return await self.gemini.generate_structured(prompt, schema)
            except Exception as e:
                print(f"Gemini generation failed: {e}. Falling back to Ollama...")
        
        if self.ollama.is_available():
            return await self.ollama.generate_structured(prompt, schema)
            
        raise RuntimeError("No LLM providers are currently available.")

    def get_provider_status(self) -> dict:
        return {
            "gemini": "configured" if self.gemini.is_available() else "unconfigured",
            "ollama": "available" if self.ollama.is_available() else "unavailable",
        }

llm_router = LLMRouter()
