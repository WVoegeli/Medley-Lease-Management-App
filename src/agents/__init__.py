"""
Medley Lease Management - Agent Framework

This module provides specialized AI agents for lease management workflows:
- LeaseIngestorAgent: Process new lease documents
- FinancialAnalystAgent: Revenue analysis and projections
- RiskAssessorAgent: Portfolio risk assessment

Usage:
    from src.agents import AgentRouter, AgentResponse, create_default_agents

    # Create router with all agents
    agents = create_default_agents(query_engine, sql_store)
    router = AgentRouter(agents, query_engine=query_engine)

    # Route and execute
    response = router.execute(message, context)
"""

from src.agents.base_agent import BaseAgent, AgentResponse, AgentContext, AgentMode
from src.agents.agent_router import AgentRouter, RoutingResult
from src.agents.financial_analyst_agent import FinancialAnalystAgent
from src.agents.risk_assessor_agent import RiskAssessorAgent
from src.agents.lease_ingestor_agent import LeaseIngestorAgent


def create_default_agents(query_engine=None, sql_store=None, llm=None):
    """
    Create all default agents with shared resources.

    Args:
        query_engine: RAG query engine for document search
        sql_store: SQLite database connection
        llm: LLM client for generation

    Returns:
        List of initialized agents
    """
    return [
        FinancialAnalystAgent(query_engine, sql_store, llm),
        RiskAssessorAgent(query_engine, sql_store, llm),
        LeaseIngestorAgent(query_engine, sql_store, llm),
    ]


__all__ = [
    # Base classes
    'BaseAgent',
    'AgentResponse',
    'AgentContext',
    'AgentMode',

    # Router
    'AgentRouter',
    'RoutingResult',

    # Agents
    'FinancialAnalystAgent',
    'RiskAssessorAgent',
    'LeaseIngestorAgent',

    # Factory
    'create_default_agents',
]
