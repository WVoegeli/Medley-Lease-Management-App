# Documentation Update & Custom Agents Design

**Date:** 2025-01-19
**Status:** Approved
**Author:** Claude (Brainstorming Session)

---

## Executive Summary

This design document outlines a two-part initiative for the Medley Lease Management App:

1. **Documentation Overhaul** - Update all documentation to reflect current MCPs, Plugins, and Skills
2. **Custom Agent Development** - Build three specialized agents for lease management workflows

### Key Decisions Made

| Decision | Choice |
|----------|--------|
| Target Audience | All three: Developers, End Users, AI Agents |
| Agent Goals | Assistance + Analysis (human-in-the-loop) |
| Priority Workflows | Lease Ingestion, Financial Analysis, Risk Assessment |
| Interaction Model | Chat-based natural language in Streamlit UI |
| Autonomy Level | Single-turn for simple, Multi-step guided for complex |

---

## Part 1: Documentation Update Strategy

### Three-Tier Documentation Architecture

#### Tier 1: Developer Documentation (`docs/DEVELOPMENT.md`)
- Complete MCP server reference with configuration examples
- Plugin installation and marketplace setup
- Skills reference with invocation patterns
- Architecture diagrams showing how MCPs integrate with the RAG pipeline
- Contributing guidelines for adding new agents

#### Tier 2: User Documentation (`docs/USER_GUIDE.md`)
- Plain-language guide to using the chat interface
- Example conversations for each agent capability
- Workflow walkthroughs (ingesting a lease, running financial analysis, checking risks)
- Troubleshooting common issues

#### Tier 3: AI Agent Documentation (Updated `CLAUDE.md` + `AGENTS.md`)
- Structured context for AI assistants working on this codebase
- Tool availability matrix (which MCPs/Skills apply to which tasks)
- Decision trees for common operations
- Project-specific patterns and conventions

### Files to Update/Create

| File | Action | Purpose |
|------|--------|---------|
| `CLAUDE.md` | Update | Add MCP/Skills/Plugin reference section |
| `AGENTS.md` | Update | Expand with agent capabilities and patterns |
| `PLUGINS.md` | Update | Current 15 plugins + 2 marketplaces |
| `docs/DEVELOPMENT.md` | Create | Full developer reference |
| `docs/USER_GUIDE.md` | Create | End-user guide |

### Current Tool Inventory

#### MCP Servers (9 Configured)

| MCP | Purpose | Config Location |
|-----|---------|-----------------|
| `context7` | Library documentation lookup | `.mcp.json` |
| `perplexity` | Web search, reasoning, deep research | `.mcp.json` |
| `linear` | Issue tracking and management | `.mcp.json` |
| `github` | Repository, PR, issue management | `.mcp.json` |
| `vibe-check` | Metacognitive questioning, pattern tracking | `.mcp.json` |
| `semgrep` | Security scanning | `.mcp.json` |
| `git` | Git operations (status, diff, commit, branch) | `.mcp.json` |
| `pieces` | Code snippet management | `.mcp.json` |
| `serena` | Semantic code analysis, symbol-level editing | `.mcp.json` |

#### Plugins (15 Enabled)

**Official Claude Plugins:**
- `frontend-design` - Create frontend interfaces
- `context7` - Library documentation
- `github` - GitHub integration
- `feature-dev` - Guided feature development
- `code-review` - PR code review
- `playwright` - Browser automation
- `greptile` - Code analysis
- `serena` - Semantic code tools

**Superpowers Marketplace (`obra/superpowers-marketplace`):**
- `superpowers` - Development methodology skills

**WSHobson Agents (`wshobson/agents`):**
- `javascript-typescript` - JS/TS development
- `backend-development` - Backend patterns
- `testing` - Test automation
- `code-review-ai` - AI code review
- `database-development` - Database design

#### Skills Available

| Skill | Purpose |
|-------|---------|
| `/brainstorming` | Explore requirements before building |
| `/writing-plans` | Create implementation plans |
| `/executing-plans` | Execute plans with checkpoints |
| `/dispatching-parallel-agents` | Run parallel tasks |
| `/systematic-debugging` | Debug issues |
| `/test-driven-development` | TDD workflow |
| `/verification-before-completion` | Verify before done |
| `/feature-dev` | Guided feature development |
| `/code-review` | Review pull requests |
| `/frontend-design` | Create frontend interfaces |

