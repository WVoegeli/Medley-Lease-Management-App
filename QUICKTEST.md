# Quick Test - 2 Minute Setup

The absolute fastest way to test the Medley Lease Analysis & Management app.

---

## 🌐 Option 1: Live Demo (0 minutes - Instant!)

**Visit the deployed app:**

### Streamlit Cloud (Recommended)
- **URL:** [Contact team for Streamlit Cloud URL]
- **Password:** `Medley2026`

**That's it!** Start querying leases immediately.

### Try These Queries:
- "What is Summit Coffee's monthly rent?"
- "Which leases expire in 2025?"
- "Show me portfolio financial summary"

---

## 💻 Option 2: Run Locally (2 minutes)

### Quick Commands

```bash
# 1. Clone & enter directory
git clone https://github.com/WVoegeli/Medley-Lease-Management-App.git
cd Medley-Lease-Management-App

# 2. Install (one command)
pip install streamlit python-dotenv openai anthropic chromadb

# 3. Run demo setup
python scripts/demo_setup.py

# 4. Start app (opens in browser)
streamlit run interfaces/chat_app.py
```

**Done!** App opens at http://localhost:8501

---

## 🚀 Option 3: Share Your Local App (3 minutes)

Want to share your local instance with others?

### Install ngrok (one-time):
```bash
# Windows
winget install ngrok.ngrok

# Mac
brew install ngrok

# Or download: https://ngrok.com/download
```

### Run with public URL:
```bash
# Windows
.\run_public.ps1

# Mac/Linux
chmod +x run_public.sh && ./run_public.sh
```

**Share the ngrok URL** that appears - anyone can access your app!

**Password:** `Medley2026`

---

## ⚡ Super Quick Test (1 minute - API only)

Test the REST API without UI:

```bash
# Install minimal deps
pip install fastapi uvicorn python-dotenv

# Copy environment template
cp .env.example .env

# Start API
python api/main.py
```

Visit: **http://localhost:8000/docs**

Try the interactive API documentation!

---

## 🎯 What to Test

### Basic Queries (Chat Interface)
1. "What is the total monthly revenue?"
2. "Show me all cafe tenants"
3. "Which leases expire this year?"
4. Ask follow-up questions (conversation memory)

### Dashboard Features
1. Financial Overview tab
2. Expiring Leases tab
3. Analytics tab (portfolio health)
4. Export reports

### Advanced Analytics (API)
1. `/api/analytics/summary` - Financial summary
2. `/api/analytics/portfolio-health` - Health score
3. `/api/analytics/risk-assessment` - Risk analysis
4. `/api/alerts/expiring` - Expiring leases

---

## 🐛 Troubleshooting

**"No module named 'streamlit'"**
```bash
pip install -r requirements.txt
```

**"OPENAI_API_KEY not found"**
- Create `.env` file from `.env.example`
- Add your OpenAI API key

**"Port 8501 already in use"**
```bash
streamlit run interfaces/chat_app.py --server.port 8502
```

**Need help?**
- Full setup: `python scripts/quickstart.py`
- Documentation: See README.md
- Demo guide: See DEMO.md

---

## 📊 For a Full Demo Presentation

See **[DEMO.md](DEMO.md)** for:
- Complete demo script (12 minutes)
- Feature highlights
- Sample queries
- Troubleshooting guide

---

## 🎉 Key Features to Highlight

✅ **Hybrid Search** - Vector + keyword for best accuracy
✅ **Conversation Memory** - Ask follow-ups without repeating context
✅ **Advanced Analytics** - Revenue forecasts, risk scoring
✅ **REST API** - 20+ endpoints for integrations
✅ **Professional Reports** - PDF, Excel, CSV exports
✅ **Real-time Alerts** - Lease expiration tracking

---

**Questions?** See full documentation in README.md

**Ready for production?** Run `python scripts/quickstart.py` for complete setup.
