import torch
import torchaudio

class SileroVAD:
    def __init__(self):
        self.model = None
        self.utils = None
        self._is_available = None

    def _load_model(self):
        if self._is_available is False:
            return False
            
        try:
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )
            self._is_available = True
            return True
        except Exception as e:
            print(f"Error loading Silero VAD: {e}")
            self._is_available = False
            return False

    def is_available(self) -> bool:
        return self._load_model()

    def has_speech(self, audio_path: str, threshold: float = 0.5) -> bool:
        """
        Detects if there is any speech in the audio file.
        In a full implementation, this would return segments of speech.
        """
        if not self.is_available():
            # If VAD is unavailable, default to assuming there is speech so the pipeline doesn't break
            return True
            
        try:
            (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = self.utils
            
            wav = read_audio(audio_path)
            speech_timestamps = get_speech_timestamps(wav, self.model, return_seconds=True)
            
            return len(speech_timestamps) > 0
        except Exception as e:
            print(f"Silero VAD processing error: {e}")
            return True

vad_service = SileroVAD()
