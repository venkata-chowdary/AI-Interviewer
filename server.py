from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException, Path
import asyncio
import logging
import os
import hashlib
from datetime import datetime, timedelta, timezone
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Tuple
import time
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
from db import get_session, init_db, async_session_factory
from models import ResumeMetadata, Interview
from models.interview import InterviewQuestionAttempt
from models.question import Question
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from embeddings import embeddings_model
from ai.service import analyse_resume, evaluate_interview
from schemas import (
    StartInterviewRequest,
    RecentInterviewResponse,
    InterviewAttemptReportItem,
    TechSkillScore,
    InterviewReportResponse,
    SubmitAnswerRequest,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

logger = logging.getLogger("ai_interviewer.cron")
scheduler = BackgroundScheduler()


class SimpleTTLCache:
    def __init__(self, ttl_seconds: int, max_size: int = 256):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str):
        entry = self._store.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any):
        if len(self._store) >= self.max_size:
            try:
                first_key = next(iter(self._store.keys()))
                self._store.pop(first_key, None)
            except StopIteration:
                pass
        self._store[key] = (time.time() + self.ttl_seconds, value)


resume_cache = SimpleTTLCache(ttl_seconds=60, max_size=512)
recent_interviews_cache = SimpleTTLCache(ttl_seconds=10, max_size=512)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from auth.routes import router as auth_router
app.include_router(auth_router)



@app.get("/")
def read_root():
    return {"Hello": "World"}

from fastapi import BackgroundTasks

from auth.security import get_current_user_id
from ai.service import evaluate_interview

@app.post("/upload-resume")
async def upload_resume(
    background_task: BackgroundTasks, 
    file: UploadFile = File(...), 
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    content=await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    #check for exsisting resume
    result = await session.exec(select(ResumeMetadata).where(ResumeMetadata.resume_hash==file_hash))
    exsisting_resume = result.first()
    if exsisting_resume:
        raise HTTPException(status_code=400, detail="Resume already exists.")

    new_resume=ResumeMetadata(
        user_id=user_id,
        file_name=file.filename,
        resume_hash=file_hash
    )

    session.add(new_resume)
    await session.commit()
    await session.refresh(new_resume)
    print(f"Saved resume to Postgres (ID: {new_resume.id})")

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        for doc in docs:
            doc.metadata["user_id"] = user_id
            doc.metadata["resume_id"] = str(new_resume.id)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents=docs)

        vector_store=QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings_model,
            url=os.getenv("QDRANT_URL", "https://404d86ae-5bcf-4b02-ba12-abbab2ed350c.sa-east-1-0.aws.cloud.qdrant.io:6333"),
            api_key=os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.6Eow570SBDAb2qMx0QWGrdvhjBOSVUhRKq5deDM22Qs"),
            collection_name="resume_collection"
        )
        print("Embeddings created and stored in Qdrant")

        # Update the database to reflect that embeddings were successfully created
        new_resume.embeddings_created = True
        session.add(new_resume)
        await session.commit()

        full_text = "\n".join([doc.page_content for doc in docs])
        background_task.add_task(analyse_resume, new_resume.id, full_text)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing and indexing resume: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"message": "Resume processed and indexed successfully.", "resume_id": new_resume.id}

