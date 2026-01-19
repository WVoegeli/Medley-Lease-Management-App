# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.
Compatible with Claude Code, Cursor, Windsurf, Copilot, and other AI development tools.

## Project Overview

**Medley Lease Analysis & Management** - Enterprise-grade RAG (Retrieval-Augmented Generation) system for commercial lease portfolio management at the Medley retail development.

### Core Capabilities

- **Intelligent Document Analysis**: Parse DOCX lease documents with NLP-powered extraction
- **Hybrid Search**: Vector embeddings + BM25 keyword search with Reciprocal Rank Fusion
- **Structured Database**: SQLite database for lease metadata, financials, and analytics
- **Financial Analytics**: Revenue projections, portfolio health scoring, risk assessment
- **Expiration Tracking**: Automated alerts for lease expirations (90/60/30 day notices)
- **REST API**: FastAPI backend for programmatic access
- **Conversation Memory**: Context-aware multi-turn queries with conversation history
- **Export & Reporting**: PDF reports, Excel workbooks, CSV exports
- **Testing Infrastructure**: Comprehensive pytest suite for reliability

## Commands

### Setup
```bash
pip install -r requirements.txt
```

### Ingest Documents
```bash
# Initial ingestion to vector database
python scripts/ingest.py

# Re-ingest with fresh database
python scripts/ingest.py --clear

# Custom chunk settings
python scripts/ingest.py --chunk-size 1000 --chunk-overlap 100
```

### Sync Structured Database
```bash
# Sync lease metadata to SQL database for analytics
python scripts/sync_database.py

# Clear and re-sync
python scripts/sync_database.py --clear
```

