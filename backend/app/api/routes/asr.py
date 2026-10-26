import os
import uuid
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.vad.silero import vad_service
from app.services.asr.router import asr_router
from app.schemas.transcription import TranscriptionResult

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    SUPPORTED_LANGUAGES = {"hi", "en", "kn", "mr", "gu", "or", "ml", "pa", "ta", "te", "bn", "as"}
    if language and language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="INVALID_LANGUAGE")

    # Basic validation
    if not audio.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.webm', '.ogg', '.mp4')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Create temporary file to save the audio
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(audio.filename)[1])
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(await audio.read())
            
        import shutil, datetime
        DEBUG_AUDIO_DIR = "/tmp/ayuflow-asr-debug"
        os.makedirs(DEBUG_AUDIO_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = os.path.join(DEBUG_AUDIO_DIR, f"debug_{timestamp}_{audio.filename}")
        shutil.copyfile(temp_path, debug_path)
        print(f"Debug audio saved to: {debug_path}")

        # 1. Voice Activity Detection (VAD)
        # We only pass audio to ASR if speech is detected to save compute and prevent hallucinations
        if not vad_service.has_speech(temp_path):
            return TranscriptionResult(
                text="",
                language=language,
                confidence=1.0,
                segments=[],
                provider="vad_silence_detection",
                model="silero"
            )

        # 2. ASR Transcription
        try:
            result = await asr_router.transcribe(temp_path, language=language)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ASR transcription failed: {str(e)}")

    finally:
        # Cleanup temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
