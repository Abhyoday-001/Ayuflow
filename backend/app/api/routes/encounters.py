from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_async_session
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview

router = APIRouter()

@router.get("/")
async def list_encounters(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Encounter, Patient)
        .join(Patient, Encounter.patient_id == Patient.id)
        .order_by(Encounter.created_at.desc())
    )
    # Return basic list of encounters with patient data
    items = result.all()
    out = []
    for enc, pat in items:
        out.append({
            "id": enc.id,
            "patient_name": pat.name,
            "patient_sex": pat.sex,
            "patient_language": pat.preferred_language,
            "status": enc.status,
            "created_at": enc.created_at.isoformat() if enc.created_at else None
        })
    return {"encounters": out}

@router.get("/{encounter_id}")
async def get_encounter(
    encounter_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    encounter = await session.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found.")
    return encounter

from app.services.draft.draft_service import draft_service

@router.get("/{encounter_id}/draft")
async def get_medical_draft(
    encounter_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    try:
        draft = await draft_service.generate_draft(session, encounter_id)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{encounter_id}/facts")
async def get_encounter_facts(
    encounter_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(ClinicalFact).where(ClinicalFact.encounter_id == encounter_id)
    )
    facts = result.scalars().all()
    return {"facts": facts}

from app.services.fhir.exporter import fhir_exporter
from app.db.models.core import AuditLog

@router.get("/{encounter_id}/fhir")
async def export_fhir(
    encounter_id: int, 
    actor: str = "system",
    session: AsyncSession = Depends(get_async_session)
):
    try:
        bundle = await fhir_exporter.export_encounter_bundle(session, encounter_id, actor)
        return bundle
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{encounter_id}/audit")
async def get_audit_logs(
    encounter_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    # Get all facts for this encounter
    facts_result = await session.execute(
        select(ClinicalFact.id).where(ClinicalFact.encounter_id == encounter_id)
    )
    fact_ids = [str(f) for f in facts_result.scalars().all()]
    
    # Retrieve audit logs for the encounter and its facts
    from sqlalchemy import or_
    result = await session.execute(
        select(AuditLog).where(
            or_(
                (AuditLog.entity_type == 'Encounter') & (AuditLog.entity_id == str(encounter_id)),
                (AuditLog.entity_type == 'ClinicalFact') & (AuditLog.entity_id.in_(fact_ids)) if fact_ids else False
            )
        ).order_by(AuditLog.timestamp.desc())
    )
    logs = result.scalars().all()
    return {"audit_logs": logs}

@router.get("/{encounter_id}/timeline")
async def get_timeline(
    encounter_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    from app.db.models import Encounter, Document, ClinicalFact
    
    # Get encounter details
    stmt = select(Encounter).where(Encounter.id == encounter_id)
    enc_res = await session.execute(stmt)
    encounter = enc_res.scalar_one_or_none()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
        
    patient_id = encounter.patient_id
    
    # Get all past encounters for this patient
    stmt_encs = select(Encounter).where(Encounter.patient_id == patient_id).order_by(Encounter.created_at.desc())
    encs_res = await session.execute(stmt_encs)
    encounters = encs_res.scalars().all()
    
    # Get all documents for this patient
    stmt_docs = select(Document).where(Document.patient_id == patient_id).order_by(Document.created_at.desc())
    docs_res = await session.execute(stmt_docs)
    documents = docs_res.scalars().all()
    
    timeline = []
    
    for e in encounters:
        timeline.append({
            "type": "encounter",
            "id": e.id,
            "date": e.created_at.isoformat(),
            "status": e.status,
            "title": f"Consultation on {e.created_at.strftime('%d %b %Y')}"
        })
        
    for d in documents:
        timeline.append({
            "type": "document",
            "id": d.id,
            "date": d.created_at.isoformat(),
            "document_type": d.document_type,
            "document_name": d.document_name,
            "title": f"{d.document_type.capitalize()} uploaded"
        })
        
    # Sort timeline by date descending
    timeline.sort(key=lambda x: x["date"], reverse=True)
    
    return {"timeline": timeline}


from pydantic import BaseModel
class StatusUpdate(BaseModel):
    status: str

@router.patch("/{encounter_id}/status")
async def update_encounter_status(
    encounter_id: int, 
    update: StatusUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    encounter = await session.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found.")
    encounter.status = update.status
    await session.commit()
    return {"status": "success", "new_status": encounter.status}
