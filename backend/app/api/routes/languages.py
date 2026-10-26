from fastapi import APIRouter
from app.core.languages import INDIAN_LANGUAGES

router = APIRouter()

@router.get("/")
async def list_languages():
    languages = [
        {
            "code": k,
            "name": v["name"],
            "nativeName": v["native_name"],
            "text": True,
            "asr": v["asr_supported"],
            "tts": v["tts_supported"],
            "providers": {
                "asr": "faster-whisper", # Will be dynamic once provider abstraction is in place
                "tts": "mms" if v["tts_supported"] else None
            }
        }
        for k, v in INDIAN_LANGUAGES.items() if v["status"] == "supported"
    ]
    return {"languages": languages}
