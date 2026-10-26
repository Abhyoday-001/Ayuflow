from typing import Any
from app.db.models.core import Evidence, ClinicalFact
from sqlalchemy.ext.asyncio import AsyncSession

class EvidenceService:
    @staticmethod
    async def attach_evidence(
        session: AsyncSession, 
        fact_id: int, 
        source_type: str, 
        source_reference: str, 
        excerpt: str, 
        confidence: float
    ) -> Evidence:
        evidence = Evidence(
            clinical_fact_id=fact_id,
            source_type=source_type,
            source_reference=source_reference,
            excerpt=excerpt,
            confidence=confidence
        )
        session.add(evidence)
        await session.commit()
        await session.refresh(evidence)
        return evidence

evidence_service = EvidenceService()