---

## Part 2: Custom Agent Architecture

### Overview

Three specialized agents that integrate with the existing chat interface:

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Chat UI                         │
│                  (interfaces/chat_app.py)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Router                              │
│               (src/agents/agent_router.py)                   │
│                                                              │
│  Analyzes message → Routes to appropriate handler            │
└────┬──────────────────┬──────────────────┬──────────────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Lease     │  │  Financial  │  │    Risk     │
│  Ingestor   │  │   Analyst   │  │  Assessor   │
│   Agent     │  │    Agent    │  │    Agent    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Existing Infrastructure                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ QueryEngine │  │  SQLStore   │  │  Analytics  │         │
│  │    (RAG)    │  │  (SQLite)   │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
src/
├── agents/                          # NEW: Agent framework
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base class for all agents
│   ├── agent_router.py             # Routes chat messages to appropriate agent
│   ├── lease_ingestor_agent.py     # Lease ingestion workflows
│   ├── financial_analyst_agent.py  # Financial analysis workflows
│   ├── risk_assessor_agent.py      # Risk assessment workflows
│   └── prompts/                    # Agent-specific system prompts
│       ├── ingestor_prompt.md
│       ├── analyst_prompt.md
│       └── risk_prompt.md
```

### Base Agent Pattern

```python
from abc import ABC, abstractmethod
from typing import Generator, Dict, Any
from dataclasses import dataclass

@dataclass
class AgentResponse:
    message: str
    data: Dict[str, Any] = None
    requires_confirmation: bool = False
    next_step: str = None

class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""

    def __init__(self, query_engine, sql_store, llm):
        self.query_engine = query_engine  # Existing RAG
        self.sql_store = sql_store        # Existing SQLite
        self.llm = llm                    # Existing LLM integration

    @abstractmethod
    def can_handle(self, message: str) -> float:
        """Return confidence score 0-1 for handling this message."""
        pass

    @abstractmethod
    def execute(self, message: str, context: dict) -> AgentResponse:
        """Single-turn execution."""
        pass

    def execute_guided(self, message: str, context: dict) -> Generator[AgentResponse, str, None]:
        """Multi-step with checkpoints, yields for user confirmation."""
        # Default implementation falls back to single-turn
        yield self.execute(message, context)
```

### Agent Router

```python
class AgentRouter:
    """Routes incoming messages to the appropriate agent or standard RAG."""

    def __init__(self, agents: list[BaseAgent], query_engine):
        self.agents = agents
        self.query_engine = query_engine
        self.confidence_threshold = 0.7

    def route(self, message: str, context: dict) -> tuple[BaseAgent | None, float]:
        """Determine which agent should handle this message."""
        best_agent = None
        best_score = 0.0

        for agent in self.agents:
            score = agent.can_handle(message)
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_score >= self.confidence_threshold:
            return best_agent, best_score
        return None, 0.0  # Falls back to standard RAG
```

---

## Agent Specifications

### Agent 1: Lease Ingestor Agent

**Purpose:** Process new lease documents, extract key terms, populate databases.

**Trigger Phrases:**
- "Ingest this lease"
- "Process the new [tenant] lease"
- "Add this document"
- "Upload and analyze [filename]"

**Capabilities:**
- Parse DOCX files using existing `docx_parser.py`
- Extract structured data (tenant, rent, sq ft, term, options)
- Validate extracted data against expected patterns
- Guided workflow with confirmation checkpoint
- Populate ChromaDB (vectors) and SQLite (structured)
- Generate ingestion summary report

**Workflow - Single Turn:**
```
User: "What's in the new lease document?"
Agent: Parses → Extracts → Returns summary of key terms (no DB write)
```

**Workflow - Multi-Step Guided:**
```
Step 1: User uploads or references file
Step 2: Agent extracts and displays:
        "Found: Tenant: Blue Bottle Coffee, Rent: $45/PSF,
         Term: 10 years, Sq Ft: 2,400, Options: 2x5yr renewals

         ⚠️ Confirm these terms are correct before I add to database?"

