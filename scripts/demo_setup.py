"""
Quick Demo Setup Script

Sets up a minimal demo environment in under 2 minutes.
Skips full ingestion and uses sample data for immediate testing.
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    console.clear()

    # Banner
    console.print("""
    ╔══════════════════════════════════════════════════════╗
    ║   MEDLEY LEASE ANALYSIS & MANAGEMENT                ║
    ║         QUICK DEMO SETUP                             ║
    ╚══════════════════════════════════════════════════════╝
    """, style="bold cyan")

    console.print("\n[bold]Setting up demo environment...[/bold]\n")

    # Check for .env
    if not Path('.env').exists():
        console.print("[yellow]⚠ No .env file found[/yellow]")
        console.print("\n[cyan]Quick fix:[/cyan]")
        console.print("1. Copy .env.example to .env")
        console.print("2. Add your OPENAI_API_KEY")
        console.print("\nOr run with demo mode (limited functionality):\n")

        create_demo_env = input("Create demo .env file now? (y/n): ").lower().strip()

        if create_demo_env == 'y':
            with open('.env.example', 'r') as f:
                content = f.read()

            api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()

            if api_key:
                content = content.replace('sk-your-openai-api-key-here', api_key)

            with open('.env', 'w') as f:
                f.write(content)

            console.print("[green]✓ Created .env file[/green]")
        else:
            console.print("\n[yellow]Continuing without .env (some features will be limited)[/yellow]")

    # Success panel
    panel = Panel(
        """[bold green]✓ Demo Setup Complete![/bold green]

[cyan]Your Medley Lease Analysis & Management demo is ready![/cyan]

[bold]Start the demo:[/bold]

[yellow]streamlit run interfaces/chat_app.py[/yellow]

The app will open in your browser at: http://localhost:8501

[bold]Try these demo queries:[/bold]
• "What is Summit Coffee's monthly rent?"
• "Which leases expire in 2025?"
• "Show me the portfolio financial summary"
• "Compare rent rates across all tenants"

[bold]Dashboard Features:[/bold]
• Financial Overview - Monthly/annual revenue
• Expiring Leases - Timeline and alerts
• Analytics - Portfolio health, risk assessment
• Export - Generate PDF/Excel reports

[bold]API Demo:[/bold]
Start API: [yellow]python api/main.py[/yellow]
API Docs: http://localhost:8000/docs

[bold]Full Setup (optional):[/bold]
For complete features: [yellow]python scripts/quickstart.py[/yellow]
        """,
        title="🎉 Demo Ready",
        border_style="green"
    )

    console.print(panel)

    # Offer to start app
    console.print("\n")
    start_now = input("Start the app now? (y/n): ").lower().strip()

    if start_now == 'y':
        console.print("\n[cyan]Starting Streamlit...[/cyan]\n")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")

        try:
            subprocess.run(
                ["streamlit", "run", "interfaces/chat_app.py"],
                check=True
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo stopped[/yellow]")
        except FileNotFoundError:
            console.print("\n[red]Streamlit not found. Install with:[/red]")
            console.print("[yellow]pip install -r requirements.txt[/yellow]")
    else:
        console.print("\n[cyan]Run when ready:[/cyan] [yellow]streamlit run interfaces/chat_app.py[/yellow]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
