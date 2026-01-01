# Code Scalpel

[![PyPI version](https://badge.fury.io/py/code-scalpel.svg)](https://pypi.org/project/code-scalpel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-4388%20passed-brightgreen.svg)](https://github.com/tescolopio/code-scalpel)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)](release_artifacts/README.md)

**MCP Server Toolkit for AI Agents - v3.3.0 "Configurable Token Efficiency"**

Code Scalpel enables AI assistants (Claude, GitHub Copilot, Cursor) to perform surgical code operations with mathematical precision, eliminating hallucinations through Abstract Syntax Trees (AST), Program Dependence Graphs (PDG), and Symbolic Execution.

## Why Code Scalpel? The Four Pillars

**🔬 Surgical Precision Through Graph Intelligence**

Traditional AI coding tools treat code as text and rely on context windows. Code Scalpel treats code as a **mathematical graph** - a deterministic pre-processor for probabilistic models.

### 💰 Cheaper: Reduce Context Window by 99%

Instead of feeding entire files to LLMs, Code Scalpel's **PDG-based extraction** surgically isolates only the relevant code:

```
Traditional: Send 10 files (15,000 tokens) → Model confused
Code Scalpel: Send function + 3 dependencies (200 tokens) → Precise fix
```

- **~150-200 tokens saved per MCP response** (configurable output filtering)
- **99% token reduction** via surgical extraction vs full file
- Operate on million-line codebases with 4K token models

### 🎯 Safer: Surgical Software Development

Code Scalpel performs **AST-validated modifications**, not string replacements:

- **Backup creation** before every change
- **Syntax validation** prevents syntax errors
- **Change budgets** enforce blast radius limits (Pro/Enterprise)
- **Policy engine** blocks dangerous patterns before execution (Enterprise)

Traditional tools do text edits and hope. Code Scalpel mathematically verifies modifications preserve AST structure.

### ✅ Accurate: Eliminate AI Hallucinations

ASTs, PDGs, and Symbolic Execution provide **deterministic code understanding**:

- **AST parsing**: Exact structure extraction (functions, classes, dependencies)
- **PDG taint tracking**: Precise vulnerability detection through variable flow
- **Symbolic execution (Z3)**: Mathematical path exploration generates provably correct test cases
- **Cross-file dependency graphs**: Exact import resolution, no guessing

**Impact**: AI agents make exact code changes with a major reduction in hallucinations. When Code Scalpel says "this function has 3 callers", it's mathematically proven, not an LLM guess.

### 🛡️ Governable: Enterprise-Ready Compliance

Code Scalpel includes **invisible governance** - enforcement happens automatically at the MCP boundary:

- **Cryptographic policy integrity** verification (Pro/Enterprise)
- **Change budgets** limit blast radius (max files, lines, complexity)
- **Compliance mapping** (OWASP, SOC2, PCI-DSS, HIPAA) - Enterprise only
- **Audit trails** for every operation (`.code-scalpel/audit.jsonl`)
- **Custom security policies** via OPA/Rego (Enterprise)

See [Governance Enforcement Status](docs/GOVERNANCE_ENFORCEMENT_STATUS.md) for full details.

🆕 **v3.3.0**: Fully configurable response output - teams control exactly which fields are returned, optimizing token efficiency for their specific use case.

---

## The Code Scalpel Advantage

**Most AI coding tools are probabilistic text generators.** They guess at code structure, estimate dependencies, and hope their edits don't break things.

**Code Scalpel is deterministic.** Through AST parsing, PDG taint analysis, and Z3 symbolic execution, it **mathematically proves** code structure, data flows, and execution paths. When Code Scalpel says "this function has 3 callers", it's not an LLM inference - it's a mathematical fact from the dependency graph.

### Real-World Impact

**For AI Agents:**
- Extract 200 tokens of relevant code instead of 15,000 tokens of full files
- Generate test cases that provably hit every branch (Z3 constraint solving)
- Detect vulnerabilities through precise taint tracking, not pattern matching
- Modify code with AST validation, preventing syntax errors before they happen

**For Development Teams:**
- **Community tier**: Free access to all 22 tools with baseline capabilities
- **Pro tier**: Unlimited findings, advanced features, cross-file analysis
- **Enterprise tier**: Compliance reporting, custom policies, organization-wide governance

**For Compliance:**
- Cryptographic policy integrity verification (HMAC-SHA256)
- Audit trails for every operation (`.code-scalpel/audit.jsonl`)
- OWASP, SOC2, PCI-DSS, HIPAA compliance mapping (Enterprise)

See [tier_capabilities_matrix.md](docs/reference/tier_capabilities_matrix.md) for complete feature comparison.

---

## Installation

### MCP-first (recommended)

Code Scalpel is **MCP-first**: the default install is the MCP server + core analyzers.

- Install core: `pip install code-scalpel`
- Install agent framework integrations (optional): `pip install "code-scalpel[agents]"`
- Install legacy REST/web adapter (optional): `pip install "code-scalpel[web]"`

**Note on the legacy REST/web adapter**: this is a backward-compatibility HTTP server (Flask) and is **not MCP-compliant**. For production usage, prefer the MCP server. If you do need the legacy REST adapter, run it in a separate virtual environment/container from the MCP server to avoid dependency conflicts with modern MCP runtime requirements.

```bash
pip install code-scalpel
```

Or with [uv](https://docs.astral.sh/uv/) (recommended for MCP):
```bash
uvx code-scalpel --help
```

## Tier Configuration

Code Scalpel offers three tiers: **Community** (free), **Pro**, and **Enterprise**.

> **🎉 All 22 MCP tools available at all tiers!** (v3.3.0+)
> 
> What differs is **capabilities and limits** within each tool, not tool availability.
> Try everything immediately, upgrade when you need more scale/features.

- **Community** (free): All 22 tools with baseline capabilities (e.g., 50 findings, 3 symbolic paths, k=1 graph hops)
- **Pro**: All 22 tools with advanced features (unlimited findings, 10 symbolic paths, k=5 graph hops, context-aware analysis, semantic neighbors)
- **Enterprise**: All 22 tools unlimited + organization-wide features, custom policies, compliance reporting, graph query language

**Configure your tier**:
```bash
# Community (default - no configuration needed)
code-scalpel mcp

# Pro (requires valid license file)
code-scalpel mcp --tier pro --license-file /path/to/license.jwt

# Enterprise (requires valid license file)
code-scalpel mcp --tier enterprise --license-file /path/to/license.jwt

# Alternative: point to a license file via env var
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
export CODE_SCALPEL_TIER=pro
code-scalpel mcp
```

**📖 Complete tier documentation**: 
- [Tier Configuration Guide](docs/TIER_CONFIGURATION.md) - Setup and configuration
- [Tier Capabilities Matrix](docs/reference/tier_capabilities_matrix.md) - What each tier gets
- [Community Tier Testing](docs/analysis/tool_validation/COMMUNITY_TIER_TOOL_TESTING.md) - Complete Community tier verification
- [Pro Tier Testing](docs/analysis/tool_validation/PRO_TIER_TOOL_TESTING.md) - Complete Pro tier verification
- [Enterprise Tier Testing](docs/analysis/tool_validation/ENTERPRISE_TIER_TOOL_TESTING.md) - Complete Enterprise tier verification

### Understanding Tier Differences

All tiers get **all 22 tools**. What differs is what each tool can do:

| Feature Category | Community (Free) | Pro | Enterprise |
|-----------------|------------------|-----|------------|
| **Tool Access** | All 22 tools ✅ | All 22 tools ✅ | All 22 tools ✅ |
| **Security Findings** | Max 50 per scan | Unlimited | Unlimited |
| **Symbolic Paths** | 3 paths, depth 5 | 10 paths, depth 10 | Unlimited |
| **Graph Traversal** | k=1 hop, 20 nodes | k=5 hops, 100 nodes | Unlimited with query language |
| **File Limits** | 100 files | 1,000 files | Unlimited |
| **Code Extraction** | Single-file only | + Cross-file (depth=1) | + Microservice extraction |
| **Context Awareness** | Basic AST | + Sanitizer recognition | + Custom policy engine |
| **Analysis Depth** | Basic complexity | + Cognitive complexity, code smells | + Custom rules, compliance |
| **Cross-File** | Direct imports | + Dependency chains | + Organization-wide |
| **Semantic Features** | ❌ | Semantic neighbors, logical relationships | + Graph query language |
| **Compliance** | ❌ | ❌ | OWASP, SOC2, PCI-DSS, HIPAA |
| **Custom Policies** | ❌ | ❌ | Full policy engine ✅ |

**When to Upgrade:**
- **Stick with Community** if: Small projects, learning, hobbyist use
- **Upgrade to Pro** if: Professional development, need context-aware scanning, working with larger codebases
- **Upgrade to Enterprise** if: Organization-wide deployment, compliance requirements, custom security policies, monorepo analysis

---

## First-Time Setup

After installation, initialize the configuration directory:

```bash
cd /your/project
code-scalpel init
```

If you are using Code Scalpel from a headless MCP client (e.g., Claude Desktop or ChatGPT) and you do not want users to run a CLI initializer, you can instead use MCP server env flags to auto-create `.code-scalpel/` in a user-level home directory. See the "Headless MCP Clients" section below.

This creates `.code-scalpel/` with governance configuration files:
- `config.yaml` - Unified governance configuration
- `policy.yaml` - OPA/Rego security policies (SQL injection, XSS blocking)
- `budgets.yaml` - Change budget limits (max files, lines, complexity)
- `dev-governance.yaml` - Development governance (AI agent behavior rules)
- `response_config.json` - MCP response output customization (NEW in v3.3.0)
- `response_config.schema.json` - JSON Schema for IDE validation (NEW in v3.3.0)
- `README.md` - Complete configuration guide

**Learn more:** [Governance Configuration](.code-scalpel/README.md) | [Policy Engine](src/code_scalpel/policy_engine/README.md)

---

## What's New in v3.3.0 🎉

### All 22 Tools at All Tiers
**The most requested feature is here!** Every tier now gets access to all 22 MCP tools. No more locked features - try everything from day one.

What changes across tiers:
- **Capabilities**: Community gets core features, Pro adds advanced analysis, Enterprise adds custom policies
- **Limits**: Community has baseline limits (50 findings, k=1 hops), Pro extends them (unlimited findings, k=5 hops), Enterprise removes limits entirely
- **Features**: Community provides solid foundation, Pro adds context-awareness and semantic analysis, Enterprise adds organization-wide features

**Tool Count by Version:**
- v3.0.0-v3.2.0: 20 tools (some locked behind tiers)
- v3.3.0+: 22 tools (all available to all tiers with capability/limit differences)

### Configurable Response Output (Token Efficiency)
Teams can now customize MCP tool responses via `.code-scalpel/response_config.json`:
- ✅ **3 Built-in Profiles** - minimal (default), standard, debug
- ✅ **Per-Tool Customization** - Configure each of 21 tools independently
- ✅ **Tier-Aware Filtering** - Automatically exclude tier-inappropriate fields
- ✅ **~150-200 tokens saved per response** - Preserves context for actual code work
- ✅ **JSON Schema Support** - IDE autocomplete and validation

**Example minimal response** (just the data you need):
```json
{
  "data": {
    "functions": ["test", "helper"],
    "classes": ["Calculator"],
    "complexity": 2
  }
}
```

**Learn more:** [Configurable Response Guide](docs/guides/configurable_response_output.md)

### Surgical Extractor Enhancements (v3.2.0)
Token-efficient code extraction now even more powerful:
- ✅ **Accurate Token Counting** - tiktoken integration for GPT-4/3.5/Claude
- ✅ **Rich Metadata** - Extract docstrings, signatures, decorators, async/generator detection
- ✅ **LLM-Ready Prompts** - `to_prompt()` formats extractions for AI consumption
- ✅ **Token Budget Management** - `trim_to_budget()` intelligently fits token limits
- ✅ **Decorator Extraction** - Extract and analyze decorator definitions
- ✅ **Impact Analysis** - `find_callers()` discovers all code calling a function
- ✅ **Performance Caching** - 2.8x faster with LRU cache

**Example:**
```python
from code_scalpel.surgical_extractor import SurgicalExtractor

extractor = SurgicalExtractor.from_file("app.py")
result = extractor.get_function("process_payment")
print(f"Tokens: {result.token_estimate}")
print(f"Async: {result.is_async}, Generator: {result.is_generator}")
print(f"Decorators: {result.decorators}")

# Find who calls this function (impact analysis)
callers = extractor.find_callers("process_payment")
for name, typ, line in callers:
    print(f"{typ} {name} calls it at line {line}")

# Format for LLM with budget constraint
extraction = extractor.get_function_with_context("process_payment")
prompt = extraction.to_prompt("Add error handling")
trimmed = extraction.trim_to_budget(max_tokens=2000)
```

See [examples/surgical_extractor_enhanced_example.py](examples/surgical_extractor_enhanced_example.py) for full demos.

---

## Quick Start by Server Type

Code Scalpel supports multiple transport methods. Choose based on your use case:

| Transport | Best For | Command |
|-----------|----------|---------|
| **stdio** | Claude Desktop, VS Code, Cursor | `uvx code-scalpel mcp` |
| **HTTP** | Remote access, team servers | `code-scalpel mcp --http --port 8593` |
| **Docker** | Isolated environments, CI/CD | `docker run -p 8593:8593 code-scalpel` |

### Option 1: VS Code / GitHub Copilot (stdio)

Create `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio",
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "${workspaceFolder}"]
    }
  }
}
```

Then in VS Code: `Ctrl+Shift+P` → "MCP: List Servers" → Start code-scalpel

### Option 2: Claude Desktop (stdio)

Add to `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "C:\\Projects\\myapp"]
    }
  }
}
```

#### Headless MCP Clients (no IDE)

If you want governance and licensing files to have a stable home *without* requiring the user to run `code-scalpel init`, configure the MCP server process to auto-init into the user config directory.

Key environment variables:
- `SCALPEL_AUTO_INIT=1` enables auto-init.
- `SCALPEL_AUTO_INIT_TARGET=user` creates `$XDG_CONFIG_HOME/code-scalpel/.code-scalpel/` (fallback: `~/.config/code-scalpel/.code-scalpel/`).
- `SCALPEL_AUTO_INIT_MODE=templates_only` creates templates only (no `.env` / no `policy.manifest.json`).
- `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block` controls how strictly the MCP server enforces governance at tool boundaries.
  - Default if unset: Community=`warn`, Pro/Enterprise=`block`.
- `SCALPEL_GOVERNANCE_BREAK_GLASS=1` (Pro/Enterprise only) allows temporarily relaxing enforcement below `block`.

Example (Claude Desktop):

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": [
        "code-scalpel",
        "mcp",
        "--auto-init",
        "--auto-init-target",
        "user",
        "--auto-init-mode",
        "templates_only"
      ],
      "env": {
        "SCALPEL_GOVERNANCE_ENFORCEMENT": "warn",
        "SCALPEL_GOVERNANCE_BREAK_GLASS": "1"
      }
    }
  }
}
```

Notes:
- To pin the user-level home explicitly, set `SCALPEL_HOME` (otherwise XDG defaults are used).
- To override where policies are read from at runtime, set `SCALPEL_POLICY_DIR`.

### Option 3: HTTP Server (Remote/Team)

```bash
# Start HTTP server on port 8593
code-scalpel mcp --http --port 8593

