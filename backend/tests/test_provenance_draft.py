import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_async_session, engine
from app.db.models import Patient, Encounter, Document, ClinicalFact, Evidence
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

@pytest.mark.asyncio
async def test_provenance_draft():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        from app.db.database import async_session_maker
        async with async_session_maker() as test_session:
            
            # Create patient
            patient = Patient(name="Test Patient", sex="Male", preferred_language="en")
            test_session.add(patient)
            await test_session.commit()
            await test_session.refresh(patient)
    
            # Create encounter
            encounter = Encounter(patient_id=patient.id)
            test_session.add(encounter)
            await test_session.commit()
            await test_session.refresh(encounter)
    
            # Mock previous consultation document
            consult_doc = Document(
                patient_id=patient.id,
                document_type="consultation",
                original_filename="Previous_Consultation_12-06-2026.pdf",
                document_date=datetime(2026, 6, 12),
                mime_type="application/pdf",
                storage_path="/tmp/mock_consult.pdf"
            )
            test_session.add(consult_doc)
    
            # Mock previous prescription document
            rx_doc = Document(
                patient_id=patient.id,
                document_type="prescription",
                original_filename="Prescription_12-06-2026.pdf",
                document_date=datetime(2026, 6, 12),
                mime_type="application/pdf",
                storage_path="/tmp/mock_rx.pdf"
            )
            test_session.add(rx_doc)
            await test_session.commit()
            await test_session.refresh(consult_doc)
            await test_session.refresh(rx_doc)
    
            # Create clinical facts and associate evidence
            # 1. Chief complaint (patient answer)
            cc_fact = ClinicalFact(
                encounter_id=encounter.id,
                category="chief_complaint",
                field="symptom",
                value="Headache",
                source_type="patient_answer",
                source_reference="I have a headache for three days.",
                confidence=0.99,
                verification_status="unverified"
            )
            test_session.add(cc_fact)
    
            # 2. Medical history (diabetes from previous consultation)
            mh_fact = ClinicalFact(
                encounter_id=encounter.id,
                category="medical_history",
                field="condition",
                value="Diabetes mellitus",
                source_type="document",
                confidence=0.96,
                verification_status="unverified"
            )
            test_session.add(mh_fact)
            await test_session.commit()
            await test_session.refresh(mh_fact)
    
            ev_mh = Evidence(
                clinical_fact_id=mh_fact.id,
                source_type="document",
                document_id=consult_doc.id,
                page_number=3,
                excerpt="Known history of diabetes mellitus.",
                confidence=0.96
            )
            test_session.add(ev_mh)
    
            # 3. Previous medication (from prescription)
            rx_fact = ClinicalFact(
                encounter_id=encounter.id,
                category="previous_medication",
                field="medication",
                value="Metformin 500 mg",
                source_type="document",
                confidence=0.99,
                verification_status="unverified"
            )
            test_session.add(rx_fact)
            await test_session.commit()
            await test_session.refresh(rx_fact)
    
            ev_rx = Evidence(
                clinical_fact_id=rx_fact.id,
                source_type="document",
                document_id=rx_doc.id,
                page_number=1,
                excerpt="Metformin 500 mg",
                confidence=0.99
            )
            test_session.add(ev_rx)
            await test_session.commit()
    
            # Hit the draft endpoint
            response = await async_client.get(f"/api/v1/encounters/{encounter.id}/draft")
            assert response.status_code == 200
            data = response.json()
    
            # Assert chief complaint
            cc = data["chief_complaint"][0]
            assert cc["value"] == "Headache"
            assert cc["sources"][0]["type"] == "patient_answer"
            assert "headache" in cc["sources"][0]["evidence"]
    
            # Assert medical history
            mh = data["medical_history"][0]
            assert mh["value"] == "Diabetes mellitus"
            assert mh["sources"][0]["type"] == "document"
            assert mh["sources"][0]["id"] == f"DOC-{consult_doc.id}"
            assert mh["sources"][0]["page"] == 3
            assert mh["sources"][0]["evidence"] == "Known history of diabetes mellitus."
    
            # Assert previous prescriptions collection
            rx = data["previous_prescriptions"][0]
            assert rx["id"] == f"RX-{rx_doc.id}"
            assert rx["document_id"] == rx_doc.id
            assert rx["page_count"] == 1
            assert rx["viewable"] is True
            
            # Assert AI summary
            ai_summary = data["ai_clinical_summary"]
            assert "diabetes mellitus" in ai_summary.lower()
            assert f"DOC-{consult_doc.id}" in ai_summary or "Consultation" in ai_summary
            assert "Page 3" in ai_summary
    