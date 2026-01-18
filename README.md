# Code Scalpel

[![PyPI version](https://badge.fury.io/py/code-scalpel.svg)](https://pypi.org/project/code-scalpel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**MCP Server for AI-Powered Code Analysis v1.0** — Surgical code operations through AST parsing, taint analysis, and symbolic execution.

Code Scalpel enables AI assistants (Claude, GitHub Copilot, Cursor) to understand and modify code with mathematical precision, eliminating hallucinations through deterministic analysis.

## Key Features

- **🔬 Surgical Extraction** — Extract functions, classes, and dependencies with 99% token reduction vs. full files
- **🛡️ Security Scanning** — Taint-based vulnerability detection (SQL injection, XSS, command injection)
- **🧪 Test Generation** — Symbolic execution (Z3) generates tests covering all execution paths
- **📊 Code Analysis** — AST parsing, call graphs, cross-file dependencies, complexity metrics
- **✏️ Safe Modifications** — AST-validated edits with backup creation and syntax verification

## Quick Start

### Installation

```bash
pip install code-scalpel
```

### MCP Configuration (Claude Desktop / VS Code)

Add to your MCP settings:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "python",
      "args": ["-m", "code_scalpel.mcp"],
      "env": {
        "SCALPEL_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

### Quick Example

```python
# Extract a function surgically (200 tokens vs 15,000 for full file)
result = extract_code(
    file_path="/project/utils.py",
    target_type="function",
    target_name="calculate_tax"
)

# Scan for security vulnerabilities
vulns = security_scan(file_path="/project/handlers.py")

# Generate tests covering all paths
tests = generate_unit_tests(file_path="/project/calculator.py")
```

## Available Tools (22 Total)

| Category | Tools |
|----------|-------|
| **Extraction** | `extract_code`, `get_file_context`, `analyze_code` |
| **Navigation** | `get_call_graph`, `get_cross_file_dependencies`, `get_symbol_references`, `get_project_map` |
| **Security** | `security_scan`, `cross_file_security_scan`, `unified_sink_detect`, `type_evaporation_scan` |
| **Testing** | `generate_unit_tests`, `symbolic_execute`, `simulate_refactor` |
| **Modification** | `update_symbol`, `rename_symbol` |
| **Project** | `crawl_project`, `scan_dependencies`, `get_graph_neighborhood`, `code_policy_check` |
| **Utilities** | `validate_paths`, `verify_policy_integrity` |

## Tier System

Code Scalpel operates on a three-tier model:

| Tier | Access | Key Features |
|------|--------|--------------|
| **Community** | Free | All 22 tools with baseline limits |
| **Pro** | License | Unlimited findings, cross-file analysis, advanced features |
| **Enterprise** | License | Compliance reporting, custom policies, audit trails |

## Documentation

- [Getting Started Guide](docs/getting_started/)
- [Tool Reference](docs/reference/)
- [Architecture](docs/architecture/)
- [Security](SECURITY.md)

## Docker

```bash
docker run -v $(pwd):/workspace ghcr.io/3d-tech-solutions/code-scalpel:latest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built for AI agents that need to understand code, not guess at it.**