Step 3: User confirms → Agent writes to ChromaDB + SQLite
Step 4: Agent returns: "✓ Added Blue Bottle Coffee. 387 chunks indexed,
         lease record created. Next expiration alert set for 2034."
```

**MCP Integration:**
| MCP | Usage |
|-----|-------|
| `Serena` | Semantic code analysis when extending parsers |
| `GitHub` | Track ingestion issues, create PRs for parser improvements |
| `Linear` | Auto-create tickets for failed ingestions or data quality issues |
| `Vibe-check` | Validate extraction logic, prevent pattern drift |

---

### Agent 2: Financial Analyst Agent

**Purpose:** Rent roll analysis, revenue projections, financial reporting.

**Trigger Phrases:**
- "Analyze financials for..."
- "What's the revenue projection?"
- "Run rent roll analysis"
- "Total rent by category"
- "Compare [tenant] to portfolio average"

**Capabilities:**
- Quick metrics (total rent, average PSF, occupancy rate)
- Full financial workup with projections
- Compare tenant performance against portfolio benchmarks
- CAM reconciliation analysis
- Generate Excel/PDF financial reports
- Uses existing `lease_analytics.py` engine

**Workflow - Single Turn:**
```
User: "What's Summit Coffee paying?"
Agent: Direct RAG query → "$42/PSF base rent, $8/PSF CAM, 1,850 sq ft"

User: "Total monthly rent?"
Agent: SQL aggregation → "$127,450/month across 14 tenants"
```

**Workflow - Multi-Step Guided:**
```
User: "Run full financial analysis for Q1"

Step 1: "I'll analyze 14 tenants across 3 categories. Include projections? [Yes/No]"
Step 2: User confirms scope
Step 3: Agent generates analysis, displays summary:
        "Portfolio Summary:
         - Total Annual Rent: $1,529,400
         - Average PSF: $38.50
         - Occupancy: 94%
         - YoY Growth: +3.2%"
Step 4: "Export to Excel/PDF?" → Generates report using existing export module
```

**MCP Integration:**
| MCP | Usage |
|-----|-------|
| `Perplexity` | Research market rent comparables, CPI data |
| `Context7` | Pull latest Pandas/NumPy docs for complex calculations |
| `GitHub` | Version control financial models and templates |

---

### Agent 3: Risk Assessor Agent

**Purpose:** Co-tenancy risks, tenant health monitoring, portfolio risk analysis.

**Trigger Phrases:**
- "What are the risks?"
- "Check co-tenancy exposure"
- "Portfolio health check"
- "Any expiring leases?"
- "Tenant concentration analysis"

**Capabilities:**
- Co-tenancy clause analysis and concentration risk
- Tenant health scoring (lease term remaining, rent vs market)
- Expiration clustering detection
- Portfolio vulnerability assessment
- Risk matrix with severity ratings
- Mitigation recommendations

**Workflow - Single Turn:**
```
User: "Any co-tenancy risks?"
Agent: Quick scan → "⚠️ 3 tenants have co-tenancy clauses tied to
       Anchor Tenant A. If they leave, potential rent reduction of 15%."
```

**Workflow - Multi-Step Guided:**
```
User: "Full portfolio risk assessment"

Step 1: Agent runs all risk checks
Step 2: Displays risk matrix:
        "Risk Assessment Complete:
         🔴 HIGH: 2 leases expiring within 90 days
         🟡 MEDIUM: Co-tenancy exposure to single anchor
         🟢 LOW: Tenant diversification healthy

         Overall Portfolio Health Score: 72/100"
