import asyncio
from app.db.database import engine
from app.db.models.base import Base
import app.db.models

async def recreate_tables():
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("DROP TABLE IF EXISTS audit_logs CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS ocr_results CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS evidence CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS documents CASCADE;"))
        await conn.run_sync(Base.metadata.create_all)
        print("Dropped and recreated tables successfully.")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
