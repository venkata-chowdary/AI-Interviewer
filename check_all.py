import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from models.resume import ResumeMetadata
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"ssl": True})
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check():
    async with async_session_factory() as session:
        q = select(ResumeMetadata).order_by(ResumeMetadata.created_at.desc())
        res = await session.exec(q)
        resumes = res.all()
        for r in resumes:
            print(f"ID: {r.id} | Status: {r.analysis_status} | Skills: {r.skills} | Level: {r.experience_level}")

asyncio.run(check())
