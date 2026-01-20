"""
Medley Lease Management - Agent Framework

This module provides specialized AI agents for lease management workflows:
- LeaseIngestorAgent: Process new lease documents
- FinancialAnalystAgent: Revenue analysis and projections
- RiskAssessorAgent: Portfolio risk assessment

Usage:
    from src.agents import AgentRouter, AgentResponse
    from src.agents.lease_ingestor_agent import LeaseIngestorAgent

    router = AgentRouter(agents=[...], query_engine=engine)
    agent, confidence = router.route(message, context)

    if agent:
        response = agent.execute(message, context)
    else:
        # Fall back to standard RAG
        response = query_engine.query(message)
"""

from src.agents.base_agent import BaseAgent, AgentResponse, AgentContext
from src.agents.agent_router import AgentRouter

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'AgentContext',
    'AgentRouter',
]
