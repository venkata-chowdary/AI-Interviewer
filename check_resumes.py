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
        resume = res.first()
        if resume:
            print(f"Status: {resume.analysis_status}")
            print(f"Skills: {resume.skills}")
            print(f"Experience: {resume.experience_level}")
            print(f"Years of Experience: {resume.years_of_experience}")
            print(f"Summary: {resume.resume_summary}")

asyncio.run(check())
