import asyncio
from db import async_session_factory
from models.resume import ResumeMetadata
from sqlmodel import select

async def main():
    async with async_session_factory() as session:
        result = await session.exec(select(ResumeMetadata).order_by(ResumeMetadata.created_at.desc()))
        resume = result.first()
        if resume:
            print(f"Latest Resume ID: {resume.id}")
            print(f"Status: {resume.analysis_status}")
            print(f"Skills: {resume.skills}")
            print(f"Experience: {resume.experience_level}")
            print(f"Years of Experience: {resume.years_of_experience}")
            print(f"Summary: {resume.resume_summary}")
        else:
            print("No resumes found.")

asyncio.run(main())
