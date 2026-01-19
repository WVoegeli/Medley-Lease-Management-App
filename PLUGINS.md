# Plugins & Agents for Medley Lease Analysis & Management

This document provides setup instructions for all recommended AI agents, plugins, and development tools for the project.

## 📦 Quick Setup (Recommended)

```bash
# 1. Add marketplaces
/plugin marketplace add obra/superpowers-marketplace
/plugin marketplace add wshobson/agents

# 2. Install essential plugins
/plugin install superpowers@superpowers-marketplace
/plugin install python-development@wshobson/agents
/plugin install llm-applications@wshobson/agents
/plugin install testing-automation@wshobson/agents
/plugin install comprehensive-review@wshobson/agents

# 3. Verify installation
/help
# Should see new commands like /superpowers:brainstorm, etc.
```

---

## 🎯 Plugin Marketplaces

### 1. Superpowers Framework
**Repository**: [obra/superpowers](https://github.com/obra/superpowers)
**Focus**: Development methodology and workflow automation

```bash
/plugin marketplace add obra/superpowers-marketplace
```

### 2. wshobson Agents
**Repository**: [wshobson/agents](https://github.com/wshobson/agents)
**Focus**: 100+ specialized AI agents for software development

```bash
/plugin marketplace add wshobson/agents
```

---

## ⭐ High Priority Plugins (Install First)

### Superpowers (Development Methodology)

**Install:**
```bash
/plugin install superpowers@superpowers-marketplace
```

**Features:**
- `/superpowers:brainstorm` - Interactive design refinement before coding
- `/superpowers:write-plan` - Create detailed implementation plans
- `/superpowers:execute-plan` - Execute plans in batches with checkpoints
- `test-driven-development` - Enforces RED-GREEN-REFACTOR TDD cycle
- `systematic-debugging` - 4-phase root cause debugging process
- `requesting-code-review` - Pre-review checklist
- `using-git-worktrees` - Parallel development branches

**When to Use:**
- Before implementing any new feature (brainstorm first)
- For multi-step tasks (write-plan, then execute-plan)
- When debugging complex issues (systematic-debugging)
- Before merging code (requesting-code-review)

**Example Workflow:**
```bash
# 1. Design a new feature
/superpowers:brainstorm

# You: "I want to add email notifications for lease expirations"
# Agent: Asks clarifying questions, explores alternatives, presents design

# 2. Create implementation plan
/superpowers:write-plan

# Agent: Breaks work into 2-5 minute tasks with file paths and verification

# 3. Execute the plan
/superpowers:execute-plan

# Agent: Dispatches subagents per task, reviews code, executes in batches
```

---

### Python Development (Language Experts)

**Install:**
```bash
/plugin install python-development@wshobson/agents
```

**Agents:**
- `python-pro` - General Python expertise
- `django-pro` - Django framework specialist
- `fastapi-pro` - FastAPI specialist (used in this project)

**Skills (Auto-activated):**
- `async-python-patterns` - AsyncIO and concurrency
- `python-testing-patterns` - pytest fixtures and patterns
- `python-packaging` - Package structure and setup
- `python-performance` - Optimization techniques
- `uv-package-manager` - Fast dependency management

**Use Cases:**
- Adding new FastAPI endpoints (activates fastapi-pro)
- Optimizing async code (activates async-python-patterns)
- Writing pytest tests (activates python-testing-patterns)

---

### LLM Applications (RAG Optimization)

**Install:**
```bash
/plugin install llm-applications@wshobson/agents
```

**Agents:**
- `langchain-expert` - LangChain framework specialist
- `rag-architect` - RAG system design and optimization

**Skills (Auto-activated):**
- `langchain-patterns` - LangChain best practices
- `prompt-engineering` - Effective prompt design
- `rag-optimization` - Improve retrieval quality
- `llm-evaluation` - Evaluate LLM outputs

**Use Cases:**
- Improving RAG search quality
- Optimizing hybrid ranking (vector + BM25)
- Tuning prompts for better answers
- Evaluating query engine performance

**Example:**
```bash
"Optimize the hybrid search to improve relevance for financial queries"
# Activates: rag-architect + rag-optimization skill
# Result: Better weight tuning, improved ranking algorithm
```

---

### Testing Automation

**Install:**
```bash
/plugin install testing-automation@wshobson/agents
```

**Agents:**
- `test-automator` - Generates tests and improves coverage

**Features:**
- Auto-generate unit tests
- TDD workflow support
- Coverage gap identification
- Test data generation

**Use Cases:**
- Adding tests for new features
- Improving test coverage
- Generating test fixtures

---

### Comprehensive Review

**Install:**
```bash
/plugin install comprehensive-review@wshobson/agents
```

**Agents:**
- `architect-review` - Architecture and design review
- `code-reviewer` - Code quality and patterns
- `security-auditor` - Security vulnerability scanning

**Use Cases:**
- Before merging PRs
- After implementing major features
- Periodic security audits

**Example:**
```bash
"Review the new analytics module for security issues and code quality"
# Runs: architect-review → code-reviewer → security-auditor
# Reports: Design issues, code smells, security vulnerabilities
```

---

## 🔧 Medium Priority Plugins

### Code Documentation

**Install:**
```bash
/plugin install code-documentation@wshobson/agents
```

**Features:**
- Auto-generate docstrings
- Create API documentation
- Generate README sections

### Database Design

**Install:**
```bash
/plugin install database-design@wshobson/agents
```

**Features:**
- Schema design and normalization
- Index optimization
- Migration strategy

**Use Case:**
```bash
"Design an optimized schema for tracking lease amendments"
# Agent: Designs normalized tables, indexes, relationships
```

### Data Engineering

**Install:**
```bash
/plugin install data-engineering@wshobson/agents
```

**Features:**
- ETL pipeline design
- Data validation
- Transformation logic

**Use Case:**
```bash
"Create a pipeline to sync lease data from external property management system"
```

---

## 🛡️ Low Priority Plugins (Optional)

### Security Scanning
```bash
/plugin install security-scanning@wshobson/agents
```
- SAST security analysis
- Dependency vulnerability scanning

### Observability
```bash
/plugin install observability@wshobson/agents
```
- Monitoring setup
- Logging strategy
- Performance tracking

---

## 📋 Complete Plugin List

| Plugin | Priority | Marketplace | Purpose |
|--------|----------|-------------|---------|
| **superpowers** | ⭐⭐⭐ High | superpowers-marketplace | Development methodology & TDD |
| **python-development** | ⭐⭐⭐ High | wshobson/agents | Python/FastAPI expertise |
| **llm-applications** | ⭐⭐⭐ High | wshobson/agents | RAG optimization |
| **testing-automation** | ⭐⭐ Medium | wshobson/agents | Test generation |
| **comprehensive-review** | ⭐⭐ Medium | wshobson/agents | Multi-agent code review |
| **code-documentation** | ⭐⭐ Medium | wshobson/agents | Auto-generate docs |
| **database-design** | ⭐⭐ Medium | wshobson/agents | Schema optimization |
| **data-engineering** | ⭐ Low | wshobson/agents | ETL pipelines |
| **security-scanning** | ⭐ Low | wshobson/agents | Security audits |
| **observability** | ⭐ Low | wshobson/agents | Monitoring setup |

---

## 🎓 Usage Examples

### Example 1: Adding a New Feature

```bash
# Step 1: Brainstorm the design
/superpowers:brainstorm

You: "Add a feature to send email alerts for lease expirations"

Agent:
- Asks about email provider (SendGrid? AWS SES? SMTP?)
- Explores scheduling options (cron? celery? APScheduler?)
- Discusses email templates and personalization
- Presents design options for approval

# Step 2: Create implementation plan
/superpowers:write-plan

Agent:
- Task 1: Add email dependencies to requirements.txt
- Task 2: Create email service module (src/notifications/email_service.py)
- Task 3: Add email templates (templates/lease_expiration.html)
- Task 4: Create scheduler (src/notifications/scheduler.py)
- Task 5: Add API endpoint to trigger alerts
- Task 6: Write tests for email service
- Task 7: Update documentation

# Step 3: Execute the plan
/superpowers:execute-plan

Agent:
- Dispatches python-pro for email service implementation
- Uses fastapi-pro for API endpoint
- Activates python-testing-patterns for tests
- Reviews each task before proceeding

# Step 4: Review before merging
/comprehensive-review

Agent:
- architect-review: Checks email service design
- code-reviewer: Validates code quality
- security-auditor: Ensures no email injection vulnerabilities
```

### Example 2: Optimizing RAG Search

```bash
You: "The RAG search isn't returning good results for financial queries. Optimize it."

# Activates: rag-architect + rag-optimization skill

Agent:
1. Analyzes current hybrid_ranker.py
2. Identifies issues:
   - Vector weight too high (0.6) for keyword-heavy financial queries
   - BM25 not tuned for financial terms
   - RRF_K constant may be suboptimal
3. Suggests improvements:
   - Adjust VECTOR_WEIGHT to 0.4, BM25_WEIGHT to 0.6
   - Add financial term boosting in BM25
   - Tune RRF_K to 45 for better fusion
4. Implements changes
5. Runs tests to validate improvements
```

### Example 3: Adding Tests

```bash
You: "Generate comprehensive tests for the analytics module"

# Activates: test-automator + python-testing-patterns

Agent:
1. Analyzes src/analytics/lease_analytics.py
2. Identifies test gaps:
   - No tests for edge cases (empty portfolio, single lease)
   - Missing tests for revenue projection edge cases
   - No tests for risk assessment thresholds
3. Generates tests:
   - tests/test_analytics.py with 20+ test cases
   - Uses pytest fixtures from conftest.py
   - Includes parametrized tests for multiple scenarios
   - Adds docstrings explaining each test
4. Runs tests to ensure they pass
```

---

## 🔄 Plugin Updates

```bash
# Update all plugins to latest versions
/plugin update superpowers
/plugin update python-development
/plugin update llm-applications

# Or update all at once
/plugin update --all
```

---

## 📚 Additional Resources

- **Superpowers Docs**: https://github.com/obra/superpowers
- **wshobson Agents Docs**: https://github.com/wshobson/agents
- **AGENTS.md Format**: https://agents.md/
- **Claude Code Docs**: https://claude.com/code

---

## 💡 Best Practices

### 1. **Always Brainstorm First**
Use `/superpowers:brainstorm` before implementing any non-trivial feature. It saves time by clarifying requirements upfront.

### 2. **Use Plan → Execute for Complex Tasks**
For multi-step features:
1. `/superpowers:write-plan`
2. Review the plan
3. `/superpowers:execute-plan`

### 3. **Let Skills Activate Automatically**
Don't manually invoke skills. They activate based on context:
- Working on FastAPI code? → `fastapi-pro` activates automatically
- Writing async code? → `async-python-patterns` activates
- Optimizing RAG? → `rag-optimization` activates

### 4. **Run Comprehensive Review Before Merging**
Always run a multi-agent review before merging to main:
```bash
/comprehensive-review
```

### 5. **Use TDD Workflow**
Let `test-driven-development` skill enforce RED-GREEN-REFACTOR:
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor for quality

---

## 🚀 Getting Started Checklist

For new team members:

- [ ] Install Claude Code CLI
- [ ] Add both marketplaces (`superpowers-marketplace` and `wshobson/agents`)
- [ ] Install high-priority plugins (5 plugins)
- [ ] Run `/help` to verify installation
- [ ] Try `/superpowers:brainstorm` on a small task to get familiar
- [ ] Read AGENTS.md for project-specific context
- [ ] Review FEATURES.md to understand the codebase

---

## 📞 Support

- **Plugin Issues**: Check marketplace GitHub repos
- **Project Setup**: See `AGENTS.md` and `IMPLEMENTATION_SUMMARY.md`
- **Quick Start**: Run `python scripts/quickstart.py`

---

**Configuration File**: See `.claude/recommended-plugins.json` for machine-readable plugin list.
