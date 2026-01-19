# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG (Retrieval-Augmented Generation) system for querying commercial lease agreements at the Medley retail development. Parses DOCX lease documents, creates embeddings, and enables natural language Q&A with hybrid search.

## Commands

### Setup
```bash
pip install -r requirements.txt
```

### Ingest Documents
```bash
# Initial ingestion
python scripts/ingest.py

# Re-ingest with fresh database
python scripts/ingest.py --clear

# Custom chunk settings
python scripts/ingest.py --chunk-size 1000 --chunk-overlap 100
```

### Run Interfaces
```bash
# Streamlit chat UI (recommended)
streamlit run interfaces/chat_app.py

# Streamlit query UI (single-turn)
streamlit run interfaces/web_app.py

# CLI interactive mode
python interfaces/cli.py

# CLI chat mode with conversation history
python interfaces/cli.py --chat

# CLI single query
python interfaces/cli.py "What is Summit Coffee's rent?"

# CLI with tenant filter
python interfaces/cli.py --tenant "Summit Coffee" "What are the renewal options?"
```

## Architecture

### Data Pipeline
```
DOCX Files → DocxParser → TextCleaner → Chunker → Embedder → ChromaDB
                ↓
         MetadataExtractor (tenant name, rent, sq ft, term)
```

### Query Pipeline
```
User Question → HybridRanker → AnswerGenerator → Response
                    ↓
    Vector Search (OpenAI embeddings) + BM25 Keyword Search
                    ↓
         Reciprocal Rank Fusion (RRF)
```

### Key Components

- **`src/parsing/docx_parser.py`**: Extracts text, tables, sections from DOCX. Data Sheet extraction handles multi-line patterns where labels and values are on separate lines.

- **`src/search/hybrid_ranker.py`**: Combines vector similarity (ChromaDB) with BM25 keyword search using RRF. Weights configurable in `config/settings.py`.

- **`src/database/chroma_store.py`**: Persistent ChromaDB storage. Collection name: `medley_leases`. Stores embeddings + metadata (tenant_name, section_name, source_file).

- **`src/llm/answer_generator.py`**: Supports OpenAI and Anthropic. Has both single-query (`generate_answer`) and multi-turn chat (`generate_chat_response`) methods.

- **`src/search/query_engine.py`**: Orchestrates search and LLM. `query()` for single questions, `chat()` for conversations with history.

### Configuration

Environment variables (`.env`):
- `OPENAI_API_KEY` - Required for embeddings
- `ANTHROPIC_API_KEY` - Optional, for Anthropic LLM
- `LLM_PROVIDER` - "openai" or "anthropic" (default: openai)
- `LLM_MODEL` - Model name (default: gpt-4o)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)

Search tuning (`config/settings.py`):
- `VECTOR_WEIGHT` / `BM25_WEIGHT` - Hybrid search weights (0.6/0.4)
- `RRF_K` - RRF constant (60)
- `CHUNK_SIZE` / `CHUNK_OVERLAP` - Token-based chunking (1000/100)

### Data Location

- Lease documents: `Lease Contracts/` (DOCX files)
- Vector database: `data/chroma_db/`

## Windows Notes

Console encoding fixed in `scripts/ingest.py` for Rich library compatibility. OpenAI embeddings truncated to 8000 tokens to avoid API limits.
