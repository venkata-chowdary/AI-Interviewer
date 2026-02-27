from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
import os
import hashlib
from tempfile import NamedTemporaryFile
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db import get_session
from models import ResumeMetadata
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from embeddings import embeddings_model
from ai.service import analyse_resume

app = FastAPI()

from auth.routes import router as auth_router
app.include_router(auth_router)



@app.get("/")
def read_root():
    return {"Hello": "World"}

from fastapi import BackgroundTasks

@app.post("/upload-resume")
async def upload_resume(background_task: BackgroundTasks, user_id: str = Form(...), file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
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
            url="http://localhost:6333",
            collection_name="resume_collection"
        )
        print("Embeddings created and stored in Qdrant")

        full_text = "\n".join([doc.page_content for doc in docs])
        background_task.add_task(analyse_resume, new_resume.id, full_text)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing and indexing resume: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"message": "Resume processed and indexed successfully.", "resume_id": new_resume.id}

    