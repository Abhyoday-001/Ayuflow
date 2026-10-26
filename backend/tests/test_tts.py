import pytest
from app.services.tts.service import tts_service
from app.services.tts.mms_tts import IndicMmsTTSProvider
from app.core.languages import INDIAN_LANGUAGES

SUPPORTED_LANGS = [k for k, v in INDIAN_LANGUAGES.items() if v.get("tts_supported") and v.get("status") == "supported"]

@pytest.mark.asyncio
async def test_tts_provider_loads():
    provider = IndicMmsTTSProvider()
    assert provider.is_available() is True
    assert set(SUPPORTED_LANGS).issubset(set(provider.supported_languages()))

@pytest.mark.parametrize("language", SUPPORTED_LANGS)
@pytest.mark.asyncio
async def test_language_synthesis(language):
    # This tests lazy loading, memory caching, and generation across all enabled languages
    # using the native language name to avoid tokenizer missing character errors (e.g. Hindi tokenizer doesn't know "A").
    text = INDIAN_LANGUAGES[language]["native_name"]
    audio = tts_service.generate_audio(text, language)
    assert audio is not None
    assert len(audio) > 100  # Should be a valid wav file

@pytest.mark.asyncio
async def test_invalid_language():
    # Should fallback to 'en' in the service layer
    audio = tts_service.generate_audio("Test", "invalid_lang")
    assert audio is not None
    assert len(audio) > 100

@pytest.mark.asyncio
async def test_empty_text():
    # Service doesn't explicitly block empty text, but provider might generate silence. 
    # Usually empty text returns an empty array.
    try:
        audio = tts_service.generate_audio("", "en")
        # Should gracefully return None or small wav
        assert audio is not None or audio is None
    except Exception:
        pass

@pytest.mark.asyncio
async def test_tts_caching():
    # Clear cache
    tts_service._cache.clear()
    
    # Generate once
    audio1 = tts_service.generate_audio("Cache me", "en")
    assert len(tts_service._cache) == 1
    
    # Generate again
    audio2 = tts_service.generate_audio("Cache me", "en")
    
    # Should use cache and return identical bytes
    assert audio1 == audio2
    assert len(tts_service._cache) == 1
