import asyncio
from typing import List, Dict, Union
from .base import OCRProvider

class PaddleOCRProvider(OCRProvider):
    def __init__(self):
        self.model = None
        self._is_available = None

    def _load_model(self):
        if self._is_available is False:
            return False
        
        try:
            from paddleocr import PaddleOCR
            # Loading English by default, can be extended for multilingual
            self.model = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False) 
            self._is_available = True
            return True
        except ImportError:
            self._is_available = False
            return False
        except Exception as e:
            print(f"Error loading PaddleOCR: {e}")
            self._is_available = False
            return False

    async def extract_text(self, document_path: str) -> Union[List[Dict], Dict]:
        if not self.is_available():
            raise RuntimeError("PaddleOCR is not available.")
            
        loop = asyncio.get_running_loop()
        
        # PaddleOCR returns a list of results, one list per page.
        results = await loop.run_in_executor(
            None,
            lambda: self.model.ocr(document_path, cls=True)
        )
        
        pages_data = []
        if results:
            for page_idx, page_lines in enumerate(results):
                if not page_lines:
                    continue
                    
                page_text_data = []
                for line in page_lines:
                    bbox_points, (text, confidence) = line
                    
                    x_coords = [p[0] for p in bbox_points]
                    y_coords = [p[1] for p in bbox_points]
                    bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                    
                    page_text_data.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
                
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text_data": page_text_data
                })
                
        return {"pages": pages_data}

    def is_available(self) -> bool:
        return self._load_model()
