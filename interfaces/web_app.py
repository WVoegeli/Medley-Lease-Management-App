"""
Streamlit web interface for Medley Lease Management System
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.search.query_engine import QueryEngine


# Page config
st.set_page_config(
    page_title="Medley Lease Management",
    page_icon="🏢",
    layout="wide"
)


@st.cache_resource
def get_query_engine():
    """Initialize and cache the query engine"""
    return QueryEngine()


def main():
    # Header
    st.title("🏢 Medley Lease Management System")
    st.markdown("*Query your lease agreements using natural language*")

    # Initialize engine
    try:
        engine = get_query_engine()
        stats = engine.get_stats()
    except Exception as e:
        st.error(f"Error initializing: {e}")
        st.warning("Make sure you've run the ingestion script first: `python scripts/ingest.py`")
        return

    # Sidebar
    with st.sidebar:
        st.header("📊 Database Stats")
        st.metric("Total Chunks", stats["total_chunks"])
        st.metric("Number of Tenants", stats["num_tenants"])

        st.divider()

        st.header("🏪 Tenants")
        tenants = engine.get_tenant_list()

        # Tenant filter
        selected_tenant = st.selectbox(
            "Filter by Tenant",
            options=["All Tenants"] + tenants,
            index=0
        )

        tenant_filter = None if selected_tenant == "All Tenants" else selected_tenant

        st.divider()

        st.header("⚙️ Settings")
        num_results = st.slider("Number of sources", 3, 10, 5)

        st.divider()

        st.header("📝 Example Questions")
        example_questions = [
            "What is Summit Coffee's monthly rent?",
            "Which tenants have percentage rent?",
            "What are the renewal options for Sephora?",
            "Compare security deposits across tenants",
            "What are the prohibited uses for restaurants?",
            "When do the leases expire?",
            "What maintenance is landlord responsible for?",
            "What is the total square footage leased?"
        ]

        for q in example_questions:
            if st.button(q, key=f"example_{q[:20]}"):
                st.session_state.query = q

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Query input
        query = st.text_input(
            "Ask a question about your leases",
            value=st.session_state.get("query", ""),
            placeholder="e.g., What is the monthly rent for Summit Coffee?",
            key="query_input"
        )

        if st.button("🔍 Search", type="primary") or query:
            if query:
                with st.spinner("Searching and generating answer..."):
                    try:
                        response = engine.query(
                            question=query,
                            tenant_filter=tenant_filter,
                            n_results=num_results
                        )

                        # Display answer
                        st.subheader("📝 Answer")
                        st.markdown(response.answer)

                        # Display sources
                        if response.sources:
                            st.subheader("📚 Sources")

                            for i, source in enumerate(response.sources, 1):
                                with st.expander(
                                    f"Source {i}: {source['tenant']} - {source['section'][:40]}",
                                    expanded=(i == 1)
                                ):
                                    st.markdown(f"**Tenant:** {source['tenant']}")
                                    st.markdown(f"**Section:** {source['section']}")
                                    st.markdown(f"**File:** {source['source_file']}")
                                    st.markdown(f"**Relevance Score:** {source['score']:.3f}")
                                    st.divider()
                                    st.text(source['content'])

                    except Exception as e:
                        st.error(f"Error processing query: {e}")
            else:
                st.info("Enter a question to search your lease documents.")

    with col2:
        st.subheader("🔧 Quick Actions")

        # Tenant comparison
        st.markdown("**Compare Tenants**")
        compare_tenants = st.multiselect(
            "Select tenants to compare",
            options=tenants,
            max_selections=4
        )

        compare_question = st.text_input(
            "Comparison question",
            placeholder="e.g., What is the monthly rent?"
        )

        if st.button("📊 Compare") and compare_tenants and compare_question:
            with st.spinner("Comparing tenants..."):
                try:
                    comparisons = engine.compare_tenants(
                        question=compare_question,
                        tenants=compare_tenants
                    )

                    st.subheader("Comparison Results")
                    for tenant, response in comparisons.items():
                        with st.expander(tenant, expanded=True):
                            st.markdown(response.answer)

                except Exception as e:
                    st.error(f"Error comparing: {e}")

        st.divider()

        # Tenant summary
        st.markdown("**Tenant Quick Info**")
        info_tenant = st.selectbox(
            "Select tenant for quick info",
            options=tenants,
            key="info_tenant"
        )

        if st.button("ℹ️ Get Info"):
            with st.spinner("Getting tenant info..."):
                try:
                    # Get basic lease info for selected tenant
                    info_query = (
                        f"What are the key terms of the {info_tenant} lease "
                        "including rent, term length, and square footage?"
                    )
                    response = engine.query(
                        question=info_query,
                        tenant_filter=info_tenant,
                        n_results=3
                    )
                    st.markdown(response.answer)
                except Exception as e:
                    st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
