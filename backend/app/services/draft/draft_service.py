from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.models import Patient, Encounter, ClinicalFact, Evidence, Document
import json
from app.services.rag.conflicts import detect_conflicts
from app.services.rag.red_flags import detect_red_flags

class MedicalDraftService:
    async def generate_draft(self, session: AsyncSession, encounter_id: int) -> dict:
        encounter = await session.get(Encounter, encounter_id)
        if not encounter:
            raise ValueError("Encounter not found")
        patient = await session.get(Patient, encounter.patient_id)
        
        # Load facts with evidence and document
        result = await session.execute(
            select(ClinicalFact)
            .where(ClinicalFact.encounter_id == encounter_id)
        )
        facts = result.scalars().all()
        
        fact_ids = [f.id for f in facts]
        evidences = []
        if fact_ids:
            ev_result = await session.execute(
                select(Evidence).options(selectinload(Evidence.document)).where(Evidence.clinical_fact_id.in_(fact_ids))
            )
            evidences = ev_result.scalars().all()

        ev_map = {}
        for ev in evidences:
            if ev.clinical_fact_id not in ev_map:
                ev_map[ev.clinical_fact_id] = []
            ev_map[ev.clinical_fact_id].append(ev)

        draft = {
            "chief_complaint": [],
            "current_symptoms": [],
            "medical_history": [],
            "current_medications": [],
            "allergies": [],
            "previous_prescriptions": [],
            "abnormal_labs": [],
            "questionnaire_summary": "",
            "ai_clinical_summary": "",
            "conflicts": [],
            "red_flags": []
        }

        # Also get patient documents
        doc_result = await session.execute(
            select(Document).where(Document.patient_id == patient.id).order_by(Document.created_at.desc())
        )
        documents = doc_result.scalars().all()

        for doc in documents:
            if doc.document_type == "prescription":
                draft["previous_prescriptions"].append({
                    "id": f"RX-{doc.id}",
                    "date": doc.document_date.isoformat() if doc.document_date else doc.created_at.isoformat(),
                    "document_id": doc.id,
                    "document_name": doc.document_name,
                    "page_count": doc.page_count,
                    "viewable": True
                })

        for fact in facts:
            fact_data = {
                "id": fact.id,
                "value": fact.value,
                "confidence": fact.confidence,
                "verification_status": fact.verification_status,
                "sources": []
            }
            
            # Map evidence to sources
            for ev in ev_map.get(fact.id, []):
                source_data = {
                    "type": ev.source_type,
                    "evidence": ev.excerpt,
                    "viewable": False
                }
                if ev.document:
                    source_data.update({
                        "id": f"DOC-{ev.document.id}",
                        "name": ev.document.document_name,
                        "date": ev.document.document_date.isoformat() if ev.document.document_date else None,
                        "page": ev.page_number,
                        "viewable": True
                    })
                fact_data["sources"].append(source_data)

            # Fallback if no specific evidence object but source_reference exists (e.g. older facts)
            if not fact_data["sources"] and fact.source_reference:
                fact_data["sources"].append({
                    "type": fact.source_type,
                    "evidence": fact.source_reference,
                    "viewable": False
                })

            if fact.category == "chief_complaint":
                draft["chief_complaint"].append(fact_data)
            elif fact.category == "symptom":
                draft["current_symptoms"].append(fact_data)
            elif fact.category == "medical_history":
                fact_data["status"] = "previously_documented" if fact.source_type == "document" else "patient_reported"
                draft["medical_history"].append(fact_data)
            elif fact.category == "medication":
                fact_data["status"] = "patient_reported"
                draft["current_medications"].append(fact_data)
            elif fact.category == "allergy":
                draft["allergies"].append(fact_data)
            elif fact.category == "lab_result":
                is_abnormal = False
                if "hba1c" in str(fact.field).lower() and float(fact.value) > 6.5:
                    is_abnormal = True
                if "glucose" in str(fact.field).lower() and float(fact.value) > 140:
                    is_abnormal = True
                fact_data["abnormal"] = is_abnormal
                if is_abnormal:
                    draft["abnormal_labs"].append(fact_data)

        # Basic AI summary generation
        summary_lines = []
        if draft["chief_complaint"]:
            cc_vals = [f["value"] for f in draft["chief_complaint"] if f["value"]]
            summary_lines.append(f"The patient reports {', '.join(cc_vals)}.")
        
        hist_vals = []
        hist_sources = []
        for f in draft["medical_history"]:
            if f["value"] and any(s.get("type") == "document" for s in f.get("sources", [])):
                hist_vals.append(f["value"])
                doc_sources = [s for s in f.get("sources", []) if s.get("type") == "document"]
                if doc_sources:
                    s = doc_sources[0]
                    page_str = f", Page {s['page']}" if s.get('page') else ""
                    hist_sources.append(f"{f['value']} -> {s.get('name', 'Document')}{page_str}")

        if hist_vals:
            summary_lines.append(f"Previous records document {', '.join(hist_vals)}.")
        
        if hist_sources:
            summary_lines.append("\nSource references:\n" + "\n".join(hist_sources))

        
        draft["conflicts"] = detect_conflicts(facts)
        draft["red_flags"] = detect_red_flags(facts)

        draft["ai_clinical_summary"] = "\n".join(summary_lines)
        if not draft["allergies"]:
            draft["allergies"] = "Not assessed in current questionnaire."

        return draft

draft_service = MedicalDraftService()
