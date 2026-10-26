from abc import ABC, abstractmethod

class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str) -> bytes:
        """
        Synthesizes text into audio bytes (WAV format).
        Returns raw audio bytes.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Returns whether this TTS provider is loaded and ready.
        """
        pass

    @abstractmethod
    def supported_languages(self) -> list[str]:
        """
        Returns list of supported language codes (e.g. ['hi', 'en']).
        """
        pass
