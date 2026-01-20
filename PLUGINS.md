# AI Tools: MCPs, Plugins & Skills

This document provides comprehensive documentation for all AI development tools configured for the Medley Lease Management project.

---

## Quick Reference

| Category | Count | Configuration File |
|----------|-------|-------------------|
| MCP Servers | 9 | `.mcp.json` |
| Plugins | 15 | `.claude/settings.json` |
| Marketplaces | 2 | `.claude/settings.json` |
| Skills | 15+ | Via superpowers plugin |

---

## MCP Servers (Model Context Protocol)

MCP servers extend Claude's capabilities with external tools and data sources. Configuration is in `.mcp.json`.

### Server Reference

| Server | Type | Purpose |
|--------|------|---------|
| **context7** | Documentation | Query up-to-date library documentation |
| **perplexity** | Research | Web search, reasoning, deep research |
| **linear** | Project Management | Issue tracking and task management |
| **github** | Version Control | Repository, PR, issue management |
| **vibe-check** | Metacognition | Question assumptions, track learning |
| **semgrep** | Security | SAST analysis, vulnerability scanning |
| **git** | Version Control | Git operations (status, diff, commit) |
| **pieces** | Snippets | Code snippet management |
| **serena** | Code Analysis | Semantic code navigation and editing |

### Detailed Server Documentation

#### Context7
**Purpose:** Query up-to-date documentation for any programming library.

**Usage:**
```
"Look up the latest FastAPI documentation for dependency injection"
"What's the current ChromaDB API for adding documents?"
```

**When to Use:**
- Need current library documentation (not training data)
- Checking API changes in recent versions
- Finding code examples for specific libraries

---

#### Perplexity
**Purpose:** Web search and research with AI reasoning.

**Modes:**
- `search` - Quick searches for straightforward questions
- `reason` - Complex multi-step reasoning tasks
- `deep_research` - In-depth analysis and detailed reports

**Usage:**
```
"Search for current market rent rates in Dallas retail"
"Research best practices for commercial lease management software"
```

**When to Use:**
- Need current information from the web
- Market research and competitive analysis
- Finding external data not in training data

---

#### Linear
**Purpose:** Issue tracking and project management.

**Capabilities:**
- Create issues with priority and labels
- Search and filter issues
- Update issue status
- Track project progress

**Usage:**
```
"Create a Linear issue for the lease ingestion bug"
"List all high-priority issues in the current sprint"
```

---

#### GitHub
**Purpose:** Repository and code collaboration.

**Capabilities:**
- Create and manage pull requests
- File and issue management
- Branch operations
- Code search across repositories

**Usage:**
```
"Create a PR for the analytics improvements"
"Search for similar implementations in open source projects"
```

---

#### Vibe-Check
**Purpose:** Metacognitive questioning and pattern tracking.

**Capabilities:**
- Challenge assumptions before major decisions
- Track common mistakes and solutions
- Maintain session-specific rules
- Prevent recurring errors

**Usage:**
```
"Before I refactor the query engine, let me do a vibe check"
"Track this pattern: always test with empty database first"
```

**When to Use:**
- Before major architectural decisions
- When debugging complex issues
- To prevent repeating past mistakes

---

#### Semgrep
**Purpose:** Security scanning and code analysis.

**Capabilities:**
- SAST (Static Application Security Testing)
- Custom rule creation
- Vulnerability detection
- Code pattern matching

**Usage:**
```
"Scan the API endpoints for security vulnerabilities"
"Check for SQL injection risks in the database module"
```

---

#### Git
**Purpose:** Git operations directly from Claude.

**Capabilities:**
- `git_status` - Working tree status
- `git_diff` - Show changes
- `git_commit` - Record changes
- `git_log` - Commit history
- `git_branch` - Branch management
- `git_checkout` - Switch branches

**Usage:**
```
"Show me the git status"
"Create a new branch for the feature"
"Show commits from the last week"
```

---

#### Serena
**Purpose:** Semantic code analysis and manipulation.

**Capabilities:**
- Find symbols by name/pattern
- Navigate code relationships
- Replace symbol bodies
- Insert code at specific locations
- Rename symbols across codebase

**Usage:**
```
"Find all usages of the LeaseAnalytics class"
"Show me the structure of the query_engine module"
"Rename the calculate_rent method to compute_rent"
```

**When to Use:**
- Navigating large codebases
- Refactoring with confidence
- Understanding code relationships

---

## Plugins

Plugins are managed through `.claude/settings.json`. We use plugins from three sources:

### Source 1: Official Claude Plugins

| Plugin | Purpose | Key Features |
|--------|---------|--------------|
| **frontend-design** | UI Development | Create production-grade interfaces |
| **context7** | Documentation | Library docs lookup |
| **github** | Version Control | GitHub integration |
| **feature-dev** | Development | Guided feature workflows |
| **code-review** | Quality | PR code review |
| **playwright** | Testing | Browser automation |
| **greptile** | Analysis | Code analysis, PR management |
| **serena** | Code Tools | Semantic code operations |

### Source 2: Superpowers Marketplace

**Repository:** `obra/superpowers-marketplace`

```bash
# Add marketplace
/plugin marketplace add obra/superpowers-marketplace

# Install
/plugin install superpowers@superpowers-marketplace
```

**Plugin: superpowers**

The superpowers plugin provides development methodology skills:

