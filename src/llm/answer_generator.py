"""
LLM-based answer generation for lease queries
Supports both OpenAI and Anthropic models
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic

from config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    LLM_MODEL, LLM_PROVIDER
)


SYSTEM_PROMPT = """You are a helpful assistant specialized in analyzing commercial lease agreements for the Medley retail development. Your role is to answer questions about lease terms, rent amounts, tenant obligations, and other lease-related information.

When answering questions:
1. Be precise and cite specific information from the provided lease excerpts
2. If the information is not available in the provided context, say so clearly
3. When discussing financial terms, be exact with numbers and dates
4. Distinguish between different tenants when relevant
5. Use clear, professional language suitable for property management

Always base your answers on the provided lease document excerpts. Do not make up information."""

CHAT_SYSTEM_PROMPT = """You are a helpful assistant specialized in analyzing commercial lease agreements for the Medley retail development. You are having a conversation with a user about their lease documents.

When answering questions:
1. Be precise and cite specific information from the provided lease excerpts
2. If the information is not available in the provided context, say so clearly
3. When discussing financial terms, be exact with numbers and dates
4. Distinguish between different tenants when relevant
5. Use clear, professional language suitable for property management
6. Remember the context of the conversation - if the user refers to "they", "their", "it", etc., understand they're referring to previously discussed tenants or topics
7. Build on previous answers when relevant

