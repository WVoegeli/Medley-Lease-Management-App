"""
Tests for the Agent Framework.

Tests cover:
- BaseAgent abstract class and response types
- AgentRouter routing logic
- Context handling
- Fallback behavior
"""

import pytest
from typing import List

from src.agents.base_agent import (
    BaseAgent,
    AgentResponse,
    AgentContext,
    AgentMode
)
from src.agents.agent_router import AgentRouter, RoutingResult


# ============== Test Fixtures ==============

class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(
        self,
        name: str = "MockAgent",
        triggers: List[str] = None,
        confidence: float = 0.8
    ):
        super().__init__()
        self._name = name
        self._triggers = triggers or ["mock", "test"]
        self._confidence = confidence

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "A mock agent for testing"

    @property
    def trigger_patterns(self) -> List[str]:
        return self._triggers

    def can_handle(self, message: str, context: AgentContext) -> float:
        if self._quick_pattern_match(message):
            return self._confidence
        return 0.0

    def execute(self, message: str, context: AgentContext) -> AgentResponse:
        return AgentResponse(
            message=f"MockAgent handled: {message}",
            agent_name=self.name
        )


class MockQueryEngine:
    """Mock query engine for testing fallback behavior."""

    def chat(self, message, conversation_history=None, tenant_filter=None):
        class MockResponse:
            answer = f"RAG response for: {message}"
            sources = [{"source": "test.docx", "content": "test content"}]
        return MockResponse()


# ============== AgentContext Tests ==============

