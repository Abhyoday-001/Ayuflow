from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    identifier: str
    password: str
    role: str

@router.post("/login")
async def login(req: LoginRequest):
    # Dummy authentication for the prototype
    if req.role not in ["PATIENT", "DOCTOR", "AYUSH_WORKER"]:
        return {"error": "Invalid role"}
    
    return {
        "access_token": "dummy_token_123",
        "token_type": "bearer",
        "user": {
            "id": "u-123",
            "name": req.identifier,
            "role": req.role,
            "hospital_id": "HOSP-001"
        }
    }
