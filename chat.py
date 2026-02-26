from langchain_qdrant import QdrantVectorStore
from embeddings import embeddings_model
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


user_query="is this guy a good candidate for the role of GEN AI?"

vector_store=QdrantVectorStore.from_existing_collection(
    embedding=embeddings_model,
    url="http://localhost:6333",
    collection_name="resume_collection"
)

results=vector_store.similarity_search(query=user_query)
context = "\n".join([doc.page_content for doc in results])

SYSTEM_PROMPT=f"""
you are an AI assistant.
and answers user's queries based on the available context:
{context} 
"""

model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.9
)

messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content=user_query)
]

print("Querying the model...")
response = model.invoke(messages)
print("\n--- Response ---")
print(response.content[0]['text'])