# With LAN access for team
code-scalpel mcp --http --port 8593 --allow-lan

# Health check endpoint (port 8594)
curl http://localhost:8594/health
```

Connect from VS Code:
```json
{
  "servers": {
    "code-scalpel": {
      "type": "http",
      "url": "http://localhost:8593/mcp"
    }
  }
}
```

### Option 4: Docker (Isolated/CI)

```bash
# Run with project mounted
docker run -d \
  --name code-scalpel \
  -p 8593:8593 \
  -p 8594:8594 \
  -v /path/to/project:/project \
  ghcr.io/tescolopio/code-scalpel:3.0.0

# Verify health
curl http://localhost:8594/health
# {"status":"healthy","version":"3.3.0","tools":22}

# Connect via HTTP transport
```

**Docker Compose:**
```yaml
services:
  code-scalpel:
    image: ghcr.io/tescolopio/code-scalpel:3.0.0
    ports:
      - "8593:8593"
      - "8594:8594"
    volumes:
      - ./:/project
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8594/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Option 5: Cursor IDE

Add to Cursor settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"]
    }
  }
}
```

---

> **v3.0.0 "AUTONOMY" RELEASE** (December 18, 2025)  
> Comprehensive Coverage, Stability, and Autonomy Foundation
>
> | Component | Status | Notes |
> |-----------|--------|-------|
> | Languages | **4** | Python, TypeScript, JavaScript, Java |
> | Security Scanning | **17+ types** | SQL, XSS, NoSQL, LDAP, DOM XSS, Prototype Pollution |
> | Cross-File Analysis | **STABLE** | Import resolution, taint tracking, extraction |
> | MCP Protocol | **COMPLETE** | Health endpoint, Progress tokens, Roots capability |
> | Token Efficiency | **99%** | Surgical extraction vs full file |
> | Response Optimization | **CONFIGURABLE** | ~150-200 tokens saved per call (v3.3.0) |
> | Performance | **25,000+ LOC/sec** | Project-wide analysis |
> | MCP Tools | **22 tools** | All tools available at all tiers (v3.3.0+) |
> | Test Suite | **4,033 tests** | 94.86% combined coverage |
> | Tier System | **3 tiers** | Community (free), Pro, Enterprise |
>
> See [RELEASE_NOTES_v3.0.0.md](docs/release_notes/RELEASE_NOTES_v3.0.0.md) for full details.

---

## How It Works: AST + PDG + Symbolic Execution

Code Scalpel combines three mathematical approaches to eliminate guesswork from AI code generation:

### 1. Abstract Syntax Trees (AST) - Structural Intelligence

**What it does**: Parses code into a mathematical tree structure representing the exact syntax.

**Why it matters**:
- Extract functions/classes with zero ambiguity
- Validate edits preserve syntax before applying
- Navigate code structure without regex pattern matching

**Tools using AST**: `analyze_code`, `extract_code`, `update_symbol`, `rename_symbol`

### 2. Program Dependence Graphs (PDG) - Data Flow Analysis

**What it does**: Maps how data flows through variables, tracking tainted data from sources to sinks.

**Why it matters**:
- Detect vulnerabilities by following tainted data (SQL injection, XSS)
- Understand which code depends on which (impact analysis)
- Surgical extraction: only include code that's actually used

**Tools using PDG**: `security_scan`, `cross_file_security_scan`, `get_call_graph`, `get_cross_file_dependencies`

**Example**:
```python
# PDG tracks: user_input → query → execute (SQL injection detected)
user_input = request.GET['id']  # Source: untrusted data
query = f"SELECT * FROM users WHERE id={user_input}"  # Tainted
cursor.execute(query)  # Sink: SQL execution with tainted data
```

### 3. Symbolic Execution (Z3 Solver) - Path Exploration

**What it does**: Uses constraint solving to explore all possible execution paths mathematically.

**Why it matters**:
- Generate test cases that hit every branch (100% path coverage)
- Detect dead code and impossible conditions
- Verify refactoring preserves behavior

**Tools using Symbolic Execution**: `symbolic_execute`, `generate_unit_tests`, `simulate_refactor`

**Example**:
```python
def loan_approval(credit_score, income):
    if credit_score < 600:
        return "REJECT"
    if income > 100000:
        return "INSTANT"
    return "STANDARD"

