"""
Agent Router - Routes incoming messages to the appropriate specialized agent.

The router analyzes each message, scores it against all registered agents,
and either routes to the best-matching agent or falls back to standard RAG.
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import logging

from src.agents.base_agent import BaseAgent, AgentContext, AgentResponse

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Result of the routing decision."""
    agent: Optional[BaseAgent]
    confidence: float
    all_scores: Dict[str, float]
    fallback_to_rag: bool

    @property
    def agent_name(self) -> Optional[str]:
        return self.agent.name if self.agent else None


class AgentRouter:
    """
    Routes incoming messages to specialized agents or standard RAG.

    The router maintains a list of registered agents and for each message:
    1. Scores the message against all agents
    2. Selects the highest-scoring agent above the threshold
    3. Falls back to standard RAG if no agent qualifies

    Usage:
        router = AgentRouter(agents=[agent1, agent2], query_engine=engine)
        result = router.route(message, context)

        if result.agent:
            response = result.agent.execute(message, context)
        else:
            response = query_engine.chat(message)
    """

    def __init__(
        self,
        agents: List[BaseAgent],
        query_engine=None,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize the router.

        Args:
            agents: List of specialized agents to route to
            query_engine: Fallback RAG engine for standard queries
            confidence_threshold: Minimum confidence to route to an agent (0-1)
        """
        self.agents = agents
        self.query_engine = query_engine
        self.confidence_threshold = confidence_threshold

        logger.info(
            f"AgentRouter initialized with {len(agents)} agents, "
            f"threshold={confidence_threshold}"
        )

    def route(
        self,
        message: str,
        context: Optional[AgentContext] = None
    ) -> RoutingResult:
        """
        Route a message to the appropriate agent.

        Args:
            message: The user's message
            context: Conversation context (optional)

        Returns:
            RoutingResult with the selected agent (or None for RAG fallback)
        """
        if context is None:
            context = AgentContext()

        # Score all agents
        scores = self._score_all_agents(message, context)

        # Find best match
        best_agent = None
        best_score = 0.0

        for agent, score in scores.items():
            if score > best_score:
                best_score = score
                best_agent = agent

        # Check threshold
        if best_score >= self.confidence_threshold and best_agent is not None:
            logger.info(
                f"Routing to {best_agent.name} with confidence {best_score:.2f}"
            )
            return RoutingResult(
                agent=best_agent,
                confidence=best_score,
                all_scores={a.name: s for a, s in scores.items()},
                fallback_to_rag=False
            )

        # Fall back to RAG
        logger.info(
            f"No agent matched threshold ({best_score:.2f} < {self.confidence_threshold}), "
            f"falling back to RAG"
        )
        return RoutingResult(
            agent=None,
            confidence=best_score,
            all_scores={a.name: s for a, s in scores.items()},
            fallback_to_rag=True
        )

    def _score_all_agents(
        self,
        message: str,
        context: AgentContext
    ) -> Dict[BaseAgent, float]:
        """Score all agents for a given message."""
        scores = {}

        for agent in self.agents:
            try:
                # Quick filter first
                if not agent._quick_pattern_match(message):
                    scores[agent] = 0.0
                    continue

                # Full scoring
                score = agent.can_handle(message, context)
                scores[agent] = max(0.0, min(1.0, score))  # Clamp to 0-1

            except Exception as e:
                logger.error(f"Error scoring agent {agent.name}: {e}")
                scores[agent] = 0.0

        return scores

    def execute(
        self,
        message: str,
        context: Optional[AgentContext] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AgentResponse:
        """
        Route and execute in one call.

        This is a convenience method that routes the message and either
        executes the matched agent or falls back to RAG.

        Args:
            message: The user's message
            context: Conversation context
            conversation_history: Chat history (used if context not provided)

        Returns:
            AgentResponse from either the agent or RAG fallback
        """
        # Build context if not provided
        if context is None:
            context = AgentContext(
                conversation_history=conversation_history or []
            )

        # Route
        result = self.route(message, context)

        # Execute
        if result.agent:
            response = result.agent.execute(message, context)
            response.agent_name = result.agent.name
            return response

        # Fallback to RAG
        return self._execute_rag_fallback(message, context)

    def _execute_rag_fallback(
        self,
        message: str,
        context: AgentContext
    ) -> AgentResponse:
        """Execute standard RAG query as fallback."""
        if self.query_engine is None:
            return AgentResponse(
                message="No query engine configured for fallback.",
                is_complete=True,
                agent_name="fallback"
            )

        try:
            # Use the query engine's chat method
            rag_response = self.query_engine.chat(
                message=message,
                conversation_history=context.conversation_history,
                tenant_filter=context.tenant_filter
            )

            return AgentResponse(
                message=rag_response.answer,
                sources=rag_response.sources if hasattr(rag_response, 'sources') else [],
                is_complete=True,
                agent_name="rag"
            )

        except Exception as e:
            logger.error(f"RAG fallback error: {e}")
            return AgentResponse(
                message=f"I encountered an error processing your request: {str(e)}",
                is_complete=True,
                agent_name="error"
            )

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the router."""
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent by name."""
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                logger.info(f"Unregistered agent: {agent_name}")
                return True
        return False

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with their info."""
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "triggers": agent.trigger_patterns,
                "supports_guided": agent.supports_guided_mode()
            }
            for agent in self.agents
        ]

    def __repr__(self) -> str:
        agent_names = [a.name for a in self.agents]
        return f"AgentRouter(agents={agent_names}, threshold={self.confidence_threshold})"
