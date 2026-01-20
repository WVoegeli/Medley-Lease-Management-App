# User Guide

Welcome to Medley Lease Analysis & Management. This guide helps property managers and team members get the most out of the system.

---

## Getting Started

### Launching the Application

```bash
streamlit run interfaces/chat_app.py
```

Open your browser to http://localhost:8501

### Main Interface

The chat interface has 6 tabs:

| Tab | Purpose |
|-----|---------|
| **AI Chat** | Ask questions in natural language |
| **Lease Database** | Browse and search all tenants |
| **Co-Tenancy Risk** | View risk assessments |
| **10-Year Projection** | Revenue forecasts and trends |
| **Tenant Mix** | Portfolio composition analysis |
| **Critical Dates** | Lease expirations and deadlines |

---

## AI Chat

The AI Chat is your primary interface for asking questions about leases.

### What You Can Ask

#### Tenant Information
```
"What is Summit Coffee's rent?"
"When does Medley Books' lease expire?"
"What are the renewal options for Fitness First?"
"Show me all tenant contact information"
```

#### Financial Queries
```
"What is the total monthly rent?"
"Which tenant pays the highest rent per square foot?"
"What's the average rent in the Food & Beverage category?"
"Compare Summit Coffee and Medley Books financially"
```

#### Lease Terms
```
"What are the co-tenancy clauses?"
"Which leases have percentage rent?"
"What are the CAM charges for retail tenants?"
"Show me all exclusivity clauses"
```

#### Dates and Deadlines
```
"Which leases expire this year?"
"What renewal notices are due in the next 90 days?"
"When is the next rent escalation for Summit Coffee?"
```

### Conversation Memory

The chat remembers context, so you can ask follow-up questions:

```
You: "What is Summit Coffee's rent?"
AI: "Summit Coffee pays $3,500 per month ($42/PSF)..."

You: "What about their renewal options?"
AI: "Summit Coffee has two 5-year renewal options..."

You: "When do they need to notify us?"
AI: "They must provide 180 days written notice..."
```

### Tips for Better Answers

1. **Be specific** - "What is Summit Coffee's base rent?" works better than "Tell me about Summit"
2. **Use tenant names** - The AI recognizes all tenant names in your portfolio
3. **Ask follow-ups** - The AI remembers context within your session
4. **Try different phrasings** - If one question doesn't work, rephrase it

---

## Lease Database

The Lease Database tab shows all tenants in a searchable table.

### Features

- **Search**: Type any text to filter tenants
- **Sort**: Click column headers to sort
- **Details**: Click a tenant row to see full lease details

### Columns

| Column | Description |
|--------|-------------|
| Tenant | Business name |
| Suite | Unit number |
| Sq Ft | Leased square footage |
| Base Rent | Monthly base rent |
| Rent/PSF | Rent per square foot |
| Lease Start | Commencement date |
| Lease End | Expiration date |
| Category | Business type |

---

## Co-Tenancy Risk

This tab analyzes risks related to tenant dependencies.

### Risk Categories

| Level | Color | Meaning |
|-------|-------|---------|
| High | Red | Immediate attention needed |
| Medium | Yellow | Monitor closely |
| Low | Green | Acceptable risk |

### What It Tracks

- **Anchor dependencies** - Tenants with co-tenancy clauses tied to anchor tenants
- **Concentration risk** - Over-reliance on single tenant or category
- **Trigger events** - What could activate co-tenancy clauses

### Example

```
⚠️ HIGH RISK: 3 tenants have co-tenancy clauses requiring
Anchor Store A to remain open. If Anchor Store A closes:
- Tenant B can reduce rent by 15%
- Tenant C can terminate with 30 days notice
- Tenant D can reduce rent by 10%

Total revenue at risk: $24,500/month
```

---

## 10-Year Projection

Revenue forecasting and trend analysis.

### What You'll See

- **Current Revenue**: Total monthly and annual rent
- **Projection Chart**: 10-year revenue forecast
- **Growth Rate**: Historical and projected growth
- **Risk Factors**: Events that could impact revenue

### Understanding the Chart

- **Solid line**: Projected revenue assuming all renewals
- **Dotted line**: Conservative estimate (some non-renewals)
- **Shaded area**: Revenue at risk from expirations

### Key Metrics

| Metric | Description |
|--------|-------------|
| NOI | Net Operating Income |
| Occupancy | Percentage of space leased |
| WALT | Weighted Average Lease Term |
| Revenue at Risk | Income from leases expiring in 12 months |

---

## Tenant Mix

Portfolio composition analysis.

### Category Breakdown

See how your tenant mix is distributed:

