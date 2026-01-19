"""
Conversation memory management for multi-turn lease queries.

Features:
- Context-aware responses based on conversation history
- Tenant context persistence
- Query refinement suggestions
- Conversation summarization
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import deque
import json
import hashlib


class ConversationTurn:
    """Represents a single turn in the conversation."""

    def __init__(self, query: str, response: str, context: Dict[str, Any] = None):
        self.query = query
        self.response = response
        self.context = context or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'response': self.response,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }


class ConversationMemory:
    """
    Manages conversation history and context for enhanced multi-turn queries.

    Tracks:
    - Previous questions and answers
    - Active tenant context
    - Referenced lease details
    - User preferences
    """

    def __init__(self, max_history: int = 10):
        """
        Initialize conversation memory.

        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.session_id = self._generate_session_id()
        self.active_context = {
            'tenant': None,
            'lease_id': None,
            'topic': None,
            'mentioned_tenants': set(),
            'mentioned_dates': []
        }
        self.session_start = datetime.now()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def add_turn(self, query: str, response: str, context: Dict[str, Any] = None):
        """
        Add a conversation turn to history.

        Args:
            query: User's question
            response: System's answer
            context: Additional context (tenant filter, sources, etc.)
        """
        turn = ConversationTurn(query, response, context)
        self.history.append(turn)

        # Update active context based on the query
        self._update_context(query, context)

    def _update_context(self, query: str, context: Dict[str, Any]):
        """Update active context based on query content."""
        if not context:
            return

        # Track tenant mentions
        if 'tenant_filter' in context and context['tenant_filter']:
            self.active_context['tenant'] = context['tenant_filter']
            self.active_context['mentioned_tenants'].add(context['tenant_filter'])

        # Track lease references
        if 'lease_id' in context:
            self.active_context['lease_id'] = context['lease_id']

        # Extract topic from query (basic keyword detection)
        topic_keywords = {
            'rent': ['rent', 'payment', 'price', 'cost'],
            'expiration': ['expire', 'expiration', 'end date', 'renewal'],
            'terms': ['term', 'length', 'duration'],
            'square_footage': ['square', 'footage', 'sqft', 'size', 'area'],
            'financial': ['revenue', 'income', 'financial', 'analytics']
        }

        query_lower = query.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in query_lower for kw in keywords):
                self.active_context['topic'] = topic
                break

    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation turns."""
        recent = list(self.history)[-count:]
        return [turn.to_dict() for turn in recent]

    def get_conversation_context(self) -> str:
        """
        Build a formatted context string for the LLM.

        Returns conversation history in a format that helps the LLM
        understand the ongoing conversation.
        """
        if not self.history:
            return ""

        context_parts = ["Previous conversation:"]

        for i, turn in enumerate(list(self.history)[-5:], 1):  # Last 5 turns
            context_parts.append(f"\nTurn {i}:")
            context_parts.append(f"User: {turn.query}")
            # Include brief version of response (first 200 chars)
            brief_response = turn.response[:200] + "..." if len(turn.response) > 200 else turn.response
            context_parts.append(f"Assistant: {brief_response}")

        # Add active context
        if self.active_context['tenant']:
            context_parts.append(f"\nActive tenant context: {self.active_context['tenant']}")

        if self.active_context['topic']:
            context_parts.append(f"Current topic: {self.active_context['topic']}")

        return "\n".join(context_parts)

    def get_active_tenant(self) -> Optional[str]:
        """Get the currently active tenant context."""
        return self.active_context['tenant']

    def set_active_tenant(self, tenant_name: str):
        """Set active tenant context."""
        self.active_context['tenant'] = tenant_name
        self.active_context['mentioned_tenants'].add(tenant_name)

    def clear_active_tenant(self):
        """Clear active tenant context."""
        self.active_context['tenant'] = None

    def get_mentioned_tenants(self) -> List[str]:
        """Get all tenants mentioned in this conversation."""
        return list(self.active_context['mentioned_tenants'])

    def suggest_follow_up_questions(self) -> List[str]:
        """
        Generate contextual follow-up question suggestions.

        Based on conversation history and active context.
        """
        suggestions = []

        if not self.history:
            return [
                "What is the total monthly revenue from all leases?",
                "Which leases are expiring in the next 90 days?",
                "Show me a financial summary of the portfolio"
            ]

        # Get last turn
        last_turn = list(self.history)[-1]
        topic = self.active_context.get('topic')
        tenant = self.active_context.get('tenant')

        # Generate contextual suggestions
        if topic == 'rent' and tenant:
            suggestions.extend([
                f"What are the renewal terms for {tenant}?",
                f"When does {tenant}'s lease expire?",
                f"How does {tenant}'s rent compare to similar tenants?"
            ])
        elif topic == 'expiration':
            suggestions.extend([
                "What is the total revenue at risk from expiring leases?",
                "Show me renewal options for expiring leases",
                "Which expiring leases have below-market rates?"
            ])
        elif tenant:
            suggestions.extend([
                f"What is the lease history for {tenant}?",
                f"Show me all financial terms for {tenant}",
                f"What special provisions does {tenant} have?"
            ])
        else:
            # General suggestions
            suggestions.extend([
                "What are the top tenants by revenue?",
                "Show me portfolio health metrics",
                "Which leases need attention soon?"
            ])

        return suggestions[:5]  # Return top 5

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the conversation.

        Useful for analytics and understanding user patterns.
        """
        return {
            'session_id': self.session_id,
            'turn_count': len(self.history),
            'duration_minutes': (datetime.now() - self.session_start).seconds / 60,
            'tenants_discussed': list(self.active_context['mentioned_tenants']),
            'topics': self._extract_topics(),
            'session_start': self.session_start.isoformat()
        }

    def _extract_topics(self) -> List[str]:
        """Extract unique topics from conversation history."""
        topics = set()
        for turn in self.history:
            if turn.context and 'topic' in turn.context:
                topics.add(turn.context['topic'])
        return list(topics)

    def export_conversation(self) -> str:
        """Export conversation history as JSON string."""
        data = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'history': [turn.to_dict() for turn in self.history],
            'context': {
                'tenant': self.active_context['tenant'],
                'topic': self.active_context['topic'],
                'mentioned_tenants': list(self.active_context['mentioned_tenants'])
            }
        }
        return json.dumps(data, indent=2)

    def clear(self):
        """Clear conversation history and reset context."""
        self.history.clear()
        self.active_context = {
            'tenant': None,
            'lease_id': None,
            'topic': None,
            'mentioned_tenants': set(),
            'mentioned_dates': []
        }

    def __len__(self) -> int:
        """Return number of turns in history."""
        return len(self.history)


class ConversationManager:
    """
    Manages multiple conversation sessions.

    Useful for web applications handling multiple concurrent users.
    """

    def __init__(self):
        """Initialize conversation manager."""
        self.sessions = {}

    def get_or_create_session(self, session_id: str = None) -> ConversationMemory:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional session ID. If None, creates new session.

        Returns:
            ConversationMemory instance
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        # Create new session
        memory = ConversationMemory()
        self.sessions[memory.session_id] = memory
        return memory

    def get_session(self, session_id: str) -> Optional[ConversationMemory]:
        """Get existing session by ID."""
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.sessions.keys())

    def cleanup_old_sessions(self, max_age_minutes: int = 60):
        """Remove sessions older than specified age."""
        now = datetime.now()
        to_remove = []

        for session_id, memory in self.sessions.items():
            age_minutes = (now - memory.session_start).seconds / 60
            if age_minutes > max_age_minutes:
                to_remove.append(session_id)

        for session_id in to_remove:
            del self.sessions[session_id]

        return len(to_remove)
