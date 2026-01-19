"""
Medley Shopping Center - Lease Dashboard
Comprehensive analytics and lease management interface
"""

import sys
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from src.data.lease_data import (
    LEASE_DATA,
    get_all_leases,
    get_categories,
    get_tenants_with_cotenancy,
    calc_rent_for_year,
    get_summary_stats,
)


# Formatting helpers
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


# Category colors for charts
CATEGORY_COLORS = {
    'Restaurant': '#10b981',
    'Food & Beverage': '#34d399',
    'Anchor': '#3b82f6',
    'Retail': '#8b5cf6',
    'Beauty/Spa': '#ec4899',
    'Medical/Spa': '#f472b6',
    'Fitness': '#f59e0b',
    'Wellness': '#fbbf24',
    'Pet Services': '#6366f1',
}


def render_lease_database():
    """Render the Lease Database view."""
    st.subheader("Lease Database")

    col1, col2 = st.columns([1, 3])

    with col1:
        # Search and filter
        search = st.text_input("Search tenants", placeholder="Enter tenant name...")
        categories = ["All"] + get_categories()
        category_filter = st.selectbox("Filter by Category", categories)

        # Filter leases
        filtered = get_all_leases()
        if search:
            filtered = [l for l in filtered if search.lower() in l.tenant.lower()]
        if category_filter != "All":
            filtered = [l for l in filtered if l.category == category_filter]

        # Sort by suite
        filtered = sorted(filtered, key=lambda x: x.suite)

        # Tenant list
        st.markdown("---")
        selected_id = st.session_state.get("selected_lease_id", None)

        for lease in filtered:
            badge = " ⚠️" if lease.co_tenancy else ""
            if st.button(
                f"**{lease.tenant}**{badge}\n\nSuite {lease.suite} • {fmt_number(lease.sqft)} SF",
                key=f"lease_{lease.id}",
                use_container_width=True,
            ):
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
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {lease.tenant}")
        st.caption(lease.legal_entity)
        st.markdown(f"**Suite {lease.suite}** • {fmt_number(lease.sqft)} SF • {lease.term}")
    with col2:
        st.metric("Year 1 Rent/SF", fmt_currency(lease.rent.year1_psf, 2))

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Rent Schedule", "TI Allowance", "Recoveries", "Co-Tenancy"])

    with tab1:
        st.markdown(f"**Escalation:** {lease.rent.escalation}")

        df = pd.DataFrame([
            {
                "Period": entry.period,
                "Rent/SF": fmt_currency(entry.psf, 2),
                "Monthly": fmt_currency(entry.monthly),
                "Notes": entry.notes or ""
            }
            for entry in lease.rent_schedule
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        if lease.options:
            st.info(f"**Renewal Options:** {lease.options}")

    with tab2:
        if lease.ti.total:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Per SF", fmt_currency(lease.ti.psf, 2))
            with col2:
                st.metric("Total Allowance", fmt_currency(lease.ti.total))
            with col3:
                st.metric("Premises", f"{fmt_number(lease.sqft)} SF")
            if lease.ti.notes:
                st.caption(lease.ti.notes)
        else:
            st.info("No TI Allowance")
            if lease.ti.notes:
                st.caption(lease.ti.notes)

    with tab3:
        st.markdown(f"**Type:** {lease.cam.type}")

        col1, col2, col3 = st.columns(3)
        with col1:
            cam_val = fmt_currency(lease.cam.year1, 2) + "/SF" if lease.cam.year1 else "Included"
            st.metric("CAM (Year 1)", cam_val)
            if lease.cam.increases:
                st.caption(lease.cam.increases)
        with col2:
            tax_val = fmt_currency(lease.tax, 2) + "/SF" if lease.tax else "Included"
            st.metric("Taxes (Est.)", tax_val)
        with col3:
            ins_val = fmt_currency(lease.insurance, 2) + "/SF" if lease.insurance else "Included"
            st.metric("Insurance (Est.)", ins_val)

        if lease.recovery_note:
            st.caption(lease.recovery_note)

    with tab4:
        if lease.co_tenancy:
            ct = lease.co_tenancy

            # Risk level indicator
            risk_colors = {"high": "red", "medium": "orange", "low": "green"}
            st.markdown(f"### {ct.type} Co-Tenancy • :{'red' if ct.risk_level == 'high' else 'orange' if ct.risk_level == 'medium' else 'green'}[{ct.risk_level.upper()} RISK]")

            st.markdown(f"**Threshold:** {ct.threshold}")

            if ct.named_tenant:
                st.markdown(f"**Named Co-Tenant:** {ct.named_tenant}")

            st.markdown(f"**Remedy:** {ct.remedy}")

            if ct.termination:
                st.markdown(f"**Termination:** {ct.termination}")

            st.metric("Annual Rent at Risk", fmt_currency(ct.rent_at_risk), delta=None)
        else:
            st.info("No Co-Tenancy Clause")


def render_cotenancy_risk():
    """Render the Co-Tenancy Risk view."""
    st.subheader("Co-Tenancy Risk Analysis")

    tenants = get_tenants_with_cotenancy()

    # Risk breakdown
    high_risk = [l for l in tenants if l.co_tenancy.risk_level == "high"]
    medium_risk = [l for l in tenants if l.co_tenancy.risk_level == "medium"]
    low_risk = [l for l in tenants if l.co_tenancy.risk_level == "low"]
    total_at_risk = sum(l.co_tenancy.rent_at_risk for l in tenants)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tenants with Co-Tenancy", len(tenants))
    with col2:
        st.metric("High Risk", len(high_risk))
    with col3:
        st.metric("Medium Risk", len(medium_risk))
    with col4:
        st.metric("Total Annual Rent at Risk", fmt_currency(total_at_risk))

    st.markdown("---")

    # Scenario Analysis
    st.markdown("### Risk Scenarios")
    col1, col2, col3 = st.columns(3)

    with col1:
        high_risk_total = sum(l.co_tenancy.rent_at_risk for l in high_risk)
        st.error(f"""
        **Worst Case: TJ's Delays 6+ Months**

        **{fmt_currency(high_risk_total)}** annual rent at risk

        Affected: Sephora, High Country, CRU, Fado
        """)

    with col2:
        medium_risk_total = sum(l.co_tenancy.rent_at_risk for l in medium_risk)
        st.warning(f"""
        **Moderate: 60% Occupancy at Opening**

        **{fmt_currency(medium_risk_total)}** annual rent at risk

        Affected: Pause Studio, Fado, CRU
        """)

    with col3:
        st.success(f"""
        **Best Case: On-Time Opening, 75%+ Leased**

        **$0** rent at risk

        All tenants pay full rent from Day 1
        """)

    st.markdown("---")

    # Detailed table
    st.markdown("### Co-Tenancy Clause Details")

    df = pd.DataFrame([
        {
            "Tenant": l.tenant,
            "Type": l.co_tenancy.type,
            "Threshold": l.co_tenancy.threshold[:50] + "..." if len(l.co_tenancy.threshold) > 50 else l.co_tenancy.threshold,
            "Named Tenant": l.co_tenancy.named_tenant or "—",
            "Rent at Risk": l.co_tenancy.rent_at_risk,
            "Risk Level": l.co_tenancy.risk_level.upper(),
        }
        for l in tenants
    ])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rent at Risk": st.column_config.NumberColumn(format="$%d"),
        }
    )


