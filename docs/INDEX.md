# Code Scalpel Documentation

**v3.0.0 "Autonomy" - MCP Server Toolkit for AI Agents**

> **Coverage Gate:** ≥90% combined (statement + branch)  
> **Current Coverage:** 94.86% | **Tests:** 4,033

---

## Quick Links

| Document | Description |
|----------|-------------|
| [**COMPREHENSIVE_GUIDE.md**](COMPREHENSIVE_GUIDE.md) | Full documentation with examples |
| [**README.md**](../README.md) | Project overview and quick start |
| [**RELEASE_NOTES_v3.3.0.md**](release_notes/RELEASE_NOTES_v3.3.0.md) | Clean Slate release - v3.3.0 latest |
| [**RELEASE_NOTES_v3.0.0.md**](release_notes/RELEASE_NOTES_v3.0.0.md) | Autonomy release - Comprehensive coverage, stability, autonomy foundation |
| [**RELEASE_NOTES_v2.5.0.md**](release_notes/RELEASE_NOTES_v2.5.0.md) | Guardian release - Policy, semantic blocking, tamper resistance |

---

## Current Release - v3.3.0

Latest version and migration guides:

| Document | Description |
|----------|-------------|
| [**RELEASE_NOTES_v3.3.0.md**](release_notes/RELEASE_NOTES_v3.3.0.md) | Latest release notes and features |
| [**CHANGELOG.md**](release_notes/CHANGELOG.md) | Chronological change log |
| [**EXECUTIVE_SUMMARY.md**](release_notes/EXECUTIVE_SUMMARY.md) | High-level summary of project state |
| [**IMPLEMENTATION_CHECKLIST.md**](release_notes/IMPLEMENTATION_CHECKLIST.md) | Implementation checklist and gates |

---

## Tool Documentation

> [20260103_DOCS] Added comprehensive tool documentation structure

**NEW:** Layered documentation for all 20 MCP tools:

| Layer | Location | Audience | Purpose |
|-------|----------|----------|---------|
| **Deep Dive** | [tools/deep_dive/](tools/deep_dive/) | Developers, Contributors | Complete technical reference |
| **User Guides** | [tools/user_guides/](tools/user_guides/) | End Users, Integrators | Practical how-to guides |
| **Quick Reference** | [tools/quick_reference/](tools/quick_reference/) | Experienced Users | Fast parameter lookups |
| **Marketing** | [tools/marketing/](tools/marketing/) | Decision Makers | Feature highlights |

**Getting Started:**
- [Tool Documentation README](tools/README.md) - Overview and structure
- [Tool Documentation Template](reference/TOOL_DOCUMENTATION_TEMPLATE.md) - Deep dive template
- [Tool Documentation Guide](reference/TOOL_DOCUMENTATION_GUIDE.md) - How to create tool docs

**Available Tools (v3.1.0):** 20 MCP tools for surgical code operations
- Code Analysis: `analyze_code`, `get_file_context`, `get_project_map`, `crawl_project`
- Code Extraction: `extract_code`, `get_symbol_references`, `get_cross_file_dependencies`
- Code Modification: `update_symbol`
- Code Flow: `get_call_graph`, `get_graph_neighborhood`, `symbolic_execute`
- Security: `security_scan`, `unified_sink_detect`, `cross_file_security_scan`, `type_evaporation_scan`, `scan_dependencies`
- Testing: `generate_unit_tests`, `simulate_refactor`
- Utilities: `validate_paths`, `verify_policy_integrity`

---

## Module Documentation

Detailed reference for each module:

| Module | File | Description |
|--------|------|-------------|
| **AST Tools** | [modules/AST_TOOLS.md](modules/AST_TOOLS.md) | Code parsing, analysis, transformation |
| **PDG Tools** | [modules/PDG_TOOLS.md](modules/PDG_TOOLS.md) | Data flow analysis, program slicing |
| **Symbolic Execution** | [modules/SYMBOLIC_EXECUTION.md](modules/SYMBOLIC_EXECUTION.md) | Path exploration, constraint solving |
| **MCP Server** | [modules/MCP_SERVER.md](modules/MCP_SERVER.md) | AI assistant integration |
| **Integrations** | [modules/INTEGRATIONS.md](modules/INTEGRATIONS.md) | AutoGen, CrewAI, LangChain |

---

## Polyglot Parsers Module

The polyglot parsers infrastructure provides static analysis:

| Language | Documentation |
|----------|-----------------|
| **C++** | [CPP_PARSERS_README.md](parsers/CPP_PARSERS_README.md) |
| **C#** | [CSHARP_PARSERS_README.md](parsers/CSHARP_PARSERS_README.md) |
| **Go** | [GO_PARSERS_README.md](parsers/GO_PARSERS_README.md) |
| **Swift** | [SWIFT_PARSERS_README.md](parsers/SWIFT_PARSERS_README.md) |
| **Python** | [python_parser.md](parsers/python_parser.md) |
| **Base** | [base_parser.md](parsers/base_parser.md) |

**Reference Documentation:**
- [PHASE1_DELIVERY_REPORT.md](parsers/PHASE1_DELIVERY_REPORT.md) - Parser implementation status
- [DOCUMENTATION_INDEX.md](parsers/DOCUMENTATION_INDEX.md) - Parser docs index

---

## Architecture

