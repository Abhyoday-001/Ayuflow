from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_async_session, async_session_maker
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview, QuestionnaireResponse
from app.services.questionnaire.planner import planner_service
from app.services.audit.logger import audit_logger

router = APIRouter()


class ConsentRequest(BaseModel):
    patient_id: int
    status: str
    purpose: Optional[str] = "clinical_consultation"
    scope: Optional[str] = "voice,documents,history"
    consent_version: Optional[str] = "v1"

@router.post("/consent")
async def record_consent(
    request: ConsentRequest,
    session: AsyncSession = Depends(get_async_session)
):
    from app.db.models import Consent
    consent = Consent(
        patient_id=request.patient_id,
        status=request.status,
        purpose=request.purpose,
        scope=request.scope,
        consent_version=request.consent_version
    )
    session.add(consent)
    await session.commit()
    
    await audit_logger.log(
        session=session,
        actor="patient",
        action="CONSENT_RECORDED",
        entity_type="Consent",
        entity_id=str(consent.id),
        metadata={"patient_id": request.patient_id, "status": request.status}
    )
    await session.commit()
    return {"status": "success", "consent_id": consent.id}

class NextQuestionRequest(BaseModel):

    encounter_id: int
    language: str = "en"
    intake_type: str = "allopathy"

class NextQuestionResponse(BaseModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    is_complete: bool = False

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    request: NextQuestionRequest,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Get answered questions for this encounter
        stmt = select(QuestionnaireResponse).where(QuestionnaireResponse.encounter_id == request.encounter_id)
        result = await session.execute(stmt)
        responses = result.scalars().all()
        answered_question_ids = [r.question_id for r in responses]
        
        next_q = planner_service.determine_next_question(answered_question_ids, responses)
        
        if next_q is None:
            # Mark encounter as intake_completed
            stmt_enc = select(Encounter).where(Encounter.id == request.encounter_id)
            res_enc = await session.execute(stmt_enc)
            encounter = res_enc.scalar_one_or_none()
            if encounter and encounter.status == "in_progress":
                encounter.status = "intake_completed"
                await session.commit()
            return NextQuestionResponse(is_complete=True)
            
        phrased_text = await planner_service.phrase_question(
            question_id=next_q["question_id"],
            base_text=next_q["text"],
            language=request.language
        )
        
        return NextQuestionResponse(
            question_id=next_q["question_id"],
            question_text=phrased_text,
            is_complete=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Questionnaire planner failed: {str(e)}")

class CreatePatientRequest(BaseModel):
    name: str
    sex: Optional[str] = None
    preferred_language: Optional[str] = None

@router.post("/patient")
async def create_patient(
    request: CreatePatientRequest,
    session: AsyncSession = Depends(get_async_session)
):
    patient = Patient(name=request.name, sex=request.sex, preferred_language=request.preferred_language)
    session.add(patient)
    await session.commit()
    await session.refresh(patient)
    return {"id": patient.id, "name": patient.name, "preferred_language": patient.preferred_language}

class CreateEncounterRequest(BaseModel):
    patient_id: int

@router.post("/session")
async def create_encounter(
    request: CreateEncounterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    encounter = Encounter(patient_id=request.patient_id)
    session.add(encounter)
    await session.commit()
    await session.refresh(encounter)
    
    await audit_logger.log(
        session=session,
        actor="system",
        action="ENCOUNTER_CREATED",
        entity_type="Encounter",
        entity_id=str(encounter.id),
        metadata={"patient_id": request.patient_id}
    )
    await session.commit()
    return {"id": encounter.id, "status": encounter.status}


from app.services.questionnaire.schema import get_schema

@router.get("/schema")
async def fetch_schema(pathway: str = "allopathy"):
    return get_schema(pathway)

class BulkSubmitRequest(BaseModel):
    encounter_id: int
    language: str = "en"
    clinical_pathway: str = "allopathy"
    responses: List[Dict[str, Any]]


class SubmitResponseRequest(BaseModel):
    encounter_id: int
    question_id: str
    transcript_text: str
    language: str = "en"
    input_method: str = "voice"

from app.services.extraction.clinical_extractor import extractor_service
import asyncio

async def background_extract_facts(encounter_id: int, transcript_text: str):
    try:
        extracted_data = await extractor_service.extract_facts(transcript_text)
        
        async with async_session_maker() as session:
            facts = []
            for f in extracted_data.get("facts", []):
                fact = ClinicalFact(
                    encounter_id=encounter_id,
                    category=f["category"],
                    field=f["field"],
                    value=f["value"],
                    source_type=f["source_type"],
                    source_reference=f.get("source_text", ""),
                    confidence=f.get("confidence", 0.90),
                    verification_status=f["verification_status"]
                )
                session.add(fact)
                facts.append(fact)
                
            await session.commit()
            
            # Audit log each fact creation
            for fact in facts:
                await session.refresh(fact)
                await audit_logger.log(
                    session=session,
                    actor="system",
                    action="CLINICAL_FACT_CREATED",
                    entity_type="ClinicalFact",
                    entity_id=str(fact.id),
                    metadata={"encounter_id": encounter_id, "field": fact.field, "value": fact.value}
                )
            await session.commit()
    except Exception as e:
        print(f"Background extraction failed: {e}")

@router.post("/response")
async def submit_response(
    request: SubmitResponseRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    # Store the raw patient response in QuestionnaireResponse table FAST
    qr = QuestionnaireResponse(
        encounter_id=request.encounter_id,
        question_id=request.question_id,
        question_text="", # Optional, could look it up
        answer=request.transcript_text,
        language=request.language,
        source=request.input_method
    )
    session.add(qr)
    await session.commit()

    # Move heavy LLM extraction to background task
    background_tasks.add_task(background_extract_facts, request.encounter_id, request.transcript_text)

    return {"status": "success", "extracted_facts": []}



@router.post("/bulk-response")
async def bulk_submit_response(
    request: BulkSubmitRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    # Update encounter with pathway
    stmt_enc = select(Encounter).where(Encounter.id == request.encounter_id)
    res_enc = await session.execute(stmt_enc)
    encounter = res_enc.scalar_one_or_none()
    if encounter:
        encounter.status = "intake_completed"
        # We could save clinical_pathway to encounter if column exists, or rely on responses
    
    qrs = []
    combined_transcript = ""
    for r in request.responses:
        q_id = r.get("question_id")
        q_ans = r.get("answer", "")
        if not q_ans: continue
        combined_transcript += f"{q_id}: {q_ans}\n"
        
        qr = QuestionnaireResponse(
            encounter_id=request.encounter_id,
            question_id=q_id,
            question_text=r.get("question_text", ""),
            answer=str(q_ans),
            language=request.language,
            source="form"
        )
        session.add(qr)
        qrs.append(qr)
    
    await session.commit()
    
    # Run heavy extraction on combined transcript
    background_tasks.add_task(background_extract_facts, request.encounter_id, combined_transcript)
    return {"status": "success", "extracted_facts": []}