@app.get("/api/resume/me")
async def get_my_resume(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    cache_key = f"user:{user_id}:latest_resume"
    cached = resume_cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch the most recent resume for this user by ordering by created_at desc
    result = await session.exec(
        select(ResumeMetadata)
        .where(ResumeMetadata.user_id == user_id)
        .order_by(ResumeMetadata.created_at.desc())
    )
    resume = result.first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user.")
    
    resume_cache.set(cache_key, resume)
    return resume

@app.get("/api/resumes")
async def get_all_resumes(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    # Fetch all resumes for this user, ordered by most recent
    result = await session.exec(
        select(ResumeMetadata)
        .where(ResumeMetadata.user_id == user_id)
        .order_by(ResumeMetadata.created_at.desc())
    )
    resumes = result.all()
    
    return resumes

import uuid


@app.get("/api/interviews/recent", response_model=list[RecentInterviewResponse])
async def get_recent_interviews(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    safe_limit = max(1, min(limit, 50))

    cache_key = f"user:{user_id}:recent_interviews:{safe_limit}"
    cached = recent_interviews_cache.get(cache_key)
    if cached is not None:
        return cached
    interviews_result = await session.exec(
        select(Interview)
        .where(Interview.user_id == user_id)
        .order_by(Interview.created_at.desc())
        .limit(safe_limit)
    )
    interviews = interviews_result.all()

    if not interviews:
        return []

    interview_ids = [interview.id for interview in interviews]
    attempts_result = await session.exec(
        select(
            InterviewQuestionAttempt.session_id,
            func.count(InterviewQuestionAttempt.id).label("attempt_count")
        )
        .where(InterviewQuestionAttempt.session_id.in_(interview_ids))
        .group_by(InterviewQuestionAttempt.session_id)
    )

    attempts_count_map = {
        str(session_id): int(attempt_count)
        for session_id, attempt_count in attempts_result.all()
    }

    recent_interviews: list[RecentInterviewResponse] = []
    for interview in interviews:
        total_questions = len(interview.questions or [])
        answered_questions = attempts_count_map.get(str(interview.id), 0)
        progress_percent = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0

        recent_interviews.append(
            RecentInterviewResponse(
                id=str(interview.id),
                role=interview.role,
                difficulty_level=interview.difficulty_level,
                status=interview.status,
                score=interview.marks,
                selected_status=interview.selected_status,
                time_taken=interview.time_taken,
                created_at=interview.created_at,
                questions_total=total_questions,
                questions_answered=answered_questions,
                progress_percent=progress_percent
            )
        )
    recent_interviews_cache.set(cache_key, recent_interviews)
    return recent_interviews


@app.get("/api/interview/{session_id}/report", response_model=InterviewReportResponse)
async def get_interview_report(
    session_id: uuid.UUID = Path(..., description="ID of the interview session"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    interview = await session.get(Interview, session_id)
    if not interview or interview.user_id != user_id:
        raise HTTPException(status_code=404, detail="Interview session not found")

    attempts_result = await session.exec(
        select(InterviewQuestionAttempt)
        .where(InterviewQuestionAttempt.session_id == session_id)
        .order_by(InterviewQuestionAttempt.question_order.asc())
    )
    attempts = attempts_result.all()

    attempt_items: list[InterviewAttemptReportItem] = []
    # Aggregate per-technology scores based on question primary_skill
    per_skill_scores: dict[str, dict[str, float]] = {}

    for attempt in attempts:
        q_stmt = select(Question).where(Question.id == attempt.question_id)
        q_result = await session.exec(q_stmt)
        question = q_result.first()

        primary_skill = question.primary_skill if question else None
        max_score = float(question.max_score) if question else None

        attempt_items.append(
            InterviewAttemptReportItem(
                question_id=str(attempt.question_id),
                question_order=attempt.question_order,
                question_text=question.question_text if question else None,
                max_score=max_score,
                score=attempt.score,
                feedback=attempt.feedback,
                time_taken=attempt.time_taken,
                primary_skill=primary_skill,
            )
        )

        if (
            question
            and primary_skill
            and attempt.score is not None
            and max_score is not None
            and max_score > 0
        ):
            entry = per_skill_scores.setdefault(
                primary_skill, {"earned": 0.0, "max": 0.0}
            )
            entry["earned"] += float(attempt.score)
            entry["max"] += max_score

    tech_skill_radar: list[TechSkillScore] = []
    for name, values in per_skill_scores.items():
        total_max = values["max"]
        if total_max <= 0:
            continue
        percent = (values["earned"] / total_max) * 100.0
        tech_skill_radar.append(TechSkillScore(name=name, score=round(percent, 1)))

    top_tech_skills: list[TechSkillScore] | None = None
    if tech_skill_radar:
        max_score_value = max(item.score for item in tech_skill_radar)
        epsilon = 0.1
        top_tech_skills = [
            item for item in tech_skill_radar if max_score_value - item.score <= epsilon
        ]

    total_questions = len(interview.questions or [])
    answered_questions = len(attempts)
    progress_percent = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0

    return InterviewReportResponse(
        id=str(interview.id),
        role=interview.role,
        difficulty_level=interview.difficulty_level,
        duration=interview.duration,
        status=interview.status,
        marks=interview.marks,
        selected_status=interview.selected_status,
        time_taken=interview.time_taken,
        created_at=interview.created_at,
        questions_total=total_questions,
        questions_answered=answered_questions,
        progress_percent=progress_percent,
        performance_report=interview.performance_report,
        attempts=attempt_items,
        tech_skill_radar=tech_skill_radar or None,
        top_tech_skills=top_tech_skills,
    )


@app.post("/api/interview/start")
async def start_interview(
    payload: StartInterviewRequest, #payload schema
    user_id: str = Depends(get_current_user_id), #current user id
    session: AsyncSession = Depends(get_session) #db session
):
    try:
        print(f"Received start interview payload: {payload}")

        # Map textual difficulty from frontend (easy, medium, hard) to integer ratings expected by backend (1-5)
        # Here we map standard 3 levels to a combination of exact numbers or ranges
        difficulty_map = {
            "easy": [1, 2],       # Maps to "very basic" and "easy"
            "medium": [3, 4],     # Maps to "medium" and "hard"
            "hard": [4, 5]        # Maps to "hard" and "expert"
        }

        number_of_questions_map = {
            10: 5,
            20: 8,
            30: 10
        }

        resume = await session.get(ResumeMetadata, payload.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
            
        skills_context = resume.skills if resume.skills else ""

        # Formulate the search query by combining role and skills to match seed format
        search_query = f"Topic/Technology: {payload.role}. Skills: {skills_context}"
        print(f"Generating questions using semantic query: '{search_query}'")

        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embeddings_model,
            collection_name="questions",
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )

        try:
            role_domain_map = {
                "frontend": ["frontend"],
                "backend": ["backend", "system_design", "database"],
                "fullstack": ["backend", "frontend", "system_design", "database"]
            }
            role_lower=payload.role.lower()
            domains=role_domain_map.get(role_lower, [role_lower])

            domain_condition=models.Filter(
                should=[models.FieldCondition(key="domain", match=models.MatchValue(value=d)) for d in domains]
            )
            
            difficulty_int = difficulty_map.get(payload.difficulty_level.lower())
            difficulty_condition = models.FieldCondition(
                key="difficulty_level", 
                match=models.MatchAny(any=difficulty_int)
            )

            main_filter=models.Filter(
                must=[
                    domain_condition,
                    difficulty_condition
                ]
            )
                
            search_result = qdrant.similarity_search(query=search_query, k=number_of_questions_map.get(payload.duration, 5), filter=main_filter)
            print("seach result:", search_result)
            
            question_ids = []
            for doc in search_result:
                 qid = doc.metadata.get("question_id") or doc.metadata.get("_id")
                 if qid:
                    question_ids.append(qid)
            print(f"Found {len(question_ids)} questions")
            
        except Exception as e:
            print(f"Qdrant Search Error: {e}")
            raise HTTPException(status_code=500, detail="Error fetching questions from database")

        # Create the interview session
        new_interview = Interview(
            user_id=user_id,
            resume_id=payload.resume_id,
            role=payload.role,
            difficulty_level=payload.difficulty_level,
            duration=payload.duration,
            questions=question_ids, # Attached Qdrant question IDs
            status="active"
        )    
        session.add(new_interview)
        await session.commit()
        await session.refresh(new_interview)
        
        return {
            "session_id": new_interview.id, 
            "message": "Interview session created",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting interview: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while starting the interview session")


#GET /api/interview/{session_id}/next-question
@app.get("/api/interview/{session_id}/next-question")
async def get_next_question(
    session_id: str = Path(..., description="ID of the interview session"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    try:
        #check iterview exsisted
        interview = await session.get(Interview, session_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview session not found")

        if interview.status in ["completed", "under_evaluation"]:
            return {
                "message": "Interview completed", 
                "completed": True, 
                "status": interview.status
            }

        if interview.status != "active":
            raise HTTPException(status_code=400, detail="Interview session is not active")

        if not interview.questions:
            raise HTTPException(status_code=400, detail="Interview session has no questions")
        
        statement = select(InterviewQuestionAttempt).where(InterviewQuestionAttempt.session_id == session_id)
        result = await session.exec(statement)
        attempts = result.all()
        
        attempted_question_ids = {attempt.question_id for attempt in attempts}
        
        next_question_id = None
        for q in interview.questions:
            if q not in attempted_question_ids:
                next_question_id = q
                break
                
        if not next_question_id:
            if interview.status != "under_evaluation" and interview.status != "completed":
                interview.status = "under_evaluation"
                session.add(interview)
                await session.commit()
            return {"message": "Interview completed", "completed": True, "status": interview.status}
        
        question = await session.get(Question, next_question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {next_question_id} not found in database")
        
        return {
            "completed": False,
            "question": question,
            "question_order": len(attempted_question_ids) + 1,
            "total_questions": len(interview.questions)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching new question: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the next question")

@app.post("/api/interview/{session_id}/answer")
async def submit_answer(
    payload: SubmitAnswerRequest,
    background_tasks: BackgroundTasks,
    session_id: uuid.UUID = Path(..., description="ID of the interview session"),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    try:
        interview = await session.get(Interview, session_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview session not found")

        if interview.status != "active":
            raise HTTPException(status_code=400, detail="Interview session is not active")

        statement = select(InterviewQuestionAttempt).where(InterviewQuestionAttempt.session_id == session_id)
        result = await session.exec(statement)
        attempts = result.all()
        
        for attempt in attempts:
            if attempt.question_id == payload.question_id:
                raise HTTPException(status_code=400, detail="Question already answered")
                
        if payload.question_id not in interview.questions:
            raise HTTPException(status_code=400, detail="Question does not belong to this interview")
            
        new_attempt = InterviewQuestionAttempt(
            session_id=session_id,
            question_id=payload.question_id,
            question_order=len(attempts) + 1,
            answer_text=payload.answer_text,
            time_taken=payload.time_taken
        )
        session.add(new_attempt)
        
        is_completed = False
        if len(attempts) + 1 >= len(interview.questions):
            interview.status = "under_evaluation"
            session.add(interview)
            is_completed = True
            
            background_tasks.add_task(evaluate_interview, session_id)
            
        await session.commit()
        
        return {
            "message": "Answer submitted successfully",
            "is_completed": is_completed,
            "status": interview.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting answer: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while submitting the answer")


async def _run_evaluation_sweep(batch_size: int = 3) -> None:
    """Simple periodic sweep to (re)enqueue interviews for evaluation."""
    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        stmt = (
            select(Interview.id)
            .where(Interview.status == "under_evaluation")
            .where((Interview.marks == None) | (Interview.performance_report == None))
            .where(
                (Interview.evaluation_lock_until == None)
                | (Interview.evaluation_lock_until < now)
            )
            .order_by(Interview.created_at.asc())
            .limit(batch_size)
        )

        result = await session.exec(stmt)
        interview_ids = result.all()

    if interview_ids:
        logger.info(
            "evaluation_sweeper_found count=%s interview_ids=%s",
            len(interview_ids),
            [str(i) for i in interview_ids],
        )

    for interview_id in interview_ids:
        logger.info("evaluation_sweeper_run interview_id=%s", str(interview_id))
        await evaluate_interview(interview_id)


def _evaluation_sweeper_job() -> None:
    """APScheduler job wrapper that runs the async sweep."""
    try:
        asyncio.run(_run_evaluation_sweep())
    except Exception as exc:
        logger.exception("evaluation_sweeper_job_error err=%s", str(exc))


@app.on_event("startup")
async def _startup() -> None:
    await init_db()
    logger.info("startup: init_db done, starting APScheduler evaluation sweeper")

    # Run every 30 seconds; keep config simple and adjustable via env if needed.
    sweep_interval = int(os.getenv("EVALUATION_SWEEP_INTERVAL", "30"))
    scheduler.add_job(_evaluation_sweeper_job, "interval", seconds=sweep_interval)
    scheduler.start()