```
code-scalpel/
├── src/code_scalpel/
│   ├── ast_tools/          # AST parsing and analysis
│   ├── pdg_tools/          # Program Dependence Graphs
│   ├── symbolic_execution_tools/  # Z3-powered symbolic execution
│   ├── mcp/                # MCP server
│   ├── integrations/       # AutoGen, CrewAI, LangChain
│   └── cli.py              # Command-line interface
├── docs/                   # Documentation
│   ├── modules/            # Module-specific docs
│   ├── guides/             # How-to guides
│   └── internal/           # Team documentation
├── demos/                  # Example code
│   └── real_world/         # Real-world vulnerability demos
└── tests/                  # Test suite (4,033 tests)
```

---

## Compliance

| Document | Description |
|----------|-------------|
| [**LICENSING_SYSTEM_GUIDE.md**](compliance/LICENSING_SYSTEM_GUIDE.md) | Licensing system overview and guidance |
| [**policy_integrity_verification.md**](guides/policy_integrity_verification.md) | Policy integrity verification guide |

---

## Deployment

| Document | Description |
|----------|-------------|
| [**PUBLIC_REPO_PREPARATION.md**](deployment/PUBLIC_REPO_PREPARATION.md) | Steps for preparing public repository |

---

## Research

| Document | Description |
|----------|-------------|
| [**FEATURE_EXTRACTION_PLAN.md**](research/FEATURE_EXTRACTION_PLAN.md) | Feature extraction planning document |
| [**FEATURE_EXTRACTION_PLANNING_INDEX.md**](research/FEATURE_EXTRACTION_PLANNING_INDEX.md) | Index of feature extraction planning |

---

## Community Edition

| Document | Description |
|----------|-------------|
| [**README_COMMUNITY_EDITION.md**](code_scalpel_community/README_COMMUNITY_EDITION.md) | Community Edition overview and docs links |

## Guides

| Guide | Description |
|-------|-------------|
| [guides/CONTRIBUTING.md](guides/CONTRIBUTING.md) | Developer contribution guide |
| [internal/CONTRIBUTING_ROOT.md](internal/CONTRIBUTING_ROOT.md) | Legacy root CONTRIBUTING (archived reference) |
| [guides/README_CLAIMS_DEMOS_v1.0.md](guides/README_CLAIMS_DEMOS_v1.0.md) | README claim validation and demo scripts |
| [guides/agent_integration.md](guides/agent_integration.md) | AI agent and framework integration |
| [guides/graph_engine_guide.md](guides/graph_engine_guide.md) | Unified graph engine documentation |

---

## API Reference

### Core Imports

```python
from code_scalpel import (
    # Analysis
    CodeAnalyzer,
    analyze_code,
    
    # AST
    ASTAnalyzer,
    ASTBuilder,
    build_ast,
    
    # PDG
    PDGBuilder,
    PDGAnalyzer,
    build_pdg,
    
    # Server
    run_server,
)
```

### Module-Specific Imports

```python
# Symbolic Execution
from code_scalpel.symbolic_execution_tools import (
    SymbolicAnalyzer,
    SecurityAnalyzer,
    analyze_security,
)

# MCP Server
from code_scalpel.mcp import mcp, run_server

# Integrations
from code_scalpel.integrations import (
    AutogenScalpel,
    CrewAIScalpel,
)
```

---

## Examples

### Quick Analysis

```python
from code_scalpel import analyze_code

result = analyze_code("""
def calculate(x, y):
    if x > y:
        return x - y
    return y - x
""")

print(f"Functions: {result.function_count}")
print(f"Complexity: {result.metrics.cyclomatic_complexity}")
```

### Security Scan

```python
from code_scalpel.symbolic_execution_tools import analyze_security

result = analyze_security("""
user_id = request.args.get("id")
query = f"SELECT * FROM users WHERE id={user_id}"
cursor.execute(query)
""")

if result.has_vulnerabilities:
    for vuln in result.vulnerabilities:
        print(f"[{vuln.severity}] {vuln.vulnerability_type}")
```

### MCP Server

```bash
# Start server
code-scalpel mcp

# Or with HTTP
code-scalpel mcp --transport http --port 8593
```

---

## Version History

<!-- [20251216_DOCS] Add v2.5.0 and v3.0.0 planned features from 3rd party review -->

| Version | Codename | Highlights |
|---------|----------|------------|
| v3.0.0 | "Autonomy" | (Planned) Mutation Test Gate, Self-Correction Loop |
| v2.5.0 | "Guardian" | (In Progress) Policy Engine, Confidence Decay, Graph Neighborhood View, Cryptographic Policy Verification |
| v2.2.0 | "Nexus" | Unified Graph Engine, Cross-Language Dependencies, Type Narrowing |
| v2.0.1 | "Coverage Lock" | Coverage policy/exclusions documented; warning-path tests for RefactorSimulator |
| v1.3.0 | "Hardening" | NoSQL/LDAP injection, secret detection, Float support |
| v1.2.3 | - | Path resolution, FunctionInfo/ClassInfo models |
| v1.2.2 | - | Bug fixes, stability improvements |
| v1.1.0 | "The Scalpel" | 100% AST Tools coverage |
| v1.0.0 | "The Standard" | Caching, API freeze, Z3 hardening |

---

## Support

- **GitHub Issues**: [tescolopio/code-scalpel/issues](https://github.com/tescolopio/code-scalpel/issues)
- **PyPI**: [pypi.org/project/code-scalpel](https://pypi.org/project/code-scalpel/)

---

*Code Scalpel - Precision tools for AI-driven code analysis.*
