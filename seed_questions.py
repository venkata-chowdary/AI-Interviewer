import asyncio
import json
import logging
from uuid import UUID
from sqlmodel import select

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import required modules from the project
# Ensure this script is run from the 'server' directory
from db import get_session, engine, init_db
from models.question import Question, DomainEnum, CategoryEnum
from embeddings import embeddings_model

# Qdrant client
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "https://404d86ae-5bcf-4b02-ba12-abbab2ed350c.sa-east-1-0.aws.cloud.qdrant.io:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.6Eow570SBDAb2qMx0QWGrdvhjBOSVUhRKq5deDM22Qs")
COLLECTION_NAME = "questions"
VECTOR_SIZE = 768  # We thought Gemini was 768 but actually 768 is older models; current text-embedding-004 is 768. Wait, error explicitly states "got 3072". We'll set to 3072.
VECTOR_SIZE = 3072

async def main():
    logger.info("Starting question seeding process...")
    
    # 1. Load JSON Data
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), "out.json")
        if not os.path.exists(json_path):
            logger.error("out.json not found in server or project root.")
            return

    with open(json_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)
        
    logger.info(f"Loaded {len(questions_data)} questions from out.json.")

    # 2. Re-initialize DB tables just in case
    await init_db()

    # 3. Setup Qdrant Client
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    # We need to recreate the collection entirely because we previously created it with 768.
    logger.info(f"Recreating Qdrant collection '{COLLECTION_NAME}' with size {VECTOR_SIZE}...")
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    logger.info("Creating payload indices for 'domain' and 'difficulty_level'...")
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="domain",
        field_schema="keyword",
    )
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="difficulty_level",
        field_schema="integer",
    )

    points_to_upsert = []

    # 4. Insert into Postgres and Prepare Qdrant Payloads
    from sqlalchemy.ext.asyncio import AsyncSession
    from db import async_session_factory

    from sqlalchemy import text
    async with async_session_factory() as session:
        # Clear existing table data to prevent duplicates
        logger.info("Clearing existing questions from Postgres...")
        await session.execute(text("TRUNCATE TABLE question RESTART IDENTITY CASCADE"))
        await session.commit()
    
        for idx, q_data in enumerate(questions_data):
            
            # Create Question Model instance (mapped 'secondary_skills' to 'secondary_skill')
            db_question = Question(
                domain=DomainEnum(q_data["domain"]),
                category=CategoryEnum(q_data["category"]),
                topic=q_data["topic"],
                difficulty_level=q_data["difficulty_level"],
                primary_skill=q_data["primary_skill"],
                secondary_skill=q_data.get("secondary_skills", []),
                question_text=q_data["question_text"],
                expected_concepts=q_data["expected_concepts"],
                max_score=q_data["max_score"],
                scoring_guidelines=q_data["scoring_guidelines"]
            )
            
            session.add(db_question)
            
            # Need to commit to generate the UUID, but committing in a loop is slow.
            # Instead, we will commit after adding all, but then we need to fetch them back or rely on flush.
            # We'll rely on session.flush() to populate the IDs without a full commit transaction overhead per item.
            await session.flush()
            
            question_id_str = str(db_question.id)

            logger.info(f"Generating embedding for question {idx+1}/{len(questions_data)} (ID: {question_id_str})")
            
            # Generate Embedding with a slight delay to respect free-tier rate limits
            text_to_embed = f"Topic/Technology: {db_question.topic}. Skills: {db_question.primary_skill}, {', '.join(db_question.secondary_skill)}. Question: {db_question.question_text}"
            embedding = embeddings_model.embed_query(text_to_embed)
            await asyncio.sleep(1.5) # Prevent rate limiting freeze

            # Prepare Qdrant Payload
            payload = {
                "question_id": question_id_str,
                "domain": q_data["domain"],
                "category": q_data["category"],
                "topic": q_data["topic"],
                "difficulty_level": q_data["difficulty_level"],
                "primary_skill": q_data["primary_skill"],
                "secondary_skills": q_data.get("secondary_skills", []),
                "max_score": q_data["max_score"],
                "scoring_guidelines": q_data.get("scoring_guidelines", {})
            }

            # Create PointStruct
            points_to_upsert.append(
                PointStruct(
                    id=str(uuid.uuid4()), # Qdrant requires its own UUID or int for point ID, or we can use question ID
                    vector=embedding,
                    payload=payload
                )
            )
            # Instead of generating a new uuid for qdrant point, we can just map the question_id directly:
            points_to_upsert[-1].id = question_id_str 
            
        # Commit all records to Postgres
        logger.info("Committing all records to Postgres...")
        await session.commit()
        logger.info("Postgres insertion complete.")

    # 5. Upsert to Qdrant in batches
    logger.info(f"Upserting {len(points_to_upsert)} points to Qdrant...")
    batch_size = 50
    for i in range(0, len(points_to_upsert), batch_size):
        batch = points_to_upsert[i : i + batch_size]
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
        logger.info(f"Upserted items {i} to {i+len(batch)} to Qdrant.")
        
    logger.info("Question seeding completed successfully!")
    await engine.dispose()


if __name__ == "__main__":
    import uuid # ensure uuid is ready if we need it
    asyncio.run(main())
