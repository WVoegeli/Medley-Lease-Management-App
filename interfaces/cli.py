"""
Command-line interface for querying lease documents
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from src.search.query_engine import QueryEngine


console = Console()


def print_welcome():
    """Print welcome message"""
    welcome_text = """
[bold blue]Medley Lease Analysis & Management System[/bold blue]
[dim]Query your lease agreements using natural language[/dim]

Commands:
  [cyan]q[/cyan] or [cyan]quit[/cyan]  - Exit the program
  [cyan]tenants[/cyan]     - List all tenants
  [cyan]stats[/cyan]       - Show database statistics
  [cyan]help[/cyan]        - Show this help message

You can also filter by tenant:
  [cyan]@TenantName[/cyan] your question

Example queries:
  - What is Summit Coffee's monthly rent?
  - @Sephora What are the renewal options?
  - Compare security deposits across tenants
"""
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))


def print_chat_welcome():
    """Print chat mode welcome message"""
    welcome_text = """
[bold blue]Medley Lease Chat Mode[/bold blue]
[dim]Have a conversation about your lease agreements[/dim]

Commands:
  [cyan]/quit[/cyan]    - Exit chat
  [cyan]/clear[/cyan]   - Clear conversation history
  [cyan]/history[/cyan] - Show conversation history
  [cyan]/help[/cyan]    - Show this help message

The assistant remembers your conversation context.
Ask follow-up questions like "What about their renewal options?"
"""
    console.print(Panel(welcome_text, title="Chat Mode", border_style="green"))


def print_response(response):
    """Print a query response"""
    # Print answer
    console.print("\n[bold green]Answer:[/bold green]")
    console.print(Panel(response.answer, border_style="green"))

    # Print sources
    if response.sources:
        console.print("\n[bold yellow]Sources:[/bold yellow]")
        source_table = Table(show_header=True, header_style="bold")
        source_table.add_column("Tenant", style="cyan", width=20)
        source_table.add_column("Section", width=25)
        source_table.add_column("Score", justify="right", width=8)

        for source in response.sources[:5]:  # Limit to top 5
            source_table.add_row(
                source["tenant"],
                source["section"][:25] if source["section"] else "N/A",
                f"{source['score']:.3f}"
            )

        console.print(source_table)


def run_cli():
    """Run the interactive CLI"""
    print_welcome()

    # Initialize query engine
    console.print("[dim]Initializing query engine...[/dim]")
    try:
        engine = QueryEngine()
        stats = engine.get_stats()
        chunks = stats['total_chunks']
        tenants = stats['num_tenants']
        console.print(f"[green]Ready! {chunks} chunks from {tenants} tenants loaded.[/green]\n")
    except Exception as e:
        console.print(f"[red]Error initializing: {e}[/red]")
        console.print("[yellow]Make sure you've run the ingestion script first.[/yellow]")
        return

    # Main loop
    while True:
        try:
            # Get input
            query = Prompt.ask("\n[bold blue]Question[/bold blue]")
            query = query.strip()

            if not query:
                continue

            # Handle commands
            if query.lower() in ["q", "quit", "exit"]:
                console.print("[dim]Goodbye![/dim]")
                break

            elif query.lower() == "help":
                print_welcome()
                continue

            elif query.lower() == "tenants":
                tenants = engine.get_tenant_list()
                console.print("\n[bold]Tenants in database:[/bold]")
                for i, tenant in enumerate(tenants, 1):
                    console.print(f"  {i}. {tenant}")
                continue

            elif query.lower() == "stats":
                stats = engine.get_stats()
                stats_table = Table(title="Database Statistics")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", justify="right")
                stats_table.add_row("Total Chunks", str(stats["total_chunks"]))
                stats_table.add_row("Number of Tenants", str(stats["num_tenants"]))
                console.print(stats_table)
                continue

            # Check for tenant filter
            tenant_filter = None
            if query.startswith("@"):
                parts = query.split(" ", 1)
                if len(parts) == 2:
                    tenant_filter = parts[0][1:]  # Remove @
                    query = parts[1]
                    console.print(f"[dim]Filtering by tenant: {tenant_filter}[/dim]")

            # Execute query
            with console.status("[bold blue]Searching and generating answer...[/bold blue]"):
                response = engine.query(
                    question=query,
                    tenant_filter=tenant_filter,
                    n_results=5
                )

            print_response(response)

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'quit' to exit.[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def single_query(question: str, tenant: str = None):
    """Run a single query and exit"""
    engine = QueryEngine()
    response = engine.query(question=question, tenant_filter=tenant)
    print_response(response)


def run_chat(tenant_filter: str = None):
    """Run interactive chat mode with conversation history"""
    print_chat_welcome()

    # Initialize query engine
    console.print("[dim]Initializing chat engine...[/dim]")
    try:
        engine = QueryEngine()
        stats = engine.get_stats()
        chunks = stats['total_chunks']
        tenants = stats['num_tenants']
        console.print(f"[green]Ready! {chunks} chunks from {tenants} tenants loaded.[/green]")
        if tenant_filter:
            console.print(f"[yellow]Filtering by tenant: {tenant_filter}[/yellow]")
        console.print()
    except Exception as e:
        console.print(f"[red]Error initializing: {e}[/red]")
        console.print("[yellow]Make sure you've run the ingestion script first.[/yellow]")
        return

    # Conversation history
    conversation_history = []

    # Main chat loop
    while True:
        try:
            # Get input
            message = Prompt.ask("[bold green]You[/bold green]")
            message = message.strip()

            if not message:
                continue

            # Handle commands
            if message.lower() == "/quit":
                console.print("[dim]Goodbye![/dim]")
                break

            elif message.lower() == "/clear":
                conversation_history = []
                console.print("[yellow]Conversation cleared.[/yellow]")
                continue

            elif message.lower() == "/history":
                if not conversation_history:
                    console.print("[dim]No conversation history yet.[/dim]")
                else:
                    console.print("\n[bold]Conversation History:[/bold]")
                    for i, msg in enumerate(conversation_history):
                        role = "[cyan]You[/cyan]" if msg["role"] == "user" else "[green]Assistant[/green]"
                        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        console.print(f"  {role}: {content}")
                continue

            elif message.lower() == "/help":
                print_chat_welcome()
                continue

            # Generate response
            with console.status("[bold blue]Thinking...[/bold blue]"):
                response = engine.chat(
                    message=message,
                    conversation_history=conversation_history,
                    tenant_filter=tenant_filter,
                    n_results=5
                )

            # Print response
            console.print("\n[bold green]Assistant:[/bold green]")
            console.print(Panel(response.answer, border_style="green"))

            # Update conversation history
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": response.answer})

            # Show source count
            if response.sources:
                console.print(f"[dim]({len(response.sources)} sources used)[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type '/quit' to exit.[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query lease documents")
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask (if provided, runs single query and exits)"
    )
    parser.add_argument(
        "--tenant",
        type=str,
        help="Filter by tenant name"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Run in chat mode with conversation history"
    )

    args = parser.parse_args()

    if args.chat:
        run_chat(tenant_filter=args.tenant)
    elif args.question:
        single_query(args.question, args.tenant)
    else:
        run_cli()
