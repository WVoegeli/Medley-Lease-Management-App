# Medley Lease Analysis & Management

Enterprise-grade RAG (Retrieval-Augmented Generation) system for commercial lease portfolio management at the Medley retail development.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.98+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **🔍 Intelligent Document Analysis** - Parse DOCX lease documents with NLP-powered extraction
- **🔎 Hybrid Search** - Vector embeddings + BM25 keyword search with Reciprocal Rank Fusion
- **💾 Dual Database System** - ChromaDB (vector) + SQLite (structured analytics)
- **📊 Advanced Analytics** - Revenue projections, portfolio health scoring, risk assessment
- **⏰ Automated Alerts** - Lease expiration tracking (90/60/30 day notices)
- **🚀 REST API** - FastAPI backend with 20+ endpoints
- **💬 Conversation Memory** - Context-aware multi-turn queries
- **📄 Professional Reporting** - PDF, Excel, CSV exports
- **✅ Comprehensive Testing** - Pytest suite with 25+ tests

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Add your API keys to .env
# Required: OPENAI_API_KEY
# Optional: ANTHROPIC_API_KEY
```

### 3. Run Quick Start Setup
```bash
python scripts/quickstart.py
```

This interactive wizard will:
- Verify dependencies
- Ingest lease documents
- Sync databases
- Run tests
- Show next steps

### 4. Start Using

**Chat Interface:**
```bash
streamlit run interfaces/chat_app.py
```

**REST API:**
```bash
python api/main.py
# API docs: http://localhost:8000/docs
```

**Dashboard:**
```bash
streamlit run interfaces/dashboard_app.py
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[AGENTS.md](AGENTS.md)** | Complete system documentation for AI agents |
| **[PLUGINS.md](PLUGINS.md)** | Recommended AI plugins and setup |
| **[FEATURES.md](FEATURES.md)** | Detailed feature documentation |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Implementation overview |
| **API Docs** | http://localhost:8000/docs (after starting API) |

---

## 🏗️ Architecture

### Dual Database System

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

### Key Components

- **Document Processing**: DOCX parsing, text cleaning, chunking, embedding
- **Search**: Hybrid ranking (vector + BM25), query engine
- **Database**: ChromaDB (vector), SQLite (structured)
- **Analytics**: Revenue forecasting, risk assessment, portfolio health
- **Memory**: Conversation tracking, context persistence
- **Export**: PDF, Excel, CSV report generation
- **API**: FastAPI with 20+ endpoints

---

## 🛠️ Tech Stack

**Core:**
- Python 3.11+
- FastAPI (REST API)
- Streamlit (UI)
- ChromaDB (Vector DB)
- SQLite (Structured DB)

**AI/ML:**
- OpenAI (Embeddings & LLM)
- Anthropic Claude (Optional LLM)
- LangChain patterns
- RAG architecture

**Testing:**
- pytest
- pytest-asyncio

**Reporting:**
- ReportLab (PDF)
- pandas + openpyxl (Excel)

---

## 📖 Usage Examples

### Natural Language Queries
```python
from src.search.query_engine import QueryEngine

engine = QueryEngine()
result = engine.query("What is Summit Coffee's monthly rent?")
print(result['answer'])
# "Summit Coffee pays $3,500 per month"
```

### Financial Analytics
```python
from src.database.sql_store import SQLStore
from src.analytics.lease_analytics import LeaseAnalytics

db = SQLStore()
analytics = LeaseAnalytics(db)

# Revenue projections
projections = analytics.project_revenue(months_ahead=12)
print(f"Trend: {projections['trend']}")

# Portfolio health
health = analytics.calculate_portfolio_health_score()
print(f"Score: {health['health_score']}/100")
```

### REST API
```bash
# Natural language query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which leases expire in 2025?"}'

# Get portfolio health
curl http://localhost:8000/api/analytics/portfolio-health

# Get expiring leases
curl http://localhost:8000/api/alerts/expiring?days_ahead=90
```

### Generate Reports
```python
from src.export.report_generator import ReportGenerator

report = ReportGenerator(db, analytics)

# PDF report
report.export_portfolio_pdf("reports/Q1_2025_Portfolio.pdf")

# Excel workbook
report.export_portfolio_excel("reports/lease_data.xlsx")
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_sql_store.py -v

# Specific test
pytest tests/test_sql_store.py::TestTenantOperations::test_add_tenant
```

---

## 🤖 AI Agents & Plugins

This project uses specialized AI agents for enhanced development productivity.

**Quick Install:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin marketplace add wshobson/agents

/plugin install superpowers@superpowers-marketplace
/plugin install python-development@wshobson/agents
/plugin install llm-applications@wshobson/agents
```

**Full Setup:** See [PLUGINS.md](PLUGINS.md)

---

## 📊 Project Stats

- **Lines of Code**: ~4,500+ lines
- **Modules**: 13 modules
- **REST Endpoints**: 20+
- **Database Tables**: 5 tables (SQLite)
- **Test Cases**: 25+ tests
- **Export Formats**: 4 formats (PDF, Excel, CSV, Text)
- **Documentation Pages**: 5 comprehensive docs

---

## 🔧 Development

### Project Structure

```
medley-lease-management/
├── src/
│   ├── database/         # ChromaDB + SQLite
│   ├── analytics/        # Business intelligence
│   ├── memory/           # Conversation tracking
│   ├── export/           # Report generation
│   ├── parsing/          # Document processing
│   ├── search/           # RAG + hybrid search
│   ├── llm/              # LLM integration
│   └── metadata/         # Structured extraction
├── api/                  # FastAPI application
├── interfaces/           # Streamlit UIs
├── scripts/              # Automation scripts
├── tests/                # Pytest test suite
├── config/               # Configuration
└── Lease Contracts/      # Source documents
```

### Adding New Features

1. **Brainstorm first** (if using Superpowers plugin):
   ```bash
   /superpowers:brainstorm
   ```

2. **Create implementation plan**:
   ```bash
   /superpowers:write-plan
   ```

3. **Write tests** (TDD approach)

4. **Implement feature**

5. **Run comprehensive review**:
   ```bash
   /comprehensive-review
   ```

6. **Commit and push**

---

## 🚢 Deployment

### Streamlit Cloud

The app is deployed on Streamlit Cloud:
1. Push to GitHub
2. Streamlit Cloud auto-deploys
3. Configure secrets in Streamlit dashboard

### Local Production

```bash
# Run API with uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Run Streamlit with custom config
streamlit run interfaces/chat_app.py --server.port 8501
```

---

## 🤝 Contributing

1. Install recommended plugins (see [PLUGINS.md](PLUGINS.md))
2. Review [AGENTS.md](AGENTS.md) for project context
3. Run quick start: `python scripts/quickstart.py`
4. Create feature branch
5. Write tests (TDD)
6. Submit PR with comprehensive review

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Built with Claude Code AI development tools
- Uses Superpowers development methodology
- Leverages wshobson/agents AI agent library

---

## 📞 Support

- **Documentation**: See docs folder and markdown files
- **API Reference**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Quick Start**: `python scripts/quickstart.py`

---

**Made with ⚡ by the Medley team**

*Transform your lease management with AI-powered intelligence.*
