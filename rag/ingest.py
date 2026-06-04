"""
ingest.py
---------
Handles document ingestion: loading PDFs and TXT files,
splitting them into overlapping chunks, and storing them
in the ChromaDB vector store via VectorStore.
"""

import hashlib
import logging
import os
import uuid
from typing import List, Tuple, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

# Default chunking parameters — tuned for RAG quality
DEFAULT_CHUNK_SIZE = 500       # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 100    # Overlap between consecutive chunks


class DocumentIngestor:
    """
    Handles the full RAG ingestion pipeline:
    1. Load document (PDF or TXT)
    2. Split into overlapping chunks
    3. Attach metadata to each chunk
    4. Store chunks + embeddings in ChromaDB
    """

    def __init__(
        self,
        vector_store: VectorStore,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        """
        Args:
            vector_store: Initialized VectorStore instance
            chunk_size: Target character length per chunk
            chunk_overlap: Characters shared between adjacent chunks
        """
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],  # Prefer semantic breaks
        )

    def _clean_text(self, text: str) -> str:
        """
        Remove surrogate characters and fix common PDF encoding issues.
        Surrogates (\ud800-\udfff) appear in PDFs with math symbols or
        special fonts and cause UTF-8 encoding errors in ChromaDB.
        """
        # Strip surrogates and any other non-encodable characters
        text = text.encode("utf-8", errors="ignore").decode("utf-8")
        # Replace common PDF ligatures and punctuation look-alikes
        replacements = {
            "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
            "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "--", "\u00a0": " ", "\u00ad": "",
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)
        return text

    def _load_pdf(self, file_path: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Load a PDF and return list of (text, metadata) tuples per page.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of (page_text, metadata) tuples
        """
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        logger.info(f"Loaded PDF with {len(pages)} pages: {file_path}")

        return [
            (
                self._clean_text(page.page_content),
                {
                    "source": os.path.basename(file_path),
                    "file_type": "pdf",
                    "page": page.metadata.get("page", i),
                },
            )
            for i, page in enumerate(pages)
        ]

    def _load_txt(self, file_path: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Load a plain text file and return as single (text, metadata) tuple.

        Args:
            file_path: Path to the TXT file

        Returns:
            List with one (text, metadata) tuple
        """
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        logger.info(f"Loaded TXT file: {file_path}")

        return [
            (
                self._clean_text(doc.page_content),
                {
                    "source": os.path.basename(file_path),
                    "file_type": "txt",
                    "page": 0,
                },
            )
            for doc in docs
        ]

    def _chunk_document(
        self, text: str, base_metadata: Dict[str, Any]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split a single document text into overlapping chunks.

        Args:
            text: Raw document text
            base_metadata: Metadata shared by all chunks from this document

        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        chunks = self.text_splitter.split_text(text)
        results = []

        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                metadata = {**base_metadata, "chunk_index": i}
                results.append((chunk, metadata))

        return results

    def _generate_chunk_id(self, source: str, chunk_index: int, text: str) -> str:
        """
        Generate a deterministic, unique ID for a chunk.
        Using a hash ensures re-ingesting the same file won't create duplicates.

        Args:
            source: Source filename
            chunk_index: Position of chunk in document
            text: Chunk text (for uniqueness)

        Returns:
            Unique string ID
        """
        content = f"{source}_{chunk_index}_{text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()

    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Full ingestion pipeline for a single file.

        Args:
            file_path: Path to the file to ingest

        Returns:
            Dict with ingestion results (chunks_added, source, status)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Ingesting file: {file_path} (type: {ext})")

        # Step 1: Load document based on file type
        if ext == ".pdf":
            pages = self._load_pdf(file_path)
        elif ext == ".txt":
            pages = self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .txt")

        # Step 2: Split each page into chunks
        all_chunks: List[str] = []
        all_metadatas: List[Dict[str, Any]] = []
        all_ids: List[str] = []

        for text, metadata in pages:
            page_chunks = self._chunk_document(text, metadata)
            for chunk_text, chunk_metadata in page_chunks:
                chunk_id = self._generate_chunk_id(
                    metadata["source"],
                    chunk_metadata["chunk_index"],
                    chunk_text,
                )
                all_chunks.append(chunk_text)
                all_metadatas.append(chunk_metadata)
                all_ids.append(chunk_id)

        if not all_chunks:
            logger.warning(f"No chunks extracted from {file_path}")
            return {"chunks_added": 0, "source": os.path.basename(file_path), "status": "empty"}

        # Step 3: Store in ChromaDB
        added = self.vector_store.add_documents(all_chunks, all_metadatas, all_ids)

        result = {
            "chunks_added": added,
            "source": os.path.basename(file_path),
            "file_type": ext.lstrip("."),
            "status": "success",
        }
        logger.info(f"Ingestion complete: {result}")
        return result