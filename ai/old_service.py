from uuid import UUID
from sqlmodel import select
from db import async_session_factory
from dotenv import load_dotenv
from models.resume import ResumeMetadata
from models.interview import Interview, InterviewQuestionAttempt
from models.question import Question
from ai.schemas import ResumeAnalysis, InterviewEvaluation
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

load_dotenv()


def _normalize_selected_status(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"selected", "hire", "hired", "shortlisted", "strong_hire"}:
        return "selected"
    if normalized in {"rejected", "reject", "not_selected", "no_hire", "weak_hire"}:
        return "rejected"
    return None


def _derive_selected_status(performance_report: dict, overall_marks: float) -> str:
    for key in ("selected_status", "recommendation", "hiring_recommendation", "overall_recommendation"):
        if key in performance_report:
            normalized = _normalize_selected_status(str(performance_report.get(key)))
            if normalized:
                return normalized
    return "selected" if overall_marks >= 70 else "rejected"

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
                temperature=0.7
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

async def evaluate_interview(session_id: UUID):
    async with async_session_factory() as session:
        q = select(Interview).where(Interview.id == session_id)
        result = await session.exec(q)
        interview = result.first()
        
        if not interview:
            return
            
        print(f"Starting LLM evaluation for interview {session_id}...")
        
        try:
            attempts_query = select(InterviewQuestionAttempt).where(InterviewQuestionAttempt.session_id == session_id)
            attempts_result = await session.exec(attempts_query)
            attempted_questions = attempts_result.all()
            
            if not attempted_questions:
                print("No attempts found to evaluate.")
                interview.status = "completed"
                interview.time_taken = 0
                session.add(interview)
                await session.commit()
                return

            evaluation_context = []
            for attempt in attempted_questions:
                q_stmt = select(Question).where(Question.id == attempt.question_id)
                q_result = await session.exec(q_stmt)
                question = q_result.first()
                if question:
                    evaluation_context.append({
                        "question_id": str(attempt.question_id),
                        "question_text": question.question_text,
                        "max_score": question.max_score,
                        "expected_concepts": question.expected_concepts,
                        "scoring_guidelines": question.scoring_guidelines,
                        "candidate_answer": attempt.answer_text,
                        "time_taken_seconds": attempt.time_taken
                    })

            # Construct LLM prompt
            SYSTEM_PROMPT = f"""
You are an expert technical interviewer evaluating a candidate's interview performance.
The candidate applied for a {{interview.role}} role at {{interview.difficulty_level}} difficulty.

You will be provided with a list of questions asked during the interview, the expected concepts, scoring guidelines, and the candidate's actual answers.

Your task is to:
1. Evaluate each individual answer and provide a score (out of the max_score) and constructive feedback.
2. Provide a single overall score for the entire interview out of 100.
3. Generate `performance_report` with exactly these keys and no extras:
   - strengts: list of key strengths
   - weakness: list of key weaknesses
   - suggestions: list of actionable improvement suggestions
   - summary: concise overall summary
4. Provide selected_status strictly as either "selected" or "rejected".

Return the result as a structured JSON object matching the InterviewEvaluation schema.
"""
            model = ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
                temperature=0.7
            )
            
            structured_llm = model.with_structured_output(InterviewEvaluation)
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=json.dumps(evaluation_context, indent=2))
            ]
            
            print("Sending evaluation request to Gemini...")
            evaluation_result = await structured_llm.ainvoke(messages)
            performance_report = evaluation_result.performance_report.model_dump()
            
            for attempt in attempted_questions:
                eval_for_attempt = next((e for e in evaluation_result.question_evaluations if str(e.question_id) == str(attempt.question_id)), None)
                if eval_for_attempt:
                    attempt.score = eval_for_attempt.score
                    attempt.feedback = eval_for_attempt.feedback
                session.add(attempt)

            total_time_taken = sum((attempt.time_taken or 0) for attempt in attempted_questions)
            selected_status = _normalize_selected_status(evaluation_result.selected_status)
            if not selected_status:
                selected_status = _derive_selected_status(
                    performance_report,
                    evaluation_result.overall_marks
                )

            interview.marks = evaluation_result.overall_marks
            interview.performance_report = performance_report
            interview.selected_status = selected_status
            interview.time_taken = total_time_taken
            interview.status = "completed"
            
            session.add(interview)
            await session.commit()
            print(f"Evaluation completed successfully for interview {session_id}.")
            
        except Exception as e:
            import traceback
            print(f"Error evaluating interview: {e}")
            traceback.print_exc()
            interview.status = "failed_evaluation"
            session.add(interview)
            await session.commit()

