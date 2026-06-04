"""
vector_store.py
---------------
Manages the ChromaDB vector database for storing and retrieving
document embeddings. Uses Sentence Transformers for local embeddings
(no API cost for embedding generation).
"""

import logging
import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to persist ChromaDB data
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")


class VectorStore:
    """
    Manages document embeddings in ChromaDB.

    This class handles:
    - Initializing the ChromaDB client and collection
    - Generating embeddings using Sentence Transformers
    - Adding document chunks to the vector store
    - Searching for similar chunks given a query
    """

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_path: str = CHROMA_DB_PATH,
    ):
        """
        Initialize the VectorStore.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Sentence Transformer model name
            persist_path: Directory path to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_path = persist_path

        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize ChromaDB with persistent storage
        logger.info(f"Initializing ChromaDB at: {persist_path}")
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )
        logger.info(f"ChromaDB collection '{collection_name}' ready.")

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> int:
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of text chunks to store
            metadatas: List of metadata dicts (e.g., source file, page number)
            ids: Unique IDs for each chunk

        Returns:
            Number of chunks added
        """
        if not chunks:
            logger.warning("No chunks provided to add_documents.")
            return 0

        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self._generate_embeddings(chunks)

        logger.info(f"Adding {len(chunks)} chunks to ChromaDB...")
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Successfully added {len(chunks)} chunks.")
        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for the most relevant chunks given a query.

        Args:
            query: The search query string
            n_results: Number of results to return
            where: Optional filter conditions for metadata

        Returns:
            List of result dicts with 'text', 'metadata', 'distance', and 'id'
        """
        logger.info(f"Searching for: '{query}' (top {n_results} results)")

        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]

        # Perform similarity search
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        # Format results into a clean list of dicts
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append(
                    {
                        "text": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "id": results["ids"][0][i],
                    }
                )

        logger.info(f"Found {len(formatted)} relevant chunks.")
        return formatted

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Retrieve all unique source documents stored in the collection.

        Returns:
            List of dicts with document metadata
        """
        try:
            results = self.collection.get(include=["metadatas"])
            seen_sources = set()
            documents = []

            for metadata in results.get("metadatas", []):
                source = metadata.get("source", "Unknown")
                if source not in seen_sources:
                    seen_sources.add(source)
                    documents.append(
                        {
                            "source": source,
                            "file_type": metadata.get("file_type", "unknown"),
                        }
                    )

            return documents
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return []

    def get_chunk_count(self) -> int:
        """Return the total number of chunks stored."""
        return self.collection.count()

    def delete_document(self, source: str) -> int:
        """
        Delete all chunks for a given source document.

        Args:
            source: The source filename to delete

        Returns:
            Number of chunks deleted
        """
        results = self.collection.get(where={"source": source})
        ids_to_delete = results.get("ids", [])

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for source: {source}")

        return len(ids_to_delete)
