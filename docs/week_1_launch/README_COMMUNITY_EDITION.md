# Code Scalpel Community Edition

> **🚀 Placeholder README for Code Scalpel v1.0 Public Release**  
> This README will be finalized upon public release. Content is subject to change.

**Surgical code operations for AI agents. Extract. Analyze. Refactor. Verify.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/package-PyPI-green.svg)](https://pypi.org/project/code-scalpel/)

Code Scalpel is an **MCP (Model Context Protocol) server** designed as the primary interface for AI agents to perform precise code operations on real codebases without hallucination. Extract functions, analyze code structure, detect vulnerabilities, and refactor safely—all with surgical precision.

**MCP Server is the recommended way to use Code Scalpel.** It integrates seamlessly with Claude, GitHub Copilot, Cursor, and any MCP-compatible AI agent. A Python package is available as an alternative for direct scripting and automation.

Works with: Claude, GitHub Copilot, Cursor, AutoGen, LangChain, and any MCP-compatible client.

## Community Docs

Find community-focused documentation in the repository under [docs/code_scalpel_community/README.md](docs/code_scalpel_community/README.md):
- Tool reference: [docs/code_scalpel_community/TOOL_REFERENCE.md](docs/code_scalpel_community/TOOL_REFERENCE.md)
- Examples: [docs/code_scalpel_community/EXAMPLES.md](docs/code_scalpel_community/EXAMPLES.md)
- Configuration: [docs/code_scalpel_community/CONFIGURATION.md](docs/code_scalpel_community/CONFIGURATION.md)
- Troubleshooting: [docs/code_scalpel_community/TROUBLESHOOTING.md](docs/code_scalpel_community/TROUBLESHOOTING.md)
- FAQ: [docs/code_scalpel_community/FAQ.md](docs/code_scalpel_community/FAQ.md)
- Contributing: [docs/code_scalpel_community/CONTRIBUTING.md](docs/code_scalpel_community/CONTRIBUTING.md)
- Security policy: [docs/code_scalpel_community/SECURITY.md](docs/code_scalpel_community/SECURITY.md)
- Code of Conduct: [docs/code_scalpel_community/CODE_OF_CONDUCT.md](docs/code_scalpel_community/CODE_OF_CONDUCT.md)

License: MIT (c) 3D Tech Solutions LLC. See [LICENSE](LICENSE).

## Quick Start

### Option 1: MCP Server with uvx (Recommended for AI Agents)

Run directly with uvx (no installation needed):

```bash
# Initialize Code Scalpel (creates .code-scalpel directory)
uvx code-scalpel init

# Start MCP server
uvx code-scalpel mcp
```

Configure in Claude's `claude_desktop_config.json`:

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

Now Claude can use tools directly:

```
User: "Extract the calculate_tax function from src/utils.py"

Claude uses: extract_code tool
  - file_path: "src/utils.py"
  - target_type: "function"
  - target_name: "calculate_tax"

Result: Full function code with cross-file dependencies
```

### Option 2: Python Package with pip (For Development)

Install for development/scripting:

```bash
pip install code-scalpel
code-scalpel init
```

Use as a Python library:

```python
from code_scalpel import CodeScalpel

# Initialize the scalpel
scalpel = CodeScalpel(project_root="/path/to/project")

# Extract a function
result = scalpel.extract_code(
    file_path="src/utils.py",
    target_type="function",
    target_name="calculate_tax"
)
print(result.code)

# Analyze code structure
analysis = scalpel.analyze_code(code=result.code)
print(f"Functions: {analysis.functions}")

# Security scan
vulnerabilities = scalpel.security_scan(code=result.code)
print(f"Issues found: {len(vulnerabilities.vulnerabilities)}")
```

## What's Included

All 22 Code Scalpel tools are available at every tier (Community, Pro, Enterprise). The tier determines analysis limits and advanced features, not tool availability:

### Code Analysis (6 tools)
- **`analyze_code`** — Parse code structure (functions, classes, imports, complexity)
- **`extract_code`** — Surgically extract specific functions/classes by name
- **`get_file_context`** — Get surrounding context for any code location
- **`get_symbol_references`** — Find all usages of a symbol across the project
- **`get_call_graph`** — Generate call graphs and trace execution flow
- **`get_project_map`** — High-level project structure overview

### Security Analysis (6 tools)
- **`security_scan`** — Detect vulnerabilities via taint analysis (SQL injection, XSS, command injection, path traversal, hardcoded secrets)
- **`unified_sink_detect`** — Unified polyglot sink detection with confidence thresholds
- **`cross_file_security_scan`** — Track taint flow across file boundaries
- **`scan_dependencies`** — Check dependencies for known vulnerabilities (CVE scanning)
- **`type_evaporation_scan`** — Detect TypeScript type system vulnerabilities
- **`get_graph_neighborhood`** — Extract k-hop neighborhood for focused analysis

### Code Modification (4 tools)
- **`update_symbol`** — Safely replace functions/classes while preserving surrounding code
- **`simulate_refactor`** — Verify refactor preserves behavior before applying
- **`rename_symbol`** — Rename functions, classes, or methods across the codebase
- **`validate_behavior_changes`** — Verify code modifications preserve functionality

### Testing & Exploration (4 tools)
- **`generate_unit_tests`** — Auto-generate test cases from symbolic execution paths
- **`symbolic_execute`** — Explore execution paths with Z3 symbolic execution
- **`validate_cves_for_java`** — Check Java dependencies for known vulnerabilities
- **`crawl_project`** — Project-wide analysis of code structure and metrics

### Advanced Analysis (2 tools)
- **`get_cross_file_dependencies`** — Analyze cross-file dependency chains
- **`code_policy_check`** — Evaluate code against compliance standards

## Editions

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| **License** | MIT (Open Source) | Commercial | Commercial |
| **Tools Available** | All 22 | All 22 | All 22 |
| **Analysis Limits** | Standard | 10x limits | Unlimited |
| **Custom Rules** | No | Limited | Full |
| **Organization Features** | Single user | Single user | Teams & hierarchy |
| **Support** | Community | Email | Dedicated |

### Community Edition Features
- All 22 tools available
- Standard analysis limits (1000 files, 30s timeout)
- Unlimited project size
- MIT License (open source)
- Community support (GitHub issues)

### Pro Edition Features
- All 22 tools available
- 10x analysis limits (10,000 files, 300s timeout)
- Custom rule sets
- Email support
- Commercial license

### Enterprise Edition Features
- All 22 tools available
- Unlimited analysis depth
- Organization-wide licensing
- Seat management and team features
- Custom integrations
- Dedicated support

[Compare editions in detail →](docs/EDITIONS.md)

## Documentation
To be included soon

## Use Cases

### For AI Agents (Primary)
Code Scalpel MCP server is designed for AI agents (Claude, GitHub Copilot, Cursor, etc.) to work on real codebases:

**Claude with Code Scalpel:**
```
User: "Refactor the payment processing code to remove the security vulnerability"

Claude:
1. Uses extract_code to get src/handlers/payment.py
2. Uses security_scan to identify the vulnerability
3. Uses analyze_code to understand structure
4. Uses simulate_refactor to test the fix
5. Uses update_symbol to safely apply the change
```

**GitHub Copilot integration:**
```
@code-scalpel extract the process_payment function
@code-scalpel scan for security issues in payment.py
@code-scalpel find all calls to process_payment
```

### For Developers (Secondary)
- Use MCP server with Claude/Copilot for AI-assisted code work
- Or use Python package directly for scripting and automation
- Understand code structure before modifications
- Find all usages before refactoring
- Detect security vulnerabilities
- Generate unit tests automatically

### For CI/CD Pipelines
- Run as MCP server or Python package
- Security scanning in pull request workflows
- Dependency vulnerability checking
- Code complexity analysis
- Automated test generation

## Requirements

- Python 3.9+
- pip (or any Python package manager)
- Optional: Z3 theorem prover (for symbolic execution features)

## Installation

### Quick Start with uvx (Recommended)

```bash
# Initialize Code Scalpel (creates .code-scalpel directory)
uvx code-scalpel init

# Start MCP server
uvx code-scalpel mcp
```

No installation needed. This starts the MCP server that connects to Claude, Copilot, Cursor, or other MCP-compatible clients.

### With pip (For Development)

```bash
pip install code-scalpel
code-scalpel init
code-scalpel mcp
```

Import and use directly in Python:

```python
from code_scalpel import CodeScalpel
scalpel = CodeScalpel(project_root="/path/to/project")
```

### From Source

```bash
git clone https://github.com/tescolopio/code_scalpel_community.git
cd code-scalpel
pip install -e .
code-scalpel init
code-scalpel mcp
```

### Docker

```bash
docker run -v /path/to/project:/project code-scalpel:latest init
docker run -v /path/to/project:/project code-scalpel:latest mcp
```

## Configuration

### Initialize Configuration

Create `.code-scalpel` directory with default settings:

```bash
code-scalpel init
```

This creates:
- `.code-scalpel/config.json` — Project configuration
- `.code-scalpel/rules/` — Custom analysis rules (Pro/Enterprise)
- `.code-scalpel/cache/` — Analysis cache

### MCP Server Configuration

Set environment variables before starting the server:

```bash
export CODE_SCALPEL_PROJECT_ROOT=/path/to/project
export CODE_SCALPEL_TIMEOUT=30
export CODE_SCALPEL_MAX_FILES=1000
code-scalpel mcp
```

Or configure in client (Claude):

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"],
      "env": {
        "CODE_SCALPEL_PROJECT_ROOT": "/path/to/project",
        "CODE_SCALPEL_TIMEOUT": "30"
      }
    }
  }
}
```

### Configuration File

Edit `.code-scalpel/config.json` after `code-scalpel init`:

```json
{
  "analysis": {
    "timeout": 30,
    "max_files": 1000,
    "languages": ["python", "javascript", "typescript", "java"]
  }
}
```

[Full configuration guide →](docs/configuration.md)

## Examples

### MCP Server (With AI Agent)

**Claude conversation:**
```
User: "Analyze the security of src/handlers/payment.py"

