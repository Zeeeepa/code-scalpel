# Code Scalpel: Surgical Code Operations for AI Agents

**Latest Release: v1.0.1 | January 25, 2026**

Code Scalpel is the bridge between **Generative AI** and **Reliable Software Engineering**.

It is an **MCP (Model Context Protocol) server** designed to be the primary toolset for AI agents (like Claude, GitHub Copilot, and Cursor) to perceive, analyze, and modify codebases with surgical precision.

## Quick Installation

### For Claude Desktop / VSCode / Cursor Users

```bash
uvx code-scalpel mcp
```

Then follow the [Installation Guide for Claude](docs/INSTALLING_FOR_CLAUDE.md) to integrate with your AI assistant.

**Or see all [Installation Options](#installation-options) below.**

---

## Quick Start (3 Steps)

**New to Code Scalpel?** Start here:

1. **[📖 Installation Guide for Claude](docs/INSTALLING_FOR_CLAUDE.md)** — Complete setup guide for Claude Desktop, VSCode, and Cursor with step-by-step instructions.
2. **[✅ Setup Checklist](docs/SETUP_CHECKLIST.md)** — Quick checklist to get up and running in 5 minutes.
3. **Start asking your AI assistant** — Ask Claude, Copilot, or Cursor to help you with your code.

**Maintainers?** See [Release Guide](docs/RELEASING.md) for publishing to PyPI, GitHub, and VS Code Marketplace.

**Developers?** See [Installation Options](#installation-options) and [Docs](#documentation) below.

---

## The Problem: Why Agents Struggle with Code
Today's AI agents treat code as **text**. They read file contents, guess line numbers, and generate diffs. This leads to:
*   **Hallucination**: "Replace line 50" fails when the file changed.
*   **Context Window Exhaustion**: Reading 10 files to find one definition.
*   **Security Blindness**: Generating SQL injection vulnerabilities because they lack taint analysis.
*   **Regression**: Making changes that break existing behavior without verification.

## The Solution: Tools, Not Text
Code Scalpel treats code as a **Graph** (AST + PDG). It gives agents deterministic tools to interact with the codebase:
*   **Don't read the file** → `extract_function("process_payment")`
*   **Don't guess the line** → `update_symbol("process_payment", new_code)`
*   **Don't guess dependencies** → `get_cross_file_dependencies("Order")`
*   **Don't assume safety** → `security_scan(code)`

## Key Capabilities at Launch (v1.0) | Jan 2026

Code Scalpel launches with **22 specialized tools** divided into five surgical disciplines. All tools are available in the open-source Community Edition.

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

### 5. Advanced Analysis (2 Tools)
*   **`get_cross_file_dependencies`**: Analyze complex dependency chains across files.
*   **`code_policy_check`**: Evaluate code against organizational compliance standards.

## How We're Different

### Code Scalpel vs Python `scalpel` Library

Code Scalpel is NOT a fork or wrapper of the `scalpel` Python library. It's a completely independent, production-grade MCP server:

| Feature | Code Scalpel | Python `scalpel` |
|---------|--------------|------------------|
| **Interface** | MCP server (primary) | CLI tool only |
| **AI Agent Ready** | Yes (designed for agents) | CLI-only |
| **Tools** | 22 specialized tools | Limited utilities |
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
| **Tool Count** | 22 specialized tools | Query only | ~1000 rules | Limited |
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
| **Security Analysis** | ✅ 22 tools, taint-based | ⚠️ Limited | ⚠️ Limited | ⚠️ Generalist |
| **Test Generation** | ✅ Symbolic execution | ❌ No | ❌ No | ⚠️ Quality varies |
| **Behavior Verification** | ✅ Before refactoring | ❌ No | ⚠️ Limited | ⚠️ Manual only |
| **Independent of IDE** | ✅ Works anywhere | ❌ IDE-bound | ❌ IDE-bound | ❌ Web-bound |
| **Offline Capable** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Reproducible** | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic | ⚠️ Variable |

## Installation Options

### 🚀 Recommended: Claude Code / Claude Desktop (stdio transport)

**One-liner installation:**
```bash
claude mcp add codescalpel --transport stdio uvx codescalpel mcp
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
2. All 22 tools become available in your AI assistant
3. Your code is analyzed locally; no data sent to external servers

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

### Advanced: HTTP Transport (Future)

For enterprise deployments with single-sign-on, we'll soon support HTTP transport with OAuth 2.1:
```bash
codescalpel mcp --http --port 8593 --ssl-cert cert.pem --ssl-key key.pem
```

This is currently in beta. [Get in touch](https://github.com/3D-Tech-Solutions/code-scalpel/issues) if you need this feature.

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
claude mcp add codescalpel --transport stdio uvx codescalpel mcp
```

---

## Release Information
**Launch Date**: January 2026
**Version**: v1.0.0
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