### Run REST API
```bash
# Start FastAPI server (port 8000)
python api/main.py

# Or with uvicorn directly
uvicorn api.main:app --reload --port 8000

# API documentation available at:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_sql_store.py -v

# Run specific test
pytest tests/test_sql_store.py::TestTenantOperations::test_add_tenant -v
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

#### Document Processing
- **`src/parsing/docx_parser.py`**: Extracts text, tables, sections from DOCX. Data Sheet extraction handles multi-line patterns where labels and values are on separate lines.
- **`src/preprocessing/text_cleaner.py`**: Cleans and normalizes extracted text
- **`src/chunking/chunker.py`**: Token-based text chunking with overlap
- **`src/vectorization/embedder.py`**: OpenAI embedding generation
- **`src/metadata/extractor.py`**: Extracts structured metadata (tenant, rent, dates)

#### Search & Query
- **`src/search/hybrid_ranker.py`**: Combines vector similarity (ChromaDB) with BM25 keyword search using RRF. Weights configurable in `config/settings.py`.
- **`src/search/query_engine.py`**: Orchestrates search and LLM. `query()` for single questions, `chat()` for conversations with history.
- **`src/llm/answer_generator.py`**: Supports OpenAI and Anthropic. Has both single-query (`generate_answer`) and multi-turn chat (`generate_chat_response`) methods.

#### Database Layer
- **`src/database/chroma_store.py`**: Persistent ChromaDB vector storage. Collection name: `medley_leases`. Stores embeddings + metadata (tenant_name, section_name, source_file).
- **`src/database/sql_store.py`**: SQLite database for structured data. Tables: `tenants`, `leases`, `financial_records`, `lease_alerts`, `query_log`.

#### Analytics & Intelligence
- **`src/analytics/lease_analytics.py`**: Advanced analytics engine with:
  - `project_revenue()` - Revenue forecasting considering expirations
  - `compare_tenants()` - Multi-tenant comparative analysis
  - `assess_portfolio_risk()` - Risk scoring and identification
  - `get_optimization_opportunities()` - Below-market rent detection
  - `calculate_portfolio_health_score()` - Overall health (0-100)
  - `analyze_expiration_timeline()` - Quarterly expiration clustering

#### Memory & Context
- **`src/memory/conversation_memory.py`**: Multi-turn conversation tracking with:
  - `ConversationMemory` - Session-based conversation history
  - `ConversationManager` - Multi-session management
  - Context-aware follow-up suggestions
  - Topic and tenant context persistence

#### Export & Reporting
- **`src/export/report_generator.py`**: Report generation in multiple formats:
  - `export_leases_csv()` - CSV export of lease data
  - `export_portfolio_excel()` - Multi-sheet Excel workbooks
  - `export_portfolio_pdf()` - Comprehensive PDF reports with tables and analytics
  - `generate_text_report()` - Plain text summaries

#### REST API
- **`api/main.py`**: FastAPI application with endpoints:
  - `/api/query` - Natural language RAG queries
  - `/api/leases/*` - Lease CRUD operations
  - `/api/tenants/*` - Tenant management
  - `/api/analytics/*` - Financial analytics and portfolio insights
  - `/api/alerts/*` - Expiration alerts and notifications

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
- Vector database: `data/chroma_db/` (ChromaDB embeddings)
- Structured database: `data/leases.db` (SQLite for analytics)
- Test files: `tests/` (pytest test suite)
- API layer: `api/` (FastAPI application)

## New Features & Usage

### Financial Analytics

```python
from src.database.sql_store import SQLStore
from src.analytics.lease_analytics import LeaseAnalytics

db = SQLStore()
analytics = LeaseAnalytics(db)

# Revenue projections
projections = analytics.project_revenue(months_ahead=12)
print(f"Trend: {projections['trend']}")
print(f"Revenue at risk: ${projections['revenue_at_risk']:,.2f}")

# Portfolio health score
health = analytics.calculate_portfolio_health_score()
print(f"Health Score: {health['health_score']}/100 ({health['health_status']})")
for rec in health['recommendations']:
    print(f"- {rec}")

# Risk assessment
risk = analytics.assess_portfolio_risk()
print(f"Risk Level: {risk['risk_level']}")
for r in risk['risks']:
    print(f"[{r['severity']}] {r['description']}")
```

### Expiration Tracking

```python
# Get leases expiring soon
expiring = db.get_expiring_leases(days_ahead=90)
for lease in expiring:
    print(f"{lease['tenant_name']}: {lease['days_until_expiration']} days")

# Get active alerts
alerts = db.get_active_alerts(days_ahead=30)
for alert in alerts:
    print(f"{alert['tenant_name']}: {alert['message']}")
```

### Conversation Memory

```python
from src.memory.conversation_memory import ConversationMemory

memory = ConversationMemory()

# Add conversation turns
memory.add_turn("What is Summit Coffee's rent?", "Summit Coffee pays $3,500/month")
memory.add_turn("When does their lease expire?", "December 31, 2025")

# Get context for next query
context = memory.get_conversation_context()

# Get smart follow-up suggestions
suggestions = memory.suggest_follow_up_questions()
```

### Export Reports

```python
from src.export.report_generator import ReportGenerator

report_gen = ReportGenerator(db, analytics)

# Export to PDF
report_gen.export_portfolio_pdf("reports/portfolio_report.pdf")

# Export to Excel
report_gen.export_portfolio_excel("reports/portfolio_data.xlsx")

# Export to CSV
csv_data = report_gen.export_leases_csv(status='active')
```

### REST API Examples

```bash
# Natural language query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total monthly revenue?"}'

# Get financial summary
curl http://localhost:8000/api/analytics/summary

# Get portfolio health
curl http://localhost:8000/api/analytics/portfolio-health

# Get expiring leases
curl http://localhost:8000/api/alerts/expiring?days_ahead=90

# Compare tenants
curl -X POST http://localhost:8000/api/analytics/compare-tenants \
  -H "Content-Type: application/json" \
  -d '["Summit Coffee", "Medley Books", "Fitness First"]'
```

### Theme & Dark Mode

Streamlit theme configuration (`.streamlit/config.toml`):
- **Light theme** (default) - Configured in `config.toml`
- **Dark theme** - Users can toggle in app: Click ⋮ (top right) → Settings → Theme
- **Permanent dark mode** - Use `config_dark.toml` as reference or uncomment dark theme lines in `config.toml`

## Windows Notes

Console encoding fixed in `scripts/ingest.py` for Rich library compatibility. OpenAI embeddings truncated to 8000 tokens to avoid API limits.
