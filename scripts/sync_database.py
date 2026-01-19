"""
Synchronize structured database with lease document data.

This script populates the SQLite database with metadata extracted from
lease documents, creating a structured layer for analytics and tracking.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.sql_store import SQLStore
from src.data.lease_data import LEASE_DATA
from rich.console import Console
from rich.table import Table
from rich.progress import track
import argparse

console = Console()


def sync_lease_data(clear: bool = False):
    """Sync lease data from lease_data.py to SQL database."""

    console.print("\n[bold cyan]Medley Lease Database Synchronization[/bold cyan]\n")

    # Initialize database
    db = SQLStore()

    if clear:
        console.print("[yellow]Clearing existing database...[/yellow]")
        # Recreate database by deleting and reinitializing
        import os
        if os.path.exists(db.db_path):
            os.remove(db.db_path)
        db = SQLStore()

    # Sync lease data
    console.print(f"[green]Syncing {len(LEASE_DATA)} leases...[/green]\n")

    synced_count = 0
    for lease in track(LEASE_DATA, description="Processing leases"):
        try:
            lease_id = db.add_lease(
                tenant_name=lease['tenant_name'],
                lease_file=lease['lease_file'],
                start_date=lease.get('start_date'),
                end_date=lease.get('end_date'),
                term_months=lease.get('term_months'),
                square_footage=lease.get('square_footage'),
                base_rent=lease.get('base_rent'),
                rent_frequency=lease.get('rent_frequency', 'monthly'),
                security_deposit=lease.get('security_deposit'),
                renewal_options=lease.get('renewal_options'),
                special_provisions=lease.get('special_provisions'),
                status='active'
            )
            synced_count += 1
        except Exception as e:
            console.print(f"[red]Error syncing {lease['tenant_name']}: {e}[/red]")

    console.print(f"\n[green]✓ Successfully synced {synced_count} leases[/green]\n")

    # Display summary
    display_summary(db)

    db.close()


def display_summary(db: SQLStore):
    """Display database summary."""

    # Financial summary
    summary = db.get_financial_summary()

    table = Table(title="Financial Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")

    table.add_row("Active Leases", str(summary['active_leases']))
    table.add_row("Monthly Revenue", f"${summary['monthly_revenue']:,.2f}")
    table.add_row("Annual Revenue", f"${summary['annual_revenue']:,.2f}")
    table.add_row("Total Square Footage", f"{summary['total_square_footage']:,.0f} sq ft")
    table.add_row("Avg Rent per Sq Ft", f"${summary['avg_rent_per_sqft']:.2f}")
    table.add_row("Expiring in 90 Days", str(summary['expiring_within_90_days']))

    console.print(table)

    # Expiring leases
    expiring = db.get_expiring_leases(90)
    if expiring:
        console.print(f"\n[yellow]⚠ {len(expiring)} lease(s) expiring in the next 90 days:[/yellow]\n")

        exp_table = Table(show_header=True, header_style="bold yellow")
        exp_table.add_column("Tenant", style="cyan")
        exp_table.add_column("Expiration Date", style="yellow")
        exp_table.add_column("Days Until", style="red", justify="right")

        for lease in expiring:
            exp_table.add_row(
                lease['tenant_name'],
                lease['end_date'],
                f"{int(lease['days_until_expiration'])} days"
            )

        console.print(exp_table)

    # Top tenants by revenue
    revenue_by_tenant = db.get_revenue_by_tenant()
    if revenue_by_tenant:
        console.print("\n")
        rev_table = Table(title="Top Tenants by Revenue", show_header=True, header_style="bold magenta")
        rev_table.add_column("Tenant", style="cyan")
        rev_table.add_column("Monthly Rent", style="green", justify="right")
        rev_table.add_column("Annual Rent", style="green", justify="right")
        rev_table.add_column("Sq Ft", justify="right")
        rev_table.add_column("$/Sq Ft", justify="right")

        for tenant in revenue_by_tenant[:10]:  # Top 10
            rev_table.add_row(
                tenant['tenant_name'],
                f"${tenant['monthly_rent']:,.2f}",
                f"${tenant['annual_rent']:,.2f}",
                f"{tenant['square_footage']:,.0f}" if tenant['square_footage'] else "N/A",
                f"${tenant['rent_per_sqft']:.2f}" if tenant['rent_per_sqft'] else "N/A"
            )

        console.print(rev_table)


def main():
    parser = argparse.ArgumentParser(description="Sync lease database")
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing database before syncing')
    args = parser.parse_args()

    try:
        sync_lease_data(clear=args.clear)
        console.print("\n[bold green]✓ Database sync completed successfully![/bold green]\n")
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]\n")
        raise


if __name__ == "__main__":
    main()
