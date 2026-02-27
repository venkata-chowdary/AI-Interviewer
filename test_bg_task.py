import asyncio
from uuid import uuid4
from db import async_session_factory
from models.resume import ResumeMetadata
from ai.service import analyse_resume
from sqlmodel import select

async def main():
    print("Testing analyse_resume directly...")
    async with async_session_factory() as session:
        # Create a dummy resume first
        new_resume = ResumeMetadata(
            user_id="test_user_ai",
            file_name="dummy.pdf",
            resume_hash="dummy_hash_12345"
        )
        session.add(new_resume)
        await session.commit()
        await session.refresh(new_resume)
        resume_id = new_resume.id
        print(f"Created dummy resume in DB: {resume_id}")

    test_text = """
    John Doe
    Software Engineer

    Summary: Passionate and driven software engineer with 5 years of experience building scalable web applications. Strong background in Python, FastAPI, and Postgres.

    Skills:
    - Programming: Python, JavaScript, SQL
    - Frameworks: FastAPI, React, Node.js
    - Tools: Docker, Git, AWS
    
    Experience:
    Sr. Backend Developer @ TechCorp (2020 - Present)
    - Built REST APIs handling 10k requests per second using FastAPI and PostgreSQL.
    - Mentored junior developers.
    """

    print("Running analyze_resume...")
    await analyse_resume(resume_id, test_text)
    print("Analyze resume finished. Checking DB for results...")

    async with async_session_factory() as session:
        q = select(ResumeMetadata).where(ResumeMetadata.id == resume_id)
        res = await session.exec(q)
        updated_resume = res.first()
        print("======== RESULTS ========")
        print(f"Status: {updated_resume.analysis_status}")
        print(f"Skills: {updated_resume.skills}")
        print(f"Experience Level: {updated_resume.experience_level}")
        print(f"Years of Experience: {updated_resume.years_of_experience}")
        print(f"Summary: {updated_resume.resume_summary}")
        print("=========================")

asyncio.run(main())
