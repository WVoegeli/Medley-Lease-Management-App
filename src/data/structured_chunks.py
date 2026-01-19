"""
Convert structured lease data into RAG-compatible chunks
This ensures the AI chat can answer questions using the dashboard data
"""

import uuid
from typing import List
from ..chunking.chunker import Chunk
from .lease_data import (
    LEASE_DATA,
    Lease,
    get_summary_stats,
    get_tenants_with_cotenancy,
    calc_rent_for_year,
)


def generate_lease_summary_chunk(lease: Lease) -> Chunk:
    """Generate a comprehensive summary chunk for a lease."""
    content = f"""LEASE SUMMARY: {lease.tenant}

Legal Entity: {lease.legal_entity}
Suite: {lease.suite}
Square Footage: {lease.sqft:,} SF
Use: {lease.use}
Category: {lease.category}

TERM INFORMATION:
- Lease Term: {lease.term} ({lease.term_months} months)
- Commencement Date: {lease.commence_date}
- Expiration Date: {lease.expire_date}
- Renewal Options: {lease.options or 'None'}

RENT INFORMATION:
- Year 1 Rent PSF: ${lease.rent.year1_psf:.2f}
- Year 1 Annual Rent: ${lease.rent.year1_annual:,.0f}
- Escalation: {lease.rent.escalation}
- Escalation Rate: {lease.rent.escalation_rate * 100:.1f}%
- Escalation Period: Every {lease.rent.escalation_period} year(s)

RENT SCHEDULE:
"""
    for entry in lease.rent_schedule:
        notes = f" ({entry.notes})" if entry.notes else ""
        content += f"- {entry.period}: ${entry.psf:.2f}/SF, ${entry.monthly:,.0f}/month{notes}\n"

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": lease.tenant,
            "source_file": "structured_data",
            "section_type": "lease_summary",
            "section_name": "Lease Summary",
            "sqft": lease.sqft,
            "category": lease.category,
        },
        token_count=len(content.split()) * 2,  # Rough estimate
        source_file="structured_data",
        section_type="lease_summary",
        section_name="Lease Summary"
    )


def generate_ti_chunk(lease: Lease) -> Chunk:
    """Generate TI allowance chunk for a lease."""
    if not lease.ti.total:
        content = f"""TENANT IMPROVEMENT ALLOWANCE: {lease.tenant}

{lease.tenant} has NO Tenant Improvement (TI) Allowance.
{lease.ti.notes or 'Landlord delivers shell condition.'}
"""
    else:
        content = f"""TENANT IMPROVEMENT ALLOWANCE: {lease.tenant}

Tenant: {lease.tenant}
Suite: {lease.suite}
Square Footage: {lease.sqft:,} SF

TI ALLOWANCE DETAILS:
- TI Per Square Foot: ${lease.ti.psf:.2f}
- Total TI Allowance: ${lease.ti.total:,.0f}
- Notes: {lease.ti.notes or 'Standard buildout allowance'}

This TI allowance is provided by the Landlord to help {lease.tenant} build out their space.
"""

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": lease.tenant,
            "source_file": "structured_data",
            "section_type": "ti_allowance",
            "section_name": "TI Allowance",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="ti_allowance",
        section_name="TI Allowance"
    )


def generate_recovery_chunk(lease: Lease) -> Chunk:
    """Generate recovery/CAM chunk for a lease."""
    cam_str = f"${lease.cam.year1:.2f}/SF per year" if lease.cam.year1 else "Included in rent"
    tax_str = f"${lease.tax:.2f}/SF per year" if lease.tax else "Included in rent"
    ins_str = f"${lease.insurance:.2f}/SF per year" if lease.insurance else "Included in rent"

    content = f"""RECOVERY STRUCTURE / CAM / NNN: {lease.tenant}

Tenant: {lease.tenant}
Suite: {lease.suite}

OPERATING EXPENSE RECOVERY:
- Recovery Type: {lease.cam.type}
- CAM (Year 1): {cam_str}
- CAM Increases: {lease.cam.increases or 'Not specified'}
- Estimated Taxes: {tax_str}
- Estimated Insurance: {ins_str}
"""
    if lease.recovery_note:
        content += f"- Note: {lease.recovery_note}\n"

    total_recovery = (lease.cam.year1 or 0) + (lease.tax or 0) + (lease.insurance or 0)
    if total_recovery > 0:
        content += f"""
TOTAL ESTIMATED RECOVERIES:
- Total Recovery PSF: ${total_recovery:.2f}/SF per year
- Total Annual Recovery: ${total_recovery * lease.sqft:,.0f}
"""

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": lease.tenant,
            "source_file": "structured_data",
            "section_type": "recoveries",
            "section_name": "Recoveries/CAM",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="recoveries",
        section_name="Recoveries/CAM"
    )


