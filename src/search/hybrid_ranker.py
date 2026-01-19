"""
Hybrid search combining vector similarity and BM25 keyword search
Uses Reciprocal Rank Fusion (RRF) for combining results
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from rank_bm25 import BM25Okapi

from config.settings import (
    VECTOR_SEARCH_K, BM25_SEARCH_K, FINAL_RESULTS_K,
    RRF_K, VECTOR_WEIGHT, BM25_WEIGHT
)
from ..database.chroma_store import ChromaStore


@dataclass
class SearchResult:
    """Represents a search result with score and metadata"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    vector_rank: Optional[int] = None
    bm25_rank: Optional[int] = None


class HybridRanker:
    """
    Hybrid search combining vector similarity and BM25 keyword matching
    Uses Reciprocal Rank Fusion to combine rankings
    """

    def __init__(
        self,
        chroma_store: ChromaStore,
        vector_k: int = VECTOR_SEARCH_K,
        bm25_k: int = BM25_SEARCH_K,
        final_k: int = FINAL_RESULTS_K,
        rrf_k: int = RRF_K,
        vector_weight: float = VECTOR_WEIGHT,
        bm25_weight: float = BM25_WEIGHT
    ):
        """
        Initialize the hybrid ranker

        Args:
            chroma_store: ChromaDB store instance
            vector_k: Number of results from vector search
            bm25_k: Number of results from BM25 search
            final_k: Number of final results after fusion
            rrf_k: Constant for RRF calculation
            vector_weight: Weight for vector search results
            bm25_weight: Weight for BM25 results
        """
        self.store = chroma_store
        self.vector_k = vector_k
        self.bm25_k = bm25_k
        self.final_k = final_k
        self.rrf_k = rrf_k
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight

        # BM25 index (built on first search)
        self._bm25_index = None
        self._bm25_docs = None
        self._bm25_ids = None
        self._bm25_metadatas = None

    def _build_bm25_index(self) -> None:
        """Build BM25 index from all documents in the store"""
        all_data = self.store.get_all_chunks()

        self._bm25_ids = all_data["ids"]
        self._bm25_docs = all_data["documents"]
        self._bm25_metadatas = all_data["metadatas"]

        # Tokenize documents for BM25
        tokenized_docs = [self._tokenize(doc) for doc in self._bm25_docs]
        self._bm25_index = BM25Okapi(tokenized_docs)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25"""
        # Lowercase and split on non-alphanumeric characters
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def search(
        self,
        query: str,
        n_results: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining vector and BM25

        Args:
            query: Search query
            n_results: Number of results (defaults to final_k)
            where: Metadata filter for vector search

        Returns:
            List of SearchResult objects ranked by hybrid score
        """
        n_results = n_results or self.final_k

        # Get vector search results
        vector_results = self._vector_search(query, where)

        # Get BM25 results
        bm25_results = self._bm25_search(query)

        # Combine with RRF
        combined = self._reciprocal_rank_fusion(vector_results, bm25_results)

        # Apply metadata filter to combined results if needed
        if where:
            combined = self._apply_metadata_filter(combined, where)

        return combined[:n_results]

    def _vector_search(
        self,
        query: str,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, str, Dict[str, Any], float]]:
        """
        Perform vector similarity search

        Returns:
            List of (id, content, metadata, distance) tuples
        """
        results = self.store.search(
            query=query,
            n_results=self.vector_k,
            where=where
        )

        return list(zip(
            results["ids"],
            results["documents"],
            results["metadatas"],
            results["distances"]
        ))

    def _bm25_search(self, query: str) -> List[Tuple[str, str, Dict[str, Any], float]]:
        """
        Perform BM25 keyword search

        Returns:
            List of (id, content, metadata, score) tuples
        """
        # Build index if needed
        if self._bm25_index is None:
            self._build_bm25_index()

        # Tokenize query
        query_tokens = self._tokenize(query)

        # Get BM25 scores
        scores = self._bm25_index.get_scores(query_tokens)

        # Get top-k results
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        top_k = indexed_scores[:self.bm25_k]

        results = []
        for idx, score in top_k:
            if score > 0:  # Only include results with positive scores
                results.append((
                    self._bm25_ids[idx],
                    self._bm25_docs[idx],
                    self._bm25_metadatas[idx],
                    score
                ))

        return results

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Tuple[str, str, Dict[str, Any], float]],
        bm25_results: List[Tuple[str, str, Dict[str, Any], float]]
    ) -> List[SearchResult]:
        """
        Combine results using Reciprocal Rank Fusion

        RRF Score = sum(1 / (k + rank)) for each result list
        """
        # Create score dictionaries
        scores = {}  # id -> RRF score
        contents = {}  # id -> content
        metadatas = {}  # id -> metadata
        vector_ranks = {}  # id -> vector rank
        bm25_ranks = {}  # id -> bm25 rank

        # Process vector results
        for rank, (chunk_id, content, metadata, distance) in enumerate(vector_results, 1):
            rrf_score = self.vector_weight * (1.0 / (self.rrf_k + rank))
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            contents[chunk_id] = content
            metadatas[chunk_id] = metadata
            vector_ranks[chunk_id] = rank

        # Process BM25 results
        for rank, (chunk_id, content, metadata, bm25_score) in enumerate(bm25_results, 1):
            rrf_score = self.bm25_weight * (1.0 / (self.rrf_k + rank))
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            contents[chunk_id] = content
            metadatas[chunk_id] = metadata
            bm25_ranks[chunk_id] = rank

        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Create SearchResult objects
        results = []
        for chunk_id in sorted_ids:
            result = SearchResult(
                chunk_id=chunk_id,
                content=contents[chunk_id],
                metadata=metadatas[chunk_id],
                score=scores[chunk_id],
                vector_rank=vector_ranks.get(chunk_id),
                bm25_rank=bm25_ranks.get(chunk_id)
            )
            results.append(result)

        return results

    def _apply_metadata_filter(
        self,
        results: List[SearchResult],
        where: Dict[str, Any]
    ) -> List[SearchResult]:
        """Apply metadata filter to results"""
        filtered = []
        for result in results:
            match = True
            for key, value in where.items():
                if key not in result.metadata:
                    match = False
                    break
                if result.metadata[key] != value:
                    match = False
                    break
            if match:
                filtered.append(result)
        return filtered

    def refresh_bm25_index(self) -> None:
        """Refresh the BM25 index after adding new documents"""
        self._bm25_index = None
        self._build_bm25_index()

    def vector_only_search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Perform vector-only search (no BM25)"""
        results = self._vector_search(query, where)

        return [
            SearchResult(
                chunk_id=chunk_id,
                content=content,
                metadata=metadata,
                score=1.0 / (1.0 + distance),  # Convert distance to similarity
                vector_rank=rank
            )
            for rank, (chunk_id, content, metadata, distance) in enumerate(results[:n_results], 1)
        ]

    def keyword_only_search(
        self,
        query: str,
        n_results: int = 10
    ) -> List[SearchResult]:
        """Perform keyword-only search (BM25 only)"""
        results = self._bm25_search(query)

        return [
            SearchResult(
                chunk_id=chunk_id,
                content=content,
                metadata=metadata,
                score=score,
                bm25_rank=rank
            )
            for rank, (chunk_id, content, metadata, score) in enumerate(results[:n_results], 1)
        ]
