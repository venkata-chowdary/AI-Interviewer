from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

from sqlalchemy.pool import NullPool

# Async Engine with SSL and NullPool for script runner compatibility
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": True},
    poolclass=NullPool,
)

# Async Session factory
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

# Initialize tables
async def init_db():
    from models.resume import ResumeMetadata
    from auth.models import User
    from models.interview import Interview
    from models.question import Question
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        await conn.execute(
            text(
                """
                ALTER TABLE IF EXISTS interview
                    ADD COLUMN IF NOT EXISTS evaluation_retry_count INTEGER NOT NULL DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS evaluation_last_error TEXT,
                    ADD COLUMN IF NOT EXISTS evaluation_failed_at TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS evaluation_lock_until TIMESTAMPTZ;
                """
            )
        )
