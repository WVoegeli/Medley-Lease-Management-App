# Developer Guide

Complete reference for developers working on the Medley Lease Management project.

---

## Quick Start

```bash
# 1. Clone and install
git clone <repository>
cd "Medley Lease Management App"
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Ingest documents
python scripts/ingest.py

# 4. Sync to SQLite
python scripts/sync_database.py

# 5. Run the app
streamlit run interfaces/chat_app.py
```

---

## Project Structure

```
Medley Lease Management App/
├── .claude/                    # Claude Code configuration
│   ├── settings.json          # Enabled plugins
│   └── settings.local.json    # Local permissions
├── .mcp.json                  # MCP server configuration
├── .streamlit/                # Streamlit config
│   └── config.toml            # Theme and settings
├── api/                       # REST API
│   └── main.py                # FastAPI application (20+ endpoints)
├── config/                    # Application config
│   └── settings.py            # Search weights, chunking params
├── data/                      # Runtime data (gitignored)
│   ├── chroma_db/             # Vector database
│   └── lease_data.db          # SQLite database
├── docs/                      # Documentation
│   ├── plans/                 # Design documents
│   ├── DEVELOPMENT.md         # This file
│   ├── USER_GUIDE.md          # End-user guide
│   └── RAG_IMPROVEMENTS.md    # RAG system docs
├── interfaces/                # User interfaces
│   ├── chat_app.py            # Main Streamlit UI (6 tabs)
│   ├── dashboard_app.py       # Analytics dashboard
│   ├── web_app.py             # Legacy single-turn UI
│   └── cli.py                 # Command-line interface
├── Lease Contracts/           # Source DOCX files
├── reports/                   # Generated exports
├── scripts/                   # Automation scripts
│   ├── ingest.py              # Document ingestion
│   ├── sync_database.py       # DB synchronization
│   ├── quickstart.py          # Setup wizard
│   └── demo_setup.py          # Quick demo setup
├── src/                       # Core modules
│   ├── agents/                # Custom agents (planned)
│   ├── analytics/             # Analytics engine
│   ├── chunking/              # Text chunking
│   ├── database/              # ChromaDB + SQLite
│   ├── export/                # Report generation
│   ├── llm/                   # LLM integration
│   ├── memory/                # Conversation memory
│   ├── metadata/              # Metadata extraction
│   ├── parsing/               # Document parsing
│   └── search/                # Hybrid search
├── tests/                     # Test suite
├── CLAUDE.md                  # AI agent instructions
├── AGENTS.md                  # Agent documentation
├── PLUGINS.md                 # MCP/Plugin docs
└── requirements.txt           # Python dependencies
```

---

## Core Modules

### Document Processing

#### `src/parsing/docx_parser.py`

Extracts content from DOCX lease documents.

```python
from src.parsing.docx_parser import DocxParser

parser = DocxParser()
result = parser.parse("Lease Contracts/summit_coffee.docx")

# Result contains:
# - full_text: Complete extracted text
# - sections: Dict of section_name → content
# - tables: List of table data
# - metadata: Document metadata
```

**Key Methods:**
- `parse(file_path)` - Extract all content
- `extract_data_sheet(text)` - Extract structured data from Data Sheet section

#### `src/parsing/text_cleaner.py`

Normalizes and cleans extracted text.

```python
from src.parsing.text_cleaner import TextCleaner

cleaner = TextCleaner()
clean_text = cleaner.clean(raw_text)
```

#### `src/chunking/chunker.py`

Token-based text chunking with overlap.

```python
from src.chunking.chunker import Chunker

chunker = Chunker(chunk_size=1000, chunk_overlap=100)
chunks = chunker.chunk(text, metadata={"tenant": "Summit Coffee"})
```

### Database Layer

#### `src/database/chroma_store.py`

Vector database for semantic search.

```python
from src.database.chroma_store import ChromaStore

store = ChromaStore()

# Add documents
store.add_documents(chunks)

# Search
results = store.search("rent escalation", n_results=5)
```

**Collection:** `medley_leases`
**Location:** `data/chroma_db/`

#### `src/database/sql_store.py`

SQLite for structured data and analytics.

```python
from src.database.sql_store import SQLStore

db = SQLStore()

# Get all tenants
tenants = db.get_all_tenants()

# Get expiring leases
expiring = db.get_expiring_leases(days_ahead=90)

# Add financial record
db.add_financial_record(tenant_id, amount, record_type, date)
```