# Z3 generates:
# Test 1: credit_score=599 → "REJECT"
# Test 2: credit_score=700, income=100001 → "INSTANT"
# Test 3: credit_score=700, income=50000 → "STANDARD"
```

### The Result: Deterministic Code Intelligence

| Traditional AI Tools | Code Scalpel |
|---------------------|--------------|
| "Here are 50 files. Good luck." | "Here's the function, 3 callers, 1 test. Nothing else." |
| Retrieve similar text (fuzzy) | Trace dependencies (exact) |
| Context limit is a wall | Surgical slicing fits any budget |
| "I think this fixes it" | "Z3 verified this path" |
| String replacement | AST-validated modification |
| LLM guesses callers | PDG proves callers |

### From Chatbot to Autonomous Operator

Code Scalpel enables the **OODA Loop** for AI agents:

1. **Observe**: `analyze_code` → Map structure via AST
2. **Orient**: `extract_code` → PDG isolates relevant code
3. **Decide**: `symbolic_execute` → Z3 verifies fix mathematically
4. **Act**: `update_symbol` → AST validates and applies change

---

## Quick Comparison

| Feature | Traditional Tools | Code Scalpel |
|---------|------------------|--------------|
| Pattern matching (regex) | [COMPLETE] | **Taint tracking** through variables |
| Single file analysis | [COMPLETE] | **Cross-file** dependency graphs |
| Manual test writing | [COMPLETE] | **Z3-powered** test generation |
| Generic output | [COMPLETE] | **AI-optimized** structured responses |
| Context strategy | Stuff everything | **Surgical slicing** |

---

## Quick Demo

### 1. Security: Find Hidden Vulnerabilities

```python
# The SQL injection is hidden through 3 variable assignments
# Regex linters miss this. Code Scalpel doesn't.

