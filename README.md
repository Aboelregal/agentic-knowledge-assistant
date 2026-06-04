# 🧠 Agentic Knowledge Assistant

> Built by **Ahmed AboElregal** — AI Engineer

[![Author](https://img.shields.io/badge/Author-Ahmed%20AboElregal-6C63FF?style=flat)](https://github.com/AhmedAboElregal)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-green?logo=langchain)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/Groq-Llama3-purple)](https://groq.com)

---

## 📖 What Is This?

The **Agentic Knowledge Assistant** is a complete, portfolio-ready AI application that lets you:

1. **Upload** PDF and TXT documents to a vector knowledge base
2. **Ask questions** about those documents in natural language
3. **Get accurate answers** grounded in your documents — with source citations

It demonstrates real-world skills used in AI engineering:
**LangChain · RAG · AI Agents · ChromaDB · FastAPI · Streamlit · Groq API**

---

## 🏗️ Architecture

```
User Question
     │
     ▼
┌─────────────────────────────────────────────────┐
│              Streamlit Frontend                  │
│  (Upload Page | Chat Page | Knowledge Base)      │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (REST)
                       ▼
┌─────────────────────────────────────────────────┐
│               FastAPI Backend                    │
│   POST /upload  │  POST /ask  │  GET /documents  │
└──────────┬──────────────┬───────────────────────┘
           │              │
           ▼              ▼
  ┌─────────────┐  ┌──────────────────────────────┐
  │  Ingestion  │  │        Agent Router           │
  │  Pipeline   │  │                               │
  │             │  │  ┌────────────────────────┐   │
  │ Load → Split│  │  │   Retrieval Agent      │   │
  │  → Embed →  │  │  │  ChromaDB similarity   │   │
  │   Store     │  │  │  search → top-k chunks │   │
  └──────┬──────┘  │  └───────────┬────────────┘   │
         │         │              │ context         │
         ▼         │              ▼                 │
  ┌─────────────┐  │  ┌────────────────────────┐   │
  │  ChromaDB   │  │  │       QA Agent         │   │
  │  (Vectors)  │◄─┘  │  Groq Llama3 + prompt  │   │
  └─────────────┘     │  → grounded answer     │   │
                       └────────────────────────┘   │
                       └──────────────────────────┘
```

---

## 🚀 RAG Pipeline Explained

**RAG (Retrieval-Augmented Generation)** prevents LLM hallucination by grounding answers in real documents.

### Ingestion Phase (one-time per document)

```
PDF/TXT File
    │
    ▼ PyPDFLoader / TextLoader
Page Text(s)
    │
    ▼ RecursiveCharacterTextSplitter (500 chars, 100 overlap)
Overlapping Chunks  ← overlap ensures context isn't lost at boundaries
    │
    ▼ SentenceTransformer (all-MiniLM-L6-v2)
Embedding Vectors (384 dimensions)
    │
    ▼ ChromaDB (cosine similarity index)
Stored & Ready
```

### Query Phase (every question)

```
User Question
    │
    ▼ SentenceTransformer
Query Embedding
    │
    ▼ ChromaDB cosine similarity search
Top-K Relevant Chunks (filtered by distance threshold)
    │
    ▼ Context Assembly (formatted with source citations)
Prompt = System + Context + Question
    │
    ▼ Groq API (Llama 3)
Grounded Answer + Source Citations
```

---

## 🤖 AI Agents Workflow

This project uses a **two-agent architecture** with a simple router:

### Retrieval Agent (`agents/retrieval_agent.py`)
- **Role**: Knowledge retrieval specialist
- **Input**: User query string
- **Action**: Searches ChromaDB using vector similarity
- **Output**: `RetrievalResult` — chunks, context string, source list

### QA Agent (`agents/qa_agent.py`)
- **Role**: Reasoning and answer generation
- **Input**: User question + `RetrievalResult` from Retrieval Agent
- **Action**: Constructs a RAG prompt, calls Groq's Llama 3
- **Output**: `QAResult` — answer, model used, status

### Router (FastAPI `/ask` endpoint)
```python
retrieval_result = retrieval_agent.run(query=question)   # Step 1
qa_result        = qa_agent.run(question, retrieval_result)  # Step 2
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Groq + Llama 3 | Fast, free text generation |
| Orchestration | LangChain | Prompt management, loaders, splitters |
| Vector DB | ChromaDB | Storing and searching embeddings |
| Embeddings | `all-MiniLM-L6-v2` | Local, free sentence embeddings |
| Backend | FastAPI | REST API with type-safe endpoints |
| Frontend | Streamlit | Interactive web UI |
| PDF Parsing | PyPDF | Extract text from PDFs |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com) (takes 30 seconds to get)

### Step-by-Step Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/agentic-knowledge-assistant.git
cd agentic-knowledge-assistant
```

**2. Create and activate a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your API key**
```bash
cp .env.example .env
```
Open `.env` and replace `your_groq_api_key_here` with your actual key from [console.groq.com](https://console.groq.com).

**5. Start the FastAPI backend** (Terminal 1)
```bash
uvicorn api.main:app --reload --port 8000
```
You should see: `Uvicorn running on http://127.0.0.1:8000`

**6. Start the Streamlit frontend** (Terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```
Your browser will open to `http://localhost:8501` automatically.

**7. Use the app!**
- Go to **📁 Upload Documents** → upload a PDF or TXT file
- Go to **💬 Chat** → ask a question about your document
- Go to **📚 Knowledge Base** → view all indexed documents

---

## 🐳 Docker Setup (Optional)

**Run everything with one command:**
```bash
# Copy env file first
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Build and start both services
docker-compose up --build
```

- API: `http://localhost:8000`
- Frontend: `http://localhost:8501`

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check if API is running |
| `POST` | `/upload` | Upload a PDF or TXT document |
| `POST` | `/ask` | Ask a question about documents |
| `GET` | `/documents` | List all ingested documents |

Interactive API docs: `http://localhost:8000/docs`

### Example: Ask a question via curl
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

---

## 📁 Project Structure

```
agentic-knowledge-assistant/
├── agents/
│   ├── __init__.py
│   ├── retrieval_agent.py    # Searches ChromaDB for relevant chunks
│   └── qa_agent.py           # Calls Groq LLM with retrieved context
│
├── rag/
│   ├── __init__.py
│   ├── ingest.py             # Document loading, chunking, embedding
│   ├── retriever.py          # Vector similarity search + filtering
│   └── vector_store.py       # ChromaDB client wrapper
│
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI app with all endpoints
│
├── frontend/
│   └── streamlit_app.py      # Streamlit UI (3 pages)
│
├── data/                     # Place sample documents here
├── chroma_db/                # ChromaDB persists here (auto-created)
│
├── requirements.txt
├── .env.example              # Copy to .env and add your API key
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *required* | Your Groq API key |
| `GROQ_MODEL` | `llama3-8b-8192` | Model name (or `llama3-70b-8192`) |
| `CHROMA_DB_PATH` | `./chroma_db` | Where ChromaDB stores data |
| `API_BASE_URL` | `http://localhost:8000` | Backend URL for Streamlit |

---

## 🐞 Troubleshooting

**"GROQ_API_KEY not found"**
→ Make sure `.env` exists and contains your key. Copy `.env.example` → `.env`.

**"Cannot connect to API"**
→ Make sure the FastAPI server is running: `uvicorn api.main:app --reload`

**"No relevant chunks found"**
→ Upload documents first before asking questions.

**Slow first question?**
→ The embedding model downloads on first use (~90MB). Subsequent questions are fast.

---

## 🎯 Skills Demonstrated

This project is designed to showcase the following AI Engineer skills on your CV:

- ✅ **LangChain** — document loaders, text splitters, LLM integration
- ✅ **RAG** — full ingestion and retrieval pipeline
- ✅ **AI Agents** — modular retrieval + QA agent architecture
- ✅ **ChromaDB** — persistent vector storage with cosine similarity
- ✅ **FastAPI** — production-style REST API with Pydantic models
- ✅ **Streamlit** — multi-page interactive frontend
- ✅ **Groq API** — fast LLM inference with Llama 3
- ✅ **Python best practices** — type hints, logging, OOP, error handling

---

## 👨‍💻 Author

**Ahmed AboElregal**  
AI Engineer

[![GitHub](https://img.shields.io/badge/GitHub-AhmedAboElregal-181717?logo=github)](https://github.com/AhmedAboElregal)

---

## 📄 License

MIT License — Copyright (c) 2025 Ahmed AboElregal

See the [LICENSE](LICENSE) file for full details.