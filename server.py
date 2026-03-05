from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
import os
import hashlib
from tempfile import NamedTemporaryFile
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db import get_session
from models import ResumeMetadata, Interview
from models.question import Question
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from embeddings import embeddings_model
from ai.service import analyse_resume

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    # Fetch the most recent resume for this user by ordering by created_at desc
    result = await session.exec(
        select(ResumeMetadata)
        .where(ResumeMetadata.user_id == user_id)
        .order_by(ResumeMetadata.created_at.desc())
    )
    resume = result.first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found for this user.")
        
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

from pydantic import BaseModel
import uuid

class StartInterviewRequest(BaseModel):
    resume_id: str
    role: str
    difficulty: str
    duration: int

@app.post("/api/interview/start")
async def start_interview(
    payload: StartInterviewRequest, #payload schema
    user_id: str = Depends(get_current_user_id), #current user id
    session: AsyncSession = Depends(get_session) #db session
):
    print(f"Received start interview payload: {payload}")

    # Map text difficulty to integer rating based on out.json
    difficulty_map = {
        "very basic": 1,
        "easy": 2,
        "medium": 3,
        "hard": 4,
        "expert": 5
    }

    number_of_questions_map = {
        10: 5,
        20: 8,
        30: 10
    }

    # Fetch the user's resume to get skills
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
        limit = number_of_questions_map.get(payload.duration, 5)
        difficulty_int = difficulty_map.get(payload.difficulty.lower(), 3)
        
        filter_qdrant = models.Filter(
            must=[models.FieldCondition(key="difficulty_level", match=models.MatchValue(value=difficulty_int))]
        )
        # We perform semantic search without an embedding vector here if using Langchain wrapper
        # The from_existing_collection uses the Langchain abstraction `similarity_search`
        search_result = qdrant.similarity_search(query=search_query, k=limit, filter=filter_qdrant)
        print("seach result:", search_result)
        # The points from similarity_search return Langchain Documents where metadata usually stores IDs
        question_ids = []
        for doc in search_result:
             # Look for the question_id we put in the payload
             qid = doc.metadata.get("question_id") or doc.metadata.get("_id")
             if qid:
                 question_ids.append(qid)
        print(f"Found {len(question_ids)} questions: {question_ids}")
        
    except Exception as e:
        print(f"Qdrant Search Error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching questions from database")

    # Create the interview session
    new_interview = Interview(
        user_id=user_id,
        resume_id=payload.resume_id,
        role=payload.role,
        difficulty=payload.difficulty,
        duration=payload.duration,
        questions=question_ids, # Attached Qdrant question IDs
        status="active"
    )
    #displaying those uqesions
    for qid in question_ids:
        question = await session.get(Question, qid)
        if question:
            print(question)
    
    # session.add(new_interview)
    # await session.commit()
    # await session.refresh(new_interview)
    
    print("interview created", new_interview.id)
    return {
        "session_id": new_interview.id, 
        "message": "Interview session created",
        "question_ids": question_ids
    }
