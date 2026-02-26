from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")