code-scalpel scan demos/vibe_check.py
# → SQL Injection (CWE-89) detected at line 38
#   Taint path: request.args → user_id → query_base → final_query
```

### 2. Secret Scanning: Detect Hardcoded Secrets

```python
# Detects AWS Keys, Stripe Secrets, Private Keys, and more
# Handles bytes, f-strings, and variable assignments

code-scalpel scan demos/config.py
# → Hardcoded Secret (AWS Access Key) detected at line 12
# → Hardcoded Secret (Stripe Secret Key) detected at line 45
```

### 3. Analysis: Understand Complex Code

```python
from code_scalpel import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.analyze("""
def loan_approval(income, debt, credit_score):
    if credit_score < 600:
        return "REJECT"
    if income > 100000 and debt < 5000:
        return "INSTANT_APPROVE"
    return "STANDARD"
""")

print(f"Functions: {result.metrics.num_functions}")
print(f"Complexity: {result.metrics.cyclomatic_complexity}")
```

### 4. Test Generation: Cover Every Path

```bash
# Z3 solver derives exact inputs for all branches
code-scalpel analyze demos/test_gen_scenario.py

# Generates:
# - test_reject: credit_score=599
# - test_instant_approve: income=100001, debt=4999, credit_score=700
# - test_standard: income=50000, debt=20000, credit_score=700
```

## MCP Tools Reference (22 Total)

> **v3.3.0 Update:** All 22 tools available at all tiers. What differs are the capabilities and limits within each tool.

### Complete Tool Inventory

Code Scalpel provides **22 MCP tools** organized into 5 categories. Every tool leverages AST/PDG/Symbolic execution for deterministic code intelligence.

**Core Analysis & Surgery (8 tools)** - AST-based code understanding and modification
| Tool | Technology | Community | Pro | Enterprise |
|------|-----------|-----------|-----|------------|
| `analyze_code` | AST | Parse structure, basic complexity | + Code smells, Halstead, cognitive complexity | + Custom rules, naming conventions, compliance |
| `extract_code` | AST + PDG | Single-file extraction | + Cross-file deps (depth=1), variable promotion | + Unlimited depth, microservice extraction, Dockerfiles |
| `update_symbol` | AST | Safe replacement with validation | + Advanced refactoring patterns | + Organization-wide updates |
| `rename_symbol` | AST + PDG | Definition rename only | + Cross-file references/imports (bounded) | + Organization-wide rename (unlimited) |
| `symbolic_execute` | Z3 Solver | 3 paths, depth 5 | 10 paths, depth 10, string/float support | Unlimited paths/depth, formal verification |
| `generate_unit_tests` | Z3 Solver | 3 test cases | 10 test cases, advanced patterns | Unlimited tests, custom frameworks |
| `simulate_refactor` | Z3 Solver | Behavior preservation check | + Change impact analysis | + Formal equivalence checking |
| `crawl_project` | AST | 100 files, discovery mode | 1000 files, deep parsing | Unlimited files, org-wide indexing |

**Context & Graph Navigation (7 tools)** - PDG-based dependency analysis
| Tool | Technology | Community | Pro | Enterprise |
|------|-----------|-----------|-----|------------|
| `get_file_context` | AST | 20 nodes of context | 100 nodes + rich metadata | Unlimited + custom patterns |
| `get_symbol_references` | PDG | Find usages (100 refs) | Advanced filtering (1000 refs) | Organization-wide search (unlimited) |
| `get_call_graph` | PDG | 50 nodes, basic graph | 500 nodes, advanced analysis | Unlimited depth, custom queries |
| `get_graph_neighborhood` | PDG | k=1 hop, 20 nodes | k=5 hops, 100 nodes, semantic neighbors | Unlimited + graph query language |
| `get_project_map` | AST | 100 files, structure | 1000 files, detailed architecture | Enterprise-scale (unlimited) |
| `get_cross_file_dependencies` | PDG | Direct imports (100 files) | Dependency chains (1000 files) | Organization-wide resolution (unlimited) |

**Security Analysis (4 tools)** - PDG taint tracking for vulnerability detection
| Tool | Technology | Community | Pro | Enterprise |
|------|-----------|-----------|-----|------------|
| `security_scan` | PDG Taint | OWASP Top 10 (50 findings max) | Unlimited + sanitizer recognition | + Compliance (SOC2, HIPAA), custom policies |
| `unified_sink_detect` | PDG Taint | Polyglot sink detection | + Confidence scoring | + Custom sink patterns |
| `cross_file_security_scan` | PDG Taint | Single-file (50 findings) | Cross-file taint (unlimited) | Organization-wide + custom policies |
| `type_evaporation_scan` | AST | TypeScript type checking | + Network boundary analysis | + Schema gen (Zod/Pydantic), API validation |
| `scan_dependencies` | OSV API | 100 deps, CVE detection | 1000 deps + risk scoring | Unlimited + custom vulnerability DBs |

**Governance & Compliance (3 tools)** - Policy enforcement and validation
| Tool | Technology | Community | Pro | Enterprise |
|------|-----------|-----------|-----|------------|
| `verify_policy_integrity` | Crypto | Policy file verification | Integrity checks + HMAC | Cryptographic audit trails |
| `code_policy_check` | OPA/Rego | Basic policy checking | Advanced enforcement | Custom compliance frameworks |
| `validate_paths` | Filesystem | Basic path validation | Advanced validation | Organization-wide validation |

### Technology Stack per Tool Category

- **AST Tools** (9 tools): `analyze_code`, `extract_code`, `update_symbol`, `rename_symbol`, `crawl_project`, `get_file_context`, `get_project_map`, `type_evaporation_scan`, `validate_paths`
- **PDG Tools** (8 tools): `get_symbol_references`, `get_call_graph`, `get_graph_neighborhood`, `get_cross_file_dependencies`, `security_scan`, `unified_sink_detect`, `cross_file_security_scan`, `rename_symbol` (hybrid)
- **Z3 Symbolic Execution** (3 tools): `symbolic_execute`, `generate_unit_tests`, `simulate_refactor`
- **External APIs** (1 tool): `scan_dependencies` (OSV vulnerability database)
- **Cryptographic** (1 tool): `verify_policy_integrity` (HMAC-SHA256)

### Tier Capability Matrix

**Community Tier (Free)**
- ✅ All 22 tools available
- ✅ OWASP Top 10 security scanning
- ✅ Basic AST analysis and complexity metrics
- ✅ Symbolic execution (3 paths, depth 5)
- ✅ Single-file code extraction
- ✅ Direct neighbor graph traversal (k=1)
- ⚠️ Limited to 50 findings, 100 files, 20 nodes

**Pro Tier**
- ✅ Everything in Community, plus:
- ✅ Context-aware scanning with sanitizer recognition
- ✅ Advanced symbolic execution (10 paths, depth 10, string/float support)
- ✅ Cross-file dependency resolution (depth=1)
- ✅ Variable promotion and closure detection
- ✅ Semantic neighbors and logical relationships
- ✅ Extended graph traversal (k=5 hops, 100 nodes)
- ✅ Code smells and cognitive complexity
- ✅ Unlimited security findings
- ⚠️ Limited to 1000 files, 500 graph nodes

**Enterprise Tier**
- ✅ Everything in Pro, plus:
- ✅ Custom policy engine with org-specific rules
- ✅ Microservice extraction with Dockerfile generation
- ✅ Organization-wide symbol resolution (monorepo-aware)
- ✅ Graph query language for custom traversals
- ✅ Formal verification and equivalence checking
- ✅ Compliance reporting (OWASP, SOC2, PCI-DSS, HIPAA)
- ✅ Cryptographic audit trails
- ✅ Unlimited depth, files, nodes, and findings
- ✅ Custom extraction patterns and service boundary detection
- ✅ Schema generation (Zod/Pydantic) and API contract validation

### Quick Examples by Tier

**Community Example: Basic Security Scan**
```bash
# Detect OWASP Top 10 vulnerabilities
code-scalpel scan app.py
# → SQL Injection (CWE-89) at line 42
# → Max 50 findings
```

**Pro Example: Context-Aware Scanning**
```bash
# Recognizes sanitizers - reduces false positives
code-scalpel scan payment_service.py
# → Sanitizer detected: sanitize_input() at line 15
# → SQL Injection suppressed (data sanitized)
# → Unlimited findings
```

**Enterprise Example: Custom Policy Enforcement**
```bash
# Enforce org-specific rules
code-scalpel scan --policy .code-scalpel/custom-policy.rego
# → Compliance violation: All logs must be encrypted (line 67)
# → Naming convention: Use camelCase for methods (line 102)
# → Full compliance report generated
```

## Features

### Polyglot Analysis
- **Python**: Full AST + PDG + Symbolic Execution
- **JavaScript**: Tree-sitter parsing + IR normalization
- **Java**: Enterprise-ready cross-file analysis

### Security Analysis (Tier-Aware)

**Community Tier - OWASP Top 10 (50 findings max)**
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79) - Flask/Django sinks
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Code Injection (CWE-94) - eval/exec
- Insecure Deserialization (CWE-502) - pickle
- SSRF (CWE-918)
- Weak Cryptography (CWE-327) - MD5/SHA1
- Hardcoded Secrets (CWE-798) - 30+ patterns (AWS, GitHub, Stripe, private keys)
- NoSQL Injection (CWE-943) - MongoDB PyMongo/Motor
- LDAP Injection (CWE-90) - python-ldap/ldap3

**Pro Tier - Context-Aware Scanning (Unlimited findings)**
- ✅ All Community features, plus:
- Sanitizer recognition - Reduces false positives by detecting sanitize() calls
- Confidence scoring - Per-vulnerability confidence ratings (0.7-0.9)
- Data-flow sensitive analysis - Tracks tainted data across assignments
- False positive reduction - Metadata about suppressed findings
- Remediation suggestions - Actionable fix recommendations

**Enterprise Tier - Custom Policy Engine (Unlimited)**
- ✅ All Pro features, plus:
- Custom policy engine - Enforce org-specific security rules
- Cross-file taint tracking - Detect vulnerabilities spanning modules
- Compliance reporting - OWASP, SOC2, PCI-DSS, HIPAA mappings
- Organization-specific rules - "All logs must be encrypted", custom patterns
- Priority CVE alerts - Critical vulnerability notifications
- Cryptographic audit trails - HMAC-signed audit logs

### Governance & Policy System (v2.5.0+)

Code Scalpel provides **invisible governance**: enforcement happens automatically at the MCP boundary before tools execute, without requiring explicit tool calls.

#### Enforcement by Tier

| Governance Feature | Community | Pro | Enterprise |
|--------------------|-----------|-----|------------|
| Response shaping (`response_config.json`) | ✅ | ✅ | ✅ |
| Tier limits (`limits.toml`) | ✅ | ✅ | ✅ |
| Policy integrity (`policy.manifest.json`) | ❌ | ✅ Auto | ✅ Auto |
| Change budgets (`budget.yaml`) | ❌ | ✅ Auto | ✅ Auto |
| Policy evaluation (`policy.yaml`) | ❌ | ✅ Opt-in | ✅ Opt-in |
| Audit logging (`audit.jsonl`) | ❌ | ✅ Auto | ✅ Auto |

#### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `SCALPEL_GOVERNANCE_ENFORCEMENT` | `off\|warn\|block` | Global enforcement posture (default: `off` for Community, `block` for Pro/Enterprise) |
| `SCALPEL_GOVERNANCE_FEATURES` | comma-separated | Feature gates: `policy_integrity,budget,policy_evaluation,response_config,limits` |
| `SCALPEL_GOVERNANCE_BREAK_GLASS` | `1` | Pro/Enterprise only: allows `warn` mode to proceed (otherwise `warn` behaves as `block`) |
| `SCALPEL_GOVERNANCE_AUDIT` | `0\|1` | Enable/disable audit logging (default: `1`) |
| `SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY` | `1` | Only enforce governance on write tools (`update_symbol`, `rename_symbol`) |

#### Governance Files Reference

**`.code-scalpel/policy.manifest.json`** - Policy Integrity Verification
```bash
# Pro/Enterprise: Auto-verified before every tool call
# Requires SCALPEL_MANIFEST_SECRET env var for cryptographic verification