Claude:
1. Uses extract_code tool to get the file
2. Uses security_scan tool to find vulnerabilities
3. Uses get_symbol_references tool to check how it's used

Result: Detailed vulnerability report with context
```

**Configuration for Claude:**
```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"],
      "env": {
        "CODE_SCALPEL_PROJECT_ROOT": "/path/to/project"
      }
    }
  }
}
```

### Python Package (Direct Usage)

**Extract a Function**
```python
from code_scalpel import extract_code

result = extract_code(
    file_path="src/utils.py",
    target_type="function",
    target_name="calculate_discount"
)
print(result.code)  # Full function code with dependencies
```

**Find All Usages**
```python
from code_scalpel import get_symbol_references

refs = get_symbol_references(symbol_name="process_order")
for ref in refs.references:
    print(f"{ref.file}:{ref.line} - {ref.context}")
```

**Security Scan**
```python
from code_scalpel import security_scan

result = security_scan(code="""
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!
    cursor.execute(query)
    return cursor.fetchone()
""")

for vuln in result.vulnerabilities:
    print(f"{vuln.type} ({vuln.cwe}): {vuln.description}")
```

**Generate Tests**
```python
from code_scalpel import generate_unit_tests

tests = generate_unit_tests(
    code="""
def validate_email(email):
    return "@" in email and "." in email.split("@")[1]
    """,
    framework="pytest"
)
print(tests.pytest_code)  # Ready-to-run test code
```

[More examples →](examples/)

## Licensing

Code Scalpel Community Edition is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

**Commercial editions** (Pro, Enterprise) require a license key. [Learn more →](docs/LICENSING.md)

## Support

- **GitHub Issues** — Report bugs and request features
- **Discussions** — Ask questions and share ideas
- **Documentation** — Full guides and API reference
- **Pro/Enterprise** — Email support available

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- **v3.3.0** (Current) — All 22 tools in beta
- **v3.4.0** (Q1 2026) — Plugin system for Pro/Enterprise
- **v3.5.0** (Q2 2026) — Async execution improvements
- **v4.0.0** (Q3 2026) — Full TypeScript/JavaScript support

[View full roadmap →](docs/DEVELOPMENT_ROADMAP.md)

## Security

Code Scalpel takes security seriously. See [SECURITY.md](SECURITY.md) for:
- Vulnerability disclosure process
- Security considerations
- Best practices

## How We're Different

### Code Scalpel vs Python `scalpel` Library

Code Scalpel is NOT a fork or wrapper of the `scalpel` Python library. It's a completely independent, production-grade MCP server:

| Feature | Code Scalpel | Python `scalpel` |
|---------|--------------|------------------|
| **Interface** | ✅ MCP server (primary) | CLI tool only |
| **AI Agent Ready** | ✅ Yes (designed for agents) | ❌ CLI-only |
| **Tools** | 22 specialized tools | Limited utilities |
| **Security Scanning** | ✅ Taint analysis (12 CWEs) | Basic pattern matching |
| **Symbolic Execution** | ✅ Z3-powered (all paths) | Not supported |
| **Test Generation** | ✅ Auto-generate from paths | Not supported |
| **Refactor Verification** | ✅ Behavior preservation check | Manual verification |
| **Cross-file Analysis** | ✅ Full dependency tracking | Limited scope |
| **Licensing** | Community (MIT) + Pro/Enterprise | N/A |
| **Production Grade** | ✅ v3.3.0 (4,700+ tests, 97.93% coverage) | Experimental |

### Code Scalpel vs Other Code Analysis Tools

| Feature | Code Scalpel | AST Explorer | Semgrep | Pylint |
|---------|--------------|--------------|---------|--------|
| **Primary Use** | MCP server for AI agents | Code visualization | Security patterns | Style linting |
| **Tool Count** | 22 specialized tools | Query only | ~1000 rules | Limited |
| **Code Extraction** | By symbol name, safe | Manual AST inspection | Not primary | Not supported |
| **Security Scan** | Full taint analysis (12 CWEs) | No | Pattern-based | Basic only |
| **Symbolic Execution** | ✅ Z3-powered | ❌ No | ❌ No | ❌ No |
| **Test Generation** | ✅ Auto-generate from paths | ❌ No | ❌ No | ❌ No |
| **Safe Refactoring** | Behavior verification | Manual | Not supported | Not supported |
| **Cross-file Deps** | ✅ Full tracking | Limited | Limited | Limited |
| **MCP Server** | ✅ Primary interface | ❌ No | ❌ No | ❌ No |
| **LLM-Friendly** | ✅ Designed for agents | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| **Polyglot** | Python, JS, TS, Java | Multi-language | Multi-language | Python-only |

### Code Scalpel vs IDE Extensions

| Feature | Code Scalpel | VS Code Pylance | JetBrains IDEs | Copilot |
|---------|--------------|-----------------|----------------|---------|
| **Interface** | MCP server | IDE plugin | IDE plugin | Chat-only |
| **Surgical Extraction** | ✅ By name, safe, cross-file | Partial (line-based) | Partial (line-based) | ❌ Not precise |
| **Security Analysis** | 22 tools, taint-based | Limited | Limited | Generalist |
| **Test Generation** | ✅ Symbolic execution | ❌ No | ❌ No | ⚠️ Quality varies |
| **Behavior Verification** | ✅ Before refactoring | ❌ No | ⚠️ Limited | ⚠️ Manual only |
| **Independent of IDE** | ✅ Works anywhere | IDE-bound | IDE-bound | Web-bound |
| **Offline Capable** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Reproducible** | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic | ⚠️ Variable |

### Why Code Scalpel is Different

1. **MCP-First Architecture** — Designed from the ground up as an MCP server, not a wrapper around a library
2. **AI-Agent Centric** — Every tool is optimized for AI reasoning, not human users
3. **Surgical Precision** — Extract by symbol name, not line numbers. No guessing. No collateral damage.
4. **Behavior Preservation** — Verify refactors preserve functionality before applying
5. **Full Symbolic Execution** — Z3-powered exploration of all code paths for test generation
6. **Taint-Based Security** — Track data flow across files, detect real vulnerabilities
7. **22 Specialized Tools** — Not a single "code analysis" tool; 22 focused instruments
8. **Production Ready** — 4,700+ tests, 97.93% coverage, used in enterprise settings
9. **All Tools at All Tiers** — Community gets all 22 tools, tiers only differ in limits
10. **Open Source Foundation** — MIT Community edition, with commercial Pro/Enterprise options

[Detailed comparison →](docs/COMPARISON.md)

## Status

**Code Scalpel v1.0** is the first public release, coming Q1 2026. Current version (v3.3.0) is in beta.

- ✅ All 22 tools implemented and tested (4,700+ tests)
- ✅ Production-grade JWT licensing system
- ✅ Plugin architecture designed (Pro/Enterprise)
- ⏳ Public release preparations underway
- ⏳ Documentation finalization
- ⏳ Public GitHub repository setup

## Citation

```bibtex
@software{codescalpel2026,
  title={Code Scalpel: Surgical Code Operations for AI Agents},
  author={Code Scalpel Team},
  url={https://github.com/code-scalpel/code-scalpel},
  year={2026}
}
```

## License

MIT License — See [LICENSE](LICENSE) for details.

---

**Ready to get started?** → [Installation Guide](docs/getting_started.md) | [API Reference](docs/TOOL_REFERENCE.md) | [Examples](examples/)