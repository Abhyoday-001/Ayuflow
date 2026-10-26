import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cloud Storage Config
    CLOUD_STORAGE_BUCKET: str = "medical-documents-private"
    CLOUD_STORAGE_REGION: str = "ap-south-1"
    CLOUD_STORAGE_ACCESS_KEY: str = ""
    CLOUD_STORAGE_SECRET_KEY: str = ""

    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://ayuflow:ayuflow_dev_pass@localhost:5432/ayuflow"
    ASR_PRIMARY: str = "indicconformer"
    ASR_FALLBACK: str = "faster_whisper"
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OCR_PRIMARY: str = "paddleocr"
    ENABLE_TROCR: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()
