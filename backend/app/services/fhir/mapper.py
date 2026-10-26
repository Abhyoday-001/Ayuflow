from typing import Dict, Any, List
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview

class FHIRMapper:
    @staticmethod
    def map_patient(patient: Patient) -> Dict[str, Any]:
        return {
            "resourceType": "Patient",
            "id": str(patient.id),
            "identifier": [{"value": patient.external_patient_id}] if patient.external_patient_id else [],
            "name": [{"text": patient.name}],
            "gender": patient.sex.lower() if patient.sex else "unknown",
            "birthDate": patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else None
        }

    @staticmethod
    def map_encounter(encounter: Encounter, patient: Patient) -> Dict[str, Any]:
        return {
            "resourceType": "Encounter",
            "id": str(encounter.id),
            "status": "finished" if encounter.status == "FINALIZED" else "in-progress",
            "subject": {"reference": f"Patient/{patient.id}"},
            "period": {
                "start": encounter.created_at.isoformat() + "Z"
            }
        }

    @staticmethod
    def map_condition(fact: ClinicalFact, patient_id: int, encounter_id: int) -> Dict[str, Any]:
        # Only map verified facts
        if fact.verification_status != "verified":
            return None
            
        return {
            "resourceType": "Condition",
            "id": f"fact-{fact.id}",
            "clinicalStatus": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
            },
            "verificationStatus": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]
            },
            "code": {
                "text": fact.value
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"}
        }

fhir_mapper = FHIRMapper()
