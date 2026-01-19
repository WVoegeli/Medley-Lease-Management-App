"""
Query engine that orchestrates search and answer generation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .hybrid_ranker import HybridRanker, SearchResult
from ..database.chroma_store import ChromaStore
from ..llm.answer_generator import AnswerGenerator


@dataclass
class QueryResponse:
    """Response from the query engine"""
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    num_results: int


class QueryEngine:
    """
    Main query engine that combines search and LLM answer generation
    """

    def __init__(
        self,
        chroma_store: Optional[ChromaStore] = None,
        answer_generator: Optional[AnswerGenerator] = None
    ):
        """
        Initialize the query engine

        Args:
            chroma_store: ChromaDB store instance (creates new if None)
            answer_generator: LLM answer generator (creates new if None)
        """
        self.store = chroma_store or ChromaStore()
        self.ranker = HybridRanker(self.store)
        self.answer_generator = answer_generator or AnswerGenerator()

    def query(
        self,
        question: str,
        n_results: int = 5,
        tenant_filter: Optional[str] = None,
        include_sources: bool = True
    ) -> QueryResponse:
        """
        Process a question and return an answer

        Args:
            question: User's question
            n_results: Number of source chunks to retrieve
            tenant_filter: Optional tenant name to filter results
            include_sources: Whether to include source information

        Returns:
            QueryResponse with answer and sources
        """
        # Build metadata filter
        where = None
        if tenant_filter:
            where = {"tenant_name": tenant_filter}

        # Search for relevant chunks
        search_results = self.ranker.search(
            query=question,
            n_results=n_results,
            where=where
        )

        # Generate answer using LLM
        answer = self.answer_generator.generate_answer(
            question=question,
            contexts=[r.content for r in search_results],
            metadatas=[r.metadata for r in search_results]
        )

        # Prepare sources
        sources = []
        if include_sources:
            for result in search_results:
                sources.append({
                    "content": result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    "tenant": result.metadata.get("tenant_name", "Unknown"),
                    "section": result.metadata.get("section_name", "Unknown"),
                    "source_file": result.metadata.get("source_file", "Unknown"),
                    "score": result.score
                })

        return QueryResponse(
            answer=answer,
            sources=sources,
            query=question,
            num_results=len(search_results)
        )

    def search_only(
        self,
        query: str,
        n_results: int = 10,
        tenant_filter: Optional[str] = None,
        search_type: str = "hybrid"
    ) -> List[SearchResult]:
        """
        Search without generating an answer

        Args:
            query: Search query
            n_results: Number of results
            tenant_filter: Optional tenant filter
            search_type: "hybrid", "vector", or "keyword"

        Returns:
            List of SearchResult objects
        """
        where = {"tenant_name": tenant_filter} if tenant_filter else None

        if search_type == "vector":
            return self.ranker.vector_only_search(query, n_results, where)
        elif search_type == "keyword":
            return self.ranker.keyword_only_search(query, n_results)
        else:
            return self.ranker.search(query, n_results, where)

    def get_tenant_list(self) -> List[str]:
        """Get list of all tenants in the database"""
        return self.store.get_unique_tenants()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the database"""
        return {
            "total_chunks": self.store.count(),
            "tenants": self.get_tenant_list(),
            "num_tenants": len(self.get_tenant_list())
        }

    def compare_tenants(
        self,
        question: str,
        tenants: List[str]
    ) -> Dict[str, QueryResponse]:
        """
        Compare answers across multiple tenants

        Args:
            question: Question to ask about each tenant
            tenants: List of tenant names to compare

        Returns:
            Dictionary mapping tenant names to responses
        """
        responses = {}
        for tenant in tenants:
            responses[tenant] = self.query(
                question=question,
                tenant_filter=tenant
            )
        return responses

    def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        n_results: int = 5,
        tenant_filter: Optional[str] = None,
        include_sources: bool = True
    ) -> QueryResponse:
        """
        Process a chat message with conversation history

        Args:
            message: Current user message
            conversation_history: List of {"role": "user/assistant", "content": "..."}
            n_results: Number of source chunks to retrieve
            tenant_filter: Optional tenant name to filter results
            include_sources: Whether to include source information

        Returns:
            QueryResponse with answer and sources
        """
        # Build metadata filter
        where = None
        if tenant_filter:
            where = {"tenant_name": tenant_filter}

        # Search for relevant chunks based on current message
        search_results = self.ranker.search(
            query=message,
            n_results=n_results,
            where=where
        )

        # Generate answer using LLM with conversation history
        answer = self.answer_generator.generate_chat_response(
            message=message,
            contexts=[r.content for r in search_results],
            conversation_history=conversation_history,
            metadatas=[r.metadata for r in search_results]
        )

        # Prepare sources
        sources = []
        if include_sources:
            for result in search_results:
                sources.append({
                    "content": result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    "tenant": result.metadata.get("tenant_name", "Unknown"),
                    "section": result.metadata.get("section_name", "Unknown"),
                    "source_file": result.metadata.get("source_file", "Unknown"),
                    "score": result.score
                })

        return QueryResponse(
            answer=answer,
            sources=sources,
            query=message,
            num_results=len(search_results)
        )
