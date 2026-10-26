import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
from typing import Dict, Any

from app.main import app
from app.db.database import get_async_session, engine
from app.db.models.base import Base

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_e2e_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Patient
        res = await client.post("/api/v1/intake/patient", json={"name": "Test Patient", "sex": "Male"})
        assert res.status_code == 200
        patient_data = res.json()
        patient_id = patient_data["id"]

        # 2. Create Encounter
        res = await client.post("/api/v1/intake/session", json={"patient_id": patient_id})
        assert res.status_code == 200
        encounter_data = res.json()
        encounter_id = encounter_data["id"]

        # 3. Submit Response (Mocking LLM in this test or assuming it returns deterministic fallback if unconfigured)
        # To avoid calling real Gemini, we could mock the extractor_service, but we will test the actual endpoint.
        # Since it's an E2E test, if LLM is unavailable, it throws 500, but we can mock the router specifically for tests.
        
        # We will dynamically mock the llm_router for this test run.
        from app.services.extraction.clinical_extractor import extractor_service
        async def mock_generate_structured(*args, **kwargs):
            return {
                "facts": [
                    {
                        "category": "symptom",
                        "field": "fever",
                        "value": True,
                        "duration": "3 days",
                        "source_text": "Mujhe teen din se bukhar hai.",
                        "confidence": 0.95,
                        "verification_status": "unverified",
                        "source_type": "patient_statement"
                    }
                ]
            }
        
        # Patch the llm_router inside extractor
        original_generate = extractor_service.llm.generate_structured
        extractor_service.llm.generate_structured = mock_generate_structured
        
        res = await client.post("/api/v1/intake/response", json={
            "encounter_id": encounter_id,
            "question_id": "chief_complaint",
            "transcript_text": "Mujhe teen din se bukhar hai. Raat ko zyada hota hai.",
            "language": "hi",
            "input_method": "voice"
        })
        assert res.status_code == 200, res.text
        
        # Check fact in DB via endpoint (wait for background task)
        await asyncio.sleep(0.5)
        res = await client.get(f"/api/v1/encounters/{encounter_id}/facts")
        db_facts = res.json()["facts"]
        assert len(db_facts) == 1
        fact_id = db_facts[0]["id"]
        assert db_facts[0]["verification_status"] == "unverified"

        # 4. Doctor accepts fact
        res = await client.post(f"/api/v1/reviews/{encounter_id}", json={
            "fact_id": fact_id,
            "action": "accept",
            "reviewer_id": "doc-123"
        })
        assert res.status_code == 200
        assert res.json()["fact"]["status"] == "verified"

        # 5. Doctor finalizes encounter
        res = await client.post(f"/api/v1/reviews/{encounter_id}/finalize", json={
            "reviewer_id": "doc-123"
        })
        assert res.status_code == 200

        # Verify it's finalized
        res = await client.get(f"/api/v1/encounters/{encounter_id}")
        assert res.json()["status"] == "FINALIZED"

        # 6. Audit logs exist
        res = await client.get(f"/api/v1/encounters/{encounter_id}/audit")
        logs = res.json()["audit_logs"]
        assert len(logs) > 0
        actions = [log["action"] for log in logs]
        assert "ENCOUNTER_CREATED" in actions
        assert "CLINICAL_FACT_CREATED" in actions
        assert "CLINICAL_FACT_ACCEPTED" in actions
        assert "ENCOUNTER_FINALIZED" in actions

        # 7. FHIR export
        res = await client.get(f"/api/v1/encounters/{encounter_id}/fhir")
        assert res.status_code == 200
        bundle = res.json()
        assert bundle["resourceType"] == "Bundle"
        
        # Verify unverified facts aren't in FHIR? Wait, we verified this fact, so it should be there.
        conditions = [e for e in bundle["entry"] if e["resource"]["resourceType"] == "Condition"]
        assert len(conditions) == 1
        assert str(conditions[0]["resource"]["code"]["text"]).lower() == "true" # fever = true

        # Restore original function
        extractor_service.llm.generate_structured = original_generate