Step 3: "Generate mitigation recommendations? [Yes/No]"
Step 4: User confirms → Detailed action plan with priorities
```

**MCP Integration:**
| MCP | Usage |
|-----|-------|
| `Perplexity` | Research tenant company health, news, credit ratings |
| `Linear` | Auto-create risk mitigation tasks with deadlines |
| `Vibe-check` | Challenge assumptions, prevent blind spots in risk models |

---

## Implementation Roadmap

### Phase 1: Documentation Foundation
**Priority:** First
**Estimated Effort:** Medium

**Deliverables:**
- [ ] Update `CLAUDE.md` with MCP/Skills/Plugin reference
- [ ] Update `PLUGINS.md` with current 15 plugins + marketplace config
- [ ] Update `AGENTS.md` with agent capability matrix
- [ ] Create `docs/DEVELOPMENT.md` - full developer reference
- [ ] Create `docs/USER_GUIDE.md` - end-user guide

**Why First:** Clean documentation enables AI agents to work more effectively on subsequent phases.

### Phase 2: Agent Framework Core
**Priority:** Second
**Estimated Effort:** Medium

**Deliverables:**
- [ ] `src/agents/__init__.py` - Module initialization
- [ ] `src/agents/base_agent.py` - Abstract base class
- [ ] `src/agents/agent_router.py` - Message routing logic
- [ ] Integration with `interfaces/chat_app.py`
- [ ] Unit tests for framework (`tests/test_agents.py`)

### Phase 3: Individual Agents
**Priority:** Third (can be parallelized)
**Estimated Effort:** High

**3A: Lease Ingestor Agent**
- [ ] `src/agents/lease_ingestor_agent.py`
- [ ] `src/agents/prompts/ingestor_prompt.md`
- [ ] Parser integration, extraction validation
- [ ] Guided workflow with confirmation
- [ ] Test with 2-3 new lease documents

**3B: Financial Analyst Agent**
- [ ] `src/agents/financial_analyst_agent.py`
- [ ] `src/agents/prompts/analyst_prompt.md`
- [ ] Connect to `lease_analytics.py`
- [ ] Projection workflows
- [ ] Excel/PDF export integration

**3C: Risk Assessor Agent**
- [ ] `src/agents/risk_assessor_agent.py`
- [ ] `src/agents/prompts/risk_prompt.md`
- [ ] Risk scoring engine
- [ ] Mitigation recommendations
- [ ] Perplexity integration for external research

### Phase 4: Polish & Integration
**Priority:** Fourth
**Estimated Effort:** Low-Medium

**Deliverables:**
- [ ] Refine prompts based on real usage
- [ ] Add agent status indicators to UI
- [ ] Documentation updates with real examples
- [ ] Performance optimization

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Trigger phrase accuracy | 90%+ correct agent routing |
| User confirmations per workflow | <2 average for multi-step |
| Chat UI integration | All 3 agents accessible |
| Backward compatibility | Zero breaking changes to existing RAG |
| Test coverage | 80%+ for agent module |
| Documentation completeness | All MCPs/Plugins/Skills documented |

---

## Skills for Development

When building/extending these agents, developers should use:

| Skill | When to Use |
|-------|-------------|
| `/brainstorming` | Design new agent capabilities |
| `/writing-plans` | Plan agent implementation |
| `/test-driven-development` | Build agent test suites |
| `/systematic-debugging` | Debug agent behavior issues |
| `/code-review` | Review agent code before merge |
| `/verification-before-completion` | Verify agents work correctly |

---

## Appendix: Integration Points

### Chat App Integration

The agent router integrates into `interfaces/chat_app.py`:

```python
# In chat_app.py
from src.agents.agent_router import AgentRouter
from src.agents.lease_ingestor_agent import LeaseIngestorAgent
from src.agents.financial_analyst_agent import FinancialAnalystAgent
from src.agents.risk_assessor_agent import RiskAssessorAgent

# Initialize agents
agents = [
    LeaseIngestorAgent(query_engine, sql_store, llm),
    FinancialAnalystAgent(query_engine, sql_store, llm),
    RiskAssessorAgent(query_engine, sql_store, llm),
]
router = AgentRouter(agents, query_engine)

# In chat handler
def handle_message(user_message, context):
    agent, confidence = router.route(user_message, context)

    if agent:
        return agent.execute(user_message, context)
    else:
        # Fall back to standard RAG
        return query_engine.query(user_message)
```

### Existing Module Dependencies

| Agent | Uses These Existing Modules |
|-------|----------------------------|
| Lease Ingestor | `docx_parser.py`, `chroma_store.py`, `sql_store.py`, `chunker.py` |
| Financial Analyst | `lease_analytics.py`, `sql_store.py`, `report_generator.py` |
| Risk Assessor | `lease_analytics.py`, `sql_store.py`, `conversation_memory.py` |

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-19 | 1.0 | Initial design approved |