**Tables:**
- `tenants` - Tenant information
- `leases` - Lease terms and dates
- `financial_records` - Transactions
- `lease_alerts` - Expiration alerts
- `query_log` - Audit trail

**Location:** `data/lease_data.db`

### Search & RAG

#### `src/search/hybrid_ranker.py`

Combines vector and keyword search using Reciprocal Rank Fusion.

```python
from src.search.hybrid_ranker import HybridRanker

ranker = HybridRanker(chroma_store)
results = ranker.search(
    query="What is Summit Coffee's rent?",
    n_results=10
)
```

**Configuration** (`config/settings.py`):
- `VECTOR_WEIGHT`: 0.6 (semantic similarity)
- `BM25_WEIGHT`: 0.4 (keyword matching)
- `RRF_K`: 60 (fusion constant)

#### `src/search/query_engine.py`

Orchestrates search and LLM response generation.

```python
from src.search.query_engine import QueryEngine

engine = QueryEngine()

# Single query
response = engine.query("What is the total rent?")

# Conversational query with memory
response = engine.chat(
    "What about their renewal options?",
    conversation_id="session-123"
)
```

### Analytics

#### `src/analytics/lease_analytics.py`

Advanced portfolio analytics.

```python
from src.analytics.lease_analytics import LeaseAnalytics
from src.database.sql_store import SQLStore

db = SQLStore()
analytics = LeaseAnalytics(db)

# Revenue projection
projections = analytics.project_revenue(months_ahead=12)

# Portfolio health (0-100)
health = analytics.calculate_portfolio_health_score()

# Risk assessment
risks = analytics.assess_portfolio_risk()

# Optimization opportunities
opportunities = analytics.get_optimization_opportunities()

# Tenant comparison
comparison = analytics.compare_tenants(["Summit Coffee", "Medley Books"])
```

### LLM Integration

#### `src/llm/answer_generator.py`

Supports OpenAI and Anthropic.

```python
from src.llm.answer_generator import AnswerGenerator

generator = AnswerGenerator(provider="openai", model="gpt-4o")

# Single answer
answer = generator.generate_answer(question, context_chunks)

# Chat response with history
answer = generator.generate_chat_response(question, context, history)
```

**Environment Variables:**
- `OPENAI_API_KEY` - Required
- `ANTHROPIC_API_KEY` - Optional
- `LLM_PROVIDER` - "openai" or "anthropic"
- `LLM_MODEL` - Model name

#### `src/llm/embedder.py`

OpenAI embeddings with automatic truncation.

```python
from src.llm.embedder import Embedder

embedder = Embedder()
embedding = embedder.embed("Some text to embed")
```

### Export & Reporting

#### `src/export/report_generator.py`

Multi-format report generation.

```python
from src.export.report_generator import ReportGenerator

report_gen = ReportGenerator(db, analytics)

# PDF report
report_gen.export_portfolio_pdf("reports/portfolio.pdf")

# Excel workbook
report_gen.export_portfolio_excel("reports/portfolio.xlsx")

# CSV export
csv_data = report_gen.export_leases_csv(status='active')

# Text summary
text = report_gen.generate_text_report()
```

### Memory

#### `src/memory/conversation_memory.py`

Multi-turn conversation tracking.

```python
from src.memory.conversation_memory import ConversationMemory, ConversationManager

# Single session
memory = ConversationMemory()
memory.add_turn("What is Summit's rent?", "$3,500/month")
context = memory.get_conversation_context()
suggestions = memory.suggest_follow_up_questions()

# Multi-session manager
manager = ConversationManager()
session_id = manager.create_session()
manager.add_turn(session_id, question, answer)
```

---

## REST API

### Running the API

```bash
python api/main.py
# Or
uvicorn api.main:app --reload --port 8000
```

**Documentation:** http://localhost:8000/docs

### Key Endpoints

#### Query
```bash
# Natural language query
POST /api/query
{"question": "What is the total rent?"}

# Chat with memory
POST /api/chat
{"question": "What about renewals?", "conversation_id": "abc123"}
```

#### Leases
```bash
GET /api/leases              # List all
GET /api/leases/{id}         # Get by ID
POST /api/leases             # Create
PUT /api/leases/{id}         # Update
DELETE /api/leases/{id}      # Delete
```

#### Analytics
```bash
GET /api/analytics/summary           # Financial summary
GET /api/analytics/portfolio-health  # Health score
GET /api/analytics/projections       # Revenue projections
POST /api/analytics/compare-tenants  # Tenant comparison
```

