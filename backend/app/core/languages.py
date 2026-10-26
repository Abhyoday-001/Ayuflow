from typing import Dict, List, Optional

INDIAN_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "iso639_3": "hin",
        "tts_model": "facebook/mms-tts-hin",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "iso639_3": "eng",
        "tts_model": "facebook/mms-tts-eng",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "bn": {
        "name": "Bengali",
        "native_name": "বাংলা",
        "iso639_3": "ben",
        "tts_model": "facebook/mms-tts-ben",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "gu": {
        "name": "Gujarati",
        "native_name": "ગુજરાતી",
        "iso639_3": "guj",
        "tts_model": "facebook/mms-tts-guj",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "kn": {
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "iso639_3": "kan",
        "tts_model": "facebook/mms-tts-kan",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "ml": {
        "name": "Malayalam",
        "native_name": "മലയാളം",
        "iso639_3": "mal",
        "tts_model": "facebook/mms-tts-mal",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "mr": {
        "name": "Marathi",
        "native_name": "मराठी",
        "iso639_3": "mar",
        "tts_model": "facebook/mms-tts-mar",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "or": {
        "name": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "iso639_3": "ory",
        "tts_model": "facebook/mms-tts-ory",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "pa": {
        "name": "Punjabi",
        "native_name": "ਪੰਜਾਬੀ",
        "iso639_3": "pan",
        "tts_model": "facebook/mms-tts-pan",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "ta": {
        "name": "Tamil",
        "native_name": "தமிழ்",
        "iso639_3": "tam",
        "tts_model": "facebook/mms-tts-tam",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "te": {
        "name": "Telugu",
        "native_name": "తెలుగు",
        "iso639_3": "tel",
        "tts_model": "facebook/mms-tts-tel",
        "tts_supported": True,
        "asr_supported": True,
        "status": "supported"
    },
    "as": {
        "name": "Assamese",
        "native_name": "অসমীয়া",
        "iso639_3": "asm",
        "tts_model": "facebook/mms-tts-asm",
        "tts_supported": False,
        "asr_supported": False,
        "status": "testing" # or unavailable until we explicitly test
    },
    "ur": {
        "name": "Urdu",
        "native_name": "اردو",
        "iso639_3": "urd",
        "tts_model": "facebook/mms-tts-urd",
        "tts_supported": False,
        "asr_supported": False,
        "status": "testing"
    }
}

def get_supported_languages() -> List[Dict]:
    """Returns a list of all languages marked as supported."""
    return [
        {"code": k, **v} 
        for k, v in INDIAN_LANGUAGES.items() 
        if v["status"] == "supported"
    ]

def get_language_info(code: str) -> Optional[Dict]:
    """Returns metadata for a specific language code."""
    return INDIAN_LANGUAGES.get(code)
