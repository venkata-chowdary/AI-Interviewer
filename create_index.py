from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType
import os
from dotenv import load_dotenv

load_dotenv()
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

try:
    qdrant_client.create_payload_index(
        collection_name="questions",
        field_name="difficulty_level",
        field_schema=PayloadSchemaType.INTEGER,
    )
    print("Successfully created index for difficulty_level.")
except Exception as e:
    print(f"Failed to create index: {e}")
