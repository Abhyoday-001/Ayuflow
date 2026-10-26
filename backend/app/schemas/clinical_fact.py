from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ExtractedFact(BaseModel):
    category: str = Field(description="Category of the fact, e.g., 'symptom', 'medication', 'allergy'")
    field: str = Field(description="Specific field, e.g., 'fever', 'back_pain', 'metformin'")
    value: Any = Field(description="The extracted value, can be boolean, string, or number")
    duration: Optional[str] = Field(None, description="Duration of the symptom or medication if stated")
    pattern: Optional[str] = Field(None, description="Pattern if stated, e.g., 'worse_at_night'")
    source_text: str = Field(description="The exact text snippet from the input that supports this fact")

class FactExtractionResponse(BaseModel):
    facts: List[ExtractedFact]