# Generate manifest (admin task)
code-scalpel manifest create --policy-dir .code-scalpel --secret $SECRET

# Verify manually
code-scalpel manifest verify --policy-dir .code-scalpel
```

**`.code-scalpel/budget.yaml`** - Change Budget Limits
```yaml
# Enforced automatically on write tools (Pro/Enterprise)
budgets:
  default:
    max_files: 10
    max_lines_per_file: 100
    max_total_lines: 500
    max_complexity_increase: 50
    allowed_file_patterns: ["*.py", "*.js", "*.ts"]
    forbidden_paths: [".git/", "node_modules/", "__pycache__/"]
```

**`.code-scalpel/policy.yaml`** - OPA/Rego Policy Rules
```yaml
# Opt-in via SCALPEL_GOVERNANCE_FEATURES=policy_evaluation
policies:
  - name: prevent-sql-injection
    description: Block raw SQL string concatenation
    severity: CRITICAL
    action: DENY
    rule: |
      package code_scalpel.security
      deny[msg] {
        input.operation == "code_edit"
        contains(input.code, "execute(")
        not contains(input.code, "parameterized")
        msg := "SQL injection risk: use parameterized queries"
      }
```

**`.code-scalpel/response_config.json`** - Response Token Optimization
```json
{
  "version": "1.0",
  "profile": "minimal",
  "tool_overrides": {
    "security_scan": {
      "include_fields": ["vulnerabilities", "severity", "cwe_id"]
    }
  }
}
```

**`.code-scalpel/limits.toml`** - Tier/Tool Capability Limits
```toml
# Project-level limits (override package defaults)
[community]
max_findings = 50
max_files = 100
symbolic_max_paths = 3

