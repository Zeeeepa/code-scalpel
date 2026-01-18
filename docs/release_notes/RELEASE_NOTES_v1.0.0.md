# Code Scalpel v1.0.0 Release Notes

**Release Date:** January 17, 2026

## Overview

Code Scalpel v1.0.0 is the official public release of our comprehensive MCP server toolkit for AI agents. This release represents a production-ready, feature-complete implementation with all core tools, tier-based access control, and automatic initialization system.

## Key Features

### Core Capabilities

- **22 MCP Tools** for surgical code analysis and modification:
  - Code Analysis: `analyze_code`, `extract_code`, `get_file_context`
  - Navigation: `get_symbol_references`, `get_call_graph`, `get_cross_file_dependencies`
  - Security: `security_scan`, `unified_sink_detect`, `type_evaporation_scan`
  - Refactoring: `rename_symbol`, `update_symbol`, `simulate_refactor`
  - Testing: `symbolic_execute`, `generate_unit_tests`
  - And more...

### Tier System

- **Community Tier** (Default): Essential code analysis tools with per-file limits
- **Pro Tier**: Advanced graph analysis, semantic relationships, and filtering controls
- **Enterprise Tier**: Policy engine, governance enforcement, CODEOWNERS integration

### Auto-Initialization

- Automatic `.code-scalpel/` configuration directory creation on first MCP server startup
- Standard config files: `policy.yaml`, `budget.yaml`, `config.json`, `dev-governance.yaml`
- Policy directories for architecture, devops, devsecops, and project governance
- Template-only mode ensures no sensitive data is generated

### Production Ready

- All 534 tests passing (9 skipped)
- Comprehensive error handling and validation
- Type hints throughout (Python 3.10-3.13)
- Security-focused taint analysis for vulnerability detection
- SBOM generation for supply chain transparency

## What's New in v1.0.0

### From v3.3.0

1. **Public Release Cleanup**
   - Removed 357 internal files (planning docs, benchmarks, old versions)
   - Reduced repository size from 72M to 56M (22% reduction)
   - Clean, professional codebase suitable for public use

2. **Documentation**
   - Professional README (100 lines vs 1115 lines)
   - CONTRIBUTING.md with developer guidelines
   - Fresh CHANGELOG with comprehensive tool list
   - Improved getting started experience

3. **CI/CD Infrastructure**
   - GitHub Actions OIDC trusted publisher for PyPI
   - No credentials stored in repository
   - Automated publishing on version tags

4. **Initialization System**
   - Auto-init now called at MCP server startup
   - Creates essential config structure automatically
   - Safe template-only mode for first-time setup

## Installation

```bash
pip install code-scalpel
```

## Quick Start

### Configure as MCP Server

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` or `~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "python",
      "args": ["-m", "code_scalpel.mcp.server"]
    }
  }
}
```

**Cursor** or other MCP clients: Use similar configuration with the same command.

### First Run

The `.code-scalpel/` directory is created automatically on first MCP server startup with:
- Standard configuration files
- Policy templates (architecture, devops, devsecops, project)
- License and audit directories

### Use a Tool

```python
from code_scalpel.mcp.client import MCPClient

client = MCPClient("code-scalpel")
result = client.call("analyze_code", file_path="src/app.py")
print(result)
```

## Breaking Changes

None. This is the inaugural public release (v1.0.0).

## Security

- **Vulnerability Detection**: SQL injection, XSS, command injection, path traversal, XXE, SSTI, hardcoded secrets
- **Type Safety**: Full type hints, Pydantic validation, type checking in CI/CD
- **Dependency Management**: Regular audits, security-focused dependencies, SBOM generation
- **Code Review**: All tools extensively tested, edge cases covered

## Known Limitations

- **Community Tier**: Per-file size limits on graph analysis to control complexity
- **Symbol Analysis**: Requires well-formed Python/JavaScript/TypeScript code
- **Performance**: Large monorepos may need incremental analysis for best performance

## Supported Languages

- Python (3.7+)
- JavaScript/TypeScript (ES6+)
- Java (7+)

## Tier Comparison

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| Core Tools | ✓ | ✓ | ✓ |
| Graph Analysis | Limited | ✓ | ✓ |
| Semantic Analysis | - | ✓ | ✓ |
| Policy Engine | - | - | ✓ |
| Governance | - | - | ✓ |

## Support

- **Documentation**: Check [README.md](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/3D-Tech-Solutions/code-scalpel/issues)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup

## Thank You

Thanks to all contributors who helped make Code Scalpel a robust, production-ready tool for AI-powered code analysis. This release represents months of testing, refinement, and community feedback.

---

**Code Scalpel v1.0.0 - Surgical Code Analysis for AI Agents**
