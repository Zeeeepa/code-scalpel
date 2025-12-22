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
| [**graph_engine_guide.md**](graph_engine_guide.md) | Unified Graph Engine documentation |
| [**RELEASE_NOTES_v3.0.0.md**](release_notes/RELEASE_NOTES_v3.0.0.md) | Autonomy release - Comprehensive coverage, stability, autonomy foundation |  <!-- [20251218_DOCS] Added v3.0 notes link -->
| [**RELEASE_NOTES_v2.5.0.md**](release_notes/RELEASE_NOTES_v2.5.0.md) | Guardian release - Policy, semantic blocking, tamper resistance |
| [**RELEASE_NOTES_v2.2.0.md**](release_notes/RELEASE_NOTES_v2.2.0.md) | Nexus release - Unified Graph Engine |

---

## v3.0.0 Release Documentation

Critical upgrade and reference guides for v3.0.0:

| Document | Description | Use Case |
|----------|-------------|----------|
| [**MIGRATION_v2.5_to_v3.0.md**](./MIGRATION_v2.5_to_v3.0.md) | Step-by-step upgrade guide | Upgrading from v2.5.0 |
| [**API_CHANGES_v3.0.0.md**](./API_CHANGES_v3.0.0.md) | Detailed API changes and new features | Understanding API differences |
| [**KNOWN_ISSUES_v3.0.0.md**](./KNOWN_ISSUES_v3.0.0.md) | Known limitations and workarounds | Troubleshooting issues |

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

The polyglot parsers infrastructure provides static analysis for 10 language families:

| Language | Status | Documentation |
|----------|--------|-----------------|
| **Java** | Phase 1 ✅ | [JAVA_PARSERS_COMPLETION.md](parsers/JAVA_PARSERS_COMPLETION.md) |
| **Kotlin** | Phase 1 ✅ | [KOTLIN_PARSERS_COMPLETION.md](parsers/KOTLIN_PARSERS_COMPLETION.md) |
| **JavaScript** | Phase 1 ✅ | [JAVASCRIPT_PARSERS_COMPLETION.md](parsers/JAVASCRIPT_PARSERS_COMPLETION.md) |
| **TypeScript** | Phase 1 ✅ | [TYPESCRIPT_PARSERS_COMPLETION.md](parsers/TYPESCRIPT_PARSERS_COMPLETION.md) |
| **Ruby** | Phase 1 ✅ | [RUBY_PARSERS_COMPLETION.md](parsers/RUBY_PARSERS_COMPLETION.md) |
| **PHP** | Phase 1 ✅ | [PHP_PARSERS_COMPLETION.md](parsers/PHP_PARSERS_COMPLETION.md) |
| **Swift** | Phase 1 ✅ | [SWIFT_PARSERS_README.md](parsers/SWIFT_PARSERS_README.md) |
| **C++** | Phase 1 ✅ | [CPP_PARSERS_README.md](parsers/CPP_PARSERS_README.md) |
| **C#** | Phase 1 ✅ | [CSHARP_PARSERS_README.md](parsers/CSHARP_PARSERS_README.md) |
| **Go** | Phase 1 ✅ | [GO_PARSERS_README.md](parsers/GO_PARSERS_README.md) |

**Overview:** [POLYGLOT_PARSERS_SUMMARY.md](parsers/POLYGLOT_PARSERS_SUMMARY.md) - Comprehensive summary of all language modules

**Phase 1 Status:** 10/10 language modules complete ✅
- All modules have comprehensive factory registries
- All modules have [20251221_TODO] Phase 2 markers
- All modules have detailed READMEs with tool specifications
- Ready for Phase 2 implementation across all tools

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

## Guides

| Guide | Description |
|-------|-------------|
| [guides/CONTRIBUTING.md](guides/CONTRIBUTING.md) | Developer contribution guide |
| [guides/PUBLIC_FORK_CHECKLIST_v1.0.md](guides/PUBLIC_FORK_CHECKLIST_v1.0.md) | Public fork + v1.0 go-public checklist and evidence gates | <!-- [20251221_DOCS] Add public-fork checklist link -->
| [guides/README_CLAIMS_DEMOS_v1.0.md](guides/README_CLAIMS_DEMOS_v1.0.md) | README claim-by-claim demo scripts + evidence artifacts | <!-- [20251221_DOCS] Add README claims demo plan -->

---

## Internal Documentation

Team-only documentation:

| Document | Description |
|----------|-------------|
| [internal/ROADMAP.md](internal/ROADMAP.md) | Development roadmap |
| [internal/PRODUCT_BACKLOG.md](internal/PRODUCT_BACKLOG.md) | Feature backlog |
| [internal/RELEASE_PROTOCOL.md](internal/RELEASE_PROTOCOL.md) | Release process |
| [internal/CHECKLIST.md](internal/CHECKLIST.md) | Milestone tracking |
| [internal/COVERAGE_ANALYSIS.md](internal/COVERAGE_ANALYSIS.md) | Test coverage analysis |

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