[pro]
max_findings = -1  # unlimited
max_files = 1000
symbolic_max_paths = 10
```

**`.code-scalpel/audit.jsonl`** - Audit Trail (auto-generated)
```jsonl
{"ts":1735689600,"tool_id":"update_symbol","tier":"pro","check":"budget","decision":"allow"}
{"ts":1735689601,"tool_id":"update_symbol","tier":"pro","check":"policy_integrity","decision":"deny","reason":"SCALPEL_MANIFEST_SECRET not set"}
```

#### Example: Enable Full Governance (Pro/Enterprise)

```bash
# Enable all governance features with strict enforcement
export SCALPEL_GOVERNANCE_ENFORCEMENT=block
export SCALPEL_GOVERNANCE_FEATURES=policy_integrity,budget,policy_evaluation
export SCALPEL_MANIFEST_SECRET=your-secret-key
export SCALPEL_GOVERNANCE_AUDIT=1

# Start MCP server
code-scalpel mcp --tier pro --license-file /path/to/license.jwt
```

#### Example: Relax Governance Temporarily (Break-Glass)

```bash
# Pro/Enterprise: Allow operations with warnings instead of blocking
export SCALPEL_GOVERNANCE_ENFORCEMENT=warn
export SCALPEL_GOVERNANCE_BREAK_GLASS=1

