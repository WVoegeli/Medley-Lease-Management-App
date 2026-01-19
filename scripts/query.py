"""
Quick query script for command-line queries
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from src.search.query_engine import QueryEngine


console = Console()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Query lease documents")
    parser.add_argument(
        "question",
        help="Question to ask"
    )
    parser.add_argument(
        "--tenant",
        "-t",
        type=str,
        help="Filter by tenant name"
    )
    parser.add_argument(
        "--results",
        "-n",
        type=int,
        default=5,
        help="Number of results (default: 5)"
    )
    parser.add_argument(
        "--no-sources",
        action="store_true",
        help="Don't show sources"
    )

    args = parser.parse_args()

    # Initialize engine
    try:
        engine = QueryEngine()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Run 'python scripts/ingest.py' first.[/yellow]")
        return

    # Execute query
    with console.status("[bold blue]Processing query...[/bold blue]"):
        response = engine.query(
            question=args.question,
            tenant_filter=args.tenant,
            n_results=args.results,
            include_sources=not args.no_sources
        )

    # Print answer
    console.print("\n[bold green]Answer:[/bold green]")
    console.print(Panel(response.answer, border_style="green"))

    # Print sources
    if response.sources and not args.no_sources:
        console.print("\n[bold yellow]Sources:[/bold yellow]")
        for i, source in enumerate(response.sources, 1):
            console.print(f"\n[cyan]{i}. {source['tenant']} - {source['section']}[/cyan]")
            console.print(f"[dim]{source['content'][:200]}...[/dim]")


if __name__ == "__main__":
    main()
