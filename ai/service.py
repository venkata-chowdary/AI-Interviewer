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
You are an expert technical recruiter and resume analyst.
Your task is to thoroughly analyze the provided candidate resume and reliably extract structured professional information.

Please extract the following data points with high accuracy:
1. Technical skills: Extract all relevant technical hard skills (e.g., programming languages, frameworks, databases, cloud providers, tools). Normalize the names where appropriate (e.g., "React.js" to "React").
2. Experience level: Categorize the candidate as strictly one of: 'entry', 'mid', or 'senior'. 
   - Entry: 0-2 years
   - Mid: 3-5 years
   - Senior: 6+ years
3. Estimated years of experience: Calculate the total years of professional experience based on the dates provided in the work history. If explicit dates are missing, make your best conservative estimate based on the content. Return as an integer.
4. Professional summary: Write a concise, impactful 2-3 sentence summary highlighting the candidate's core expertise, primary domain, and standout achievements. Do not simply copy their summary verbatim; synthesize it into a recruiter-friendly format.

Resume text:
{resume_text}
"""

        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
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
