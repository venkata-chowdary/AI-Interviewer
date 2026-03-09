import asyncio
from sqlmodel import select
from db import async_session_factory
from models.resume import ResumeMetadata
from models.interview import Interview

async def get_test_resume():
    async with async_session_factory() as session:
        result = await session.exec(select(ResumeMetadata))
        resumes = result.all()
        if not resumes:
            print("No resumes found in the DB. Please upload a resume first.")
            return None
        return resumes[0]

if __name__ == "__main__":
    resume = asyncio.run(get_test_resume())
    if resume:
        print(f"Found resume: {resume.id}")