class TestAgentContext:
    """Tests for AgentContext class."""

    def test_empty_context(self):
        """Test creating an empty context."""
        ctx = AgentContext()
        assert ctx.conversation_history == []
        assert ctx.tenant_filter is None
        assert ctx.session_id is None
        assert ctx.metadata == {}

    def test_context_with_history(self):
        """Test context with conversation history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        ctx = AgentContext(conversation_history=history)
        assert len(ctx.conversation_history) == 2

    def test_get_last_user_message(self):
        """Test extracting last user message."""
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Second question"},
        ]
        ctx = AgentContext(conversation_history=history)
        assert ctx.get_last_user_message() == "Second question"

    def test_get_last_user_message_empty(self):
        """Test last user message with empty history."""
        ctx = AgentContext()
        assert ctx.get_last_user_message() is None

    def test_tenant_filter(self):
        """Test tenant filter."""
        ctx = AgentContext(tenant_filter="Summit Coffee")
        assert ctx.tenant_filter == "Summit Coffee"


# ============== AgentResponse Tests ==============

class TestAgentResponse:
    """Tests for AgentResponse class."""

    def test_simple_response(self):
        """Test creating a simple response."""
        resp = AgentResponse(message="Hello!")
        assert resp.message == "Hello!"
        assert resp.requires_confirmation is False
        assert resp.is_complete is True
        assert resp.mode == AgentMode.SINGLE_TURN

    def test_confirmation_response(self):
        """Test response requiring confirmation."""
        resp = AgentResponse(
            message="Found 5 items",
            requires_confirmation=True,
            confirmation_prompt="Proceed with import?"
        )
        assert resp.requires_confirmation is True
        assert resp.confirmation_prompt == "Proceed with import?"

    def test_response_with_data(self):
        """Test response with extracted data."""
        resp = AgentResponse(
            message="Analysis complete",
            data={"total_rent": 50000, "tenant_count": 10}
        )
        assert resp.data["total_rent"] == 50000
        assert resp.data["tenant_count"] == 10

    def test_to_chat_response(self):
        """Test conversion to chat-compatible format."""
        resp = AgentResponse(
            message="Test message",
            sources=[{"file": "test.docx"}],
            agent_name="TestAgent"
        )
        chat_resp = resp.to_chat_response()
        assert chat_resp["answer"] == "Test message"
        assert chat_resp["agent"] == "TestAgent"
        assert len(chat_resp["sources"]) == 1


# ============== BaseAgent Tests ==============

class TestBaseAgent:
    """Tests for BaseAgent class."""

    def test_mock_agent_properties(self):
        """Test basic agent properties."""
        agent = MockAgent(name="TestAgent", triggers=["analyze", "check"])
        assert agent.name == "TestAgent"
        assert "analyze" in agent.trigger_patterns
        assert agent.description == "A mock agent for testing"

    def test_quick_pattern_match(self):
        """Test quick pattern matching."""
        agent = MockAgent(triggers=["ingest", "process"])

        assert agent._quick_pattern_match("Please ingest this document")
        assert agent._quick_pattern_match("PROCESS the lease")
        assert not agent._quick_pattern_match("What is the rent?")

    def test_can_handle_with_match(self):
        """Test can_handle with matching message."""
        agent = MockAgent(triggers=["analyze"], confidence=0.9)
        ctx = AgentContext()

        score = agent.can_handle("Please analyze the financials", ctx)
        assert score == 0.9

    def test_can_handle_no_match(self):
        """Test can_handle with non-matching message."""
        agent = MockAgent(triggers=["analyze"], confidence=0.9)
        ctx = AgentContext()

        score = agent.can_handle("What is the rent?", ctx)
        assert score == 0.0

    def test_execute(self):
        """Test agent execution."""
        agent = MockAgent()
        ctx = AgentContext()

        response = agent.execute("mock request", ctx)
        assert "MockAgent handled" in response.message

    def test_supports_guided_mode(self):
        """Test guided mode support detection."""
        agent = MockAgent()
        # MockAgent doesn't override execute_guided
        assert not agent.supports_guided_mode()

    def test_repr(self):
        """Test string representation."""
        agent = MockAgent(name="TestAgent")
        assert "TestAgent" in repr(agent)


# ============== AgentRouter Tests ==============

class TestAgentRouter:
    """Tests for AgentRouter class."""

    def test_router_initialization(self):
        """Test router initialization."""
        agents = [MockAgent(name="Agent1"), MockAgent(name="Agent2")]
        router = AgentRouter(agents, confidence_threshold=0.7)

        assert len(router.agents) == 2
        assert router.confidence_threshold == 0.7

    def test_route_to_matching_agent(self):
        """Test routing to a matching agent."""
        agent = MockAgent(name="AnalyzerAgent", triggers=["analyze"], confidence=0.9)
        router = AgentRouter([agent], confidence_threshold=0.7)

        result = router.route("Please analyze this", AgentContext())

        assert result.agent is not None
        assert result.agent.name == "AnalyzerAgent"
        assert result.confidence == 0.9
        assert not result.fallback_to_rag

    def test_route_fallback_to_rag(self):
        """Test fallback when no agent matches."""
        agent = MockAgent(name="AnalyzerAgent", triggers=["analyze"], confidence=0.9)
        router = AgentRouter([agent], confidence_threshold=0.7)

        result = router.route("What is the rent?", AgentContext())

        assert result.agent is None
        assert result.fallback_to_rag is True

    def test_route_below_threshold(self):
        """Test fallback when confidence is below threshold."""
        agent = MockAgent(name="WeakAgent", triggers=["check"], confidence=0.5)
        router = AgentRouter([agent], confidence_threshold=0.7)

        result = router.route("Please check this", AgentContext())

        assert result.agent is None
        assert result.confidence == 0.5
        assert result.fallback_to_rag is True

    def test_route_multiple_agents(self):
        """Test routing with multiple agents - best match wins."""
        agent1 = MockAgent(name="Agent1", triggers=["analyze"], confidence=0.8)
        agent2 = MockAgent(name="Agent2", triggers=["analyze"], confidence=0.95)
        router = AgentRouter([agent1, agent2], confidence_threshold=0.7)

        result = router.route("analyze this", AgentContext())

        assert result.agent.name == "Agent2"
        assert result.confidence == 0.95

    def test_execute_with_agent(self):
        """Test execute() routing to agent."""
        agent = MockAgent(name="TestAgent", triggers=["test"], confidence=0.9)
        router = AgentRouter([agent], confidence_threshold=0.7)

        response = router.execute("test message")

        assert "MockAgent handled" in response.message
        assert response.agent_name == "TestAgent"

    def test_execute_with_rag_fallback(self):
        """Test execute() falling back to RAG."""
        agent = MockAgent(name="TestAgent", triggers=["test"], confidence=0.9)
        engine = MockQueryEngine()
        router = AgentRouter([agent], query_engine=engine, confidence_threshold=0.7)

        response = router.execute("what is the rent?")

        assert "RAG response" in response.message
        assert response.agent_name == "rag"

    def test_register_agent(self):
        """Test registering a new agent."""
        router = AgentRouter([], confidence_threshold=0.7)
        agent = MockAgent(name="NewAgent")

        router.register_agent(agent)

        assert len(router.agents) == 1
        assert router.agents[0].name == "NewAgent"

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        agent = MockAgent(name="ToRemove")
        router = AgentRouter([agent], confidence_threshold=0.7)

        result = router.unregister_agent("ToRemove")

        assert result is True
        assert len(router.agents) == 0

    def test_unregister_nonexistent(self):
        """Test unregistering non-existent agent."""
        router = AgentRouter([], confidence_threshold=0.7)

        result = router.unregister_agent("DoesNotExist")

        assert result is False

    def test_get_agent(self):
        """Test getting agent by name."""
        agent = MockAgent(name="FindMe")
        router = AgentRouter([agent], confidence_threshold=0.7)

        found = router.get_agent("FindMe")
        not_found = router.get_agent("NotHere")

        assert found is not None
        assert found.name == "FindMe"
        assert not_found is None

    def test_list_agents(self):
        """Test listing all agents."""
        agent1 = MockAgent(name="Agent1", triggers=["a", "b"])
        agent2 = MockAgent(name="Agent2", triggers=["c"])
        router = AgentRouter([agent1, agent2], confidence_threshold=0.7)

        agents = router.list_agents()

        assert len(agents) == 2
        assert agents[0]["name"] == "Agent1"
        assert agents[0]["triggers"] == ["a", "b"]

    def test_routing_result_agent_name(self):
        """Test RoutingResult agent_name property."""
        agent = MockAgent(name="NamedAgent")

        result_with_agent = RoutingResult(
            agent=agent, confidence=0.9, all_scores={}, fallback_to_rag=False
        )
        result_without_agent = RoutingResult(
            agent=None, confidence=0.0, all_scores={}, fallback_to_rag=True
        )

        assert result_with_agent.agent_name == "NamedAgent"
        assert result_without_agent.agent_name is None

    def test_repr(self):
        """Test string representation."""
        agent = MockAgent(name="TestAgent")
        router = AgentRouter([agent], confidence_threshold=0.8)

        repr_str = repr(router)
        assert "TestAgent" in repr_str
        assert "0.8" in repr_str


# ============== Integration Tests ==============

class TestAgentIntegration:
    """Integration tests for the agent framework."""

    def test_full_routing_flow(self):
        """Test complete routing flow with context."""
        # Create agents with different specialties
        ingest_agent = MockAgent(
            name="IngestAgent",
            triggers=["ingest", "process", "add document"],
            confidence=0.85
        )
        analyze_agent = MockAgent(
            name="AnalyzeAgent",
            triggers=["analyze", "financial", "revenue"],
            confidence=0.9
        )
        risk_agent = MockAgent(
            name="RiskAgent",
            triggers=["risk", "co-tenancy", "health"],
            confidence=0.88
        )

        router = AgentRouter(
            [ingest_agent, analyze_agent, risk_agent],
            confidence_threshold=0.7
        )

        # Test different message types
        ctx = AgentContext()

        # Should route to IngestAgent
        result1 = router.route("ingest the new lease document", ctx)
        assert result1.agent.name == "IngestAgent"

        # Should route to AnalyzeAgent
        result2 = router.route("analyze the financial performance", ctx)
        assert result2.agent.name == "AnalyzeAgent"

        # Should route to RiskAgent
        result3 = router.route("what are the co-tenancy risks?", ctx)
        assert result3.agent.name == "RiskAgent"

        # Should fall back to RAG
        result4 = router.route("what is summit coffee's rent?", ctx)
        assert result4.fallback_to_rag is True

    def test_context_preservation(self):
        """Test that context is preserved through routing."""
        agent = MockAgent(name="ContextAgent", triggers=["context"])
        router = AgentRouter([agent], confidence_threshold=0.7)

        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        ctx = AgentContext(
            conversation_history=history,
            tenant_filter="Summit Coffee",
            session_id="test-session"
        )

        result = router.route("context test", ctx)

        # Context should be available to agent
        assert result.agent is not None
        # Agent could use context in execution
        response = result.agent.execute("context test", ctx)
        assert response is not None
