from uuid import UUID
from sqlmodel import select
from db import async_session_factory
from dotenv import load_dotenv
from models.resume import ResumeMetadata
from ai.schemas import ResumeAnalysis
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage

load_dotenv()

async def analyse_resume(resume_id: UUID, resume_text: str):
    async with async_session_factory() as session:
        q = select(ResumeMetadata).where(ResumeMetadata.id == resume_id)
        result = await session.exec(q)
        resume = result.first()
        
        if not resume:
            return
            
        resume.analysis_status = "processing"
        session.add(resume)
        await session.commit()
        await session.refresh(resume)

        SYSTEM_PROMPT = f"""
Analyze the following resume and extract:
- Technical skills
- Experience level (entry, mid, senior)
- Estimated years of experience
- A short professional summary

Resume text:
{resume_text}
"""

        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.0
            )
            
            structured_llm = model.with_structured_output(ResumeAnalysis)
            
            from langchain_core.messages import HumanMessage
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content="Please provide the structured analysis of the resume."),
            ]
            
            analysis = await structured_llm.ainvoke(messages)
            
            resume.skills = ", ".join(analysis.skills) if isinstance(analysis.skills, list) else str(analysis.skills)
            resume.experience_level = analysis.experience_level
            resume.years_of_experience = analysis.years_of_experience
            resume.resume_summary = analysis.summary
            resume.analysis_status = "completed"
            
            session.add(resume)
            await session.commit()
            
        except Exception as e:
            import traceback
            print(f"Error analyzing resume: {e}")
            traceback.print_exc()
            resume.analysis_status = "failed"
            session.add(resume)
            await session.commit()
