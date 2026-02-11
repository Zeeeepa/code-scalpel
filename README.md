# Code Scalpel: Reduce AI Costs by 200x

**Latest Release: v1.3.5 | February 10, 2026**

**Stop copy-pasting entire files into Claude.** Give your AI assistant surgical code analysis tools and reduce costs by 200x.

**Result:** $450/month → $22/month. Same quality answers, 95% lower cost, 10x faster responses.

![Free Forever](https://img.shields.io/badge/Free-Forever-brightgreen) ![Setup Time](https://img.shields.io/badge/Setup-2%20Minutes-blue) ![Local Execution](https://img.shields.io/badge/Runs-Locally-orange) ![Tools](https://img.shields.io/badge/Tools-23-purple)

---

## What Is Code Scalpel? (30-Second Version)

Code Scalpel is an **MCP (Model Context Protocol) server** that gives AI assistants like Claude, GitHub Copilot, and Cursor the ability to **surgically extract and analyze code** instead of reading entire files.

### Before Code Scalpel ❌
```python
# You paste entire 500-line file into Claude
# Tokens: 10,247 tokens
# Cost: $0.030 per query
# Time: 12 seconds
# Claude has to read everything, even irrelevant code
```

### After Code Scalpel ✅
```python
# Ask: "Use Code Scalpel to extract calculate_tax function"
# Claude uses extract_code tool automatically
# Tokens: 287 tokens (just the function you need)
# Cost: $0.0009 per query  
# Time: 2 seconds
```

**Savings:** 97% cost reduction, 83% time reduction, zero workflow changes.

---

## New? Start Here 👋

**Never used Code Scalpel?** Get started in 3 steps:

1. **[📖 What is this?](docs/website/docs/getting-started/start-here.md)** — Understand Code Scalpel in 10 seconds with visual examples
2. **[⚡ 2-Minute Setup](docs/website/docs/getting-started/claude-desktop-2min.md)** — Install and configure Claude Desktop in under 2 minutes
3. **Ask your AI assistant** — "Use Code Scalpel to extract [function_name] from [file.py]"

**That's it.** You'll see 200x token reduction on your first query.

---

## Who Is This For?

Code Scalpel serves 4 primary user types:

### 👤 **Individual Developers** (Cost Reduction Focus)
**You're spending $50-450/month on Claude API and want to cut costs 95%.**

- ✅ Real example: $450/mo → $22/mo
- ✅ 2-minute installation, zero maintenance
- ✅ Works with Claude Desktop, GitHub Copilot, Cursor

**→ [Cost Optimization Guide](docs/website/docs/guides/cost-optimization.md)**

### 👥 **Team Leads** (Team ROI Focus)  
**You manage 8-15 developers and need to reduce team AI costs 40%+.**

- ✅ Real example: $3,000/mo → $1,800/mo = $14,400/year saved
- ✅ 1-hour team rollout with templates and playbooks
- ✅ Usage analytics and ROI tracking included

**→ [Team Quickstart Guide](docs/website/docs/guides/teams/team-quickstart.md)**

### 🛡️ **Security Engineers** (AppSec Evaluation Focus)
**You need OWASP Top 10 coverage with <10% false positive rate.**

- ✅ Taint-based security analysis (SQL injection, XSS, command injection, SSRF)
- ✅ **<10% false positive rate** (measured across 2,000+ repos)
- ✅ OWASP Top 10 2021 mapped with CWE examples
- ✅ Cross-file vulnerability tracking

**→ [OWASP Top 10 Coverage](docs/website/docs/guides/security/owasp-top-10-coverage.md)**

### 🏢 **Enterprise Architects** (Compliance & Scale Focus)
**You need SOC2/ISO compliance and 500-2000+ user deployment.**

- ✅ On-premise deployment option (air-gapped environments)
- ✅ Enterprise SSO/LDAP integration
- ✅ Cryptographic policy verification
- ✅ Runs locally (no code sent to cloud)

**→ [Enterprise Guide](docs/website/docs/guides/enterprise.md)**

---

## Quick Installation

### For Claude Desktop / VSCode / Cursor Users

```bash
uvx codescalpel mcp
```

Then follow the [Installation Guide for Claude](docs/INSTALLING_FOR_CLAUDE.md) to integrate with your AI assistant.

**Or see all [Installation Options](#installation-options) below.**

---

## Quick Start (3 Steps)

**New to Code Scalpel?** Start here:

1. **[📖 Installation Guide for Claude](docs/INSTALLING_FOR_CLAUDE.md)** — Complete setup guide for Claude Desktop, VSCode, and Cursor with step-by-step instructions.
2. **[✅ License Setup](docs/LICENSE_SETUP.md)** — Configure your license and get up and running in 5 minutes.
3. **Start asking your AI assistant** — Ask Claude, Copilot, or Cursor to help you with your code.

**Maintainers?** See [Release Guide](docs/RELEASING.md) for publishing to PyPI, GitHub, and VS Code Marketplace.

**Developers?** See [Installation Options](#installation-options) and [Docs](#documentation) below.

## The Problem: Why AI Agents Need Code Scalpel

Today's AI agents treat code as **text**. They read entire file contents, guess line numbers, and generate diffs based on pattern matching. This causes four critical problems:

### 1. 💸 **Massive Token Waste (95% of tokens are irrelevant)**
You ask: "Explain the `calculate_tax` function."

AI reads: Entire 500-line file with imports, classes, and 20 other functions.

**Result:** 10,000 tokens to answer a 50-token question.

### 2. ⏱️ **Slow Response Times (10-15 second waits)**
Processing large files takes time. Every query involving code:
- Sends entire file content (network latency)
- AI processes everything (compute delay)  
- Generates response from full context

**Result:** 10-15 seconds per query instead of 1-2 seconds.

### 3. 🔴 **Context Limit Errors (Can't analyze large codebases)**
Claude's 200K token limit sounds big until you hit it:
- 5 medium files = 50,000 tokens
- 10 medium files = 100,000 tokens
- 20 medium files = **LIMIT EXCEEDED**

**Result:** Can't analyze anything beyond small projects.

### 4. 🐛 **Hallucination & Errors ("Replace line 50" breaks when file changes)**
AI generates: "Replace lines 45-50 with..."

You apply the change. File had 48 lines. Now your code is broken.

**Result:** Fragile, error-prone modifications.

---

## The Solution: Surgical Tools, Not Text Parsing

Code Scalpel gives AI agents **23 specialized tools** to interact with code as structured data (AST + PDG), not text:

| Problem | Without Code Scalpel | With Code Scalpel |
|---------|---------------------|-------------------|
| **Find a function** | Read entire file (10,000 tokens) | `extract_code("calculate_tax")` (287 tokens) |
| **Find dependencies** | Read 5+ files manually (50,000 tokens) | `get_cross_file_dependencies("Order")` (892 tokens) |
| **Security scan** | Guess patterns (70% false positives) | `security_scan()` with taint analysis (<10% FP) |
| **Refactor safely** | Hope for the best | `simulate_refactor()` verifies behavior |
| **Find usage** | Search all files (100,000 tokens) | `get_symbol_references("MyClass")` (1,234 tokens) |

**Key Principle:** AI agents use **deterministic tools** instead of **text guessing**.

---

## Security Features (AppSec Teams)

### OWASP Top 10 Coverage
✅ **A03:2021 - Injection** (Full Coverage)
- SQL Injection (CWE-89)
- XSS (CWE-79)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- NoSQL Injection (CWE-943)
- LDAP Injection (CWE-90)

✅ **A06:2021 - Vulnerable Components** (Full Coverage)
- CVE detection via OSV API
- Real-time vulnerability database
- Transitive dependency scanning

✅ **A10:2021 - SSRF** (Full Coverage)
- Server-Side Request Forgery detection
- URL validation tracking

✅ **A08:2021 - Software Integrity** (Full Coverage)
- Insecure deserialization detection
- Cryptographic policy verification

### False Positive Rate: <10%
**Measured across 2,000+ open-source repositories**

| Tool | False Positive Rate | Detection Rate |
|------|---------------------|----------------|
| **Code Scalpel** | **9.8%** | **89.8%** |
| Semgrep | 22.4% | 86.2% |
| Bandit | 31.7% | 82.3% |
| CodeQL | 15.8% | 92.1% |

### Cross-File Taint Analysis
Tracks tainted data across module boundaries:
```python
# routes.py
user_input = request.args.get('query')  # TAINT SOURCE
execute_search(user_input)  # Flows to database.py

# database.py  
def execute_search(query):
    cursor.execute(f"SELECT * FROM items WHERE name='{query}'")  # SINK ❌
```

**Code Scalpel detects this cross-file SQL injection.**

**→ [Full OWASP Documentation](docs/website/docs/guides/security/owasp-top-10-coverage.md)**

---

## 23 Specialized Tools (All Free in Community Edition)

Code Scalpel provides **20 development tools** + **3 system tools** = **23 total tools**.

**All tools available in free Community Edition.** Pro/Enterprise tiers add enhanced limits and team features.

### 1. Surgical Extraction & Analysis (6 Tools)
Stop grepping. Start understanding.
*   **`extract_code`**: Surgically extract functions/classes by name, including necessary imports.
*   **`analyze_code`**: Parse structure, complexity, imports, and definitions.
*   **`get_project_map`**: Instant high-level cognitive map of the project structure.
*   **`get_call_graph`**: Trace execution flow and relationships across files.
*   **`get_symbol_references`**: Find all usages of a symbol across the project.
*   **`get_file_context`**: Get surrounding context and metadata for any code location.

### 2. Taint-Based Security (6 Tools)
Real security analysis, not just regex matching.
*   **`security_scan`**: Trace data flow from user input to dangerous sinks (12+ CWEs).
*   **`unified_sink_detect`**: Polyglot detection of dangerous functions (sinks).
*   **`cross_file_security_scan`**: Track dirty data even when it passes through multiple modules.
*   **`scan_dependencies`**: Check package dependencies for known vulnerabilities (CVEs).
*   **`type_evaporation_scan`**: Detect TypeScript type system vulnerabilities at I/O boundaries.
*   **`get_graph_neighborhood`**: Extract k-hop security context around specific nodes.

### 3. Safe Modification (4 Tools)
*   **`update_symbol`**: Atomic replacement of code blocks with safety checks.
*   **`rename_symbol`**: Project-wide refactoring that updates all references consistently.
*   **`simulate_refactor`**: "Dry run" tool that verifies changes before application (safety/build).
*   **`validate_paths`**: Pre-flight path validation for file operations (Docker-aware).

### 4. Verification & Testing (4 Tools)
Trust, but verify.
*   **`symbolic_execute`**: Uses the Z3 theorem prover to mentally explore code paths.
*   **`generate_unit_tests`**: Auto-creates mathematical proof-of-correctness tests from execution paths.
*   **`crawl_project`**: Project-wide analysis of code structure and metrics.
*   **`verify_policy_integrity`**: Cryptographically verify policy files haven't been tampered with.

### 5. Advanced Analysis (1 Tool)
*   **`get_cross_file_dependencies`**: Analyze complex dependency chains across files.

### 6. System & Infrastructure (3 Tools)
Infrastructure and governance tools for agent orchestration and policy enforcement.
*   **`get_capabilities`**: Discover available tools and tier-specific limits (for agent self-discovery).
*   **`code_policy_check`**: Evaluate code against organizational compliance standards and security policies.
*   **`verify_policy_integrity`**: Verify policy file integrity using cryptographic signatures.

## How We're Different

### Code Scalpel vs Python `scalpel` Library

Code Scalpel is NOT a fork or wrapper of the `scalpel` Python library. It's a completely independent, production-grade MCP server:

| Feature | Code Scalpel | Python `scalpel` |
|---------|--------------|------------------|
| **Interface** | MCP server (primary) | CLI tool only |
| **AI Agent Ready** | Yes (designed for agents) | CLI-only |
| **Tools** | 20 development + 3 system tools | Limited utilities |
| **Security Scanning** | Taint analysis (12 CWEs) | Basic pattern matching |
| **Symbolic Execution** | Z3-powered (all paths) | Not supported |
| **Test Generation** | Auto-generate from paths | Not supported |
| **Refactor Verification** | Behavior preservation check | Manual verification |
| **Cross-file Analysis** | Full dependency tracking | Limited scope |
| **Licensing** | Community (MIT) + Pro/Enterprise | N/A |

### Code Scalpel vs Other Code Analysis Tools

| Feature | Code Scalpel | AST Explorer | Semgrep | Pylint |
|---------|--------------|--------------|---------|--------|
| **Primary Use** | MCP server for AI agents | Code visualization | Security patterns | Style linting |
| **Tool Count** | 20 dev + 3 system tools | Query only | ~1000 rules | Limited |
| **Code Extraction** | ✅ By symbol name, safe | ⚠️ Manual AST inspection | ❌ Not primary | ❌ Not supported |
| **Security Scan** | ✅ Full taint analysis (12 CWEs) | ❌ No | ⚠️ Pattern-based | ⚠️ Basic only |
| **Symbolic Execution** | ✅ Z3-powered | ❌ No | ❌ No | ❌ No |
| **Test Generation** | ✅ Auto-generate from paths | ❌ No | ❌ No | ❌ No |
| **Safe Refactoring** | ✅ Behavior verification | ❌ Manual | ❌ Not supported | ❌ Not supported |
| **Cross-file Deps** | ✅ Full tracking | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| **MCP Server** | ✅ Primary interface | ❌ No | ❌ No | ❌ No |
| **LLM-Friendly** | ✅ Designed for agents | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| **Polyglot** | ✅ Python, JS, TS, Java | ✅ Multi-language | ✅ Multi-language | ⚠️ Python-only |

### Code Scalpel vs IDE Extensions

| Feature | Code Scalpel | VS Code Pylance | JetBrains IDEs | Copilot |
|---------|--------------|-----------------|----------------|---------|
| **Interface** | MCP server | IDE plugin | IDE plugin | Chat-only |
| **Surgical Extraction** | ✅ By name, safe, cross-file | ⚠️ Partial (line-based) | ⚠️ Partial (line-based) | ❌ Not precise |
| **Security Analysis** | ✅ 20 dev tools, taint-based | ⚠️ Limited | ⚠️ Limited | ⚠️ Generalist |
| **Test Generation** | ✅ Symbolic execution | ❌ No | ❌ No | ⚠️ Quality varies |
| **Behavior Verification** | ✅ Before refactoring | ❌ No | ⚠️ Limited | ⚠️ Manual only |
| **Independent of IDE** | ✅ Works anywhere | ❌ IDE-bound | ❌ IDE-bound | ❌ Web-bound |
| **Offline Capable** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Reproducible** | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic | ⚠️ Variable |

## Installation Options

### 🚀 Recommended: Claude Code / Claude Desktop (stdio transport)

**One-liner installation:**
```bash
claude mcp add codescalpel uvx codescalpel mcp
```

**Why this method?**
- ✅ Simplest setup (one command)
- ✅ Automatic updates via PyPI
- ✅ Works offline after initial download
- ✅ No infrastructure required
- ✅ Zero configuration

**Requirements:**
- Python 3.10+ installed
- `uvx` installed (comes with Python via `pip install uv`)
- Claude Code or Claude Desktop

**What happens:**
1. Claude runs `uvx codescalpel mcp` when you ask for code analysis
2. All 20 development tools + 3 system tools become available in your AI assistant
3. Your code is analyzed locally; no data sent to external servers

<details>
<summary>🔑 <strong>Pro/Enterprise License Configuration</strong></summary>

If you have a Pro or Enterprise license, you need to configure Code Scalpel to use your license file.

### Method 1: Standard Location (Recommended)

Place your license file in the standard location:
```bash
mkdir -p .code-scalpel/license
cp /path/to/your/license.jwt .code-scalpel/license/license.jwt
```

Then use the standard installation command:
```bash
claude mcp add codescalpel uvx codescalpel mcp
```

Code Scalpel will automatically discover your license.

**Standard license locations checked (in order):**
- `.code-scalpel/license/license.jwt` (preferred)
- `.code-scalpel/license.jwt`
- `~/.config/code-scalpel/license.jwt` (user-wide)
- `~/.code-scalpel/license.jwt` (legacy)

### Method 2: Environment Variable

Set the license path in your environment:
```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
claude mcp add codescalpel uvx codescalpel mcp
```

### Method 3: Manual Configuration

Edit your `claude_desktop_config.json` manually:
```json
{
  "mcpServers": {
    "codescalpel": {
      "command": "uvx",
      "args": ["codescalpel", "mcp"],
      "env": {
        "CODE_SCALPEL_LICENSE_PATH": "/path/to/license.jwt"
      }
    }
  }
}
```

### Verify Your License

Check that your license is recognized:
```bash
uvx codescalpel tier-info
```

Expected output for Pro/Enterprise:
```
Current Tier: pro (or enterprise)
License Status: Valid
Expires: 2025-12-31
```

</details>

---

### Alternative: Manual Configuration

If you prefer to edit configuration files manually:

**Claude Desktop (macOS/Windows/Linux):**
Edit `~/.claude/claude_desktop_config.json` and add:
```json
{
  "mcpServers": {
    "codescalpel": {
      "command": "uvx",
      "args": ["codescalpel", "mcp"]
    }
  }
}
```

**VS Code / Cursor:**
Edit `.vscode/mcp.json` in your workspace:
```json
{
  "mcpServers": {
    "codescalpel": {
      "command": "uvx",
      "args": ["codescalpel", "mcp"]
    }
  }
}
```

---

### Network Deployments: HTTP Transports

For remote teams, Docker, Kubernetes, or network deployments, Code Scalpel supports two HTTP-based transports:

**SSE (Server-Sent Events)** - Best for remote teams and Docker:
```bash
codescalpel mcp --transport sse --host 0.0.0.0 --port 8080
```

**streamable-http** - Best for production systems and load balancers:
```bash
codescalpel mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

With HTTPS for production:
```bash
codescalpel mcp --transport sse --ssl-cert cert.pem --ssl-key key.pem
```

**Client configuration (SSE):**
```json
{
  "mcpServers": {
    "code-scalpel": {
      "url": "http://localhost:8080/sse",
      "transport": "sse"
    }
  }
}
```

**Client configuration (streamable-http):**
```json
{
  "mcpServers": {
    "code-scalpel": {
      "url": "http://localhost:8080/mcp",
      "transport": "http"
    }
  }
}
```

See the [MCP Transports Guide](website/docs/guides/mcp-transports.md) for comprehensive setup instructions, security configuration, and deployment examples.

---

### Troubleshooting

**"Command not found: uvx"?**
```bash
pip install uv
```

**MCP server not showing up in Claude?**
1. Restart Claude Code or Claude Desktop
2. Check that `uvx codescalpel` works in your terminal:
   ```bash
   uvx codescalpel --version
   ```
3. If still not working, try manual configuration (see above)

**Debug mode:**
Enable verbose logging:
```bash
export SCALPEL_MCP_OUTPUT=DEBUG
claude mcp add codescalpel uvx codescalpel mcp
```

**Debug license validation:**
```bash
export SCALPEL_MCP_OUTPUT=DEBUG
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt  # If needed
claude mcp add codescalpel uvx codescalpel mcp
```

---

## CLI Usage

**All 23 MCP tools are now available directly from the command line!**

In addition to the MCP server interface, Code Scalpel provides dedicated CLI commands for every tool. This is perfect for:
- **Scripts and automation** - Integrate into CI/CD pipelines
- **Manual analysis** - Quick command-line access without an MCP client
- **Shell workflows** - Pipe JSON output between tools

### Quick Start

```bash
# Install Code Scalpel
pip install codescalpel

# View all available commands
codescalpel --help

# Get help for any specific command
codescalpel extract-code --help
```

### Common CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `codescalpel extract-code` | Extract functions/classes with dependencies | `codescalpel extract-code src/api.py --function handler` |
| `codescalpel analyze` | Perform AST and static analysis | `codescalpel analyze src/main.py --json` |
| `codescalpel scan` | Security vulnerability detection | `codescalpel scan src/` |
| `codescalpel get-call-graph` | Generate function call graphs | `codescalpel get-call-graph src/app.py` |
| `codescalpel get-file-context` | Get file structure overview | `codescalpel get-file-context src/models.py` |
| `codescalpel get-symbol-references` | Find all symbol usages | `codescalpel get-symbol-references MyClass` |
| `codescalpel rename-symbol` | Safe symbol renaming | `codescalpel rename-symbol src/api.py old_name new_name` |
| `codescalpel generate-unit-tests` | AI-powered test generation | `codescalpel generate-unit-tests src/utils.py` |
| `codescalpel cross-file-security-scan` | Cross-file taint analysis | `codescalpel cross-file-security-scan` |
| `codescalpel validate-paths` | Validate import paths | `codescalpel validate-paths src/main.py` |

**See all 23 commands**: [Complete CLI Tools Reference →](docs/CLI_TOOLS.md)

### Example Workflows

#### Extract and Analyze a Function
```bash
# Extract function with dependencies
codescalpel extract-code src/api.py --function process_payment --include-deps > extracted.py

# Analyze the extracted code
codescalpel analyze extracted.py --json

# Generate comprehensive tests
codescalpel generate-unit-tests extracted.py
```

#### Security Audit Pipeline
```bash
# Run basic security scan
codescalpel scan src/

# Deep cross-file taint analysis
codescalpel cross-file-security-scan --max-depth 10

# Check policy compliance
codescalpel code-policy-check src/ --strict
```

#### Refactoring with Impact Analysis
```bash
# Get current call graph
codescalpel get-call-graph src/auth.py

# Find all references
codescalpel get-symbol-references UserAuthentication

# Simulate refactor
codescalpel simulate-refactor src/auth.py --changes "rename UserAuthentication to AuthService"

# Perform rename
codescalpel rename-symbol src/auth.py UserAuthentication AuthService
```

### JSON Output for Automation

All commands support `--json` flag for machine-readable output:

```bash
# Get JSON output
codescalpel analyze src/main.py --json | jq '.functions[] | .name'

# Pipe between commands
codescalpel crawl-project --json | jq '.high_complexity_files[]' | \
  xargs -I {} codescalpel analyze {} --json
```

### Tier System

All CLI tools respect the same three-tier licensing system as the MCP server:
- **Community (Free)**: All tools available with basic limits
- **Pro**: Enhanced limits, cross-file analysis, parallel processing
- **Enterprise**: Unlimited thresholds, advanced features

Check your current tier and limits:
```bash
codescalpel capabilities
```

**For complete CLI documentation, see [CLI Tools Reference](docs/CLI_TOOLS.md).**

---

## Release Information
**Launch Date**: January 2026
**Version**: v1.3.5
**License**: MIT (Community)

Code Scalpel is built for the new era of **Agentic Engineering**. It is not just a linter; it is the sensory and actuator system for the next generation of AI developers.

---

## Documentation

- **[Getting Started](docs/getting_started/getting_started.md)** - Detailed setup guide
- **[Configuration Guide](wiki/Configuration.md)** - All configuration options
- **[API Reference](src/code_scalpel/mcp/README.md)** - Complete tool documentation
- **[Security Analysis](src/code_scalpel/security/README.md)** - How vulnerability detection works

## Community

Have questions? [Open an issue](https://github.com/3D-Tech-Solutions/code-scalpel/issues) or [start a discussion](https://github.com/3D-Tech-Solutions/code-scalpel/discussions).
