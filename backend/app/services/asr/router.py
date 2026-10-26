import os
from typing import Optional
from app.core.config import settings
from .base import ASRProvider
from .indicconformer import IndicConformerProvider
from .faster_whisper import FasterWhisperProvider
from app.schemas.transcription import TranscriptionResult

class ASRRouter:
    def __init__(self):
        self.primary = IndicConformerProvider()
        self.fallback = FasterWhisperProvider()

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        # Try primary first if configured
        if settings.ASR_PRIMARY == "indicconformer" and self.primary.is_available():
            try:
                return await self.primary.transcribe(audio_path, language)
            except Exception as e:
                print(f"Primary ASR failed: {e}. Falling back...")
        
        # Fallback to faster-whisper
        if self.fallback.is_available():
            return await self.fallback.transcribe(audio_path, language)
            
        raise RuntimeError("No ASR providers are currently available.")

    def get_provider_status(self) -> dict:
        return {
            "indicconformer": "available" if self.primary.is_available() else "unavailable",
            "faster_whisper": "available" if self.fallback.is_available() else "unavailable",
        }

asr_router = ASRRouter()
