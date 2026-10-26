from typing import Any
import json
from google import genai
from google.genai import types

from app.core.config import settings
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.client = None
        self._is_available = bool(self.api_key)
        
        if self._is_available:
            self.client = genai.Client(api_key=self.api_key)

    async def generate_structured(self, prompt: str, schema: dict) -> dict:
        if not self.is_available():
            raise RuntimeError("Gemini API is not configured (API key missing).")
            
        system_instruction = (
            "You are a clinical information extraction system. You are NOT a doctor. "
            "Do not diagnose. Do not prescribe. Do not infer medical facts. Do not interpret laboratory results. "
            "Do not recommend treatment. Extract only information explicitly stated in the input. "
            "If a field is not explicitly present, return null. "
            "Every extracted fact must contain source_text. Return only valid JSON matching the supplied schema."
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
            ),
        )
        
        # Parse the JSON response
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            # Fallback or error handling
            raise ValueError(f"Failed to parse Gemini response as JSON: {response.text}") from e

    def is_available(self) -> bool:
        return self._is_available
