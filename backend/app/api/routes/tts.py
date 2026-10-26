import base64
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.services.tts.service import tts_service

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: str = "hi"

@router.post("/synthesize")
async def synthesize_audio(request: TTSRequest):
    """
    Synthesize text to audio. Returns a base64 encoded string containing WAV data, 
    or just the raw bytes if preferred. Let's return raw bytes for direct playback.
    Wait, the user wants JSON with "audio" string if integrating directly in questionnaire flow, 
    but for a dedicated API returning audio/wav is cleaner.
    Let's return raw audio/wav.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required.")
        
    audio_bytes = tts_service.generate_audio(request.text, request.language)
    
    if not audio_bytes:
        raise HTTPException(status_code=503, detail="TTS generation failed or is unavailable.")
        
    return Response(content=audio_bytes, media_type="audio/wav")

@router.get("/health")
async def tts_health():
    return tts_service.get_status()
