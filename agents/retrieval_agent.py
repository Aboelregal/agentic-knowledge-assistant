"""
retrieval_agent.py
------------------
The Retrieval Agent is responsible for:
1. Understanding the user's query
2. Searching the ChromaDB vector store for relevant chunks
3. Returning structured results to the QA Agent

This agent acts as the "memory" of the system — it knows
how to find information but not how to answer questions.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from rag.retriever import Retriever
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Structured output from the Retrieval Agent."""

    query: str
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    context: str = ""
    sources: List[str] = field(default_factory=list)
    chunk_count: int = 0
    status: str = "success"
    error: Optional[str] = None


class RetrievalAgent:
    """
    Agent that searches the knowledge base for relevant information.

    Workflow:
    1. Receive a query string
    2. Use Retriever to fetch top-k relevant chunks from ChromaDB
    3. Format chunks into a context string for the LLM
    4. Return a RetrievalResult with chunks, context, and source list
    """

    def __init__(
        self,
        vector_store: VectorStore,
        max_results: int = 5,
        distance_threshold: float = 0.7,
    ):
        """
        Args:
            vector_store: Shared VectorStore instance
            max_results: Max chunks to retrieve per query
            distance_threshold: Relevance filter threshold
        """
        self.retriever = Retriever(
            vector_store=vector_store,
            max_results=max_results,
            distance_threshold=distance_threshold,
        )
        logger.info("RetrievalAgent initialized.")

    def run(self, query: str, source_filter: Optional[str] = None) -> RetrievalResult:
        """
        Execute the retrieval pipeline for a given query.

        Args:
            query: The user's question
            source_filter: Optionally restrict search to one document

        Returns:
            RetrievalResult with relevant chunks and formatted context
        """
        logger.info(f"[RetrievalAgent] Running for query: '{query}'")

        try:
            # Retrieve relevant chunks
            chunks = self.retriever.retrieve(
                query=query,
                source_filter=source_filter,
            )

            if not chunks:
                logger.warning("[RetrievalAgent] No relevant chunks found.")
                return RetrievalResult(
                    query=query,
                    chunks=[],
                    context="No relevant information found in the knowledge base.",
                    sources=[],
                    chunk_count=0,
                    status="no_results",
                )

            # Format chunks into a context string for the LLM
            context = self.retriever.format_context(chunks)

            # Collect unique source document names
            sources = list(
                {chunk["metadata"].get("source", "Unknown") for chunk in chunks}
            )

            logger.info(
                f"[RetrievalAgent] Retrieved {len(chunks)} chunks from {len(sources)} source(s)."
            )

            return RetrievalResult(
                query=query,
                chunks=chunks,
                context=context,
                sources=sources,
                chunk_count=len(chunks),
                status="success",
            )

        except Exception as e:
            logger.error(f"[RetrievalAgent] Error during retrieval: {e}", exc_info=True)
            return RetrievalResult(
                query=query,
                status="error",
                error=str(e),
                context="An error occurred while searching the knowledge base.",
            )
