"""
Streamlit Chat Interface for Medley Lease Management System
Supports multi-turn conversations about lease documents
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.search.query_engine import QueryEngine


# Page config
st.set_page_config(
    page_title="Medley Lease Chat",
    page_icon="💬",
    layout="wide"
)


@st.cache_resource
def get_query_engine():
    """Initialize and cache the query engine"""
    return QueryEngine()


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources" not in st.session_state:
        st.session_state.sources = []


def clear_conversation():
    """Clear the conversation history"""
    st.session_state.messages = []
    st.session_state.sources = []


def main():
    initialize_session_state()

    # Initialize engine
    try:
        engine = get_query_engine()
        stats = engine.get_stats()
    except Exception as e:
        st.error(f"Error initializing: {e}")
        st.warning("Make sure you've run the ingestion script first: `python scripts/ingest.py`")
        return

    # Header
    col_title, col_clear = st.columns([4, 1])
    with col_title:
        st.title("💬 Medley Lease Chat")
        st.caption("Have a conversation about your lease agreements")
    with col_clear:
        st.write("")  # Spacer
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_conversation()
            st.rerun()

    # Layout: Chat area and sidebar
    chat_col, sidebar_col = st.columns([3, 1])

    # Sidebar
    with sidebar_col:
        st.subheader("⚙️ Settings")

        # Tenant filter
        tenants = engine.get_tenant_list()
        selected_tenant = st.selectbox(
            "Filter by Tenant",
            options=["All Tenants"] + tenants,
            index=0,
            help="Filter responses to a specific tenant"
        )
        tenant_filter = None if selected_tenant == "All Tenants" else selected_tenant

        # Number of sources
        num_results = st.slider(
            "Sources per query",
            min_value=5,
            max_value=25,
            value=10,
            help="Number of document chunks to retrieve (use higher values for multi-tenant queries)"
        )

        # Show sources toggle
        show_sources = st.toggle("Show sources", value=True)

        st.divider()

        # Stats
        st.subheader("📊 Database")
        st.metric("Chunks", stats["total_chunks"])
        st.metric("Tenants", stats["num_tenants"])

        st.divider()

        # Example questions
        st.subheader("💡 Try asking")
        example_questions = [
            "What is Summit Coffee's rent?",
            "Tell me about renewal options",
            "What are the prohibited uses?",
            "Compare rent across tenants",
        ]

        for q in example_questions:
            if st.button(q, key=f"ex_{q[:15]}", use_container_width=True):
                # Add to messages and trigger response
                st.session_state.pending_message = q
                st.rerun()

        st.divider()

        # Current sources
        if show_sources and st.session_state.sources:
            st.subheader("📚 Latest Sources")
            for i, source in enumerate(st.session_state.sources[:3], 1):
                with st.expander(f"{source['tenant'][:20]}"):
                    st.caption(f"**Section:** {source['section'][:30]}")
                    st.caption(f"**Score:** {source['score']:.3f}")

    # Main chat area
    with chat_col:
        # Display chat messages
        chat_container = st.container()

        with chat_container:
            # Welcome message if no conversation
            if not st.session_state.messages:
                st.info(
                    "Welcome! Ask me anything about your Medley lease agreements. "
                    "I'll remember our conversation context."
                )

            # Display all messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Handle pending message from example buttons
        if "pending_message" in st.session_state:
            pending = st.session_state.pending_message
            del st.session_state.pending_message

            # Add user message
            st.session_state.messages.append({"role": "user", "content": pending})

            # Generate response
            with st.spinner("Thinking..."):
                response = engine.chat(
                    message=pending,
                    conversation_history=st.session_state.messages[:-1],
                    n_results=num_results,
                    tenant_filter=tenant_filter
                )

            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response.answer})
            st.session_state.sources = response.sources

            st.rerun()

        # Chat input
        if prompt := st.chat_input("Ask about your leases..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Generate response
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Searching documents and generating response..."):
                        # Get conversation history (excluding current message)
                        history = st.session_state.messages[:-1]

                        response = engine.chat(
                            message=prompt,
                            conversation_history=history,
                            n_results=num_results,
                            tenant_filter=tenant_filter
                        )

                    st.markdown(response.answer)

            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response.answer})
            st.session_state.sources = response.sources

            # Show sources inline if enabled
            if show_sources and response.sources:
                with st.expander("📚 Sources used for this response"):
                    for i, source in enumerate(response.sources, 1):
                        st.markdown(f"**{i}. {source['tenant']} - {source['section']}**")
                        st.caption(f"Score: {source['score']:.3f}")
                        st.text(source['content'][:300] + "...")
                        st.divider()


if __name__ == "__main__":
    main()