# Now write tools will proceed but emit warnings in the response envelope
```

#### Validation Tests

```bash
# Run governance test suite to verify enforcement
pytest -q tests/test_governance_invisible_enforcement.py
pytest -q tests/test_governance_budget_enforcement.py
pytest -q tests/test_governance_policy_evaluation_enforcement.py
pytest -q tests/test_governance_tier_gating.py
```

See [Governance Enforcement Status](docs/GOVERNANCE_ENFORCEMENT_STATUS.md) for detailed enforcement documentation.
See [Policy Engine Documentation](src/code_scalpel/policy_engine/README.md) for OPA/Rego policy details.

### API Contract & Cross-Service Analysis (v3.0.4)
- **Schema Drift Detection** - Protobuf, JSON Schema, GraphQL breaking change detection
- **gRPC Contract Analyzer** - Service definition parsing and validation
- **GraphQL Schema Tracker** - Schema evolution and drift detection
- **Kafka Taint Tracking** - Cross-service async message taint analysis
- **Frontend DOM Input Detection** - XSS risk analysis for React/Vue/Angular

### Performance
- **200x cache speedup** for unchanged files
- **5-second Z3 timeout** prevents hangs
- Content-addressable caching with version invalidation

## CLI Reference

```bash
# Analyze code structure
code-scalpel analyze app.py
code-scalpel analyze src/ --json

# Security scan
code-scalpel scan app.py
code-scalpel scan --code "cursor.execute(user_input)"

# Start MCP server
code-scalpel mcp                              # stdio (Claude Desktop)
code-scalpel mcp --http --port 8593           # HTTP (network)
code-scalpel mcp --root /project --allow-lan  # Team deployment
```

## Docker Deployment

```bash
# Build
docker build -t code-scalpel .

# Run MCP server
docker run -p 8593:8593 -v $(pwd):/app/code code-scalpel

# Connect at http://localhost:8593/mcp
```

## Documentation

### Quick Start
- **[Getting Started](docs/getting_started/getting_started.md)** - Step-by-step setup and first steps
- **[Documentation Index](docs/INDEX.md)** - Master table of contents for all docs
- **[Examples](examples/)** - Runnable integration examples

### For Contributors
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup, workflow, and guidelines
- **[Development Roadmap](DEVELOPMENT_ROADMAP.md)** - Project roadmap and future plans

### Current Release (v3.0.4)
- [Release Notes v3.0.4](docs/release_notes/RELEASE_NOTES_v3.0.4.md) - Stage 3 API Contract & Cross-Service features
- [Release Notes v3.0.0](docs/release_notes/RELEASE_NOTES_v3.0.0.md) - Autonomy release
- [Migration Guide v2.5→v3.0](docs/guides/migration/MIGRATION_GUIDE.md) - Upgrade from v2.5.0
- [API Changes v3.0.0](docs/release_notes/API_CHANGES_v3.0.0.md) - Complete API reference
- [Known Issues v3.0.0](docs/release_notes/KNOWN_ISSUES_v3.0.0.md) - Limitations and workarounds

### Core Features
- **[Policy Engine](src/code_scalpel/policy_engine/README.md)** - Enterprise governance with OPA/Rego
- **[Governance System](src/code_scalpel/governance/README.md)** - Unified governance orchestration
- **[Change Budgets](src/code_scalpel/policy_engine/README.md)** - Blast radius control
- **[Graph Engine](docs/guides/graph_engine_guide.md)** - Unified graph analysis
- **[Polyglot Parsers](docs/parsers/DOCUMENTATION_INDEX.md)** - Multi-language support

### Integration & Deployment
- **[AI Agent Integration](docs/guides/agent_integration.md)** - Autogen, CrewAI, LangChain
- **[Docker Quick Start](DOCKER_QUICK_START.md)** - Docker deployment
- **[Deployment Guides](docs/deployment/)** - Production deployment procedures

### Security & Compliance
- **[SECURITY.md](SECURITY.md)** - Security policies and vulnerability reporting
- **[Compliance Documentation](docs/compliance/)** - OWASP, CWE, NIST, PCI DSS, SOC2

## Ninja Warrior Acceptance Harness (Opt-in)

Code Scalpel includes an opt-in acceptance harness that validates MCP behavior across transports against the `Code-Scalpel-Ninja-Warrior` monorepo.

```bash
cd code-scalpel
. .venv/bin/activate

