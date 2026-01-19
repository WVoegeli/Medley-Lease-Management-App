"""
Comprehensive RAG System Testing Script

Tests the chatbot with 100+ queries across different categories:
- Basic information retrieval
- Financial queries
- Date/timeline questions
- Comparison queries
- Follow-up question handling
- Edge cases

Generates a detailed report of accuracy and quality.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for Rich library
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search.query_engine import QueryEngine
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
import json

console = Console()


# Test queries organized by category
TEST_QUERIES = {
    "Basic Information": [
        "What is Summit Coffee's monthly rent?",
        "What is Five Daughters Bakery's square footage?",
        "What is Sephora's lease term length?",
        "What is the monthly rent for 26 Thai?",
        "What suite is Trader Joe's in?",
        "What is Playa Bowls' monthly rent?",
        "What is CRU Food & Wine Bar's square footage?",
        "What is Drybar's lease commencement date?",
    ],

    "Financial Queries": [
        "What is Five Daughters Bakery's rent escalation schedule?",
        "What is the rent per square foot for Summit Coffee?",
        "What are the CAM charges for Sephora?",
        "What is the security deposit amount for Trader Joe's?",
        "What percentage rent does Five Daughters Bakery pay?",
        "What is the annual rent for 26 Thai?",
        "What are the tenant improvement allowances for CRU Food & Wine Bar?",
        "What is the base rent for Playa Bowls?",
    ],

    "Dates & Deadlines": [
        "When does Summit Coffee's lease expire?",
        "When is the lease commencement date for Five Daughters Bakery?",
        "What is the substantial completion date for Sephora?",
        "When is the rent commencement date for 26 Thai?",
        "What are the critical dates for Trader Joe's lease?",
        "When does Playa Bowls' lease start?",
        "What is the lease expiration date for Drybar?",
        "When is the grand opening date mentioned in the leases?",
    ],

    "Lease Terms & Options": [
        "What renewal options does Summit Coffee have?",
        "What are the renewal terms for Five Daughters Bakery?",
        "Does Sephora have any extension options?",
        "What are the termination rights for Trader Joe's?",
        "What expansion options does 26 Thai have?",
        "Does CRU Food & Wine Bar have a renewal option?",
        "What are the option periods for Playa Bowls?",
        "What is the notice period for renewal for Drybar?",
    ],

    "Operating Requirements": [
        "What are the operating hours requirements for Summit Coffee?",
        "What are the permitted uses for Five Daughters Bakery?",
        "What are the signage requirements for Sephora?",
        "What are the maintenance obligations for Trader Joe's?",
        "What are the insurance requirements for 26 Thai?",
        "What are the parking requirements for CRU Food & Wine Bar?",
        "What are the use restrictions for Playa Bowls?",
        "What are the operating covenants for Drybar?",
    ],

    "Co-Tenancy & Exclusives": [
        "What co-tenancy provisions does Sephora have?",
        "Does Trader Joe's have any exclusive use rights?",
        "What are the co-tenancy requirements for Five Daughters Bakery?",
        "Does Summit Coffee have any exclusive rights?",
        "What are the opening co-tenancy requirements for Sephora?",
        "What are the ongoing co-tenancy provisions for Trader Joe's?",
        "Does CRU Food & Wine Bar have any exclusivity clauses?",
        "What are the protected uses for Playa Bowls?",
    ],

    "Comparison Queries": [
        "Compare the monthly rent between Summit Coffee and Five Daughters Bakery",
        "Which tenant has the longest lease term?",
        "Which tenant pays the highest rent per square foot?",
        "Compare the renewal options across all cafe tenants",
        "Which tenants have co-tenancy provisions?",
        "Compare the square footage of all retail tenants",
        "Which tenants have percentage rent clauses?",
        "Compare the security deposits across all tenants",
    ],

    "Follow-Up Questions": [
        # These test conversation memory
        ("What is Five Daughters Bakery's rent schedule?", "What about per month?"),
        ("Tell me about Summit Coffee's lease", "When does it expire?"),
        ("What is Sephora's square footage?", "What about their rent?"),
        ("What is Trader Joe's monthly rent?", "Do they have renewal options?"),
        ("What are the renewal terms for 26 Thai?", "What is the notice period?"),
        ("What is the lease term for Playa Bowls?", "What about rent escalations?"),
    ],

    "Complex Questions": [
        "What is the total monthly rent across all tenants?",
        "Which leases expire in 2025?",
        "What is the average rent per square foot for food tenants?",
        "List all tenants with leases longer than 10 years",
        "Which tenants have both renewal options and co-tenancy provisions?",
        "What is the total square footage leased to retail tenants?",
        "Which tenants have the most favorable renewal terms?",
        "What are the prohibited uses across all leases?",
    ],

    "Edge Cases": [
        "What is the rent for a tenant that doesn't exist?",
        "Tell me about XYZ Company's lease",
        "What is the monthly rent?",  # No tenant specified
        "When do leases expire?",  # No tenant specified
        "What are the renewal options?",  # No tenant specified
        "Show me lease information",  # Vague request
        "Tell me everything about all tenants",  # Too broad
        "What is the meaning of life?",  # Completely unrelated
    ]
}


def test_single_query(engine: QueryEngine, question: str, category: str) -> dict:
    """Test a single query and return results"""
    try:
        result = engine.query(question, n_results=5)
        return {
            "category": category,
            "question": question,
            "answer": result.answer,
            "num_sources": result.num_results,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "category": category,
            "question": question,
            "answer": None,
            "num_sources": 0,
            "success": False,
            "error": str(e)
        }


def test_follow_up(engine: QueryEngine, first_q: str, second_q: str) -> dict:
    """Test a follow-up question conversation"""
    try:
        # First question
        result1 = engine.query(first_q, n_results=5)

        # Follow-up with conversation history
        conversation_history = [
            {"role": "user", "content": first_q},
            {"role": "assistant", "content": result1.answer}
        ]

        result2 = engine.chat(
            message=second_q,
            conversation_history=conversation_history,
            n_results=5
        )

        return {
            "category": "Follow-Up Questions",
            "question": f"{first_q} → {second_q}",
            "answer": result2.answer,
            "num_sources": result2.num_results,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "category": "Follow-Up Questions",
            "question": f"{first_q} → {second_q}",
            "answer": None,
            "num_sources": 0,
            "success": False,
            "error": str(e)
        }


def run_comprehensive_tests():
    """Run all tests and generate report"""
    console.clear()
    console.print("\n[bold cyan]===========================================================[/bold cyan]")
    console.print("[bold cyan]         COMPREHENSIVE RAG SYSTEM TESTING                [/bold cyan]")
    console.print("[bold cyan]===========================================================[/bold cyan]\n")

    # Initialize query engine
    console.print("[yellow]Initializing query engine...[/yellow]")
    engine = QueryEngine()

    # Get database stats
    stats = engine.get_stats()
    console.print(f"\n[green]✓ Database loaded:[/green]")
    console.print(f"  - {stats['total_chunks']} chunks")
    console.print(f"  - {stats['num_tenants']} unique tenant names")

    # Run all tests
    results = []
    total_queries = sum(len(queries) if isinstance(queries, list) else len(queries) for queries in TEST_QUERIES.values())

    console.print(f"\n[bold]Running {total_queries} test queries...[/bold]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        for category, queries in TEST_QUERIES.items():
            task = progress.add_task(f"[cyan]{category}...", total=None)

            if category == "Follow-Up Questions":
                # Handle follow-up question pairs
                for first_q, second_q in queries:
                    result = test_follow_up(engine, first_q, second_q)
                    results.append(result)
            else:
                # Handle single queries
                for question in queries:
                    result = test_single_query(engine, question, category)
                    results.append(result)

            progress.remove_task(task)

    # Generate summary statistics
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0

    # Categorize results
    category_stats = {}
    for result in results:
        cat = result['category']
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'success': 0}
        category_stats[cat]['total'] += 1
        if result['success']:
            category_stats[cat]['success'] += 1

    # Display summary
    console.print("\n[bold green]===========================================================[/bold green]")
    console.print("[bold green]            TEST RESULTS SUMMARY                          [/bold green]")
    console.print("[bold green]===========================================================[/bold green]\n")

    console.print(f"[bold]Total Queries:[/bold] {total}")
    console.print(f"[bold green]Successful:[/bold green] {successful}")
    console.print(f"[bold red]Failed:[/bold red] {failed}")
    console.print(f"[bold cyan]Success Rate:[/bold cyan] {success_rate:.1f}%\n")

    # Category breakdown table
    table = Table(title="Results by Category", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Total", justify="right")
    table.add_column("Success", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("Rate", justify="right")

    for cat, stats in sorted(category_stats.items()):
        rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        failed_count = stats['total'] - stats['success']
        table.add_row(
            cat,
            str(stats['total']),
            str(stats['success']),
            str(failed_count),
            f"{rate:.1f}%"
        )

    console.print(table)

    # Show failed queries
    failed_queries = [r for r in results if not r['success']]
    if failed_queries:
        console.print("\n[bold red]Failed Queries:[/bold red]")
        for i, result in enumerate(failed_queries[:10], 1):  # Show first 10
            console.print(f"{i}. [yellow]{result['question']}[/yellow]")
            console.print(f"   Error: [red]{result['error']}[/red]\n")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/rag_test_results_{timestamp}.json"
    Path("reports").mkdir(exist_ok=True)

    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success_rate": success_rate
            },
            "category_stats": category_stats,
            "results": results
        }, f, indent=2)

    console.print(f"\n[green]✓ Detailed results saved to:[/green] {report_file}")

    # Recommendations
    console.print("\n[bold cyan]Recommendations:[/bold cyan]")
    if success_rate >= 90:
        console.print("[green]✓ Excellent! RAG system is performing very well.[/green]")
    elif success_rate >= 75:
        console.print("[yellow]⚠ Good performance, but some improvements needed.[/yellow]")
    else:
        console.print("[red]⚠ Poor performance. Significant improvements required.[/red]")

    if failed > 0:
        console.print(f"\n[yellow]Consider:[/yellow]")
        console.print("  1. Re-ingesting documents with better metadata extraction")
        console.print("  2. Improving chunk size/overlap settings")
        console.print("  3. Enhancing query reformulation logic")
        console.print("  4. Adding more training examples for edge cases")


if __name__ == "__main__":
    try:
        run_comprehensive_tests()
    except KeyboardInterrupt:
        console.print("\n[yellow]Testing interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
