import asyncio
from app.db.database import get_async_session, engine
from app.db.models.core import Patient, Document, AuditLog
from app.db.models.encounter import Encounter
from sqlalchemy.future import select

async def run_test():
    async for session in get_async_session():
        print("1. Creating Test Patient & Consultation...")
        patient = Patient(name="Test Doc Patient")
        session.add(patient)
        await session.flush()
        
        encounter = Encounter(patient_id=patient.id, status="IN_REVIEW")
        session.add(encounter)
        await session.flush()
        
        print("2. Uploading Document for Consultation A...")
        doc = Document(
            patient_id=patient.id,
            consultation_id=encounter.id,
            uploaded_by="doctor_A",
            hospital_id="HOSP-TEST",
            document_type="prescription",
            original_filename="test.pdf",
            storage_path=f"HOSP-TEST/{patient.id}/test.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )
        session.add(doc)
        await session.commit()
        
        print("3. Testing Document Access (Consultation Active)...")
        from app.api.routes.documents import verify_authorization
        try:
            await verify_authorization(session, "doctor_A", doc)
            print("   ✅ Access Granted. Signed URL would be generated.")
        except Exception as e:
            print(f"   ❌ Access Denied unexpectedly: {e}")
            
        print("4. Marking Consultation COMPLETED...")
        encounter.status = "COMPLETED"
        await session.commit()
        
        print("5. Testing Document Access (Consultation Completed)...")
        try:
            await verify_authorization(session, "doctor_A", doc)
            print("   ❌ Access Granted unexpectedly!")
        except Exception as e:
            print(f"   ✅ Access Denied correctly. Reason: {e.detail}")
            
        print("6. Verifying Document Still Exists in Database...")
        check_doc = await session.get(Document, doc.id)
        if check_doc:
            print("   ✅ Document persists permanently.")
        else:
            print("   ❌ Document was deleted!")
            
        break

if __name__ == "__main__":
    asyncio.run(run_test())
