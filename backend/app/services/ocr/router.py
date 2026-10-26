from app.core.config import settings
from .base import OCRProvider
from .paddleocr_provider import PaddleOCRProvider
from typing import List, Dict, Union, Optional

class OCRRouter:
    def __init__(self):
        self.primary = PaddleOCRProvider()

    async def extract_text(self, document_path: str) -> Union[List[Dict], Dict]:
        if settings.OCR_PRIMARY == "paddleocr" and self.primary.is_available():
            return await self.primary.extract_text(document_path)
            
        raise RuntimeError("No OCR providers are currently available.")

    def get_provider_status(self) -> dict:
        return {
            "paddleocr": "available" if self.primary.is_available() else "unavailable",
            "trocr": "unavailable" # hardcoded until implemented
        }

ocr_router = OCRRouter()
