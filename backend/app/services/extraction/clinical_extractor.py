from app.services.llm.router import llm_router
from app.schemas.clinical_fact import FactExtractionResponse

class ClinicalExtractor:
    def __init__(self):
        self.llm = llm_router
        
    async def extract_facts(self, transcript_text: str) -> dict:
        schema = FactExtractionResponse.model_json_schema()
        
        prompt = (
            f"Extract clinical facts from the following patient statement:\n\n"
            f"\"{transcript_text}\"\n\n"
            "Only extract explicit information. Do not infer anything."
        )
        
        extracted_data = await self.llm.generate_structured(prompt, schema)
        
        # Add metadata like confidence and verification status programmatically
        if "facts" in extracted_data:
            for fact in extracted_data["facts"]:
                # In a real system, LLM might output a confidence or we calculate it. 
                # For now, we assign a baseline heuristic confidence and track the source explicitly.
                fact["confidence"] = 0.90 
                fact["verification_status"] = "unverified"
                fact["source_type"] = "patient_statement"
                
        return extracted_data

extractor_service = ClinicalExtractor()
