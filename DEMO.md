# Demo Setup Guide - Medley Lease Analysis & Management

Quick guide for testing the app without full setup.

## 🎯 Try the Live Demo (Easiest!)

**Streamlit Cloud (Always Available):**
- URL: [Ask the team for the Streamlit Cloud URL]
- Password: `Medley2026`

Just visit the URL and start querying leases!

---

## 💻 Run Locally (5 Minutes)

### Prerequisites
- Python 3.11+
- Git

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/WVoegeli/Medley-Lease-Management-App.git
cd Medley-Lease-Management-App

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment (use demo keys)
cp .env.example .env
# Edit .env and add your OpenAI API key (required for demo)

# 6. Run the app
streamlit run interfaces/chat_app.py
```

The app will open in your browser at `http://localhost:8501`

### Demo Features to Try

**Natural Language Queries:**
- "What is Summit Coffee's monthly rent?"
- "Which leases expire in 2025?"
- "Show me all cafe tenants"
- "What are the renewal terms for Medley Books?"

**Dashboard Features:**
- View portfolio financial summary
- See expiring leases timeline
- Compare tenant rates
- Generate analytics reports

**Advanced Features:**
- Revenue projections
- Portfolio health score
- Risk assessment
- Tenant benchmarking

---

## 🔑 Demo Data

The repository includes sample lease data for the following tenants:
- Summit Coffee
- Medley Books
- Fitness First
- The Yoga Studio
- Tech Startup Hub
- Artisan Bakery

**Note:** Full functionality requires running the ingestion script:
```bash
python scripts/quickstart.py
```

---

## 🌐 Create Your Own Public Demo URL

If you want to share the app running from your machine:

### Install ngrok (one-time)
```bash
# Windows (winget)
winget install ngrok.ngrok

# Or download from: https://ngrok.com/download
```

### Run with public URL
```bash
# Windows PowerShell
.\run_public.ps1

# Windows Command Prompt
run_public.bat
```

You'll get a public URL like: `https://abc123.ngrok.app`

Share this URL with anyone - they can access your local app!

**Password:** `Medley2026`

---

## 📊 API Demo (Optional)

For developers who want to test the REST API:

### 1. Start the API
```bash
python api/main.py
```

### 2. Access API Documentation
Visit: http://localhost:8000/docs

### 3. Try Sample Queries

**Get Financial Summary:**
```bash
curl http://localhost:8000/api/analytics/summary
```

**Natural Language Query:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total monthly revenue?"}'
```

**Get Expiring Leases:**
```bash
curl http://localhost:8000/api/alerts/expiring?days_ahead=90
```

**Portfolio Health:**
```bash
curl http://localhost:8000/api/analytics/portfolio-health
```

---

## 🎓 Demo Script

Follow this script for a comprehensive demo:

### 1. Financial Overview (2 min)
- Open Dashboard tab
- Show monthly/annual revenue
- Display occupancy stats
- Highlight top tenants

### 2. Natural Language Queries (3 min)
- Query: "What is Summit Coffee's rent?"
- Query: "When does their lease expire?"
- Query: "Show me all renewal options"
- Demonstrate conversation memory (follow-up questions)

### 3. Advanced Analytics (3 min)
- Show revenue projection chart
- Display portfolio health score
- Demonstrate risk assessment
- Show optimization opportunities

### 4. Expiration Management (2 min)
- Display expiring leases timeline
- Show automated alerts
- Demonstrate tenant comparison

### 5. Export & Reporting (2 min)
- Generate PDF report (if set up)
- Export to Excel
- Show CSV download

**Total Demo Time:** ~12 minutes

---

## 🐛 Troubleshooting

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"No API key found"**
- Make sure .env file exists
- Add your `OPENAI_API_KEY` to .env

**"No lease data"**
- Run: `python scripts/quickstart.py`
- Or: `python scripts/ingest.py`

**Port already in use**
- Change port: `streamlit run interfaces/chat_app.py --server.port 8502`

**Streamlit won't start**
- Check Python version: `python --version` (need 3.11+)
- Reinstall Streamlit: `pip install --upgrade streamlit`

---

## 📞 Support

- **Documentation:** See README.md, FEATURES.md, AGENTS.md
- **Quick Start:** Run `python scripts/quickstart.py`
- **Issues:** GitHub Issues
- **API Docs:** http://localhost:8000/docs (when API running)

---

## 🎉 What to Highlight in Demo

**Key Differentiators:**
1. **Hybrid Search** - Vector + keyword for best results
2. **Dual Database** - Vector (semantic) + SQL (analytics)
3. **Advanced Analytics** - Revenue forecasts, risk scoring
4. **Conversation Memory** - Context-aware follow-ups
5. **REST API** - Full programmatic access
6. **Professional Reports** - PDF, Excel exports

**Wow Factors:**
- Ask follow-up questions without context (conversation memory)
- Generate 12-month revenue projection
- Calculate portfolio health score (0-100)
- Identify optimization opportunities automatically
- Export professional PDF report

---

**Happy testing! 🚀**
