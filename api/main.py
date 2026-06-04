"""
main.py
-------
FastAPI backend for the Agentic Knowledge Assistant.

Endpoints:
  POST /upload     - Upload and ingest a PDF or TXT document
  POST /ask        - Ask a question using RAG + AI Agents
  GET  /documents  - List all ingested documents
  GET  /health     - Health check

The API acts as the orchestration layer between the frontend
and the RAG + Agent pipeline.
"""

import logging
import os
import shutil
import tempfile
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Local imports ---
from agents.qa_agent import QAAgent
from agents.retrieval_agent import RetrievalAgent
from rag.ingest import DocumentIngestor
from rag.vector_store import VectorStore
 
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── App Initialization ──────────────────────────────────────────────────────

app = FastAPI(
    title="Agentic Knowledge Assistant",
    description=(
        "A RAG-powered AI assistant that answers questions about your documents "
        "using LangChain, ChromaDB, and Groq's Llama 3."
    ),
    version="1.0.0",
)

# Allow all CORS origins (for local Streamlit development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared Instances (created once at startup) ───────────────────────────────

logger.info("Initializing shared components...")
vector_store = VectorStore()
ingestor = DocumentIngestor(vector_store=vector_store)
retrieval_agent = RetrievalAgent(vector_store=vector_store)
qa_agent = QAAgent()
logger.info("All components initialized.")


# ── Pydantic Models ──────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""
    question: str
    source_filter: str | None = None  # Optional: restrict to one document


class AskResponse(BaseModel):
    """Response body for the /ask endpoint."""
    question: str
    answer: str
    sources: List[str]
    chunks_used: int
    model_used: str
    retrieved_chunks: List[Dict[str, Any]]
    status: str


class DocumentInfo(BaseModel):
    """Info about a single ingested document."""
    source: str
    file_type: str


class DocumentsResponse(BaseModel):
    """Response body for the /documents endpoint."""
    documents: List[DocumentInfo]
    total_chunks: int


class UploadResponse(BaseModel):
    """Response body for the /upload endpoint."""
    filename: str
    chunks_added: int
    file_type: str
    status: str
    message: str


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "Agentic Knowledge Assistant"}


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload and ingest a document (PDF or TXT).

    The document is:
    1. Saved to a temp file
    2. Loaded and split into chunks
    3. Embedded and stored in ChromaDB
    """
    # Validate file type
    allowed_types = {".pdf", ".txt"}
    ext = os.path.splitext(file.filename or "")[1].lower()

    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: .pdf, .txt",
        )

    logger.info(f"Received upload: {file.filename}")

    # Save to temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = ingestor.ingest_file(tmp_path)

        # Rename result source to original filename
        result["source"] = file.filename

        logger.info(f"Successfully ingested {file.filename}: {result}")
        return UploadResponse(
            filename=file.filename or "unknown",
            chunks_added=result["chunks_added"],
            file_type=result["file_type"],
            status="success",
            message=f"Successfully ingested {result['chunks_added']} chunks from '{file.filename}'.",
        )

    except Exception as e:
        logger.error(f"Error ingesting {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always clean up temp file
        os.unlink(tmp_path)


@app.post("/ask", response_model=AskResponse, tags=["QA"])
async def ask_question(request: AskRequest) -> AskResponse:
    """
    Ask a question about ingested documents.

    Pipeline:
    1. RetrievalAgent searches ChromaDB for relevant chunks
    2. QAAgent sends context + question to Groq's Llama 3
    3. Returns the answer with source citations
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Processing question: '{request.question}'")

    # Step 1: Retrieve relevant chunks (Retrieval Agent)
    retrieval_result = retrieval_agent.run(
        query=request.question,
        source_filter=request.source_filter,
    )

    # Step 2: Generate answer with context (QA Agent)
    qa_result = qa_agent.run(
        question=request.question,
        retrieval_result=retrieval_result,
    )

    # Format retrieved chunks for the response
    retrieved_chunks = [
        {
            "text": chunk["text"],
            "source": chunk["metadata"].get("source", "Unknown"),
            "page": chunk["metadata"].get("page", "?"),
            "relevance_score": round(1 - chunk["distance"], 3),
        }
        for chunk in retrieval_result.chunks
    ]

    return AskResponse(
        question=qa_result.question,
        answer=qa_result.answer,
        sources=qa_result.sources,
        chunks_used=qa_result.chunks_used,
        model_used=qa_result.model_used,
        retrieved_chunks=retrieved_chunks,
        status=qa_result.status,
    )


@app.get("/documents", response_model=DocumentsResponse, tags=["Documents"])
async def list_documents() -> DocumentsResponse:
    """
    List all documents currently stored in the knowledge base.
    """
    docs = vector_store.get_all_documents()
    total_chunks = vector_store.get_chunk_count()

    return DocumentsResponse(
        documents=[DocumentInfo(**d) for d in docs],
        total_chunks=total_chunks,
    )
