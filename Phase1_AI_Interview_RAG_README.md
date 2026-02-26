# AI Interview Platform --- Phase 1: Resume Ingestion (RAG Foundation)

## 🎯 Objective of Phase 1

Build a production-grade resume ingestion pipeline that:

- Accepts resume uploads (PDF)
- Extracts and cleans text
- Chunks intelligently (not naive splitting)
- Generates embeddings
- Stores vectors in Qdrant
- Extracts structured skills using LLM
- Stores metadata in PostgreSQL

This phase builds the foundation for the RAG-powered interview engine.

---

# 🏗 Architecture Overview

Client → FastAPI → Resume Service →\
PDF Parser → Chunking Service → Embedding Service → Qdrant\
                                                           ↘\
                                             Skill Extraction (LLM) →
Postgres

---

# 📁 Project Structure

ai-interview-platform/

server/\
├── app.py\
├── config.py\
├── database.py\
├── models/\
├── schemas/\
├── routes/\
├── services/\
└── utils/

frontend/

---

# 🔵 Step-by-Step Flow

## 1️⃣ Upload Resume

Endpoint: POST /resume/upload

- Validate file type (PDF only)
- Limit file size (e.g., 5MB)
- Generate file hash (avoid duplicates)
- Store temporarily

---

## 2️⃣ Extract Text

Use PyPDF to extract raw text.

Processing: - Remove extra whitespace - Normalize newlines - Remove
broken characters - Preserve section structure if possible

Why this matters: Bad extraction = bad embeddings = bad retrieval.

---

## 3️⃣ Intelligent Chunking

Avoid fixed 500-token splitting.

Recommended: - \~800 token chunks - 100--150 token overlap - Preserve
section continuity

Why overlap? Ensures semantic continuity between chunks.

Output: List of chunked text segments.

---

## 4️⃣ Generate Embeddings

Use one embedding model consistently.

---

## 5️⃣ Store in Qdrant

Collection: resume_embeddings

Each vector entry:

{ id: UUID, vector: embedding, payload: { user_id, resume_id,
chunk_text, chunk_index } }

Why payload? Allows filtered search later (per user, per resume).

---

## 7️⃣ Store Resume Metadata

Table Fields:

- id
- user_id
- file_name
- resume_hash
- created_at

---

# 🧠 Why Phase 1 Is Critical

Most RAG systems fail because ingestion is weak.

This phase ensures:

- Clean semantic chunks
- Proper vector storage
- Structured metadata
- Retrieval-ready architecture
- Production-ready pipeline

---

# 🚀 Phase 1 Completion Checklist

✅ Resume upload working\
✅ Text extraction validated\
✅ Chunks stored in memory correctly\
✅ Embeddings generated\
✅ Vectors stored in Qdrant\
✅ Duplicate resume detection working