def generate_cotenancy_chunk(lease: Lease) -> Chunk:
    """Generate co-tenancy chunk for a lease."""
    if not lease.co_tenancy:
        content = f"""CO-TENANCY: {lease.tenant}

{lease.tenant} has NO co-tenancy clause in their lease.
This tenant will pay full rent regardless of other tenant occupancy levels.
"""
    else:
        ct = lease.co_tenancy
        content = f"""CO-TENANCY CLAUSE: {lease.tenant}

Tenant: {lease.tenant}
Suite: {lease.suite}

CO-TENANCY DETAILS:
- Co-Tenancy Type: {ct.type}
- Risk Level: {ct.risk_level.upper()}
- Threshold: {ct.threshold}
- Remedy if Not Met: {ct.remedy}
- Termination Rights: {ct.termination or 'No termination right'}
- Named Co-Tenant Requirement: {ct.named_tenant or 'None'}
- Annual Rent at Risk: ${ct.rent_at_risk:,.0f}

RISK ANALYSIS:
This is a {ct.risk_level.upper()} RISK co-tenancy clause.
If the co-tenancy threshold is not met, {lease.tenant} may {ct.remedy.lower()}.
"""
        if ct.notes:
            content += f"\nAdditional Notes: {ct.notes}"

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": lease.tenant,
            "source_file": "structured_data",
            "section_type": "cotenancy",
            "section_name": "Co-Tenancy",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="cotenancy",
        section_name="Co-Tenancy"
    )


def generate_portfolio_summary_chunk() -> Chunk:
    """Generate overall portfolio summary chunk."""
    stats = get_summary_stats()
    cotenancy_tenants = get_tenants_with_cotenancy()

    content = f"""MEDLEY SHOPPING CENTER - PORTFOLIO SUMMARY

OVERVIEW:
- Grand Opening: November 2026
- Total Tenants: {stats['tenant_count']}
- Total Leasable Area: {stats['total_sf']:,} SF
- Total Year 1 Annual Rent: ${stats['total_rent']:,.0f}
- Average Rent PSF: ${stats['avg_psf']:.2f}
- Total TI Commitments: ${stats['total_ti']:,.0f}

CO-TENANCY RISK:
- Tenants with Co-Tenancy Clauses: {stats['cotenancy_count']}
- Total Annual Rent at Risk: ${sum(l.co_tenancy.rent_at_risk for l in cotenancy_tenants):,.0f}

TENANT ROSTER:
"""
    for lease in sorted(LEASE_DATA, key=lambda x: x.suite):
        content += f"- {lease.tenant} (Suite {lease.suite}, {lease.sqft:,} SF, ${lease.rent.year1_psf:.2f}/SF)\n"

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": "ALL",
            "source_file": "structured_data",
            "section_type": "portfolio_summary",
            "section_name": "Portfolio Summary",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="portfolio_summary",
        section_name="Portfolio Summary"
    )


def generate_rent_comparison_chunk() -> Chunk:
    """Generate rent comparison across all tenants."""
    content = """RENT COMPARISON - ALL TENANTS

RENT RATES BY TENANT (Year 1, sorted by rent/SF):
"""
    sorted_by_rent = sorted(LEASE_DATA, key=lambda x: x.rent.year1_psf, reverse=True)

    for lease in sorted_by_rent:
        content += f"- {lease.tenant}: ${lease.rent.year1_psf:.2f}/SF (${lease.rent.year1_annual:,.0f}/year, {lease.sqft:,} SF)\n"

    # Add category averages
    content += "\nAVERAGE RENT BY CATEGORY:\n"
    categories = {}
    for lease in LEASE_DATA:
        if lease.category not in categories:
            categories[lease.category] = {"total_rent": 0, "total_sf": 0}
        categories[lease.category]["total_rent"] += lease.rent.year1_annual
        categories[lease.category]["total_sf"] += lease.sqft

    for cat, data in sorted(categories.items(), key=lambda x: x[1]["total_rent"]/x[1]["total_sf"], reverse=True):
        avg = data["total_rent"] / data["total_sf"]
        content += f"- {cat}: ${avg:.2f}/SF average\n"

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": "ALL",
            "source_file": "structured_data",
            "section_type": "rent_comparison",
            "section_name": "Rent Comparison",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="rent_comparison",
        section_name="Rent Comparison"
    )


