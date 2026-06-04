# ── Build Stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for PDF processing and ChromaDB
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Create directories for data persistence
RUN mkdir -p data chroma_db

# ── API Container ──────────────────────────────────────────────────────────────
FROM base AS api

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Frontend Container ─────────────────────────────────────────────────────────
FROM base AS frontend

EXPOSE 8501

CMD ["streamlit", "run", "frontend/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
