"""
Agent prompts module.

Contains system prompts for each specialized agent.
"""

from src.agents.prompts.financial_analyst import FINANCIAL_ANALYST_PROMPT
from src.agents.prompts.risk_assessor import RISK_ASSESSOR_PROMPT
from src.agents.prompts.lease_ingestor import LEASE_INGESTOR_PROMPT

__all__ = [
    'FINANCIAL_ANALYST_PROMPT',
    'RISK_ASSESSOR_PROMPT',
    'LEASE_INGESTOR_PROMPT',
]
