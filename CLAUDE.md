# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Medley Lease Analysis & Management** - Enterprise-grade RAG (Retrieval-Augmented Generation) system for commercial lease portfolio management at the Medley retail development. Features dual database architecture (ChromaDB + SQLite), REST API, advanced analytics, conversation memory, and professional export capabilities.

**Branding:** Toro Development Company themed with dark aesthetic, red accent color (#DC2626), professional serif typography (Merriweather), and full mobile optimization.

## Commands

### Quick Start
```bash
# Interactive setup wizard (recommended for first-time setup)
python scripts/quickstart.py

# Demo setup (2-minute quick test)
python scripts/demo_setup.py
```

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Sync ChromaDB data to SQLite (after ingestion)
python scripts/sync_database.py
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
# Streamlit chat UI with 6 integrated views (recommended)
streamlit run interfaces/chat_app.py

# Dashboard with analytics and visualizations
streamlit run interfaces/dashboard_app.py

# REST API with 20+ endpoints
python api/main.py
# API docs: http://localhost:8000/docs

# Streamlit query UI (single-turn - legacy)
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

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_sql_store.py -v
```

## Architecture

### Dual Database Architecture
```
Documents (DOCX)
       ↓
   Ingestion
       ↓
    ┌──────────────────────┐
    │                      │
ChromaDB              SQLite
(Vector Search)    (Structured Data)
    │                      │
    ↓                      ↓
RAG Engine          Analytics Engine
    │                      │
    └──────────┬───────────┘
               ↓
         REST API
               ↓
    ┌──────────┬──────────┐
    │          │          │
Chat UI   Dashboard   External Apps
```

### Data Pipeline
```
DOCX Files → DocxParser → TextCleaner → Chunker → Embedder → ChromaDB
                ↓                                                  ↓
         MetadataExtractor                               SQLite (structured)
         (tenant, rent, sq ft, term)                    (tenants, leases,
                                                         financial_records, alerts)
```

### Query Pipeline
```
User Question → HybridRanker → AnswerGenerator → Response
                    ↓
    Vector Search (OpenAI embeddings) + BM25 Keyword Search
                    ↓
         Reciprocal Rank Fusion (RRF)
                    ↓
         Conversation Memory (context tracking)
```

### Key Components

**Document Processing:**
- **`src/parsing/docx_parser.py`**: Extracts text, tables, sections from DOCX. Data Sheet extraction handles multi-line patterns where labels and values are on separate lines.
- **`src/parsing/text_cleaner.py`**: Normalizes whitespace, removes artifacts, prepares text for embeddings.
- **`src/parsing/chunker.py`**: Token-based chunking with overlap for better context retrieval.

**Search & Retrieval:**
- **`src/search/hybrid_ranker.py`**: Combines vector similarity (ChromaDB) with BM25 keyword search using RRF. Weights configurable in `config/settings.py`.
- **`src/search/query_engine.py`**: Orchestrates search and LLM. `query()` for single questions, `chat()` for conversations with history.

**Databases:**
- **`src/database/chroma_store.py`**: Persistent ChromaDB storage. Collection name: `medley_leases`. Stores embeddings + metadata (tenant_name, section_name, source_file).
- **`src/database/sql_store.py`**: SQLite database with 5 tables (tenants, leases, financial_records, lease_alerts, query_log). Provides structured data for analytics and reporting.

**Analytics & Intelligence:**
- **`src/analytics/lease_analytics.py`**: Advanced analytics including revenue projections, portfolio health scoring (0-100), risk assessment, tenant benchmarking, and optimization recommendations.
- **`src/memory/conversation_memory.py`**: Session-based conversation tracking with context persistence and follow-up question suggestions.

**LLM Integration:**
- **`src/llm/answer_generator.py`**: Supports OpenAI and Anthropic. Has both single-query (`generate_answer`) and multi-turn chat (`generate_chat_response`) methods.
- **`src/llm/embedder.py`**: OpenAI embeddings with automatic truncation to 8000 tokens.

**Export & Reporting:**
- **`src/export/report_generator.py`**: Professional report generation in PDF (ReportLab), Excel (openpyxl), CSV, and text formats. Includes portfolio summaries, financial analysis, and tenant details.

**REST API:**
- **`api/main.py`**: FastAPI application with 20+ endpoints for queries, analytics, alerts, and database operations. Auto-generated Swagger docs at `/docs`.

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

- **Lease documents:** `Lease Contracts/` (DOCX files)
- **Vector database:** `data/chroma_db/` (ChromaDB collection: `medley_leases`)
- **Structured database:** `data/lease_data.db` (SQLite with 5 tables)
- **Reports:** `reports/` (PDF, Excel, CSV exports)

## UI Features

### Chat Interface (`interfaces/chat_app.py`)
6 integrated tabs:
1. **💬 AI Chat** - Natural language Q&A with conversation memory
2. **📋 Lease Database** - Searchable tenant database with detailed lease info
3. **⚠️ Co-Tenancy Risk** - Risk assessment and concentration analysis
4. **📈 10-Year Projection** - Revenue forecasting and trend analysis
5. **🥧 Tenant Mix** - Category distribution and portfolio composition
6. **📅 Critical Dates** - Lease expiration timeline and alerts

### Branding & Theme

**Toro Development Company Styling:**
- **Colors:** Red accent (#DC2626), dark backgrounds (#0a0a0a, #1a1a1a)
- **Typography:** Merriweather serif for headings, Inter sans-serif for body
- **Mobile Optimization:** Responsive design with touch-friendly targets (44px minimum)
- **Configuration:** `.streamlit/config.toml`

### Dashboard (`interfaces/dashboard_app.py`)
Analytical dashboard with visualizations, metrics, and export capabilities.

## Testing & Documentation

**Documentation Files:**
- **AGENTS.md** - Complete system documentation for AI agents
- **PLUGINS.md** - AI plugin setup and usage guide
- **FEATURES.md** - Detailed feature documentation
- **DEMO.md** - 12-minute demo script
- **QUICKTEST.md** - 2-minute quick test guide
- **IMPLEMENTATION_SUMMARY.md** - Implementation overview

**Testing:**
- 25+ pytest test cases
- Coverage for database operations, analytics, and query engine
- Run with: `pytest --cov=src tests/`

## Windows Notes

Console encoding fixed in `scripts/ingest.py` for Rich library compatibility. OpenAI embeddings truncated to 8000 tokens to avoid API limits.
