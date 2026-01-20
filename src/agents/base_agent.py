"""
Base Agent - Abstract base class for all specialized agents.

All agents inherit from this class and implement:
- can_handle(): Determine if this agent should handle a message
- execute(): Process the message and return a response
- execute_guided(): (Optional) Multi-step workflow with checkpoints
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, Dict, Any, List, Optional
from enum import Enum


class AgentMode(Enum):
    """Execution mode for agent responses."""
    SINGLE_TURN = "single_turn"      # Quick response, no confirmation needed
    GUIDED = "guided"                 # Multi-step with user confirmation


@dataclass
class AgentContext:
    """Context passed to agents during execution."""
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    tenant_filter: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_last_user_message(self) -> Optional[str]:
        """Get the most recent user message from history."""
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "user":
                return msg.get("content")
        return None

    def get_mentioned_tenants(self) -> List[str]:
        """Extract tenant names mentioned in recent conversation."""
        tenants = []
        if "mentioned_tenants" in self.metadata:
            tenants = self.metadata["mentioned_tenants"]
        return tenants


@dataclass
class AgentResponse:
    """Response from an agent execution."""

    # The main response message
    message: str

    # Whether this response requires user confirmation before proceeding
    requires_confirmation: bool = False

    # Prompt to show user for confirmation (if requires_confirmation is True)
    confirmation_prompt: Optional[str] = None

    # Data extracted or computed (e.g., parsed lease terms)
    data: Dict[str, Any] = field(default_factory=dict)

    # Sources/citations used
    sources: List[Dict[str, Any]] = field(default_factory=list)

    # For guided workflows: description of next step
    next_step: Optional[str] = None

    # Whether the agent task is complete
    is_complete: bool = True

    # Execution mode used
    mode: AgentMode = AgentMode.SINGLE_TURN

    # Agent that generated this response
    agent_name: Optional[str] = None

    def to_chat_response(self) -> Dict[str, Any]:
        """Convert to format compatible with chat UI."""
        return {
            "answer": self.message,
            "sources": self.sources,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_prompt": self.confirmation_prompt,
            "agent": self.agent_name,
            "data": self.data,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.

    Agents analyze incoming messages and determine if they can handle them.
    If confidence is high enough, they execute specialized workflows.

    Subclasses must implement:
    - name: Property returning the agent's name
    - description: Property returning what the agent does
    - trigger_patterns: Patterns that activate this agent
    - can_handle(): Return confidence score 0-1
    - execute(): Process message and return AgentResponse

    Optionally implement:
    - execute_guided(): Multi-step workflow with checkpoints
    """

    def __init__(self, query_engine=None, sql_store=None, llm=None):
        """
        Initialize the agent with shared resources.

        Args:
            query_engine: The RAG query engine for document search
            sql_store: SQLite database for structured data
            llm: LLM client for generation
        """
        self.query_engine = query_engine
        self.sql_store = sql_store
        self.llm = llm

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent's name (e.g., 'LeaseIngestorAgent')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what this agent does."""
        pass

    @property
    @abstractmethod
    def trigger_patterns(self) -> List[str]:
        """
        Return patterns that indicate this agent should handle a message.

        These are used for quick filtering before detailed analysis.
        Examples: ["ingest", "process lease", "add document"]
        """
        pass

    @abstractmethod
    def can_handle(self, message: str, context: AgentContext) -> float:
        """
        Determine if this agent should handle the given message.

        Args:
            message: The user's message
            context: Conversation context

        Returns:
            Confidence score between 0.0 and 1.0
            - 0.0: Definitely cannot handle
            - 0.5: Uncertain, might be able to handle
            - 1.0: Definitely should handle this
        """
        pass

    @abstractmethod
    def execute(self, message: str, context: AgentContext) -> AgentResponse:
        """
        Execute the agent's primary function (single-turn).

        Args:
            message: The user's message
            context: Conversation context

        Returns:
            AgentResponse with the result
        """
        pass

    def execute_guided(
        self,
        message: str,
        context: AgentContext
    ) -> Generator[AgentResponse, Optional[str], None]:
        """
        Execute a multi-step guided workflow with user checkpoints.

        This is a generator that yields AgentResponse objects at each step.
        If a response has requires_confirmation=True, the caller should
        wait for user input before sending it back to continue.

        Args:
            message: The user's message
            context: Conversation context

        Yields:
            AgentResponse for each step

        Receives:
            User confirmation/input via generator.send()
        """
        # Default implementation: just do single-turn
        yield self.execute(message, context)

    def supports_guided_mode(self) -> bool:
        """Return True if this agent supports multi-step guided workflows."""
        # Check if execute_guided is overridden
        return type(self).execute_guided is not BaseAgent.execute_guided

    def _quick_pattern_match(self, message: str) -> bool:
        """
        Quick check if message might match this agent's triggers.

        Used for fast filtering before detailed can_handle() analysis.
        """
        message_lower = message.lower()
        return any(
            pattern.lower() in message_lower
            for pattern in self.trigger_patterns
        )

    def _extract_confidence_factors(self, message: str, context: AgentContext) -> Dict[str, float]:
        """
        Helper to extract factors contributing to confidence score.

        Subclasses can override to add domain-specific factors.

        Returns:
            Dict mapping factor name to score (0-1)
        """
        factors = {}

        # Pattern matching factor
        if self._quick_pattern_match(message):
            factors["pattern_match"] = 0.6
        else:
            factors["pattern_match"] = 0.0

        return factors

    def _compute_confidence(self, factors: Dict[str, float]) -> float:
        """
        Compute overall confidence from individual factors.

        Default: weighted average with pattern_match weighted heavily.
        Subclasses can override for custom logic.
        """
        if not factors:
            return 0.0

        # Weight pattern matching more heavily
        weights = {
            "pattern_match": 2.0,
            "context_relevance": 1.0,
            "entity_presence": 1.5,
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for factor, score in factors.items():
            weight = weights.get(factor, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return min(1.0, weighted_sum / total_weight)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
