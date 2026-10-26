import os
import tempfile
import uuid
import io
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_async_session
from app.db.models.core import Document, AuditLog, Patient, ClinicalFact
from app.db.models.encounter import Encounter
from app.services.gcs_storage import gcs_storage_service
from app.services.ocr.router import ocr_router

router = APIRouter()

class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    consultation_id: Optional[int]
    document_type: str
    original_filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    ocr_status: str
    
    class Config:
        from_attributes = True

async def verify_authorization(session: AsyncSession, doctor_id: str, document: Document, accessing_consultation_id: int = None):
    # If the doctor is requesting access via a specific active consultation
    if accessing_consultation_id:
        encounter = await session.get(Encounter, accessing_consultation_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Active consultation context not found")
            
        if encounter.patient_id != document.patient_id:
            raise HTTPException(status_code=403, detail="Consultation does not belong to the patient who owns this document")
            
        if encounter.status in ["FINALIZED", "COMPLETED"]:
            raise HTTPException(
                status_code=403, 
                detail="The provided consultation is completed. Access to new document URLs via this consultation is revoked."
            )
        # In a real app, verify `doctor_id` is assigned to `encounter`
    else:
        # Fallback strict check: if no active consultation context is provided, we must assume they are trying to access it out-of-context.
        # This requires higher-level permissions (e.g. Hospital Admin or the Patient themselves).
        # For this prototype, we require an active consultation context.
        raise HTTPException(
            status_code=403, 
            detail="Access to historical records requires an active consultation context."
        )
    return True

async def log_audit(session: AsyncSession, request: Request, actor: str, action: str, doc_id: int, patient_id: int, consultation_id: int = None):
    log = AuditLog(
        user_id=actor,
        action=action,
        document_id=doc_id,
        patient_id=patient_id,
        consultation_id=consultation_id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )
    session.add(log)
    await session.commit()

@router.post("/patients/{patient_id}/documents", response_model=DocumentResponse)
async def upload_patient_document(
    patient_id: int,
    request: Request,
    document: UploadFile = File(...),
    consultation_id: Optional[int] = None,
    doctor_id: str = "current_doctor",
    hospital_id: str = "HOSP-001",
    session: AsyncSession = Depends(get_async_session)
):
    # Validate patient
    patient = await session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate file format and size
    ext = os.path.splitext(document.filename)[1].lower()
    if ext not in ['.pdf', '.png', '.jpg', '.jpeg']:
        raise HTTPException(status_code=415, detail="Unsupported file format.")
    
    file_bytes = await document.read()
    file_size = len(file_bytes)
    if file_size > 10 * 1024 * 1024: # 10MB limit
        raise HTTPException(status_code=413, detail="File too large")
        
    file_obj = io.BytesIO(file_bytes)
    
    doc_type = "prescription" if "presc" in document.filename.lower() else ("lab_report" if "lab" in document.filename.lower() else "other")
    
    # Pre-save document to DB to get ID
    doc = Document(
        patient_id=patient_id,
        consultation_id=consultation_id,
        uploaded_by=doctor_id,
        hospital_id=hospital_id,
        document_type=doc_type,
        original_filename=document.filename,
        storage_path="pending", 
        file_size=file_size,
        mime_type=document.content_type,
        ocr_status="processing"
    )
    session.add(doc)
    await session.flush() # Get doc.id without committing
    
    # Define storage path: {hospital_id}/{patient_id}/{doc_id}/original{ext}
    storage_path = f"{hospital_id}/{patient_id}/{doc.id}/original{ext}"
    doc.storage_path = storage_path
    
    # Upload to GCS Cloud
    success = gcs_storage_service.upload_file(file_obj, storage_path, document.content_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upload to Google Cloud Storage")
        
    await session.commit()
    await session.refresh(doc)
    
    # Log audit
    await log_audit(session, request, doctor_id, "DOCUMENT_UPLOADED", doc.id, patient_id, consultation_id)
    
    # Kickoff async OCR - running inline here for demo purposes to simulate pipeline
    try:
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'wb') as f:
            f.write(file_bytes)
        
        results = await ocr_router.extract_text(temp_path)
        if "clinical_entities" in results:
            for entity in results["clinical_entities"]:
                fact = ClinicalFact(
                    encounter_id=consultation_id,
                    category=entity.get("type", "medical_history").lower(),
                    field=entity.get("type", "entity"),
                    value=entity.get("value", ""),
                    source_type="document",
                    source_reference=f"Document: {document.filename}",
                    confidence=0.9
                )
                session.add(fact)
        
        doc.ocr_status = "completed"
        await session.commit()
    except Exception as e:
        print(f"OCR Pipeline Failed: {e}")
        doc.ocr_status = "failed"
        await session.commit()
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
    
    return doc

@router.get("/patients/{patient_id}/documents", response_model=List[DocumentResponse])
async def list_patient_documents(
    patient_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Document).where(Document.patient_id == patient_id).order_by(Document.created_at.desc())
    res = await session.execute(stmt)
    return res.scalars().all()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_metadata(
    document_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/{document_id}/access")
async def get_document_access(
    document_id: int,
    request: Request,
    consultation_id: int,
    doctor_id: str = "current_doctor",
    session: AsyncSession = Depends(get_async_session)
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Security Check: We must pass the *accessing* consultation ID, not the one it was uploaded in.
    await verify_authorization(session, doctor_id, doc, accessing_consultation_id=consultation_id)
    
    # Generate GCS signed URL (expires in 15 mins)
    url = gcs_storage_service.generate_presigned_url(doc.storage_path, expiration_seconds=900)
    
    # Log Audit
    await log_audit(session, request, doctor_id, "SIGNED_URL_GENERATED", doc.id, doc.patient_id, doc.consultation_id)
    
    return {"url": url, "expires_in": 900}

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    request: Request,
    doctor_id: str = "current_doctor",
    session: AsyncSession = Depends(get_async_session)
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Check permissions (only uploader or admin can delete)
    if doc.uploaded_by != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
        
    # Delete from GCS
    gcs_storage_service.delete_file(doc.storage_path)
    
    # Delete from DB
    await session.delete(doc)
    await session.commit()
    
    # Log audit
    await log_audit(session, request, doctor_id, "DOCUMENT_DELETED", doc.id, doc.patient_id, doc.consultation_id)
    
    return {"status": "success"}

# Maintained for compatibility during migration
@router.post("/ocr")
async def extract_document_text_legacy(
    request: Request,
    document: UploadFile = File(...),
    patient_id: int = 1,
    encounter_id: int = 1,
    session: AsyncSession = Depends(get_async_session)
):
    return await upload_patient_document(patient_id, request, document, encounter_id, "legacy_frontend", "HOSP-001", session)
