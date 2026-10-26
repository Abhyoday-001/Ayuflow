from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview
from .mapper import fhir_mapper
from app.services.audit.logger import audit_logger

class FHIRExporter:
    @staticmethod
    async def export_encounter_bundle(session: AsyncSession, encounter_id: int, actor: str) -> Dict[str, Any]:
        encounter = await session.get(Encounter, encounter_id)
        if not encounter:
            raise ValueError("Encounter not found")
            
        patient = await session.get(Patient, encounter.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Get facts for the encounter
        facts_result = await session.execute(
            select(ClinicalFact).where(ClinicalFact.encounter_id == encounter_id)
        )
        facts = facts_result.scalars().all()

        entries = []
        
        # 1. Patient
        entries.append({
            "fullUrl": f"urn:uuid:patient-{patient.id}",
            "resource": fhir_mapper.map_patient(patient)
        })
        
        # 2. Encounter
        entries.append({
            "fullUrl": f"urn:uuid:encounter-{encounter.id}",
            "resource": fhir_mapper.map_encounter(encounter, patient)
        })
        
        # 3. Verified Conditions/Facts
        for fact in facts:
            if fact.category == "symptom" or fact.category == "diagnosis":
                condition_resource = fhir_mapper.map_condition(fact, patient.id, encounter.id)
                if condition_resource: # only verified facts will map
                    entries.append({
                        "fullUrl": f"urn:uuid:condition-{fact.id}",
                        "resource": condition_resource
                    })

        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": entries
        }

        # Log export
        await audit_logger.log(
            session=session,
            actor=actor,
            action="FHIR_EXPORT_CREATED",
            entity_type="Encounter",
            entity_id=str(encounter_id)
        )
        await session.commit()

        return bundle

fhir_exporter = FHIRExporter()
