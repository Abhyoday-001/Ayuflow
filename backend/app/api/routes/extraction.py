from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.extraction.clinical_extractor import extractor_service

router = APIRouter()

class ExtractionRequest(BaseModel):
    transcript_text: str

@router.post("/clinical-facts")
async def extract_clinical_facts(request: ExtractionRequest):
    if not request.transcript_text.strip():
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
        
    try:
        facts = await extractor_service.extract_facts(request.transcript_text)
        return facts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical extraction failed: {str(e)}")
