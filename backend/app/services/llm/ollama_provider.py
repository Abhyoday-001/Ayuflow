import json
import ollama

from app.core.config import settings
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL
        self.client = ollama.AsyncClient(host=self.base_url)

    async def generate_structured(self, prompt: str, schema: dict) -> dict:
        if not self.is_available():
            raise RuntimeError("Ollama is not available.")
            
        system_instruction = (
            "You are a clinical information extraction system. You are NOT a doctor. "
            "Do not diagnose. Do not prescribe. Do not infer medical facts. Do not interpret laboratory results. "
            "Do not recommend treatment. Extract only information explicitly stated in the input. "
            "If a field is not explicitly present, return null. "
            "Every extracted fact must contain source_text. Return only valid JSON matching the supplied schema."
        )

        # Ollama format supports passing JSON schema 
        response = await self.client.generate(
            model=self.model_name,
            prompt=prompt,
            system=system_instruction,
            format=schema,
            options={
                "temperature": 0.0
            }
        )
        
        try:
            return json.loads(response['response'])
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Ollama response as JSON: {response['response']}") from e

    def is_available(self) -> bool:
        # For simplicity, we just check if it's configured. In a real app we'd ping the server.
        return bool(self.base_url and self.model_name)
