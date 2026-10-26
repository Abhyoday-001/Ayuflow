from typing import Protocol, List, Dict, Union

class OCRProvider(Protocol):
    async def extract_text(self, document_path: str) -> Union[List[Dict], Dict]:
        """
        Extracts text from an image or document.
        Returns a dictionary for multi-page docs: {"pages": [{"page_number": 1, "text_data": [...]}]}
        Or falls back to List[Dict] for flat images.
        """
        ...

    def is_available(self) -> bool:
        ...
