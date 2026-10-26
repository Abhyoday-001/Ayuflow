from typing import Optional
from faster_whisper import WhisperModel
import asyncio

from .base import ASRProvider
from app.schemas.transcription import TranscriptionResult, TranscriptSegment

class FasterWhisperProvider(ASRProvider):
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size
        self.model = None

    def _load_model(self):
        if self.model is None:
            # Using CPU since we don't have CUDA. Can be optimized for MPS if supported by faster_whisper
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:

        INITIAL_PROMPTS = {
            "hi": "नमस्ते। डॉक्टर साहब, मुझे पेट में दर्द है और सिर में दर्द है। मैंने दवा ली है।",
            "en": "Hello doctor. I have a stomach ache and a headache. I took some medicine.",
            "kn": "ನಮಸ್ಕಾರ. ನನಗೆ ಹೊಟ್ಟೆ ನೋವು ಮತ್ತು ತಲೆನೋವು ಇದೆ.",
            "mr": "नमस्कार. मला पोटात दुखत आहे आणि डोकेदुखी आहे.",
            "gu": "નમસ્તે. મને પેટમાં દુખાવો છે અને માથાનો દુખાવો છે.",
            "ta": "வணக்கம். எனக்கு வயிற்று வலி மற்றும் தலைவலி உள்ளது.",
            "te": "నమస్కారం. నాకు కడుపు నొప్పి మరియు తలనొప్పి ఉంది.",
            "ml": "നമസ്കാരം ഡോക്ടർ. എനിക്ക് വയറുവേദനയും തലവേദനയും ഉണ്ട്. ഞാൻ മരുന്ന് കഴിച്ചു.",
            "bn": "নমস্কার ডাক্তারবাবু। আমার পেট ব্যথা এবং মাথা ব্যথা করছে।",
            "pa": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਡਾਕਟਰ ਸਾਹਿਬ। ਮੇਰੇ ਢਿੱਡ ਵਿੱਚ ਦਰਦ ਹੈ ਅਤੇ ਸਿਰ ਵਿੱਚ ਦਰਦ ਹੈ।",
            "or": "ନମସ୍କାର ଡାକ୍ତରବାବୁ। ମୋର ପେଟ ବିନ୍ଧା ଏବଂ ମୁଣ୍ଡ ବିନ୍ଧା ହେଉଛି।"
        }
        initial_prompt = INITIAL_PROMPTS.get(language, "")

        if not self.is_available():
            raise RuntimeError("Faster Whisper is not available.")
            
        # Run inference in a threadpool so it doesn't block the async event loop
        loop = asyncio.get_running_loop()
        
        segments, info = await loop.run_in_executor(
            None, 
            lambda: self.model.transcribe(
                audio_path, 
                language=language,
                initial_prompt=initial_prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=300),
                beam_size=2,
                best_of=2,
                temperature=[0.0, 0.2, 0.4],
                condition_on_previous_text=False
            )
        )
        

        result_segments = []
        full_text = ""
        
        sum_logprob = 0.0
        sum_no_speech = 0.0
        max_compression = 0.0
        
        segments = list(segments)
        
        if not segments:
            return TranscriptionResult(
                text="",
                language=language or "hi",
                segments=[],
                provider="faster_whisper",
                model=self.model_size,
                quality={"reason": "empty_segments"},
                quality_state="RETRY"
            )

        for segment in segments:
            result_segments.append(
                TranscriptSegment(
                    start_time=segment.start,
                    end_time=segment.end,
                    text=segment.text.strip(),
                    confidence=segment.avg_logprob,
                    avg_logprob=segment.avg_logprob,
                    no_speech_prob=segment.no_speech_prob,
                    compression_ratio=segment.compression_ratio
                )
            )
            full_text += segment.text + " "
            sum_logprob += segment.avg_logprob
            sum_no_speech += segment.no_speech_prob
            if segment.compression_ratio > max_compression:
                max_compression = segment.compression_ratio

        avg_logprob = sum_logprob / len(segments)
        avg_no_speech = sum_no_speech / len(segments)
        
        quality_state = "GOOD"
        reasons = []
        
        full_text = full_text.strip()
        
        # Hallucination / Garbage checks
        if max_compression > 2.5:
            quality_state = "RETRY"
            reasons.append("high_compression")
        
        if avg_logprob < -1.0:
            quality_state = "REVIEW" if quality_state != "RETRY" else "RETRY"
            reasons.append("low_logprob")
            if avg_logprob < -1.5:
                quality_state = "RETRY"
                reasons.append("very_low_logprob")
                
        if avg_no_speech > 0.6:
            quality_state = "REVIEW" if quality_state != "RETRY" else "RETRY"
            reasons.append("high_no_speech_prob")

        # Repetition hallucination detector
        words = full_text.split()
        if len(words) >= 4:
            # Check for same word repeating 3+ times
            word_counts = {}
            for w in words:
                word_counts[w] = word_counts.get(w, 0) + 1
            if any(c >= 3 for c in word_counts.values()) and len(set(words)) <= len(words)/2:
                quality_state = "RETRY"
                reasons.append("repetitive_hallucination")

        quality = {
            "avg_logprob": avg_logprob,
            "no_speech_prob": avg_no_speech,
            "max_compression_ratio": max_compression,
            "reasons": reasons
        }

        return TranscriptionResult(
            text=full_text,
            language=info.language,
            confidence=info.language_probability,
            segments=result_segments,
            provider="faster_whisper",
            model=self.model_size,
            quality=quality,
            quality_state=quality_state
        )


    def is_available(self) -> bool:
        try:
            self._load_model()
            return True
        except Exception as e:
            print(f"Faster Whisper unavailable: {e}")
            return False
