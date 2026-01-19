"""
Medley Lease Analysis & Management System - Combined Chat & Dashboard Interface
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

# Import chat components
from src.search.query_engine import QueryEngine

# Import dashboard components
from src.data.lease_data import (
    LEASE_DATA,
    get_all_leases,
    get_categories,
    get_tenants_with_cotenancy,
    calc_rent_for_year,
    get_summary_stats,
)

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    relativedelta = None


# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Medley Lease Analysis & Management",
    page_icon="🏢",
    layout="wide"
)


# ============== AUTHENTICATION ==============

def check_password():
    """Returns True if the user has entered the correct password."""
    correct_password = os.environ.get("APP_PASSWORD")
    if not correct_password:
        try:
            correct_password = st.secrets.get("APP_PASSWORD", "Medley2026")
        except Exception:
            correct_password = "Medley2026"

    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # Show login form
    st.title("🔐 Medley Lease Analysis & Management")
    st.markdown("Please enter the password to access the application.")

    password = st.text_input("Password", type="password", key="password_input")

    if st.button("Login", type="primary"):
        if password == correct_password:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    return False


# ============== FORMATTING HELPERS ==============

def fmt_currency(val, decimals=0):
    if val is None:
        return "—"
    return f"${val:,.{decimals}f}"

def fmt_number(val):
    if val is None:
        return "—"
    return f"{val:,}"

def fmt_percent(val):
    if val is None:
        return "—"
    return f"{val * 100:.1f}%"


# ============== CHAT FUNCTIONS ==============

@st.cache_resource
def get_query_engine():
    """Initialize and cache the query engine"""
    return QueryEngine()


def initialize_chat_state():
    """Initialize chat session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources" not in st.session_state:
        st.session_state.sources = []


def clear_conversation():
    """Clear the conversation history"""
    st.session_state.messages = []
    st.session_state.sources = []


