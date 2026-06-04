"""
streamlit_app.py
----------------
Streamlit frontend for the Agentic Knowledge Assistant.
Enhanced UI with premium design, better fonts, and polished components.
"""

import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e6f0;
}

/* ── App background ── */
.stApp {
    background: #0a0a12;
}

/* ── Main content area ── */
.main .block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1100px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0e0e1a !important;
    border-right: 1px solid #1a1a2e;
}
[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.2rem;
}

/* ── Page title ── */
.page-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6C63FF;
    margin-bottom: 0.4rem;
}
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    font-weight: 400;
    line-height: 1.1;
    color: #f0eeff;
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}
.page-title em {
    font-style: italic;
    color: #9d97ff;
}
.page-subtitle {
    font-size: 0.92rem;
    color: #a09cbf;
    font-weight: 300;
    margin-bottom: 2rem;
    letter-spacing: 0.01em;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: #f0eeff;
    letter-spacing: -0.01em;
    margin-bottom: 0.15rem;
}
.sidebar-tagline {
    font-size: 0.72rem;
    color: #7a78a0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Status pill ── */
.pill-online {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(74, 222, 128, 0.08);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.2);
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.pill-offline {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(248, 113, 113, 0.08);
    color: #f87171;
    border: 1px solid rgba(248, 113, 113, 0.2);
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.pill-dot { font-size: 0.5rem; }

/* ── Nav radio override ── */
[data-testid="stRadio"] label {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #5a5870 !important;
    padding: 0.35rem 0 !important;
    transition: color 0.15s;
}
[data-testid="stRadio"] label:hover { color: #c8c4f0 !important; }
[data-testid="stRadio"] [data-checked="true"] label { color: #9d97ff !important; }

/* ── Stat widget ── */
.stat-block {
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    text-align: center;
}
.stat-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #9d97ff;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.stat-label {
    font-size: 0.7rem;
    color: #7a78a0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* ── Tech stack tags ── */
.tech-tag {
    display: inline-block;
    background: #12121f;
    border: 1px solid #1e1e30;
    color: #9a98c0;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    margin: 0.15rem 0.1rem;
    letter-spacing: 0.03em;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #0e0e1a;
    border: 1.5px dashed #1e1e30;
    border-radius: 14px;
    padding: 0.5rem;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6C63FF;
}

/* ── Pipeline steps ── */
.pipeline-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.85rem 1rem;
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #6C63FF;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 6px;
    padding: 0.15rem 0.45rem;
    font-weight: 500;
    flex-shrink: 0;
    margin-top: 0.05rem;
}
.step-body {}
.step-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #c8c4f0;
    margin-bottom: 0.1rem;
}
.step-desc {
    font-size: 0.75rem;
    color: #7a78a0;
    font-weight: 300;
}

/* ── Ingest result card ── */
.ingest-card {
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-left: 3px solid #6C63FF;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin: 0.4rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ingest-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: #c8c4f0;
}
.ingest-meta {
    font-size: 0.75rem;
    color: #7a78a0;
    margin-top: 0.15rem;
    font-family: 'JetBrains Mono', monospace;
}
.ingest-badge {
    background: rgba(108,99,255,0.12);
    color: #9d97ff;
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
}

/* ── Chat bubbles ── */
.chat-row-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.6rem 0;
}
.chat-row-ai {
    display: flex;
    justify-content: flex-start;
    margin: 0.6rem 0;
}
.bubble-user {
    background: linear-gradient(135deg, #6C63FF 0%, #5a52e8 100%);
    color: #fff;
    padding: 0.85rem 1.15rem;
    border-radius: 20px 20px 5px 20px;
    max-width: 72%;
    font-size: 0.92rem;
    line-height: 1.55;
    box-shadow: 0 4px 20px rgba(108,99,255,0.3);
}
.bubble-ai {
    background: #111120;
    color: #d8d5f0;
    padding: 0.9rem 1.15rem;
    border-radius: 20px 20px 20px 5px;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.65;
    border: 1px solid #1e1e30;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.bubble-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7a78a0;
    margin-bottom: 0.45rem;
    font-family: 'DM Sans', sans-serif;
}

/* ── Source chunk card ── */
.chunk-card {
    background: #080813;
    border: 1px solid #14142a;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.35rem 0;
    font-size: 0.8rem;
}
.chunk-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.chunk-source {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #9d97ff;
    font-weight: 500;
}
.chunk-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #7a78a0;
    background: #0e0e1a;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    border: 1px solid #1a1a2e;
}
.chunk-text {
    color: #9a98c0;
    line-height: 1.6;
    font-size: 0.78rem;
}

/* ── Input bar ── */
.stTextInput > div > div > input {
    background: #0e0e1a !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #2a2840 !important; }

/* ── Buttons ── */
.stButton > button {
    background: #6C63FF !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #5a52e8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(108,99,255,0.35) !important;
}

/* ── Knowledge base doc card ── */
.doc-card {
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color 0.2s;
}
.doc-card:hover { border-color: #2e2e4e; }
.doc-icon {
    font-size: 1.6rem;
    flex-shrink: 0;
}
.doc-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #c8c4f0;
    margin-bottom: 0.15rem;
}
.doc-type {
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #7a78a0;
    background: #080813;
    border: 1px solid #14142a;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
}

/* ── Metric card ── */
.metric-card {
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 14px;
    padding: 1.4rem 1.2rem;
    text-align: center;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #9d97ff;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label {
    font-size: 0.7rem;
    color: #7a78a0;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
}

/* ── Divider ── */
hr { border-color: #12121f !important; margin: 1.2rem 0 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0e0e1a;
    border: 1px solid #1a1a2e !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    color: #9a98c0 !important;
    font-weight: 500 !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6C63FF, #9d97ff) !important;
}

/* ── Success/warning/error ── */
.stSuccess {
    background: rgba(74,222,128,0.06) !important;
    border: 1px solid rgba(74,222,128,0.15) !important;
    border-radius: 10px !important;
    color: #4ade80 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #0e0e1a !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0a0a12; }
::-webkit-scrollbar-thumb { background: #1e1e30; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #2e2e4e; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #6a6890;
}
.empty-state-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-state-text { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API. Make sure uvicorn is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(endpoint: str, json_data=None, files=None):
    try:
        r = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=json_data,
            files=files,
            timeout=180,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def check_api_health() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Knowledge<br>Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">RAG · Agents · LLM</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if check_api_health():
        st.markdown('<span class="pill-online"><span class="pill-dot">●</span> API Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill-offline"><span class="pill-dot">●</span> API Offline</span>', unsafe_allow_html=True)
        st.caption("Run: `uvicorn api.main:app --reload`")

    st.divider()

    page = st.radio(
        "nav",
        ["📁  Upload Documents", "💬  Chat", "📚  Knowledge Base"],
        label_visibility="collapsed",
    )

    st.divider()

    docs_data = api_get("/documents")
    if docs_data:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f'<div class="stat-block">'
                f'<div class="stat-number">{len(docs_data.get("documents", []))}</div>'
                f'<div class="stat-label">Docs</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-block">'
                f'<div class="stat-number">{docs_data.get("total_chunks", 0)}</div>'
                f'<div class="stat-label">Chunks</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    for tag in ["Groq · Llama 3", "LangChain", "ChromaDB", "FastAPI", "Streamlit"]:
        st.markdown(f'<span class="tech-tag">{tag}</span>', unsafe_allow_html=True)


# ── Page: Upload ──────────────────────────────────────────────────────────────

if page == "📁  Upload Documents":
    st.markdown('<div class="page-eyebrow">Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Upload <em>Documents</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Add PDFs or text files — they\'ll be chunked, embedded, and stored in ChromaDB</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.7, 1.3], gap="large")

    with col_left:
        uploaded_files = st.file_uploader(
            "Drop files here or click to browse",
            type=["pdf", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡  Ingest Documents", use_container_width=True):
                progress = st.progress(0, text="Preparing...")
                results = []

                for i, f in enumerate(uploaded_files):
                    progress.progress((i + 1) / len(uploaded_files), text=f"Ingesting {f.name}...")
                    result = api_post("/upload", files={"file": (f.name, f.getvalue(), f.type)})
                    if result:
                        results.append((f.name, result))

                progress.empty()

                if results:
                    st.success(f"✅  {len(results)} document(s) ingested successfully")
                    st.markdown("<br>", unsafe_allow_html=True)
                    for name, res in results:
                        st.markdown(
                            f'<div class="ingest-card">'
                            f'<div><div class="ingest-name">📄 {name}</div>'
                            f'<div class="ingest-meta">{res["file_type"].upper()} · {res["chunks_added"]} chunks stored</div></div>'
                            f'<div class="ingest-badge">{res["chunks_added"]} chunks</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

    with col_right:
        st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#3a3850;margin-bottom:1rem;">RAG Pipeline</div>', unsafe_allow_html=True)

        steps = [
            ("01", "Load", "PyPDF or TextLoader extracts raw text"),
            ("02", "Chunk", "500-char overlapping splits"),
            ("03", "Embed", "MiniLM-L6 → 384-dim vectors"),
            ("04", "Index", "ChromaDB cosine similarity index"),
            ("05", "Ready", "Queryable in milliseconds"),
        ]
        for num, title, desc in steps:
            st.markdown(
                f'<div class="pipeline-step">'
                f'<span class="step-num">{num}</span>'
                f'<div class="step-body">'
                f'<div class="step-title">{title}</div>'
                f'<div class="step-desc">{desc}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )


# ── Page: Chat ────────────────────────────────────────────────────────────────

elif page == "💬  Chat":
    st.markdown('<div class="page-eyebrow">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Chat with Your <em>Docs</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ask anything — Llama 3 answers using only your documents as context</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.expander("⚙️  Options"):
        docs_data = api_get("/documents")
        source_options = ["All Documents"] + (
            [d["source"] for d in docs_data.get("documents", [])] if docs_data else []
        )
        selected_source = st.selectbox("Search scope:", source_options)
        source_filter = None if selected_source == "All Documents" else selected_source

        if st.button("🗑️  Clear History"):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Chat history
    if not st.session_state.messages:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">💬</div>'
            '<div class="empty-state-text">Ask your first question below</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-row-user">'
                f'<div class="bubble-user">'
                f'<div class="bubble-label">You</div>'
                f'{msg["content"]}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-row-ai">'
                f'<div class="bubble-ai">'
                f'<div class="bubble-label">Assistant · {msg.get("model_used", "llm")}</div>'
                f'{msg["content"]}'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            if msg.get("sources"):
                with st.expander(f"📎  {msg['chunks_used']} source chunk(s) · {', '.join(msg['sources'])}"):
                    for chunk in msg.get("retrieved_chunks", []):
                        st.markdown(
                            f'<div class="chunk-card">'
                            f'<div class="chunk-header">'
                            f'<span class="chunk-source">📄 {chunk["source"]} · p.{chunk["page"]}</span>'
                            f'<span class="chunk-score">relevance {chunk["relevance_score"]:.2f}</span>'
                            f'</div>'
                            f'<div class="chunk-text">{chunk["text"][:320]}{"…" if len(chunk["text"]) > 320 else ""}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

    st.divider()

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        question = st.text_input(
            "question",
            placeholder="Ask something about your documents…",
            label_visibility="collapsed",
            key="question_input",
        )
    with col_btn:
        send = st.button("Send ➤", use_container_width=True)

    if send and question.strip():
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Searching knowledge base…"):
            result = api_post("/ask", json_data={
                "question": question,
                "source_filter": source_filter,
            })

        if result:
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "chunks_used": result["chunks_used"],
                "retrieved_chunks": result["retrieved_chunks"],
                "model_used": result["model_used"],
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Could not get a response. Check the API logs.",
            })

        st.rerun()


# ── Page: Knowledge Base ──────────────────────────────────────────────────────

elif page == "📚  Knowledge Base":
    st.markdown('<div class="page-eyebrow">Storage</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Knowledge <em>Base</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">All documents indexed in ChromaDB and ready for retrieval</div>', unsafe_allow_html=True)

    docs_data = api_get("/documents")

    if docs_data:
        total_docs = len(docs_data.get("documents", []))
        total_chunks = docs_data.get("total_chunks", 0)
        avg_chunks = round(total_chunks / total_docs, 1) if total_docs else 0

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{total_docs}</div>'
                f'<div class="metric-label">Documents</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{total_chunks}</div>'
                f'<div class="metric-label">Total Chunks</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{avg_chunks}</div>'
                f'<div class="metric-label">Avg Chunks / Doc</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if docs_data["documents"]:
            st.markdown(
                '<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.12em;'
                'text-transform:uppercase;color:#3a3850;margin-bottom:0.8rem;">Indexed Files</div>',
                unsafe_allow_html=True,
            )
            for doc in docs_data["documents"]:
                icon = "📕" if doc["file_type"] == "pdf" else "📄"
                st.markdown(
                    f'<div class="doc-card">'
                    f'<div class="doc-icon">{icon}</div>'
                    f'<div>'
                    f'<div class="doc-name">{doc["source"]}</div>'
                    f'<span class="doc-type">{doc["file_type"].upper()}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-state-icon">📭</div>'
                '<div class="empty-state-text">No documents yet — go to Upload to add files</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.warning("Could not reach the API. Is uvicorn running?")