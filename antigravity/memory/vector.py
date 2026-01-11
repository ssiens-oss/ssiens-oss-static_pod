"""Vector-based semantic memory for pattern recognition and learning."""

import os
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    chromadb = None
    SentenceTransformer = None


class VectorMemory:
    """Semantic memory using vector embeddings."""

    def __init__(
        self,
        collection_name: str = "pod_decisions",
        model_name: str = "all-MiniLM-L6-v2",
        persist_dir: Optional[str] = None,
    ):
        """
        Initialize vector memory.

        Args:
            collection_name: Name of the collection
            model_name: Sentence transformer model to use
            persist_dir: Directory to persist data (optional)
        """
        if not VECTOR_AVAILABLE:
            raise RuntimeError(
                "Vector memory requires chromadb and sentence-transformers. "
                "Install with: pip install chromadb sentence-transformers"
            )

        self.model = SentenceTransformer(model_name)

        # Initialize ChromaDB
        if persist_dir:
            self.client = chromadb.PersistentClient(path=persist_dir)
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "POD decision memory"}
        )

    def remember(
        self,
        text: str,
        id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store a memory.

        Args:
            text: Text to remember
            id: Unique identifier
            metadata: Optional metadata dict
        """
        try:
            embedding = self.model.encode(text).tolist()

            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                ids=[id],
                metadatas=[metadata] if metadata else None,
            )
        except Exception as e:
            print(f"Failed to store memory: {e}")

    def recall(
        self,
        query: str,
        n_results: int = 5,
        filter: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Recall similar memories.

        Args:
            query: Query text
            n_results: Number of results to return
            filter: Optional metadata filter

        Returns:
            Dict with 'ids', 'documents', 'distances', 'metadatas'
        """
        try:
            embedding = self.model.encode(query).tolist()

            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=filter,
            )

            return {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            }
        except Exception as e:
            print(f"Failed to recall memory: {e}")
            return {"ids": [], "documents": [], "distances": [], "metadatas": []}

    def has_seen_similar(
        self,
        query: str,
        similarity_threshold: float = 0.8,
    ) -> tuple[bool, Optional[Dict]]:
        """
        Check if we've seen something similar before.

        Args:
            query: Query text
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            (has_seen, most_similar_memory)
        """
        results = self.recall(query, n_results=1)

        if not results["ids"]:
            return False, None

        # Convert distance to similarity (lower distance = higher similarity)
        # ChromaDB uses L2 distance, so we need to invert it
        distance = results["distances"][0]
        similarity = 1.0 / (1.0 + distance)

        if similarity >= similarity_threshold:
            return True, {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "similarity": similarity,
                "metadata": results["metadatas"][0] if results["metadatas"] else None,
            }

        return False, None

    def count(self) -> int:
        """Get total number of memories stored."""
        return self.collection.count()

    def clear(self) -> None:
        """Clear all memories (use with caution!)."""
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.create_collection(
                name=self.collection.name,
                metadata={"description": "POD decision memory"}
            )
        except Exception as e:
            print(f"Failed to clear memory: {e}")
