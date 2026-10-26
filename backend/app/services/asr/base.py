from typing import Protocol, Optional
from app.schemas.transcription import TranscriptionResult

class ASRProvider(Protocol):
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        ...

    def is_available(self) -> bool:
        ...