def render_projection():
    """Render the 10-Year Projection view."""
    st.subheader("10-Year Rent Projection")

    # Calculate projections
    projections = []
    for year in range(1, 11):
        total_rent = 0
        active_leases = 0
        for lease in LEASE_DATA:
            term_years = lease.term_months / 12
            if year <= term_years:
                total_rent += calc_rent_for_year(lease, year)
                active_leases += 1
        projections.append({
            "year": year,
            "calendar_year": 2026 + year,
            "total_rent": total_rent,
            "active_leases": active_leases,
        })

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Year 1 Total Rent", fmt_currency(projections[0]["total_rent"]))
    with col2:
        st.metric("Year 10 Total Rent", fmt_currency(projections[9]["total_rent"]))
    with col3:
        growth = (projections[9]["total_rent"] - projections[0]["total_rent"]) / projections[0]["total_rent"]
        st.metric("10-Year Growth", fmt_percent(growth))

    st.markdown("---")

    # Chart
    st.markdown("### Annual Rent Projection (2027-2036)")

    chart_data = pd.DataFrame({
        "Year": [p["calendar_year"] for p in projections],
        "Annual Rent ($M)": [p["total_rent"] / 1_000_000 for p in projections],
    })
    st.bar_chart(chart_data, x="Year", y="Annual Rent ($M)", color="#10b981")

    st.markdown("---")

    # Table
    df = pd.DataFrame([
        {
            "Lease Year": f"Year {p['year']}",
            "Calendar Year": p["calendar_year"],
            "Projected Annual Rent": p["total_rent"],
            "Active Leases": p["active_leases"],
            "YoY Growth": fmt_percent((p["total_rent"] - projections[i-1]["total_rent"]) / projections[i-1]["total_rent"]) if i > 0 else "—",
        }
        for i, p in enumerate(projections)
    ])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Projected Annual Rent": st.column_config.NumberColumn(format="$%d"),
        }
    )