#### Alerts
```bash
GET /api/alerts/expiring?days_ahead=90  # Expiring leases
GET /api/alerts/active                   # Active alerts
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific file
pytest tests/test_sql_store.py -v

# Specific test
pytest tests/test_sql_store.py::TestTenantOperations::test_add_tenant -v
```

### Test Structure

```
tests/
├── conftest.py           # Fixtures
├── test_sql_store.py     # Database tests
├── test_analytics.py     # Analytics tests
└── test_query_engine.py  # Search tests
```

### RAG Testing

```bash
# Comprehensive RAG test suite
python scripts/test_rag_thoroughly.py
```

Tests 100+ queries across categories:
- Basic tenant info
- Financial queries
- Date/term queries
- Comparative queries
- Edge cases

---

## AI Development Tools

### Using MCPs

MCPs are configured in `.mcp.json`. Access them through natural language:

```
# Library documentation
"Look up the ChromaDB API for metadata filtering"

# Web research
"Use perplexity to research market rent rates in Dallas"

# Code navigation
"Use serena to find all usages of calculate_portfolio_health_score"

# Git operations
"Show me commits from this week"
```

### Using Skills

Skills are invoked with slash commands:

```bash
# Before new feature
/brainstorming
"I want to add email notifications for lease expirations"

# After brainstorming
/writing-plans

# Execute the plan
/executing-plans

# Debug an issue
/systematic-debugging
"The revenue projection returns negative values"

# Before merge
/verification-before-completion
```

### Development Workflow

1. **New Feature:**
   ```
   /brainstorming → /writing-plans → /executing-plans → /verification-before-completion
   ```

2. **Bug Fix:**
   ```
   /systematic-debugging → Fix → /verification-before-completion
   ```

3. **Code Review:**
   ```
   /code-review (for PR review)
   /requesting-code-review (before merge)
   ```

---

## Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai          # or "anthropic"
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

### Search Tuning

Edit `config/settings.py`:

```python
# Hybrid search weights
VECTOR_WEIGHT = 0.6    # Semantic similarity
BM25_WEIGHT = 0.4      # Keyword matching
RRF_K = 60             # Fusion constant

# Chunking
CHUNK_SIZE = 1000      # Tokens per chunk
CHUNK_OVERLAP = 100    # Overlap between chunks
```

### Streamlit Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#DC2626"        # Red accent
backgroundColor = "#0a0a0a"     # Dark background
secondaryBackgroundColor = "#1a1a1a"
textColor = "#ffffff"
```

---

## Adding New Features

### Adding a New API Endpoint

1. Add route in `api/main.py`:
   ```python
   @app.get("/api/new-endpoint")
   async def new_endpoint():
       return {"result": "data"}
   ```

2. Add tests in `tests/test_api.py`

3. Update API documentation

### Adding a New Analytics Function

1. Add method in `src/analytics/lease_analytics.py`:
   ```python
   def new_analysis(self, params):
       # Implementation
       return results
   ```

2. Add tests in `tests/test_analytics.py`

3. Expose via API if needed

### Adding a New Agent (Future)

See `docs/plans/2025-01-19-documentation-and-agents-design.md` for the agent architecture.

```python
# src/agents/new_agent.py
from src.agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def can_handle(self, message: str) -> float:
        # Return confidence 0-1
        pass

    def execute(self, message: str, context: dict) -> AgentResponse:
        # Implementation
        pass
```

---

## Troubleshooting

### Common Issues

**ChromaDB won't start:**
```bash
# Clear and reingest
python scripts/ingest.py --clear
```

**SQLite schema mismatch:**
```bash
# Clear and resync
python scripts/sync_database.py --clear
```

**Embedding rate limits:**
- Check `EMBEDDING_MODEL` is set to a cost-effective model
- Embedder truncates to 8000 tokens automatically

**Streamlit port in use:**
```bash
streamlit run interfaces/chat_app.py --server.port 8502
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Contributing

1. Use `/brainstorming` before implementing features
2. Write tests for new functionality
3. Run `/verification-before-completion` before PRs
4. Follow existing code patterns
5. Update documentation

---

## Related Documentation

- **CLAUDE.md** - AI assistant instructions
- **AGENTS.md** - Agent capabilities
- **PLUGINS.md** - MCP and plugin reference
- **docs/USER_GUIDE.md** - End-user guide
- **docs/plans/** - Design documents
