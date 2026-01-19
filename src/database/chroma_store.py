"""
ChromaDB vector store for lease documents
Handles storage and retrieval of document chunks with embeddings
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings

from config.settings import CHROMA_PERSIST_DIR, COLLECTION_NAME
from ..chunking.chunker import Chunk
from ..vectorization.embedder import Embedder


class ChromaStore:
    """ChromaDB vector store for lease document chunks"""

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = COLLECTION_NAME
    ):
        """
        Initialize ChromaDB store

        Args:
            persist_dir: Directory for persistent storage
            collection_name: Name of the collection
        """
        self.persist_dir = persist_dir or str(CHROMA_PERSIST_DIR)
        self.collection_name = collection_name

        # Ensure directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Medley lease document chunks"}
        )

        # Initialize embedder
        self.embedder = Embedder()

    def add_chunks(self, chunks: List[Chunk], show_progress: bool = True) -> int:
        """
        Add chunks to the vector store

        Args:
            chunks: List of Chunk objects to add
            show_progress: Whether to show progress bar

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        # Extract texts and metadata
        texts = [chunk.content for chunk in chunks]
        ids = [chunk.id for chunk in chunks]
        metadatas = []

        for chunk in chunks:
            # Flatten metadata for ChromaDB (only supports primitive types)
            flat_metadata = {
                "source_file": chunk.source_file,
                "section_type": chunk.section_type,
                "section_name": chunk.section_name,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count
            }

            # Add metadata from chunk
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    flat_metadata[key] = value
                elif value is not None:
                    flat_metadata[key] = str(value)

            metadatas.append(flat_metadata)

        # Create embeddings
        embeddings = self.embedder.embed_texts(texts, show_progress=show_progress)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar chunks

        Args:
            query: Search query
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions

        Returns:
            Search results with documents, metadatas, and distances
        """
        # Create query embedding
        query_embedding = self.embedder.embed_query(query)

        # Build query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results
        }

        if where:
            query_params["where"] = where
        if where_document:
            query_params["where_document"] = where_document

        # Execute search
        results = self.collection.query(**query_params)

        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }

    def get_all_chunks(self) -> Dict[str, Any]:
        """
        Get all chunks from the store

        Returns:
            All stored chunks with their metadata
        """
        results = self.collection.get()
        return {
            "ids": results["ids"],
            "documents": results["documents"],
            "metadatas": results["metadatas"]
        }

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific chunk by ID

        Args:
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk data or None if not found
        """
        results = self.collection.get(ids=[chunk_id])
        if results["ids"]:
            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0]
            }
        return None

    def delete_all(self) -> None:
        """Delete all chunks from the store"""
        # Get all IDs and delete
        all_data = self.collection.get()
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])

    def count(self) -> int:
        """Get the number of chunks in the store"""
        return self.collection.count()

    def get_unique_tenants(self) -> List[str]:
        """Get list of unique tenant names in the store"""
        all_data = self.collection.get()
        tenants = set()
        for metadata in all_data["metadatas"]:
            if "tenant_name" in metadata:
                tenants.add(metadata["tenant_name"])
        return sorted(list(tenants))

    def search_by_tenant(
        self,
        tenant_name: str,
        query: str,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search within a specific tenant's documents

        Args:
            tenant_name: Name of tenant to filter by
            query: Search query
            n_results: Number of results

        Returns:
            Search results filtered by tenant
        """
        return self.search(
            query=query,
            n_results=n_results,
            where={"tenant_name": tenant_name}
        )
