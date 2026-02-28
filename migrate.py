import asyncio
from db import engine
from sqlmodel import SQLModel
from models.resume import ResumeMetadata
from auth.models import User

async def migrate():
    print("Dropping and recreating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(migrate())
