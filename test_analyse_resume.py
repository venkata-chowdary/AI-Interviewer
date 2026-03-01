import asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from ai.schemas import ResumeAnalysis

load_dotenv()

async def test_analyse_resume():
    file_path = "venkata_immanni_full_stack_gen_ai_feb_2026.pdf"
    
    print(f"Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # Chunking as the user requested "pass the chunked resume to LLM"
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents=docs)
    
    print(f"Total chunks created: {len(chunks)}")
    
    # We combine chunk contents to pass as resume text
    resume_text = "\n\n".join([chunk.page_content for chunk in chunks])
    
    SYSTEM_PROMPT = f"""
Analyze the following resume and extract:
- Technical skills
- Experience level (entry, mid, senior)
- Estimated years of experience
- A short professional summary

Resume text:
{resume_text}
"""

    print("Analyzing with Gemini...")
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0
        )
        
        structured_llm = model.with_structured_output(ResumeAnalysis)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content="Please provide the structured analysis of the resume."),
        ]
        
        analysis = await structured_llm.ainvoke(messages)
        
        print("\n--- ANALYSIS RESULT ---")
        print(f"Skills: {analysis.skills}")
        print(f"Experience Level: {analysis.experience_level}")
        print(f"Years of Experience: {analysis.years_of_experience}")
        print(f"Summary: {analysis.summary}")
        print("-----------------------")
        
    except Exception as e:
        import traceback
        print(f"Error analyzing resume: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analyse_resume())
