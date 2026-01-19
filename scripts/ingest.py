"""
Ingestion script for processing lease documents into the vector database
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table

from config.settings import LEASE_CONTRACTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from src.parsing.docx_parser import parse_all_leases
from src.chunking.chunker import Chunker
from src.metadata.extractor import extract_all_metadata
from src.database.chroma_store import ChromaStore


console = Console()


def run_ingestion(
    lease_dir: str = None,
    clear_existing: bool = False,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
):
    """
    Run the full ingestion pipeline

    Args:
        lease_dir: Directory containing lease documents
        clear_existing: Whether to clear existing data before ingesting
        chunk_size: Size of chunks in tokens
        chunk_overlap: Overlap between chunks in tokens
    """
    lease_dir = lease_dir or str(LEASE_CONTRACTS_DIR)

    console.print("\n[bold blue]Medley Lease Document Ingestion[/bold blue]\n")
    console.print(f"Source directory: {lease_dir}")

    # Initialize store
    store = ChromaStore()

    if clear_existing:
        console.print("[yellow]Clearing existing data...[/yellow]")
        store.delete_all()

    # Step 1: Parse documents
    console.print("\n[bold]Step 1: Parsing DOCX files[/bold]")
    console.print("  Parsing documents...")
    documents = parse_all_leases(lease_dir)

    console.print(f"  Parsed [green]{len(documents)}[/green] documents")

    if not documents:
        console.print("[red]No documents found! Check the lease directory.[/red]")
        return

    # Show parsed documents
    doc_table = Table(title="Parsed Documents")
    doc_table.add_column("Tenant", style="cyan")
    doc_table.add_column("File", style="dim")
    doc_table.add_column("Paragraphs", justify="right")
    doc_table.add_column("Tables", justify="right")

    for doc in documents:
        doc_table.add_row(
            doc.tenant_name,
            doc.file_name[:40] + "..." if len(doc.file_name) > 40 else doc.file_name,
            str(len(doc.paragraphs)),
            str(len(doc.tables))
        )

    console.print(doc_table)

    # Step 2: Extract metadata
    console.print("\n[bold]Step 2: Extracting metadata[/bold]")
    metadata_list = extract_all_metadata(documents)

    meta_table = Table(title="Extracted Metadata")
    meta_table.add_column("Tenant", style="cyan")
    meta_table.add_column("Sq Ft", justify="right")
    meta_table.add_column("Term (Yrs)", justify="right")
    meta_table.add_column("Year 1 Rent", justify="right")

    for meta in metadata_list:
        sqft = f"{meta.premises_sqft:,}" if meta.premises_sqft else "N/A"
        term = str(meta.lease_term_years) if meta.lease_term_years else "N/A"
        rent = f"${meta.year1_annual_rent:,.2f}" if meta.year1_annual_rent else "N/A"

        meta_table.add_row(
            meta.tenant_name[:25],
            sqft,
            term,
            rent
        )

    console.print(meta_table)

    # Step 3: Chunk documents
    console.print("\n[bold]Step 3: Chunking documents[/bold]")
    chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
        console.print(f"  {doc.tenant_name}: [green]{len(chunks)}[/green] chunks")

    console.print(f"\n  Total chunks: [green]{len(all_chunks)}[/green]")

    # Step 4: Add to vector store
    console.print("\n[bold]Step 4: Creating embeddings and storing in ChromaDB[/bold]")

    # Process in batches for progress tracking
    batch_size = 50
    total_batches = (len(all_chunks) + batch_size - 1) // batch_size
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        console.print(f"  Processing batch {batch_num}/{total_batches}...")
        store.add_chunks(batch, show_progress=False)

    # Final stats
    console.print("\n[bold green]Ingestion Complete![/bold green]")

    stats_table = Table(title="Database Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right")

    stats_table.add_row("Total Documents", str(len(documents)))
    stats_table.add_row("Total Chunks", str(store.count()))
    stats_table.add_row("Unique Tenants", str(len(store.get_unique_tenants())))

    console.print(stats_table)

    # List tenants
    console.print("\n[bold]Tenants in database:[/bold]")
    for tenant in store.get_unique_tenants():
        console.print(f"  - {tenant}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest lease documents into vector database")
    parser.add_argument(
        "--dir",
        type=str,
        help="Directory containing lease documents"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before ingesting"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Chunk size in tokens (default: {CHUNK_SIZE})"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Chunk overlap in tokens (default: {CHUNK_OVERLAP})"
    )

    args = parser.parse_args()

    run_ingestion(
        lease_dir=args.dir,
        clear_existing=args.clear,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
