import asyncio
from app.db.database import engine
from app.db.models.base import Base
# import all models so they register with Base
import app.db.models

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
