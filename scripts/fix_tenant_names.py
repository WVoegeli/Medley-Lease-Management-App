"""
Fix Tenant Name Duplicates and Normalize Tenant Names

This script:
1. Analyzes current tenant names in ChromaDB
2. Creates a mapping of variations to canonical names
3. Re-ingests documents with normalized tenant names
4. Validates the cleanup
"""

import sys
import os
import re
from pathlib import Path

# Fix Windows console encoding for Rich library
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.chroma_store import ChromaStore
from src.parsing.docx_parser import DocxParser
from src.parsing.text_cleaner import TextCleaner
from src.parsing.chunker import Chunker
from src.llm.embedder import Embedder
from src.metadata.extractor import MetadataExtractor
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from collections import defaultdict

console = Console()


# Tenant name mapping: variations → canonical name
TENANT_NAME_MAPPING = {
    "26 Thai": "26 Thai",
    "26 Thai8.3.23": "26 Thai",

    "Body 20": "Body 20",
    "Body20": "Body 20",

    "Cru Wine Bar  Lease": "CRU Food & Wine Bar",
    "CRU Food & Wine Bar": "CRU Food & Wine Bar",

    "Drybar": "Drybar",
    "Drybar Lease -Medley": "Drybar",

    "Five Daughters Bakery": "Five Daughters Bakery",

    "Kontour Medical Spa": "Kontour Medical Spa",
    "Kontour Medical Spa at Medley": "Kontour Medical Spa",

    "Rena's Italian": "Rena's Italian",
    "Rena's Italian Medley": "Rena's Italian",

    "Burdlife": "Burdlife",
    "Burdlife12.8.23": "Burdlife",

    "Summit Coffee": "Summit Coffee",
    "Sephora": "Sephora",
    "Trader Joe's": "Trader Joe's",
    "Playa Bowls": "Playa Bowls",
    "AYA Med Spa": "AYA Med Spa",
    "Clean Your Dirty Face": "Clean Your Dirty Face",
    "Pause Studio": "Pause Studio",
    "Sugarcoat Beauty": "Sugarcoat Beauty",
}


def extract_tenant_from_filename(filename: str) -> str:
    """
    Extract canonical tenant name from filename

    Examples:
        "Five Daughters Bakery - Final Execution Version 8.7.23(4587514.2).docx" → "Five Daughters Bakery"
        "Summit Coffee - Medley -  Toro Properties - Final Execution Version(4588650.1).docx" → "Summit Coffee"
        "26 Thai  (Final Execution Version) 8.3.23(4589461.1).docx" → "26 Thai"
    """
    # Remove file extension
    name = filename.replace(".docx", "")

    # Remove common suffixes
    patterns_to_remove = [
        r" - Final Execution Version.*",
        r" - Executed Lease.*",
        r" - Medley.*",
        r" - Toro.*",
        r" - Lease.*",
        r"\(Final.*\)",
        r"\d{1,2}\.\d{1,2}\.\d{2,4}",  # Dates
        r"\(\d+\.\d+\)",  # Document numbers
        r" at Medley",
    ]

    for pattern in patterns_to_remove:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Handle special cases
    if "Cru Wine Bar" in name or "CRU Food" in name:
        return "CRU Food & Wine Bar"
    if "Kontour" in name:
        return "Kontour Medical Spa"
    if "Rena" in name:
        return "Rena's Italian"

    # Return normalized name
    return name.strip()


def analyze_current_tenants():
    """Analyze current tenant names in ChromaDB"""
    console.print("\n[bold]Analyzing current tenant names...[/bold]\n")

    store = ChromaStore()
    all_results = store.collection.get(include=['metadatas'])

    tenant_counts = defaultdict(int)
    for metadata in all_results['metadatas']:
        if 'tenant_name' in metadata and metadata['tenant_name']:
            tenant_counts[metadata['tenant_name']] += 1

    # Display results
    table = Table(title="Current Tenant Names in Database", show_header=True)
    table.add_column("Tenant Name", style="cyan")
    table.add_column("Chunk Count", justify="right", style="green")

    for tenant, count in sorted(tenant_counts.items()):
        table.add_row(tenant, str(count))

    console.print(table)
    console.print(f"\n[yellow]Total unique tenant names: {len(tenant_counts)}[/yellow]")

    return tenant_counts


