import asyncio
from fastapi import HTTPException
from app.db.database import get_async_session
from app.db.models.core import Patient, Document, AuditLog
from app.db.models.encounter import Encounter
from sqlalchemy.future import select

# Dummy Request class to mock FastAPI Request
class DummyRequest:
    class Client:
        host = "127.0.0.1"
    client = Client()
    headers = {"user-agent": "test-agent"}

async def run_gcs_tests():
    async for session in get_async_session():
        print("--- GCS Storage & Access Control Test Suite ---\n")
        
        print("A. Setting up Test Patient & Consultation C001...")
        patient = Patient(name="GCS Patient")
        session.add(patient)
        await session.flush()
        
        encounter1 = Encounter(patient_id=patient.id, status="IN_REVIEW")
        session.add(encounter1)
        await session.flush()
        
        print("B. Authorized Upload (Simulated)...")
        doc = Document(
            patient_id=patient.id,
            consultation_id=encounter1.id, # Original upload context
            uploaded_by="doctor_A",
            hospital_id="HOSP-GCS",
            document_type="lab_report",
            original_filename="blood_test.pdf",
            storage_path=f"HOSP-GCS/{patient.id}/blood_test.pdf",
            file_size=2048,
            mime_type="application/pdf",
            ocr_status="completed"
        )
        session.add(doc)
        await session.commit()
        print("   ✅ Upload successful. Metadata saved.\n")
        
        print("C. Authorized doctor accessing active consultation...")
        from app.api.routes.documents import verify_authorization, log_audit
        try:
            await verify_authorization(session, "doctor_A", doc, accessing_consultation_id=encounter1.id)
            await log_audit(session, DummyRequest(), "doctor_A", "SIGNED_URL_GENERATED", doc.id, patient.id, encounter1.id)
            print("   ✅ Access Granted. Signed URL would be generated.")
        except Exception as e:
            print(f"   ❌ Failed unexpectedly: {e}")
            
        print("\nD. Consultation completed...")
        encounter1.status = "COMPLETED"
        await session.commit()
        
        print("\nE. Completed Consultation Access Check...")
        try:
            await verify_authorization(session, "doctor_A", doc, accessing_consultation_id=encounter1.id)
            print("   ❌ Access Granted unexpectedly!")
        except HTTPException as e:
            if e.status_code == 403:
                print("   ✅ Access Denied (403 Forbidden). Doctor A cannot use C001 anymore.")
            else:
                print(f"   ❌ Failed with wrong error: {e}")
                
        print("\nF. Patient starts a new consultation C002 (New Doctor B)...")
        encounter2 = Encounter(patient_id=patient.id, status="IN_REVIEW")
        session.add(encounter2)
        await session.flush()
        
        try:
            await verify_authorization(session, "doctor_B", doc, accessing_consultation_id=encounter2.id)
            await log_audit(session, DummyRequest(), "doctor_B", "SIGNED_URL_GENERATED", doc.id, patient.id, encounter2.id)
            print("   ✅ Access Granted for Doctor B on historical document through C002.")
        except Exception as e:
            print(f"   ❌ Failed unexpectedly: {e}")
            
        print("\nI. Audit Log Verification...")
        stmt = select(AuditLog).where(AuditLog.document_id == doc.id)
        res = await session.execute(stmt)
        logs = res.scalars().all()
        if logs:
            print(f"   ✅ Found {len(logs)} audit records for document access.")
            for log in logs:
                print(f"      - {log.action} by {log.user_id} via Encounter {log.consultation_id}")
        else:
            print("   ❌ Audit logs missing!")
            
        break

if __name__ == "__main__":
    asyncio.run(run_gcs_tests())
