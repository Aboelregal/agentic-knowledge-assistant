"""
retriever.py
------------
Provides a clean interface for retrieving relevant document chunks
from the vector store. Used by the Retrieval Agent.
"""

import logging
from typing import List, Dict, Any, Optional

from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Wraps VectorStore with retrieval-specific logic.

    Responsibilities:
    - Query the vector store for relevant chunks
    - Filter out low-relevance results by distance threshold
    - Format results for use by the QA Agent
    """

    def __init__(
        self,
        vector_store: VectorStore,
        max_results: int = 5,
        distance_threshold: float = 0.7,  # Cosine distance (lower = more similar)
    ):
        """
        Args:
            vector_store: Initialized VectorStore instance
            max_results: Maximum number of chunks to retrieve
            distance_threshold: Discard chunks with distance > this value
        """
        self.vector_store = vector_store
        self.max_results = max_results
        self.distance_threshold = distance_threshold

    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        source_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: User's question or search query
            n_results: Override default max_results
            source_filter: Limit search to a specific source document

        Returns:
            List of relevant chunk dicts, sorted by relevance
        """
        n = n_results or self.max_results

        # Optional: filter by source document
        where = {"source": source_filter} if source_filter else None

        # Retrieve from vector store
        raw_results = self.vector_store.search(
            query=query,
            n_results=n,
            where=where,
        )

        # Filter by distance threshold (remove irrelevant results)
        filtered = [
            r for r in raw_results
            if r["distance"] <= self.distance_threshold
        ]

        if not filtered and raw_results:
            # Fallback: return top result even if above threshold
            logger.warning(
                f"All results exceeded distance threshold ({self.distance_threshold}). "
                "Returning top result as fallback."
            )
            filtered = [raw_results[0]]

        logger.info(
            f"Retrieved {len(filtered)} chunks "
            f"(filtered from {len(raw_results)} raw results)"
        )

        return filtered

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into a single context string for the LLM.

        Args:
            chunks: List of chunk dicts from retrieve()

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("source", "Unknown")
            page = chunk["metadata"].get("page", "?")
            context_parts.append(
                f"[Source {i}: {source}, Page {page}]\n{chunk['text']}"
            )

        return "\n\n---\n\n".join(context_parts)
