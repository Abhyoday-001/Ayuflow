import os
import sys

def download_faster_whisper():
    print("Downloading Faster-Whisper 'base' model if not present...")
    try:
        from faster_whisper import WhisperModel
        # This will trigger the download if not cached
        WhisperModel("base", device="cpu", compute_type="int8")
        print("Faster-Whisper model is ready.")
    except Exception as e:
        print(f"Failed to load Faster-Whisper model: {e}")

def download_silero_vad():
    print("Downloading Silero VAD model if not present...")
    try:
        import torch
        torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        print("Silero VAD is ready.")
    except Exception as e:
        print(f"Failed to load Silero VAD: {e}")

def download_sentence_transformers():
    print("Downloading Sentence Transformers model if not present...")
    try:
        from sentence_transformers import SentenceTransformer
        SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        print("Sentence Transformers model is ready.")
    except Exception as e:
        print(f"Failed to load Sentence Transformers: {e}")

if __name__ == "__main__":
    download_faster_whisper()
    download_silero_vad()
    download_sentence_transformers()
    print("Model check complete.")