Always base your answers on the provided lease document excerpts. Do not make up information."""


class AnswerGenerator:
    """Generate answers using LLM based on retrieved context"""

    def __init__(
        self,
        provider: str = LLM_PROVIDER,
        model: str = LLM_MODEL,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialize the answer generator

        Args:
            provider: "openai" or "anthropic"
            model: Model name to use
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
        """
        self.provider = provider.lower()
        self.model = model

        if self.provider == "openai":
            api_key = openai_api_key or OPENAI_API_KEY
            if not api_key:
                raise ValueError("OpenAI API key required for OpenAI provider")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "anthropic":
            api_key = anthropic_api_key or ANTHROPIC_API_KEY
            if not api_key:
                raise ValueError("Anthropic API key required for Anthropic provider")
            self.client = Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate_answer(
        self,
        question: str,
        contexts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate an answer based on question and retrieved contexts

        Args:
            question: User's question
            contexts: List of relevant text chunks
            metadatas: Optional metadata for each context
            max_tokens: Maximum tokens in response

        Returns:
            Generated answer string
        """
        # Build context string
        context_str = self._format_contexts(contexts, metadatas)

        # Build the prompt
        user_prompt = f"""Based on the following excerpts from lease agreements, please answer this question:

Question: {question}

Lease Document Excerpts:
{context_str}

Please provide a clear, accurate answer based only on the information provided above."""

        # Generate response
        if self.provider == "openai":
            return self._generate_openai(user_prompt, max_tokens)
        else:
            return self._generate_anthropic(user_prompt, max_tokens)

    def _format_contexts(
        self,
        contexts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Format contexts for the prompt"""
        formatted_parts = []

        for i, context in enumerate(contexts):
            header = f"--- Excerpt {i + 1}"
            if metadatas and i < len(metadatas):
                meta = metadatas[i]
                tenant = meta.get("tenant_name", "Unknown")
                section = meta.get("section_name", "")
                header += f" (Tenant: {tenant}"
                if section:
                    header += f", Section: {section}"
                header += ")"
            header += " ---"

            formatted_parts.append(f"{header}\n{context}")

        return "\n\n".join(formatted_parts)

    def _generate_openai(self, user_prompt: str, max_tokens: int) -> str:
        """Generate response using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.1  # Low temperature for factual responses
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, user_prompt: str, max_tokens: int) -> str:
        """Generate response using Anthropic Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text

    def generate_chat_response(
        self,
        message: str,
        contexts: List[str],
        conversation_history: List[Dict[str, str]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1000,
        max_history_turns: int = 5
    ) -> str:
        """
        Generate a conversational response with history context

        Args:
            message: Current user message
            contexts: List of relevant text chunks from RAG
            conversation_history: List of {"role": "user/assistant", "content": "..."}
            metadatas: Optional metadata for each context
            max_tokens: Maximum tokens in response
            max_history_turns: Maximum conversation turns to include

        Returns:
            Generated response string
        """
        # Build context string from RAG results
        context_str = self._format_contexts(contexts, metadatas)

        # Build conversation history string (limit to recent turns)
        history_messages = conversation_history[-(max_history_turns * 2):]

        if self.provider == "openai":
            return self._generate_chat_openai(message, context_str, history_messages, max_tokens)
        else:
            return self._generate_chat_anthropic(message, context_str, history_messages, max_tokens)

    def _generate_chat_openai(
        self,
        message: str,
        context_str: str,
        history: List[Dict[str, str]],
        max_tokens: int
    ) -> str:
        """Generate chat response using OpenAI"""
        messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]

        # Add conversation history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message with context
        user_content = f"""Based on the following lease document excerpts, please answer my question.

Lease Document Excerpts:
{context_str}

My question: {message}"""

        messages.append({"role": "user", "content": user_content})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content

    def _generate_chat_anthropic(
        self,
        message: str,
        context_str: str,
        history: List[Dict[str, str]],
        max_tokens: int
    ) -> str:
        """Generate chat response using Anthropic Claude"""
        messages = []

        # Add conversation history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message with context
        user_content = f"""Based on the following lease document excerpts, please answer my question.

Lease Document Excerpts:
{context_str}

My question: {message}"""

        messages.append({"role": "user", "content": user_content})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=CHAT_SYSTEM_PROMPT,
            messages=messages
        )
        return response.content[0].text

    def reformulate_query(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        max_tokens: int = 100
    ) -> str:
        """
        Reformulate a vague follow-up question into a complete, standalone question

        Args:
            message: Current user message (may be vague like "what about per month?")
            conversation_history: Recent conversation history
            max_tokens: Maximum tokens for reformulation

        Returns:
            Reformulated complete question that can be searched independently
        """
        if not conversation_history:
            return message

        # Build recent history (last 2-3 turns)
        recent_history = conversation_history[-(min(6, len(conversation_history))):]
        history_str = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content'][:200]}"
            for msg in recent_history
        ])

        prompt = f"""Given this conversation history, reformulate the user's latest message into a complete, standalone question that includes all necessary context (like tenant names, specific topics, etc.).

Conversation History:
{history_str}

Latest User Message: {message}

Reformulated Complete Question:"""

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You reformulate vague follow-up questions into complete, searchable questions by adding context from conversation history. Output only the reformulated question, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            reformulated = response.choices[0].message.content.strip()
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system="You reformulate vague follow-up questions into complete, searchable questions by adding context from conversation history. Output only the reformulated question, nothing else.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            reformulated = response.content[0].text.strip()

        return reformulated

    def generate_comparison(
        self,
        question: str,
        tenant_contexts: Dict[str, List[str]],
        max_tokens: int = 1500
    ) -> str:
        """
        Generate a comparison answer across multiple tenants

        Args:
            question: Question to answer
            tenant_contexts: Dictionary mapping tenant names to their contexts
            max_tokens: Maximum tokens in response

        Returns:
            Comparison answer
        """
        # Format contexts by tenant
        context_parts = []
        for tenant, contexts in tenant_contexts.items():
            tenant_section = f"=== {tenant} ===\n"
            tenant_section += "\n---\n".join(contexts[:3])  # Limit per tenant
            context_parts.append(tenant_section)

        context_str = "\n\n".join(context_parts)

        user_prompt = f"""Based on the following lease excerpts organized by tenant, please compare and answer this question:

Question: {question}

Lease Information by Tenant:
{context_str}

Please provide a clear comparison showing how each tenant's lease addresses this topic."""

        if self.provider == "openai":
            return self._generate_openai(user_prompt, max_tokens)
        else:
            return self._generate_anthropic(user_prompt, max_tokens)