def generate_cotenancy_risk_summary_chunk() -> Chunk:
    """Generate co-tenancy risk summary for the portfolio."""
    tenants = get_tenants_with_cotenancy()
    high_risk = [l for l in tenants if l.co_tenancy.risk_level == "high"]
    medium_risk = [l for l in tenants if l.co_tenancy.risk_level == "medium"]
    low_risk = [l for l in tenants if l.co_tenancy.risk_level == "low"]

    content = f"""CO-TENANCY RISK ANALYSIS - PORTFOLIO SUMMARY

RISK OVERVIEW:
- Total Tenants with Co-Tenancy: {len(tenants)}
- High Risk Tenants: {len(high_risk)}
- Medium Risk Tenants: {len(medium_risk)}
- Low Risk Tenants: {len(low_risk)}
- Total Annual Rent at Risk: ${sum(l.co_tenancy.rent_at_risk for l in tenants):,.0f}

HIGH RISK TENANTS (Opening/Operating Co-Tenancy with named tenants):
"""
    for lease in high_risk:
        content += f"- {lease.tenant}: ${lease.co_tenancy.rent_at_risk:,.0f} at risk. {lease.co_tenancy.type} co-tenancy. Named tenant: {lease.co_tenancy.named_tenant or 'None'}\n"

    content += "\nMEDIUM RISK TENANTS:\n"
    for lease in medium_risk:
        content += f"- {lease.tenant}: ${lease.co_tenancy.rent_at_risk:,.0f} at risk. {lease.co_tenancy.type} co-tenancy.\n"

    content += "\nLOW RISK TENANTS:\n"
    for lease in low_risk:
        content += f"- {lease.tenant}: ${lease.co_tenancy.rent_at_risk:,.0f} at risk. {lease.co_tenancy.type} co-tenancy.\n"

    content += f"""
CRITICAL DEPENDENCY:
Trader Joe's is the anchor tenant that triggers most co-tenancy clauses.
If Trader Joe's delays opening, HIGH RISK rent at risk: ${sum(l.co_tenancy.rent_at_risk for l in high_risk):,.0f}
"""

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": "ALL",
            "source_file": "structured_data",
            "section_type": "cotenancy_risk_summary",
            "section_name": "Co-Tenancy Risk Summary",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="cotenancy_risk_summary",
        section_name="Co-Tenancy Risk Summary"
    )


def generate_ten_year_projection_chunk() -> Chunk:
    """Generate 10-year rent projection chunk."""
    content = """10-YEAR RENT PROJECTION - MEDLEY SHOPPING CENTER

Annual rent projections based on contractual escalations:

"""
    projections = []
    for year in range(1, 11):
        total_rent = 0
        active_leases = 0
        for lease in LEASE_DATA:
            term_years = lease.term_months / 12
            if year <= term_years:
                total_rent += calc_rent_for_year(lease, year)
                active_leases += 1
        projections.append((year, 2026 + year, total_rent, active_leases))
        content += f"Year {year} ({2026 + year}): ${total_rent:,.0f} ({active_leases} active leases)\n"

    growth = (projections[9][2] - projections[0][2]) / projections[0][2]
    content += f"""
SUMMARY:
- Year 1 Total Rent: ${projections[0][2]:,.0f}
- Year 10 Total Rent: ${projections[9][2]:,.0f}
- 10-Year Growth: {growth * 100:.1f}%
- Leases expiring within 10 years: {29 - projections[9][3]}
"""

    return Chunk(
        id=str(uuid.uuid4()),
        content=content,
        metadata={
            "tenant_name": "ALL",
            "source_file": "structured_data",
            "section_type": "rent_projection",
            "section_name": "10-Year Rent Projection",
        },
        token_count=len(content.split()) * 2,
        source_file="structured_data",
        section_type="rent_projection",
        section_name="10-Year Rent Projection"
    )


def generate_all_structured_chunks() -> List[Chunk]:
    """Generate all structured data chunks for RAG ingestion."""
    chunks = []

    # Portfolio-level chunks
    chunks.append(generate_portfolio_summary_chunk())
    chunks.append(generate_rent_comparison_chunk())
    chunks.append(generate_cotenancy_risk_summary_chunk())
    chunks.append(generate_ten_year_projection_chunk())

    # Per-tenant chunks
    for lease in LEASE_DATA:
        chunks.append(generate_lease_summary_chunk(lease))
        chunks.append(generate_ti_chunk(lease))
        chunks.append(generate_recovery_chunk(lease))
        chunks.append(generate_cotenancy_chunk(lease))

    return chunks