def render_chat():
    """Render the Chat interface."""
    initialize_chat_state()

    # Initialize engine
    try:
        engine = get_query_engine()
        stats = engine.get_stats()
    except Exception as e:
        st.error(f"Error initializing RAG engine: {e}")
        st.warning("Make sure you've run the ingestion script first: `python scripts/ingest.py`")
        return

    # Header
    col_title, col_clear = st.columns([4, 1])
    with col_title:
        st.subheader("💬 AI-Powered Lease Q&A")
        st.caption("Ask questions about your lease agreements using natural language")
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_conversation()
            st.rerun()

    # Layout: Chat area and sidebar
    chat_col, sidebar_col = st.columns([3, 1])

    # Sidebar
    with sidebar_col:
        st.markdown("#### Settings")

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
            help="Number of document chunks to retrieve"
        )

        # Show sources toggle
        show_sources = st.toggle("Show sources", value=True)

        st.divider()

        # Stats
        st.markdown("#### Database Stats")
        st.metric("Chunks", stats["total_chunks"])
        st.metric("Tenants", stats["num_tenants"])

        st.divider()

        # Example questions
        st.markdown("#### Try asking")
        example_questions = [
            "What is Summit Coffee's rent?",
            "Tell me about renewal options",
            "What are the prohibited uses?",
            "Compare rent across tenants",
        ]

        for q in example_questions:
            if st.button(q, key=f"ex_{q[:15]}", use_container_width=True):
                st.session_state.pending_message = q
                st.rerun()

        # Current sources
        if show_sources and st.session_state.sources:
            st.divider()
            st.markdown("#### Latest Sources")
            for i, source in enumerate(st.session_state.sources[:3], 1):
                with st.expander(f"{source['tenant'][:20]}"):
                    st.caption(f"**Section:** {source['section'][:30]}")
                    st.caption(f"**Score:** {source['score']:.3f}")

    # Main chat area
    with chat_col:
        chat_container = st.container()

        with chat_container:
            if not st.session_state.messages:
                st.info(
                    "Welcome! Ask me anything about your Medley lease agreements. "
                    "I'll search the actual lease documents to find answers."
                )

            for message in st.session_state.messages:
                # Use proper avatars: user icon for user, AI icon for assistant
                avatar = "👤" if message["role"] == "user" else "🤖"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        # Handle pending message from example buttons
        if "pending_message" in st.session_state:
            pending = st.session_state.pending_message
            del st.session_state.pending_message

            st.session_state.messages.append({"role": "user", "content": pending})

            with st.spinner("Searching documents..."):
                response = engine.chat(
                    message=pending,
                    conversation_history=st.session_state.messages[:-1],
                    n_results=num_results,
                    tenant_filter=tenant_filter
                )

            st.session_state.messages.append({"role": "assistant", "content": response.answer})
            st.session_state.sources = response.sources
            st.rerun()

        # Chat input
        if prompt := st.chat_input("Ask about your leases..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)

            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Searching documents and generating response..."):
                        history = st.session_state.messages[:-1]
                        response = engine.chat(
                            message=prompt,
                            conversation_history=history,
                            n_results=num_results,
                            tenant_filter=tenant_filter
                        )
                    st.markdown(response.answer)

            st.session_state.messages.append({"role": "assistant", "content": response.answer})
            st.session_state.sources = response.sources

            if show_sources and response.sources:
                with st.expander("📚 Sources used for this response"):
                    for i, source in enumerate(response.sources, 1):
                        st.markdown(f"**{i}. {source['tenant']} - {source['section']}**")
                        st.caption(f"Score: {source['score']:.3f}")
                        st.text(source['content'][:300] + "...")
                        st.divider()


# ============== DASHBOARD FUNCTIONS ==============

def render_lease_database():
    """Render the Lease Database view."""
    col1, col2 = st.columns([1, 3])

    with col1:
        search = st.text_input("Search tenants", placeholder="Enter tenant name...")
        categories = ["All"] + get_categories()
        category_filter = st.selectbox("Filter by Category", categories)

        filtered = get_all_leases()
        if search:
            filtered = [l for l in filtered if search.lower() in l.tenant.lower()]
        if category_filter != "All":
            filtered = [l for l in filtered if l.category == category_filter]

        filtered = sorted(filtered, key=lambda x: x.suite)

        st.markdown("---")

        for lease in filtered:
            badge = " ⚠️" if lease.co_tenancy else ""
            label = f"{lease.tenant}{badge} | Suite {lease.suite}"
            if st.button(label, key=f"lease_{lease.id}", use_container_width=True):
                st.session_state.selected_lease_id = lease.id
                st.rerun()

    with col2:
        selected_id = st.session_state.get("selected_lease_id", None)
        if selected_id:
            lease = next((l for l in LEASE_DATA if l.id == selected_id), None)
            if lease:
                render_lease_detail(lease)
        else:
            st.info("Select a tenant from the list to view details")


def render_lease_detail(lease):
    """Render detailed lease information."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {lease.tenant}")
        st.caption(lease.legal_entity)
        st.markdown(f"**Suite {lease.suite}** • {fmt_number(lease.sqft)} SF • {lease.term}")
    with col2:
        st.metric("Year 1 Rent/SF", fmt_currency(lease.rent.year1_psf, 2))

    tab1, tab2, tab3, tab4 = st.tabs(["Rent Schedule", "TI Allowance", "Recoveries", "Co-Tenancy"])

    with tab1:
        st.markdown(f"**Escalation:** {lease.rent.escalation}")
        df = pd.DataFrame([
            {"Period": e.period, "Rent/SF": fmt_currency(e.psf, 2), "Monthly": fmt_currency(e.monthly), "Notes": e.notes or ""}
            for e in lease.rent_schedule
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if lease.options:
            st.info(f"**Renewal Options:** {lease.options}")

    with tab2:
        if lease.ti.total:
            c1, c2, c3 = st.columns(3)
            c1.metric("Per SF", fmt_currency(lease.ti.psf, 2))
            c2.metric("Total Allowance", fmt_currency(lease.ti.total))
            c3.metric("Premises", f"{fmt_number(lease.sqft)} SF")
            if lease.ti.notes:
                st.caption(lease.ti.notes)
        else:
            st.info("No TI Allowance")

    with tab3:
        st.markdown(f"**Type:** {lease.cam.type}")
        c1, c2, c3 = st.columns(3)
        c1.metric("CAM (Year 1)", fmt_currency(lease.cam.year1, 2) + "/SF" if lease.cam.year1 else "Included")
        c2.metric("Taxes (Est.)", fmt_currency(lease.tax, 2) + "/SF" if lease.tax else "Included")
        c3.metric("Insurance (Est.)", fmt_currency(lease.insurance, 2) + "/SF" if lease.insurance else "Included")

    with tab4:
        if lease.co_tenancy:
            ct = lease.co_tenancy
            risk_color = "🔴" if ct.risk_level == "high" else "🟡" if ct.risk_level == "medium" else "🟢"
            st.markdown(f"### {risk_color} {ct.type} Co-Tenancy ({ct.risk_level.upper()} RISK)")
            st.markdown(f"**Threshold:** {ct.threshold}")
            if ct.named_tenant:
                st.markdown(f"**Named Co-Tenant:** {ct.named_tenant}")
            st.markdown(f"**Remedy:** {ct.remedy}")
            st.metric("Annual Rent at Risk", fmt_currency(ct.rent_at_risk))
        else:
            st.info("No Co-Tenancy Clause")


def render_cotenancy_risk():
    """Render the Co-Tenancy Risk view."""
    tenants = get_tenants_with_cotenancy()
    high_risk = [l for l in tenants if l.co_tenancy.risk_level == "high"]
    medium_risk = [l for l in tenants if l.co_tenancy.risk_level == "medium"]
    total_at_risk = sum(l.co_tenancy.rent_at_risk for l in tenants)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tenants with Co-Tenancy", len(tenants))
    c2.metric("High Risk", len(high_risk))
    c3.metric("Medium Risk", len(medium_risk))
    c4.metric("Total Annual Rent at Risk", fmt_currency(total_at_risk))

    st.markdown("---")
    st.markdown("### Risk Scenarios")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.error(f"**Worst Case: TJ's Delays 6+ Months**\n\n{fmt_currency(sum(l.co_tenancy.rent_at_risk for l in high_risk))} at risk")
    with c2:
        st.warning(f"**Moderate: 60% Occupancy at Opening**\n\n{fmt_currency(sum(l.co_tenancy.rent_at_risk for l in medium_risk))} at risk")
    with c3:
        st.success("**Best Case: On-Time Opening**\n\n$0 at risk")

    st.markdown("---")

    df = pd.DataFrame([
        {"Tenant": l.tenant, "Type": l.co_tenancy.type, "Named Tenant": l.co_tenancy.named_tenant or "—",
         "Rent at Risk": l.co_tenancy.rent_at_risk, "Risk": l.co_tenancy.risk_level.upper()}
        for l in tenants
    ])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Rent at Risk": st.column_config.NumberColumn(format="$%d")})


def render_projection():
    """Render the 10-Year Projection view."""
    projections = []
    for year in range(1, 11):
        total_rent = sum(calc_rent_for_year(l, year) for l in LEASE_DATA if year <= l.term_months / 12)
        active = sum(1 for l in LEASE_DATA if year <= l.term_months / 12)
        projections.append({"year": year, "calendar": 2026 + year, "rent": total_rent, "active": active})

    c1, c2, c3 = st.columns(3)
    c1.metric("Year 1 Total Rent", fmt_currency(projections[0]["rent"]))
    c2.metric("Year 10 Total Rent", fmt_currency(projections[9]["rent"]))
    growth = (projections[9]["rent"] - projections[0]["rent"]) / projections[0]["rent"]
    c3.metric("10-Year Growth", fmt_percent(growth))

    st.markdown("---")

    chart_df = pd.DataFrame({"Year": [p["calendar"] for p in projections], "Rent ($M)": [p["rent"]/1e6 for p in projections]})
    st.bar_chart(chart_df, x="Year", y="Rent ($M)", color="#10b981")

    df = pd.DataFrame([
        {"Lease Year": f"Year {p['year']}", "Calendar": p["calendar"], "Projected Rent": p["rent"], "Active Leases": p["active"]}
        for p in projections
    ])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Projected Rent": st.column_config.NumberColumn(format="$%d")})


def render_tenant_mix():
    """Render the Tenant Mix view."""
    stats = get_summary_stats()

    mix = {}
    for lease in LEASE_DATA:
        cat = lease.category
        if cat not in mix:
            mix[cat] = {"sqft": 0, "rent": 0, "count": 0}
        mix[cat]["sqft"] += lease.sqft
        mix[cat]["rent"] += lease.rent.year1_annual
        mix[cat]["count"] += 1

    mix_data = sorted([
        {"category": cat, **data, "pct_sf": data["sqft"]/stats["total_sf"], "pct_rent": data["rent"]/stats["total_rent"]}
        for cat, data in mix.items()
    ], key=lambda x: x["sqft"], reverse=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Square Footage by Category")
        sf_df = pd.DataFrame({"Category": [m["category"] for m in mix_data], "SF": [m["sqft"] for m in mix_data]})
        st.bar_chart(sf_df, x="Category", y="SF", color="#3b82f6", horizontal=True)
    with c2:
        st.markdown("### Annual Rent by Category")
        rent_df = pd.DataFrame({"Category": [m["category"] for m in mix_data], "Rent": [m["rent"] for m in mix_data]})
        st.bar_chart(rent_df, x="Category", y="Rent", color="#10b981", horizontal=True)

    st.markdown("---")

    df = pd.DataFrame([
        {"Category": m["category"], "Tenants": m["count"], "Total SF": m["sqft"],
         "Annual Rent": m["rent"], "Avg Rent/SF": m["rent"]/m["sqft"]}
        for m in mix_data
    ])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Total SF": st.column_config.NumberColumn(format="%d"),
                               "Annual Rent": st.column_config.NumberColumn(format="$%d"),
                               "Avg Rent/SF": st.column_config.NumberColumn(format="$%.2f")})


def render_critical_dates():
    """Render the Critical Dates view."""
    cotenancy_tenants = get_tenants_with_cotenancy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grand Opening", "Nov 2026")
    c2.metric("First Expirations", "2033")
    c3.metric("10-Year Expirations", len([l for l in LEASE_DATA if l.term_months <= 120]))
    c4.metric("Opening Co-Tenancy Triggers", len([l for l in cotenancy_tenants if "Opening" in l.co_tenancy.type]))

    st.markdown("---")

    events = [{"Date": "2026-11-01", "Type": "Milestone", "Tenant": "ALL", "Description": "Grand Opening"}]

    for lease in LEASE_DATA:
        events.append({"Date": lease.expire_date, "Type": "Expiration", "Tenant": lease.tenant,
                      "Description": f"Lease Expires ({fmt_number(lease.sqft)} SF)"})

    for lease in cotenancy_tenants:
        if "Opening" in lease.co_tenancy.type:
            events.append({"Date": "2026-11-01", "Type": "Co-Tenancy", "Tenant": lease.tenant,
                          "Description": f"Opening Co-Tenancy Active"})

    events = sorted(events, key=lambda x: x["Date"])

    df = pd.DataFrame(events)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Date": st.column_config.DateColumn(format="MMM D, YYYY")})


# ============== MAIN APPLICATION ==============

def main():
    if not check_password():
        return

    # Toro Development Company Branding & Mobile Optimization
    st.markdown("""
    <style>
    /* Import professional serif font for headings */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Inter:wght@300;400;600&display=swap');

    /* Toro Dark Theme */
    :root {
        --background-color: #0a0a0a;
        --secondary-background-color: #1a1a1a;
        --text-color: #FAFAFA;
        --primary-color: #DC2626;
    }

    .stApp {
        background-color: #0a0a0a;
        color: #FAFAFA;
    }

    /* Typography - Toro Style */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Merriweather', Georgia, serif !important;
        font-weight: 400;
        color: #FAFAFA;
    }

    p, div, span, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Chat Message Styling - Fix avatar display and layout */
    .stChatMessage {
        background-color: #1a1a1a !important;
        border-left: 3px solid #DC2626;
        margin: 0.5rem 0 !important;
        padding: 0.75rem 1rem !important;
        border-radius: 0.5rem;
    }

    /* Fix chat message avatar */
    .stChatMessage [data-testid="chatAvatarIcon-user"],
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
        width: 2.5rem !important;
        height: 2.5rem !important;
        font-size: 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Simpler approach: Limit the entire main content area */
    .main .block-container {
        max-height: calc(100vh - 100px);
        overflow-y: auto;
    }

    /* Style the scrollbar */
    .main .block-container::-webkit-scrollbar {
        width: 10px;
    }

    .main .block-container::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    .main .block-container::-webkit-scrollbar-thumb {
        background: #DC2626;
        border-radius: 5px;
    }

    .main .block-container::-webkit-scrollbar-thumb:hover {
        background: #EF4444;
    }

    /* Fix expander arrow display - hide broken icon text */
    [data-testid="stExpander"] details summary::before {
        content: "" !important;
    }

    /* Fix expander icon */
    [data-testid="stExpander"] details summary svg {
        display: block !important;
    }

    /* CRITICAL: Hide ALL Streamlit arrow class text artifacts */
    [class*="arrow"]::before,
    [class*="arrow"]::after {
        content: "" !important;
        display: none !important;
    }

    /* Hide arrow text content */
    [class*="arrow"]:not(svg):not(path) {
        font-size: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
        overflow: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* Restore icon size for actual SVG icons */
    [class*="arrow"] svg,
    [class*="arrow"] svg path {
        font-size: 1rem !important;
        width: auto !important;
        height: auto !important;
        display: inline-block !important;
    }

    /* Explicitly hide every arrow text variant */
    .arrow_sources,
    .arrow_right,
    .arrow_left,
    .arrow_up,
    .arrow_down,
    .arrowlast_night,
    .arrowlight,
    .arrowforward,
    .arrowback,
    .arrow {
        font-size: 0 !important;
        color: transparent !important;
        display: none !important;
    }

    /* Fix expander - hide any text inside arrow elements */
    [data-testid="stExpander"] [class*="arrow"] {
        font-size: 0 !important;
    }

    /* Restore expander text visibility */
    [data-testid="stExpander"] summary {
        font-size: 1rem !important;
    }

    [data-testid="stExpander"] summary > div:not([class*="arrow"]) {
        font-size: 1rem !important;
        display: inline-block !important;
    }

    /* Nuclear option: hide all span elements that contain arrow classes */
    span[class*="arrow"]:not(:has(svg)) {
        display: none !important;
    }

    /* Chat input stays at bottom */
    [data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;
        background-color: #0a0a0a;
        padding: 1rem 0;
        z-index: 100;
        border-top: 1px solid #333;
    }

    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #FAFAFA;
        border: 1px solid #333;
    }

    .stTextInput > div > div > input:focus {
        border-color: #DC2626;
        box-shadow: 0 0 0 1px #DC2626;
    }

    .stSelectbox > div > div > div {
        background-color: #1a1a1a;
        color: #FAFAFA;
        border: 1px solid #333;
    }

    .stMetric {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #333;
    }

    .stDataFrame {
        background-color: #1a1a1a;
    }

    [data-testid="stMarkdownContainer"] {
        color: #FAFAFA;
    }

    .stButton > button {
        background-color: #1a1a1a;
        color: #FAFAFA;
        border: 1px solid #DC2626;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }

    .stButton > button:hover {
        background-color: #DC2626;
        color: #FFFFFF;
        border: 1px solid #DC2626;
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: #FAFAFA;
        border-bottom: 2px solid transparent;
        font-family: 'Inter', sans-serif;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #DC2626;
        border-bottom: 2px solid #DC2626;
        font-weight: 600;
    }

    div[data-testid="stExpander"] {
        background-color: #1a1a1a;
        border: 1px solid #DC2626;
    }

    /* Mobile Optimization */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem !important;
        }

        h1 {
            font-size: 1.5rem !important;
        }

        h2 {
            font-size: 1.25rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        .stButton > button {
            width: 100%;
            margin: 0.25rem 0;
        }

        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
            gap: 0.25rem;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.5rem;
        }

        .stMetric {
            padding: 0.5rem;
        }

        .stChatMessage {
            padding: 0.5rem;
        }

        [data-testid="stSidebar"] {
            width: 100% !important;
        }
    }

    /* Tablet Optimization */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stApp {
            padding: 1rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
    }

    /* Touch-friendly targets for mobile devices */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            min-height: 44px;
            padding: 0.75rem 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            min-height: 44px;
            padding: 0.75rem;
        }

        input, select, textarea {
            min-height: 44px;
        }
    }

    /* Responsive tables */
    @media (max-width: 768px) {
        .stDataFrame {
            overflow-x: auto;
            font-size: 0.85rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    stats = get_summary_stats()
    st.title("🏢 Medley Shopping Center")
    st.caption(f"Grand Opening: November 2026 • {stats['tenant_count']} Tenants • {fmt_number(stats['total_sf'])} SF • {fmt_currency(stats['total_rent'])} Annual Rent")

    # Main navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 AI Chat",
        "📋 Lease Database",
        "⚠️ Co-Tenancy Risk",
        "📈 10-Year Projection",
        "🥧 Tenant Mix",
        "📅 Critical Dates"
    ])

    with tab1:
        render_chat()

    with tab2:
        render_lease_database()

    with tab3:
        render_cotenancy_risk()

    with tab4:
        render_projection()

    with tab5:
        render_tenant_mix()

    with tab6:
        render_critical_dates()


if __name__ == "__main__":
    main()