# Fast acceptance (stdio + HTTP + SSE)
RUN_NINJA_WARRIOR=1 \
NINJA_WARRIOR_ROOT=/absolute/path/to/Code-Scalpel-Ninja-Warrior \
python -m pytest -q -m ninja_warrior tests/test_ninja_warrior_acceptance_harness.py

# Heavy mode (adds crawl/map/call-graph)
RUN_NINJA_WARRIOR=1 RUN_NINJA_WARRIOR_HEAVY=1 \
NINJA_WARRIOR_ROOT=/absolute/path/to/Code-Scalpel-Ninja-Warrior \
python -m pytest -q -m ninja_warrior tests/test_ninja_warrior_acceptance_harness.py -k heavy
```

Evidence output:
- Default: `evidence/ninja-warrior/` (gitignored)
- Override: set `NINJA_WARRIOR_EVIDENCE_DIR=/path/to/output`
- Each run emits a JSON evidence report plus (for HTTP/SSE) server logs, including both repo git SHAs (best-effort) for traceability.

## MCP Contract Tests (All Tools, All Transports)

Code Scalpel includes a deterministic contract test that calls **all 20 MCP tools** over:
- `stdio`
- streamable HTTP (`/mcp`)
- SSE (`/sse`)

```bash
cd code-scalpel
. .venv/bin/activate
python -m pytest -q tests/test_mcp_all_tools_contract.py
```

Evidence output:
- Default: `evidence/mcp-contract/` (gitignored)
- Override: set `MCP_CONTRACT_ARTIFACT_DIR=/path/to/output`

Run a single transport (useful for CI or debugging):

```bash
MCP_CONTRACT_TRANSPORT=stdio python -m pytest -q tests/test_mcp_all_tools_contract.py
MCP_CONTRACT_TRANSPORT=streamable-http python -m pytest -q tests/test_mcp_all_tools_contract.py
MCP_CONTRACT_TRANSPORT=sse python -m pytest -q tests/test_mcp_all_tools_contract.py
```

CI also runs Pyright type checking:

```bash
pyright -p pyrightconfig.json
```

## Roadmap

See [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the complete roadmap.

> [20251218_DOCS] Release notes pointer updated for v3.0.0 "Autonomy"

- Latest release notes: [docs/release_notes/RELEASE_NOTES_v3.0.0.md](docs/release_notes/RELEASE_NOTES_v3.0.0.md)

| Version | Status | Release Date | Highlights |
|---------|--------|--------------|------------|
| **v1.5.x** | Released | Dec 13, 2025 | Cross-file analysis, context tools, project intelligence |
| **v2.0.0** | Released | Dec 15, 2025 | **Polyglot** - TypeScript, JavaScript, Java support |
| **v2.5.0** | Released | Dec 17, 2025 | **Guardian** - Policy engine, governance controls |
| **v3.0.0** | Released | Dec 18, 2025 | **Autonomy** - Self-correction, 4033 tests, 94.86% coverage |
| **v3.1.1** | Released | Dec 22, 2025 | **Parser Unification** - Unified extractor, richer docs, init hotfix |
| **v3.2.0** | Released | Dec 25, 2025 | **Enhanced Extraction** - Token counting, metadata, impact analysis |
| **v3.3.0** | Current | Dec 30, 2025 | **All Tools, All Tiers** - 22 tools accessible to all tiers, configurable responses |
| **v3.4.0** | Planned | Q1 2026 | **Release Solidification** - MCP contract tests + blocking CI confidence gates |

**Strategic Focus:** MCP server toolkit enabling AI agents to perform surgical code operations without hallucination.

## Stats

**Release v3.3.0 "Configurable Token Efficiency"**

### Quality Metrics
- **4,388** tests passing (100% pass rate)
- **94%** combined coverage (statement + branch)
- **100%** coverage: PDG, AST, Symbolic Execution, Security Analysis, Cross-File Analysis
- **Python 3.10-3.13** compatible

### Capabilities
- **22** MCP tools for AI agents (all available at all tiers)
- **4** languages supported: Python, TypeScript, JavaScript, Java
- **3** tier levels: Community (free), Pro, Enterprise
- **17+** vulnerability types detected: SQL, XSS, NoSQL, LDAP, DOM XSS, Prototype Pollution, secrets
- **30+** secret detection patterns: AWS, GitHub, Stripe, private keys, API keys

### Performance
- **~150-200** tokens saved per MCP response (configurable output filtering)
- **99%** token reduction via surgical extraction vs full-file retrieval
- **200x** cache speedup for unchanged files
- **25,000+** lines of code per second (project-wide analysis)

### Technology Stack
- **AST Parsing**: Python (ast), JavaScript/TypeScript (tree-sitter), Java (tree-sitter)
- **PDG Taint Analysis**: Custom data-flow engine with cross-file tracking
- **Symbolic Execution**: Z3 SMT solver (5-second timeout)
- **Governance**: OPA/Rego policy engine, HMAC-SHA256 integrity verification
- **Vulnerability DB**: OSV API for CVE/GHSA lookups

## License

MIT License - see [LICENSE](LICENSE)

"Code Scalpel" is a trademark of 3D Tech Solutions LLC.

---

**Built for the AI Agent Era** | [PyPI](https://pypi.org/project/code-scalpel/) | [GitHub](https://github.com/tescolopio/code-scalpel)

<!-- mcp-name: io.github.tescolopio/code-scalpel -->