def re_ingest_with_normalized_names():
    """Re-ingest all documents with normalized tenant names"""
    console.print("\n[bold]Re-ingesting documents with normalized tenant names...[/bold]\n")

    # Initialize components
    parser = DocxParser()
    cleaner = TextCleaner()
    chunker = Chunker()
    embedder = Embedder()
    metadata_extractor = MetadataExtractor()

    # Get list of lease documents
    lease_dir = Path("Lease Contracts")
    docx_files = list(lease_dir.glob("*.docx"))
    docx_files = [f for f in docx_files if not f.name.startswith("~")]  # Skip temp files

    console.print(f"Found {len(docx_files)} lease documents\n")

    # Clear existing database
    console.print("[yellow]Clearing existing database...[/yellow]")
    store = ChromaStore()
    try:
        store.client.delete_collection(store.collection_name)
    except:
        pass
    store = ChromaStore()  # Recreate
    console.print("[green]✓ Database cleared[/green]\n")

    # Process each document
    all_chunks_data = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Processing documents...", total=len(docx_files))

        for docx_file in docx_files:
            # Extract canonical tenant name from filename
            canonical_tenant = extract_tenant_from_filename(docx_file.name)

            progress.update(task, description=f"[cyan]Processing {canonical_tenant}...")

            try:
                # Parse document
                parsed_doc = parser.parse(str(docx_file))

                # Process each section
                for section in parsed_doc.sections:
                    # Clean text
                    cleaned_text = cleaner.clean(section.content)

                    # Skip very short sections
                    if len(cleaned_text.strip()) < 50:
                        continue

                    # Chunk the text
                    chunks = chunker.chunk(cleaned_text)

                    # Process each chunk
                    for chunk in chunks:
                        # Create metadata
                        metadata = {
                            "tenant_name": canonical_tenant,  # Use canonical name
                            "section_name": section.title or "Unknown",
                            "source_file": docx_file.name
                        }

                        # Extract additional metadata if available
                        try:
                            extracted_meta = metadata_extractor.extract(chunk)
                            if extracted_meta:
                                # Only add non-None values
                                for key, value in extracted_meta.items():
                                    if value is not None and key != 'tenant_name':
                                        metadata[key] = value
                        except:
                            pass

                        all_chunks_data.append({
                            "content": chunk,
                            "metadata": metadata
                        })

                progress.advance(task)

            except Exception as e:
                console.print(f"[red]Error processing {docx_file.name}: {e}[/red]")
                progress.advance(task)

    # Generate embeddings and add to database
    console.print(f"\n[yellow]Generating embeddings for {len(all_chunks_data)} chunks...[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Creating embeddings...", total=len(all_chunks_data))

        batch_size = 50
        for i in range(0, len(all_chunks_data), batch_size):
            batch = all_chunks_data[i:i + batch_size]

            # Generate embeddings
            embeddings = embedder.embed_batch([c["content"] for c in batch])

            # Add to database
            store.add_batch(
                texts=[c["content"] for c in batch],
                embeddings=embeddings,
                metadatas=[c["metadata"] for c in batch]
            )

            progress.update(task, advance=len(batch))

    console.print("[green]✓ Re-ingestion complete![/green]")


def validate_cleanup():
    """Validate that tenant names are now clean"""
    console.print("\n[bold]Validating cleanup...[/bold]\n")

    store = ChromaStore()
    all_results = store.collection.get(include=['metadatas'])

    tenant_counts = defaultdict(int)
    for metadata in all_results['metadatas']:
        if 'tenant_name' in metadata and metadata['tenant_name']:
            tenant_counts[metadata['tenant_name']] += 1

    # Display results
    table = Table(title="Cleaned Tenant Names", show_header=True)
    table.add_column("Tenant Name", style="cyan")
    table.add_column("Chunk Count", justify="right", style="green")

    for tenant, count in sorted(tenant_counts.items()):
        table.add_row(tenant, str(count))

    console.print(table)
    console.print(f"\n[green]✓ Total unique tenant names: {len(tenant_counts)}[/green]")

    # Check for duplicates
    normalized_lower = {t.lower(): t for t in tenant_counts.keys()}
    if len(normalized_lower) < len(tenant_counts):
        console.print("[yellow]⚠ Warning: Some case-only duplicates may still exist[/yellow]")
    else:
        console.print("[green]✓ No duplicate tenant names detected![/green]")


def main():
    console.clear()
    console.print("\n[bold cyan]===========================================================[/bold cyan]")
    console.print("[bold cyan]       TENANT NAME NORMALIZATION & CLEANUP              [/bold cyan]")
    console.print("[bold cyan]===========================================================[/bold cyan]\n")

    # Step 1: Analyze current state
    current_tenants = analyze_current_tenants()

    # Step 2: Confirm re-ingestion
    console.print("\n[yellow]This will clear the database and re-ingest all documents.[/yellow]")
    response = input("\nProceed with re-ingestion? (y/n): ").lower().strip()

    if response != 'y':
        console.print("\n[yellow]Cancelled[/yellow]")
        return

    # Step 3: Re-ingest with normalized names
    re_ingest_with_normalized_names()

    # Step 4: Validate
    validate_cleanup()

    console.print("\n[bold green]✓ Tenant name normalization complete![/bold green]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