def render_tenant_mix():
    """Render the Tenant Mix view."""
    st.subheader("Tenant Mix Analysis")

    stats = get_summary_stats()

    # Calculate mix by category
    mix = {}
    for lease in LEASE_DATA:
        cat = lease.category
        if cat not in mix:
            mix[cat] = {"sqft": 0, "rent": 0, "count": 0}
        mix[cat]["sqft"] += lease.sqft
        mix[cat]["rent"] += lease.rent.year1_annual
        mix[cat]["count"] += 1

    mix_data = []
    for cat, data in mix.items():
        mix_data.append({
            "category": cat,
            "sqft": data["sqft"],
            "rent": data["rent"],
            "count": data["count"],
            "pct_sf": data["sqft"] / stats["total_sf"],
            "pct_rent": data["rent"] / stats["total_rent"],
            "avg_psf": data["rent"] / data["sqft"],
        })

    mix_data = sorted(mix_data, key=lambda x: x["sqft"], reverse=True)

    # Charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Square Footage by Category")
        sf_df = pd.DataFrame({
            "Category": [m["category"] for m in mix_data],
            "Square Feet": [m["sqft"] for m in mix_data],
        })
        st.bar_chart(sf_df, x="Category", y="Square Feet", color="#3b82f6", horizontal=True)

    with col2:
        st.markdown("### Annual Rent by Category")
        rent_df = pd.DataFrame({
            "Category": [m["category"] for m in mix_data],
            "Annual Rent": [m["rent"] for m in mix_data],
        })
        st.bar_chart(rent_df, x="Category", y="Annual Rent", color="#10b981", horizontal=True)

    st.markdown("---")

    # Summary table
    st.markdown("### Category Summary")

    df = pd.DataFrame([
        {
            "Category": m["category"],
            "Tenants": m["count"],
            "Total SF": m["sqft"],
            "% of SF": fmt_percent(m["pct_sf"]),
            "Annual Rent": m["rent"],
            "% of Rent": fmt_percent(m["pct_rent"]),
            "Avg Rent/SF": m["avg_psf"],
        }
        for m in mix_data
    ])

    # Add totals row
    totals = pd.DataFrame([{
        "Category": "TOTAL",
        "Tenants": stats["tenant_count"],
        "Total SF": stats["total_sf"],
        "% of SF": "100%",
        "Annual Rent": stats["total_rent"],
        "% of Rent": "100%",
        "Avg Rent/SF": stats["avg_psf"],
    }])

    df = pd.concat([df, totals], ignore_index=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total SF": st.column_config.NumberColumn(format="%d"),
            "Annual Rent": st.column_config.NumberColumn(format="$%d"),
            "Avg Rent/SF": st.column_config.NumberColumn(format="$%.2f"),
        }
    )


def render_critical_dates():
    """Render the Critical Dates view."""
    st.subheader("Critical Dates Calendar")

    cotenancy_tenants = get_tenants_with_cotenancy()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Grand Opening", "Nov 2026")
    with col2:
        st.metric("First Expirations", "2033")
        st.caption("Basil Houze (7-yr)")
    with col3:
        ten_year_exp = len([l for l in LEASE_DATA if l.term_months <= 120])
        st.metric("10-Year Lease Expirations", ten_year_exp)
    with col4:
        opening_ct = len([l for l in cotenancy_tenants if "Opening" in l.co_tenancy.type])
        st.metric("Co-Tenancy Triggers at Open", opening_ct)

    st.markdown("---")

    # Build events list
    events = []

    # Grand opening
    events.append({
        "date": "2026-11-01",
        "type": "Milestone",
        "tenant": "ALL",
        "description": "Grand Opening",
        "priority": "Critical",
    })

    # Lease expirations
    for lease in LEASE_DATA:
        events.append({
            "date": lease.expire_date,
            "type": "Expiration",
            "tenant": lease.tenant,
            "description": f"Lease Expires ({fmt_number(lease.sqft)} SF)",
            "priority": "High" if lease.sqft > 3000 else "Normal",
        })

        # Option windows
        if lease.options:
            exp_date = datetime.strptime(lease.expire_date, "%Y-%m-%d")
            option_date = exp_date - relativedelta(months=9)
            events.append({
                "date": option_date.strftime("%Y-%m-%d"),
                "type": "Option",
                "tenant": lease.tenant,
                "description": f"Option Exercise Window Opens ({lease.options})",
                "priority": "Medium",
            })

    # Co-tenancy triggers
    for lease in cotenancy_tenants:
        if "Opening" in lease.co_tenancy.type:
            events.append({
                "date": "2026-11-01",
                "type": "Co-Tenancy",
                "tenant": lease.tenant,
                "description": f"Opening Co-Tenancy Active: {lease.co_tenancy.threshold[:50]}...",
                "priority": "High",
            })

    # Sort by date
    events = sorted(events, key=lambda x: x["date"])

    st.markdown("### Event Timeline")

    # Filter options
    event_types = ["All"] + list(set(e["type"] for e in events))
    selected_type = st.selectbox("Filter by Event Type", event_types)

    if selected_type != "All":
        events = [e for e in events if e["type"] == selected_type]

    df = pd.DataFrame(events[:100])  # Limit to first 100

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="MMM D, YYYY"),
        }
    )


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Medley Lease Dashboard",
        page_icon="🏢",
        layout="wide",
    )

    # Header
    stats = get_summary_stats()
    st.title("🏢 Medley Shopping Center")
    st.caption(f"Grand Opening: November 2026 • {stats['tenant_count']} Tenants • {fmt_number(stats['total_sf'])} SF")

    # Navigation
    views = {
        "Lease Database": render_lease_database,
        "Co-Tenancy Risk": render_cotenancy_risk,
        "10-Year Projection": render_projection,
        "Tenant Mix": render_tenant_mix,
        "Critical Dates": render_critical_dates,
    }

    selected_view = st.radio(
        "View",
        list(views.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Render selected view
    views[selected_view]()


if __name__ == "__main__":
    main()