```
Food & Beverage: 35%
Retail: 25%
Services: 20%
Health & Fitness: 15%
Other: 5%
```

### Why It Matters

- **Diversification**: Balanced mix reduces risk
- **Synergy**: Complementary tenants drive traffic
- **Market positioning**: Defines your property's identity

### Recommendations

The system suggests improvements:

```
💡 Recommendation: Food & Beverage concentration (35%)
is slightly high. Consider adding more Service tenants
for balance.
```

---

## Critical Dates

Never miss a deadline with the expiration timeline.

### Alert Levels

| Timeframe | Alert |
|-----------|-------|
| 30 days | 🔴 Urgent |
| 60 days | 🟡 Warning |
| 90 days | 🟢 Upcoming |

### What's Tracked

- **Lease expirations**
- **Renewal option deadlines**
- **Rent escalation dates**
- **Notice requirements**

### Example Timeline

```
🔴 URGENT (Next 30 Days)
   - Summit Coffee: Renewal notice due Jan 15

🟡 WARNING (31-60 Days)
   - Medley Books: Lease expires Feb 28
   - Fitness First: Option exercise due Feb 15

🟢 UPCOMING (61-90 Days)
   - Retail Shop A: Rent escalation Mar 1
```

---

## Exporting Reports

### Available Formats

| Format | Best For |
|--------|----------|
| PDF | Board presentations, formal reports |
| Excel | Data analysis, custom calculations |
| CSV | Importing to other systems |

### How to Export

1. Go to the relevant tab (Lease Database, Analytics, etc.)
2. Click the **Export** button
3. Choose your format
4. File downloads automatically

### Report Contents

**Portfolio Report (PDF)**:
- Executive summary
- Tenant roster
- Financial overview
- Risk assessment
- Expiration timeline

**Data Export (Excel)**:
- Tenant details sheet
- Financial records sheet
- Analytics sheet
- Charts and graphs

---

## Common Questions

### "Why doesn't the AI know about [specific detail]?"

The AI only knows what's in your lease documents. If information wasn't extracted during ingestion, it won't be available. Contact your administrator to re-ingest documents.

### "How current is the data?"

Data is current as of the last ingestion. Check with your administrator for the last update date.

### "Can I edit lease information?"

The chat interface is read-only. Use the admin tools or API for updates.

### "Why are some answers incomplete?"

The AI extracts answers from lease documents. If the original document doesn't clearly state something, the AI may not be able to answer precisely.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line in message |
| `Ctrl+L` | Clear chat history |
| `Tab` | Move between tabs |

---

## Getting Help

### In-App Help
- Click the **?** icon in any tab for contextual help

### Documentation
- **This guide**: General usage
- **DEMO.md**: 12-minute walkthrough
- **QUICKTEST.md**: 2-minute quick start

### Support
Contact your system administrator for:
- Data updates
- Access issues
- Feature requests

---

## Tips for Property Managers

### Daily Tasks

1. **Check Critical Dates** - Start each day by reviewing upcoming deadlines
2. **Monitor Risks** - Weekly review of co-tenancy risk tab
3. **Export Reports** - Generate monthly portfolio reports for stakeholders

### Best Practices

1. **Document everything** - Use consistent naming in lease documents
2. **Keep data current** - Request re-ingestion when leases change
3. **Explore the AI** - The more you use it, the more you'll discover

### Example Workflows

**Preparing for a Tenant Meeting:**
```
1. Search for tenant in Lease Database
2. Ask AI: "Summarize [tenant]'s key lease terms"
3. Check renewal options and deadlines
4. Export tenant summary PDF
```

**Monthly Portfolio Review:**
```
1. Check 10-Year Projection for trends
2. Review Tenant Mix for balance
3. Export Portfolio Report PDF
4. Review Critical Dates for next 90 days
```

**Answering a Quick Question:**
```
Just ask the AI! Examples:
- "What's the total rent for food tenants?"
- "When does the Fitness First lease end?"
- "Compare our top 3 tenants by rent"
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Base Rent** | Fixed monthly rent payment |
| **CAM** | Common Area Maintenance charges |
| **Co-tenancy** | Clause allowing rent reduction if anchor leaves |
| **NNN** | Triple Net - tenant pays taxes, insurance, maintenance |
| **NOI** | Net Operating Income |
| **PSF** | Per Square Foot |
| **WALT** | Weighted Average Lease Term |
| **Exclusivity** | Clause preventing competing tenants |

---

## What's Coming

### Planned Features

- **Email Alerts** - Automatic notifications for deadlines
- **Custom Agents** - Specialized AI for ingestion, analysis, risk
- **Mobile App** - Access on the go
- **Integrations** - Connect to property management systems

Stay tuned for updates!
