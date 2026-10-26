import asyncio
import httpx

async def seed_demo():
    print("Seeding AyuFlow Demo Data...")
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
        # Create patient
        res = await client.post("/api/v1/intake/patient", json={"name": "Demo Patient", "sex": "Female"})
        patient_id = res.json()["id"]
        print(f"Created Patient {patient_id}")
        
        # Create encounter
        res = await client.post("/api/v1/intake/session", json={"patient_id": patient_id})
        encounter_id = res.json()["id"]
        print(f"Created Encounter {encounter_id}")
        
        # Submit response
        text = "Mujhe teen din se lagatar bukhar hai, aur kal se sir dard bhi ho raha hai."
        print(f"Submitting text: {text}")
        res = await client.post("/api/v1/intake/response", json={
            "encounter_id": encounter_id,
            "transcript_text": text
        })
        facts = res.json()["extracted_facts"]
        print(f"Extracted Facts: {len(facts)}")
        
        print(f"\nSeed Complete. Open Doctor Dashboard with Encounter ID: {encounter_id}")

if __name__ == "__main__":
    asyncio.run(seed_demo())
