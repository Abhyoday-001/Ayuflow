from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_async_session
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview
from app.services.audit.logger import audit_logger
from datetime import datetime

router = APIRouter()

class ReviewActionRequest(BaseModel):
    fact_id: int
    action: str  # "accept", "edit", "reject"
    corrected_value: Optional[str] = None
    reviewer_id: str

@router.post("/{encounter_id}")
async def review_fact(
    encounter_id: int, 
    request: ReviewActionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    if request.action not in ["accept", "edit", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action.")

    fact = await session.get(ClinicalFact, request.fact_id)
    if not fact or fact.encounter_id != encounter_id:
        raise HTTPException(status_code=404, detail="Fact not found for this encounter.")

    encounter = await session.get(Encounter, encounter_id)
    if encounter and encounter.status == "FINALIZED":
        raise HTTPException(status_code=400, detail="Cannot review facts in a finalized encounter.")

    original_status = fact.verification_status
    original_value = fact.value

    if request.action == "accept":
        fact.verification_status = "verified"
        action_log = "CLINICAL_FACT_ACCEPTED"
    elif request.action == "reject":
        fact.verification_status = "rejected"
        action_log = "CLINICAL_FACT_REJECTED"
    elif request.action == "edit":
        if request.corrected_value is None:
            raise HTTPException(status_code=400, detail="corrected_value is required for edit action.")
        fact.value = request.corrected_value
        fact.verification_status = "verified" # edited implies verified by doctor
        action_log = "CLINICAL_FACT_EDITED"

    # Audit log
    await audit_logger.log(
        session=session,
        actor=request.reviewer_id,
        action=action_log,
        entity_type="ClinicalFact",
        entity_id=str(fact.id),
        metadata={
            "encounter_id": encounter_id,
            "original_status": original_status,
            "new_status": fact.verification_status,
            "original_value": original_value,
            "new_value": fact.value
        }
    )

    await session.commit()
    await session.refresh(fact)
    
    return {"status": "success", "fact": {"id": fact.id, "value": fact.value, "status": fact.verification_status}}

class FinalizeRequest(BaseModel):
    reviewer_id: str

@router.post("/{encounter_id}/finalize")
async def finalize_encounter(
    encounter_id: int, 
    request: FinalizeRequest,
    session: AsyncSession = Depends(get_async_session)
):
    encounter = await session.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found.")
        
    if encounter.status == "FINALIZED":
        raise HTTPException(status_code=400, detail="Encounter is already finalized.")

    encounter.status = "FINALIZED"
    
    review_record = DoctorReview(
        encounter_id=encounter_id,
        reviewer_id=request.reviewer_id,
        status="FINALIZED",
        finalized_at=datetime.utcnow()
    )
    session.add(review_record)

    await audit_logger.log(
        session=session,
        actor=request.reviewer_id,
        action="ENCOUNTER_FINALIZED",
        entity_type="Encounter",
        entity_id=str(encounter_id)
    )
    
    await session.commit()
    
    return {"status": "success", "message": "Encounter finalized successfully."}
