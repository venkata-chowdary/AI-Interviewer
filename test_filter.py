from langchain_qdrant import QdrantVectorStore
from qdrant_client.http import models
from embeddings import embeddings_model
import os
from dotenv import load_dotenv

load_dotenv()
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings_model,
    collection_name="questions",
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

try:
    res = qdrant.similarity_search("backend", k=1, filter={"difficulty_level": 3})
    print("Dict filter success:", len(res))
except Exception as e:
    print("Dict filter error:", e)

try:
    filter_qdrant = models.Filter(
        must=[models.FieldCondition(key="difficulty_level", match=models.MatchValue(value=3))]
    )
    res2 = qdrant.similarity_search("backend", k=1, filter=filter_qdrant)
    print("Models filter success:", len(res2))
except Exception as e:
    print("Models filter error:", e)
