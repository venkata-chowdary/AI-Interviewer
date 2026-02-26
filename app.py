import hashlib
import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from embeddings import embeddings_model
from pathlib import Path
from db import async_session_factory
from models import ResumeMetadata
from sqlmodel import select

async def main():
    pdf_path=Path(__file__).parent / "venkata_immanni_full_stack_gen_ai_feb_2026.pdf"

    # Generate file hash to avoid duplicates
    with open(pdf_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    async with async_session_factory() as session:
        result = await session.exec(select(ResumeMetadata).where(ResumeMetadata.resume_hash == file_hash))
        existing_resume = result.first()

        if existing_resume:
            print(f"Resume already processed (ID: {existing_resume.id}). Skipping Qdrant indexing.")
        else:
            new_resume = ResumeMetadata(
                user_id="dummy_user_id",
                file_name=pdf_path.name,
                resume_hash=file_hash
            )
            session.add(new_resume)
            await session.commit()
            await session.refresh(new_resume)
            print(f"Saved resume to Postgres (ID: {new_resume.id})")

            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()

            for doc in docs:
                doc.metadata["user_id"] = "dummy_user_id"
                doc.metadata["resume_id"] = str(new_resume.id)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents=docs)

            vector_store=QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=embeddings_model,
                url="http://localhost:6333",
                collection_name="resume_collection"
            )
            print("indexing completed...")

if __name__ == "__main__":
    asyncio.run(main())