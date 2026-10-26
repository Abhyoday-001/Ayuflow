from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_async_session
from app.services.asr.router import asr_router
from app.services.llm.router import llm_router
from app.services.ocr.router import ocr_router

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"database": "healthy"}
    except Exception as e:
        return {"database": "unhealthy", "reason": str(e)}

@router.get("/health/providers")
async def health_providers():
    return {
        "asr": asr_router.get_provider_status(),
        "llm": llm_router.get_provider_status(),
        "ocr": ocr_router.get_provider_status()
    }
