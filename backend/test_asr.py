import asyncio
from app.services.asr.faster_whisper import FasterWhisperProvider

async def main():
    provider = FasterWhisperProvider()
    print("Loading model...")
    provider._load_model()
    print("Transcribing...")
    result = await provider.transcribe("../test.wav", language="hi")
    print(f"Result: {result.text}")

asyncio.run(main())