| Skill | Command | Purpose |
|-------|---------|---------|
| Brainstorming | `/brainstorming` | Explore requirements before building |
| Writing Plans | `/writing-plans` | Create detailed implementation plans |
| Executing Plans | `/executing-plans` | Execute plans with checkpoints |
| TDD | `/test-driven-development` | Red-Green-Refactor workflow |
| Debugging | `/systematic-debugging` | 4-phase root cause analysis |
| Code Review | `/requesting-code-review` | Pre-merge review checklist |
| Git Worktrees | `/using-git-worktrees` | Parallel development branches |
| Verification | `/verification-before-completion` | Verify before claiming done |
| Parallel Agents | `/dispatching-parallel-agents` | Run independent tasks in parallel |
| Subagent Dev | `/subagent-driven-development` | Execute with specialized subagents |

### Source 3: WSHobson Agents

**Repository:** `wshobson/agents`

```bash
# Add marketplace
/plugin marketplace add wshobson/agents

# Install plugins
/plugin install python-development@wshobson/agents
/plugin install llm-applications@wshobson/agents
/plugin install testing-automation@wshobson/agents
```

**Currently Enabled:**

| Plugin | Purpose |
|--------|---------|
| **javascript-typescript** | JS/TS development patterns |
| **backend-development** | Backend architecture expertise |
| **testing** | Test automation and coverage |
| **code-review-ai** | AI-powered code review |
| **database-development** | Database design and optimization |

---

## Skills Reference

Skills are invoked with slash commands. They provide guided workflows for common development tasks.

### Development Workflow Skills

#### `/brainstorming`
**When:** Before implementing any feature
**Process:**
1. Explores the current codebase
2. Asks clarifying questions one at a time
3. Proposes 2-3 approaches with trade-offs
4. Presents design in sections for validation
5. Writes design doc to `docs/plans/`

#### `/writing-plans`
**When:** After brainstorming, before implementation
**Output:** Detailed task list with:
- Specific file paths
- Verification steps
- Dependencies between tasks
- Estimated complexity

#### `/executing-plans`
**When:** After plan is approved
**Process:**
1. Executes tasks in batches
2. Pauses for review at checkpoints
3. Handles failures gracefully
4. Updates plan as needed

### Quality Skills

#### `/test-driven-development`
**Workflow:**
1. **RED** - Write failing test first
2. **GREEN** - Write minimal code to pass
3. **REFACTOR** - Improve code quality

#### `/systematic-debugging`
**4-Phase Process:**
1. **Reproduce** - Confirm the bug exists
2. **Isolate** - Find the root cause
3. **Fix** - Implement minimal fix
4. **Verify** - Confirm fix works

#### `/verification-before-completion`
**Checklist:**
- [ ] Tests pass
- [ ] No regressions
- [ ] Documentation updated
- [ ] Code reviewed

### Collaboration Skills

#### `/code-review`
Review pull requests with structured feedback.

#### `/requesting-code-review`
Prepare code for review with pre-flight checks.

#### `/feature-dev`
Guided feature development with architecture focus.

---

## Usage Patterns

### Pattern 1: New Feature Development

```bash
# 1. Brainstorm the design
/brainstorming
"I want to add email notifications for lease expirations"

# 2. Create implementation plan
/writing-plans

# 3. Execute the plan
/executing-plans

# 4. Verify and review
/verification-before-completion
/requesting-code-review
```

### Pattern 2: Bug Investigation

```bash
# 1. Systematic debugging
/systematic-debugging
"The revenue projection is returning negative values"

# 2. After fix, verify
/verification-before-completion
```

### Pattern 3: Research Task

```bash
# Use MCPs directly
"Use perplexity to research current CAM reconciliation best practices"
"Use context7 to look up the ChromaDB batch insert API"
```

### Pattern 4: Code Navigation

```bash
# Use serena for code understanding
"Use serena to find all methods in LeaseAnalytics"
"Show me references to calculate_portfolio_health_score"
```

---

## Configuration Files

### `.mcp.json` Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

### `.claude/settings.json` Structure

```json
{
  "enabledPlugins": {
    "plugin-name@marketplace": true
  },
  "extraKnownMarketplaces": {
    "marketplace-name": {
      "source": {
        "source": "github",
        "repo": "owner/repo"
      }
    }
  }
}
```

---

## Troubleshooting

### MCP Server Issues

**Server not responding:**
```bash
# Check if npx can run the package
npx -y @upstash/context7-mcp --help
```

**Missing API key:**
- Check `.mcp.json` for correct env variable names
- Ensure API keys are valid and not expired

### Plugin Issues

**Plugin not found:**
```bash
# Verify marketplace is added
/plugin marketplace list

# Re-add if missing
/plugin marketplace add obra/superpowers-marketplace
```

**Skill not activating:**
- Ensure the plugin is enabled in `.claude/settings.json`
- Try explicit invocation: `/skill-name`

---

## Best Practices

1. **Always brainstorm first** for non-trivial features
2. **Use plans for multi-step work** to maintain focus
3. **Let skills activate automatically** based on context
4. **Run verification before claiming done**
5. **Use vibe-check** before major decisions
6. **Use serena** for code navigation in large files
7. **Use perplexity** for external research, not training data

---

## Quick Install Commands

```bash
# Add marketplaces
/plugin marketplace add obra/superpowers-marketplace
/plugin marketplace add wshobson/agents

# Install essential plugins
/plugin install superpowers@superpowers-marketplace
/plugin install python-development@wshobson/agents
/plugin install llm-applications@wshobson/agents
/plugin install testing-automation@wshobson/agents
/plugin install comprehensive-review@wshobson/agents

# Verify
/help
```

---

## Related Documentation

- **CLAUDE.md** - Project instructions for AI assistants
- **AGENTS.md** - Agent capabilities and patterns
- **docs/DEVELOPMENT.md** - Full developer reference
- **docs/USER_GUIDE.md** - End-user guide
- **docs/plans/** - Design documents and implementation plans
