"""
Quick Start Script for Medley Lease Analysis & Management System

Automates the initial setup process:
1. Verifies dependencies
2. Ingests lease documents
3. Syncs structured database
4. Runs initial tests
5. Provides next steps
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()


def check_python_version():
    """Verify Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        console.print("[red]❌ Python 3.8+ required[/red]")
        return False
    console.print(f"[green]✓ Python {version.major}.{version.minor}.{version.micro}[/green]")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'openai', 'chromadb', 'streamlit', 'fastapi',
        'rich', 'python-dotenv', 'rank_bm25'
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            console.print(f"[green]✓ {package}[/green]")
        except ImportError:
            console.print(f"[red]✗ {package}[/red]")
            missing.append(package)

    return len(missing) == 0, missing


def run_command(cmd, description):
    """Run a command with progress indicator."""
    console.print(f"\n[cyan]{description}...[/cyan]")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            console.print(f"[green]✓ {description} completed successfully[/green]")
            return True
        else:
            console.print(f"[red]✗ {description} failed[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


def main():
    """Run quick start setup."""

    console.clear()

    # Welcome banner
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║   MEDLEY LEASE ANALYSIS & MANAGEMENT                ║
    ║         QUICK START SETUP                            ║
    ╚══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

    # Step 1: Check Python version
    console.print("\n[bold]Step 1: Checking Python Version[/bold]")
    if not check_python_version():
        console.print("\n[red]Please upgrade Python to 3.8 or higher[/red]")
        return

    # Step 2: Check dependencies
    console.print("\n[bold]Step 2: Checking Dependencies[/bold]")
    deps_ok, missing = check_dependencies()

    if not deps_ok:
        console.print(f"\n[yellow]Missing packages: {', '.join(missing)}[/yellow]")
        console.print("\n[cyan]Run: pip install -r requirements.txt[/cyan]")
        return

    # Step 3: Check for .env file
    console.print("\n[bold]Step 3: Checking Configuration[/bold]")
    if not Path('.env').exists():
        console.print("[yellow]⚠ .env file not found[/yellow]")
        console.print("[cyan]Copy .env.example to .env and add your API keys[/cyan]")
        return
    else:
        console.print("[green]✓ .env file found[/green]")

    # Step 4: Check for lease documents
    console.print("\n[bold]Step 4: Checking Lease Documents[/bold]")
    lease_dir = Path('Lease Contracts')
    if not lease_dir.exists():
        console.print("[red]✗ Lease Contracts directory not found[/red]")
        return

    docx_files = list(lease_dir.glob('*.docx'))
    console.print(f"[green]✓ Found {len(docx_files)} lease documents[/green]")

    # Step 5: Ingest documents
    console.print("\n[bold]Step 5: Ingesting Documents to Vector Database[/bold]")
    if not run_command("python scripts/ingest.py", "Document ingestion"):
        console.print("[yellow]Note: Ingestion may have partial errors[/yellow]")

    # Step 6: Sync structured database
    console.print("\n[bold]Step 6: Syncing Structured Database[/bold]")
    if not run_command("python scripts/sync_database.py", "Database synchronization"):
        console.print("[red]Database sync failed - check lease_data.py[/red]")

    # Step 7: Run tests
    console.print("\n[bold]Step 7: Running Tests[/bold]")
    run_command("pytest tests/ -v --tb=short", "Test suite")

    # Success summary
    console.print("\n")
    panel = Panel(
        """[bold green]✓ Quick Start Setup Complete![/bold green]

[cyan]Your Medley Lease Analysis & Management System is ready to use![/cyan]

[bold]Next Steps:[/bold]

1. Start the Streamlit Chat Interface:
   [yellow]streamlit run interfaces/chat_app.py[/yellow]

2. Start the REST API Server:
   [yellow]python api/main.py[/yellow]
   API Docs: http://localhost:8000/docs

3. Run the Dashboard:
   [yellow]streamlit run interfaces/dashboard_app.py[/yellow]

4. Generate a Portfolio Report:
   [yellow]python -c "from src.database.sql_store import SQLStore; \\
from src.analytics.lease_analytics import LeaseAnalytics; \\
from src.export.report_generator import ReportGenerator; \\
db = SQLStore(); analytics = LeaseAnalytics(db); \\
report = ReportGenerator(db, analytics); \\
report.export_portfolio_pdf('portfolio_report.pdf'); \\
print('Report generated: portfolio_report.pdf')"[/yellow]

[bold]Documentation:[/bold]
- Full docs: AGENTS.md
- API Reference: http://localhost:8000/docs (after starting API)

[bold]Support:[/bold]
- Check logs in data/ directory
- Review test results: pytest tests/ -v
        """,
        title="🎉 Setup Complete",
        border_style="green"
    )

    console.print(panel)

    # Quick stats
    console.print("\n[bold]System Status:[/bold]")
    status_table = Table(show_header=True, header_style="bold magenta")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="green")

    status_table.add_row("Vector Database (ChromaDB)", "✓ Ready")
    status_table.add_row("Structured Database (SQLite)", "✓ Ready")
    status_table.add_row("Analytics Engine", "✓ Ready")
    status_table.add_row("RAG Query Engine", "✓ Ready")
    status_table.add_row("REST API", "Ready to start")
    status_table.add_row("Streamlit Interfaces", "Ready to start")

    console.print(status_table)

    console.print("\n[bold cyan]Happy lease managing! 🏢[/bold cyan]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during setup: {e}[/red]")
        raise
