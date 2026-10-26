import io
import wave
import numpy as np
from collections import OrderedDict
from .provider import TTSProvider
from app.core.languages import INDIAN_LANGUAGES

MAX_LOADED_MODELS = 2

class IndicMmsTTSProvider(TTSProvider):
    def __init__(self):
        self._models = OrderedDict()
        self._tokenizers = OrderedDict()
        self._available = False
        self._load_dependencies()

    def _load_dependencies(self):
        try:
            import torch
            from transformers import VitsModel, AutoTokenizer
            self._available = True
        except ImportError:
            self._available = False
            print("Warning: transformers or torch not installed. TTS unavailable.")

    def _lazy_load(self, lang: str):
        if not self._available:
            return False
            
        lang_info = INDIAN_LANGUAGES.get(lang)
        if not lang_info or not lang_info.get("tts_supported"):
            return False
            
        if lang in self._models:
            # Move to end to mark as recently used
            self._models.move_to_end(lang)
            self._tokenizers.move_to_end(lang)
            return True
            
        from transformers import VitsModel, AutoTokenizer
        model_id = lang_info["tts_model"]
        
        try:
            print(f"Loading TTS model for {lang} from {model_id}...")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = VitsModel.from_pretrained(model_id)
            
            # Enforce LRU cache size
            if len(self._models) >= MAX_LOADED_MODELS:
                oldest_lang, _ = self._models.popitem(last=False)
                self._tokenizers.pop(oldest_lang)
                print(f"Unloaded {oldest_lang} TTS model to free memory.")
                
            self._tokenizers[lang] = tokenizer
            self._models[lang] = model
            print(f"Loaded {lang} TTS model successfully.")
            return True
        except Exception as e:
            print(f"Failed to load {lang} TTS model: {e}")
            return False

    def synthesize(self, text: str, language: str) -> bytes:
        if not self._lazy_load(language):
            raise RuntimeError(f"Model for {language} could not be loaded or is not supported.")
            
        import torch
        tokenizer = self._tokenizers[language]
        model = self._models[language]

        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = model(**inputs).waveform
            
        audio_np = output[0].cpu().numpy()
        audio_np = audio_np / np.max(np.abs(audio_np))
        audio_int16 = (audio_np * 32767).astype(np.int16)
        
        sample_rate = model.config.sampling_rate
        
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
            
        wav_io.seek(0)
        return wav_io.read()

    def is_available(self) -> bool:
        return self._available

    def supported_languages(self) -> list[str]:
        return [k for k, v in INDIAN_LANGUAGES.items() if v.get("tts_supported")]
