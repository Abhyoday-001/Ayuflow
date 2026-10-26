import hashlib
from typing import Optional
from .mms_tts import IndicMmsTTSProvider

class TTSService:
    def __init__(self):
        self.provider = IndicMmsTTSProvider()
        self._cache: dict[str, bytes] = {}

    def _get_cache_key(self, text: str, language: str) -> str:
        # Simple hash to avoid huge dict keys
        raw = f"{language}:{text}".encode('utf-8')
        return hashlib.md5(raw).hexdigest()

    def generate_audio(self, text: str, language: str) -> Optional[bytes]:
        """
        Returns cached audio bytes if available, else synthesizes and caches it.
        Gracefully handles failures by returning None.
        """
        if not self.provider.is_available():
            return None

        # Fallback to English model if language unsupported, but realistically we expect hi or en
        if language not in self.provider.supported_languages():
            language = "en"

        cache_key = self._get_cache_key(text, language)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            print(f"Synthesizing new audio for {language}: length {len(text)}")
            audio_bytes = self.provider.synthesize(text, language)
            
            # Cache the result
            self._cache[cache_key] = audio_bytes
            return audio_bytes
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return None

    def get_status(self) -> dict:
        from app.core.languages import INDIAN_LANGUAGES
        
        languages = {}
        for code, info in INDIAN_LANGUAGES.items():
            if info.get("status") == "supported":
                languages[code] = {
                    "name": info["name"],
                    "status": "ready" if self.provider.is_available() else "unavailable"
                }
            elif info.get("status") == "testing":
                languages[code] = {
                    "name": info["name"],
                    "status": "testing"
                }
                
        return {
            "available": self.provider.is_available(),
            "provider": "indic-mms-tts",
            "languages": languages
        }

tts_service = TTSService()
