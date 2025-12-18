# Code Scalpel v1.5.1 - "CrossFile"

**Release Date:** December 13, 2025  
**Theme:** Cross-File Dependency Analysis for AI Agents  
**Status:** [COMPLETE] Production Ready

---

## Executive Summary

v1.5.1 introduces **cross-file analysis capabilities** that enable AI agents to understand and track code dependencies across module boundaries. This release adds three new core modules and two new MCP tools, giving AI assistants the ability to resolve imports, extract dependent code, and detect security vulnerabilities that span multiple files.

### Key Statistics
- **142 new tests** passing (v1.5.1 specific)
- **2,258 tests** total in test suite
- **100% test pass rate** on new modules
- **15 new MCP tools** total (2 new in v1.5.1)
- **3 new core modules** for cross-file analysis

---

## [TARGET] New Features

### 1. Import Resolution Engine

**Module:** `code_scalpel.ast_tools.import_resolver`

**Purpose:** Build and query the complete import dependency graph for any Python project.

```python
from code_scalpel.ast_tools import ImportResolver

resolver = ImportResolver("/path/to/project")
result = resolver.build()

# Resolve a symbol to its source file
source_module, definition = resolver.resolve_symbol("mymodule", "MyClass")

# Get modules that import a given module
importers = resolver.get_importers("utils")

# Detect circular imports
cycles = resolver.get_circular_imports()

# Get safe analysis order
sorted_modules = resolver.topological_sort()

# Generate Mermaid diagram
diagram = resolver.generate_mermaid()
```

**Capabilities:**
- Parses all Python files in project to extract imports
- Handles `import`, `from ... import`, and `from ... import *`
- Resolves relative imports (`.module`, `..module`)
- Maps modules to files and vice versa
- Tracks symbol definitions (functions, classes, variables)
- Detects and reports circular import cycles
- Provides topological sort for safe analysis order
- Generates Mermaid diagrams of import relationships

**Key Classes:**
- `ImportResolver` - Main orchestrator class
- `ImportInfo` - Details about each import statement
- `ImportType` - Enum: DIRECT, FROM, STAR
- `SymbolDefinition` - Where a symbol is defined
- `CircularImport` - Details about import cycles
- `ImportGraphResult` - Build results and statistics

**Tests:** 59 tests (88% coverage)

---

### 2. Cross-File Extraction

**Module:** `code_scalpel.ast_tools.cross_file_extractor`

**Purpose:** Extract code symbols with all their cross-file dependencies in one operation.

```python
from code_scalpel.ast_tools import CrossFileExtractor

extractor = CrossFileExtractor("/path/to/project")
extractor.build()

result = extractor.extract(
    file_path="services/order.py",
    symbol_name="process_order",
    depth=3,
)

# Get target symbol code
print(result.target.code)

# Get all dependencies
for dep in result.dependencies:
    print(f"Dependency: {dep.name} from {dep.file}")

# Get combined code ready for AI
print(result.combined_code)
```

**Capabilities:**
- Extracts a function/class with all its dependencies
- Recursively resolves cross-file imports
- Provides dependency-ordered combined code
- Respects depth limits to prevent explosion
- Handles circular dependencies gracefully
- Reports unresolved external imports
- Tracks all files touched during extraction

**Key Classes:**
- `CrossFileExtractor` - Main extraction engine
- `ExtractedSymbol` - Extracted code with metadata
- `ExtractionResult` - Complete extraction output
- `DependencyNode` - Node in dependency graph

**Use Case:** When an AI agent needs to understand a function that calls code from other files, it can extract everything at once instead of manually reading multiple files.

**Tests:** 32 tests

---

### 3. Cross-File Taint Tracking

**Module:** `code_scalpel.symbolic_execution_tools.cross_file_taint`

**Purpose:** Detect security vulnerabilities where tainted data flows across module boundaries.

```python
from code_scalpel.symbolic_execution_tools import CrossFileTaintTracker

tracker = CrossFileTaintTracker("/path/to/project")
result = tracker.analyze(max_depth=5)

# Check for vulnerabilities
for vuln in result.vulnerabilities:
    print(f"{vuln.vulnerability_type}: {vuln.description}")
    print(f"  Source: {vuln.flow.source_file}:{vuln.flow.source_function}")
    print(f"  Sink: {vuln.flow.sink_file}:{vuln.flow.sink_function}")

# Get all taint flows
for flow in result.taint_flows:
    print(f"Taint flow: {flow.source_function} -> {flow.sink_function}")

# Generate Mermaid diagram
diagram = tracker.get_taint_graph_mermaid()
```

**Detects Cross-File Patterns:**
- User input in `routes.py` → SQL execution in `db.py` (SQL Injection)
- Request data in `views.py` → `os.system()` in `utils.py` (Command Injection)
- Form input in `handlers.py` → `open()` in `storage.py` (Path Traversal)
- External data in `api.py` → `eval()` in `processor.py` (Code Injection)

**Vulnerability Types:**
- SQL Injection (CWE-89)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Cross-Site Scripting (CWE-79)
- Code Injection (CWE-94)
- LDAP Injection (CWE-90)
- XML Injection (CWE-91)

**Key Classes:**
- `CrossFileTaintTracker` - Main analysis engine
- `CrossFileTaintResult` - Analysis results
- `CrossFileTaintFlow` - A single taint flow
- `CrossFileVulnerability` - Detected vulnerability
- `TaintedParameter` - Function parameter with taint
- `CrossFileTaintSource` - Enum of taint sources
- `CrossFileSink` - Enum of dangerous sinks

**Tests:** 25 tests

---

### 4. `get_cross_file_dependencies` MCP Tool

**Purpose:** AI agents can extract code with all cross-file dependencies in one call.

```python
result = await get_cross_file_dependencies(
    target_file="services/order.py",
    target_symbol="process_order",
    project_root="/path/to/project",
    max_depth=3,
    include_code=True,
    include_diagram=True,
)
```

**Returns:**
```python
{
    "success": True,
    "target_name": "process_order",
    "target_file": "services/order.py",
    "extracted_symbols": [
        {
            "name": "process_order",
            "code": "def process_order(order):\n    ...",
            "file": "services/order.py",
            "line_start": 15,
            "line_end": 42,
            "dependencies": ["validate_order", "calculate_total"]
        },
        {
            "name": "validate_order",
            "code": "def validate_order(order):\n    ...",
            "file": "utils/validation.py",
            "line_start": 8,
            "line_end": 25,
            "dependencies": []
        },
        ...
    ],
    "total_dependencies": 5,
    "unresolved_imports": ["numpy", "pandas"],
    "import_graph": {
        "services/order.py": ["utils/validation.py", "models/order.py"],
        ...
    },
    "circular_imports": [],
    "combined_code": "# Combined code ready for AI analysis\n...",
    "token_estimate": 1250,
    "mermaid": "graph LR\n    ..."
}
```

**Why AI Agents Need This:**
- **Complete Context:** Get all code needed to understand a function
- **Safe Refactoring:** Know what depends on what before making changes
- **Debugging:** Trace data flow across file boundaries
- **Code Review:** Understand the full impact of changes
- **Token Efficiency:** Combined code is ready for LLM consumption

**Tests:** 8 tests

---

### 5. `cross_file_security_scan` MCP Tool

**Purpose:** AI agents can detect vulnerabilities that span multiple files.

```python
result = await cross_file_security_scan(
    project_root="/path/to/project",
    entry_points=["app.py:main", "routes.py:index"],
    max_depth=5,
    include_diagram=True,
)
```

**Returns:**
```python
{
    "success": True,
    "files_analyzed": 42,
    "has_vulnerabilities": True,
    "vulnerability_count": 3,
    "risk_level": "high",
    "vulnerabilities": [
        {
            "type": "SQL Injection",
            "cwe": "CWE-89",
            "severity": "critical",
            "source_file": "routes.py",
            "sink_file": "db.py",
            "description": "User input from request.args flows to cursor.execute",
            "flow": {
                "source_function": "search",
                "source_file": "routes.py",
                "source_line": 15,
                "sink_function": "execute_query",
                "sink_file": "db.py",
                "sink_line": 42,
                "flow_path": ["routes.py:search", "db.py:execute_query"],
                "taint_type": "request_input"
            }
        },
        ...
    ],
    "taint_flows": [...],
    "taint_sources": ["routes.py:search", "api.py:get_data"],
    "dangerous_sinks": ["db.py:execute_query", "utils.py:run_command"],
    "mermaid": "graph LR\n    ..."
}
```

**Why AI Agents Need This:**
- **Defense in Depth:** Find vulnerabilities that span multiple files
- **Architecture Review:** Understand how untrusted data flows through the app
- **Code Audit:** Generate security reports for compliance
- **Risk Assessment:** Identify highest-risk code paths

**Tests:** 8 tests

---

## [METRICS] Test Coverage Summary

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| ImportResolver | 59 | 88% | [COMPLETE] |
| CrossFileExtractor | 32 | TBD | [COMPLETE] |
| CrossFileTaintTracker | 25 | TBD | [COMPLETE] |
| MCP: get_cross_file_dependencies | 8 | TBD | [COMPLETE] |
| MCP: cross_file_security_scan | 8 | TBD | [COMPLETE] |
| Integration Tests | 10 | N/A | [COMPLETE] |
| **Total v1.5.1 Tests** | **142** | - | [COMPLETE] |

---

## [TOOL] API Changes

### New Exports in `code_scalpel.ast_tools`

```python
from code_scalpel.ast_tools import (
    # Import Resolution
    ImportResolver,
    ImportInfo,
    ImportType,
    SymbolDefinition,
    CircularImport,
    ImportGraphResult,
    
    # Cross-File Extraction
    CrossFileExtractor,
    ExtractedSymbol,
    ExtractionResult,
)
```

### New Exports in `code_scalpel.symbolic_execution_tools`

```python
from code_scalpel.symbolic_execution_tools import (
    CrossFileTaintTracker,
    CrossFileTaintResult,
    CrossFileTaintFlow,
    CrossFileVulnerability,
    TaintedParameter,
    CrossFileTaintSource,
    CrossFileSink,
)
```

### New MCP Tools

| Tool | Description |
|------|-------------|
| `get_cross_file_dependencies` | Extract code with cross-file dependencies |
| `cross_file_security_scan` | Detect vulnerabilities across files |

---

## [FOLDER] Files Changed

### New Files Created

```
src/code_scalpel/ast_tools/import_resolver.py (~850 lines)
src/code_scalpel/ast_tools/cross_file_extractor.py (~650 lines)
src/code_scalpel/symbolic_execution_tools/cross_file_taint.py (~850 lines)
tests/test_import_resolver.py (59 tests)
tests/test_cross_file_extractor.py (32 tests)
tests/test_cross_file_taint.py (25 tests)
tests/test_v151_integration.py (10 tests)
```

### Modified Files

```
src/code_scalpel/ast_tools/__init__.py - Added new exports
src/code_scalpel/symbolic_execution_tools/__init__.py - Added new exports
src/code_scalpel/mcp/server.py - Added 2 new MCP tools
tests/test_mcp.py - Added 16 new MCP tool tests
```

---

## [LAUNCH] Upgrade Guide

### From v1.5.0

No breaking changes. Simply upgrade:

```bash
pip install code-scalpel==1.5.1
```

The new tools are available immediately after upgrade.

### Using the New Features

```python
# Import Resolution
from code_scalpel.ast_tools import ImportResolver
resolver = ImportResolver("/my/project")
resolver.build()

# Cross-File Extraction  
from code_scalpel.ast_tools import CrossFileExtractor
extractor = CrossFileExtractor("/my/project")
extractor.build()
result = extractor.extract("main.py", "main", depth=3)

# Cross-File Security
from code_scalpel.symbolic_execution_tools import CrossFileTaintTracker
tracker = CrossFileTaintTracker("/my/project")
result = tracker.analyze(max_depth=5)
```

---

## [BUG] Known Issues

1. **Large Projects:** Import resolution on very large projects (>1000 files) may take several seconds. Use caching for repeated analysis.

2. **Dynamic Imports:** `importlib.import_module()` and other dynamic imports are not tracked. Only static `import` and `from ... import` statements are analyzed.

3. **Type Stubs:** `.pyi` files are not currently analyzed as import sources.

4. **Docker Path Resolution:** File-based tools require filesystem access. When running in Docker, mount user workspace with `-v /user/projects:/workspace`. Use `crawl_project` first to validate access.

---

## [COMPLETE] External Testing Validation

**Tested by:** External QA Team  
**Date:** December 13, 2025  
**Verdict:** Production-ready with industry-leading 100% detection rate

### Security Scanning Results

| Vulnerability Type | Status | Notes |
|-------------------|--------|-------|
| SQL injection (f-string) | [COMPLETE] Detected | Accurate line numbers |
| NoSQL injection (MongoDB) | [COMPLETE] Detected | CWE-943 |
| LDAP injection | [COMPLETE] Detected | CWE-90 |
| Command injection (subprocess) | [COMPLETE] Detected | CWE-78 |
| Path traversal (os.path.join) | [COMPLETE] Detected | CWE-22 |
| XSS (render_template_string) | [COMPLETE] Detected | CWE-79 |
| SSTI (Jinja2) | [COMPLETE] Detected | CWE-1336 |
| XXE (xml.etree) | [COMPLETE] Detected | CWE-611 |
| Code injection (eval) | [COMPLETE] Detected | CWE-94 |
| Deserialization (pickle) | [COMPLETE] Detected | CWE-502 |
| SSRF (urllib) | [COMPLETE] Detected | CWE-918 |
| Weak crypto (MD5) | [COMPLETE] Detected | CWE-328 |
| Hardcoded secrets (4 types) | [COMPLETE] Detected | AWS, API keys, passwords |

**Detection Rate: 16/16 (100%)**

### Project Analysis Results

| Metric | Value |
|--------|-------|
| Files Analyzed | 211 |
| Lines of Code | 79,284 |
| Functions Cataloged | 3,973 |
| Classes Identified | 761 |
| Complexity Warnings | 27 (>15 score) |

### Token Efficiency

| Tool | Savings |
|------|---------|
| `extract_code` | 61% token reduction vs full file |
| Target code | 13 lines |
| Context code | 628 lines |
| Token estimate | 7,755 (vs ~20,000 full file) |

### Detection Rate Evolution

| Version | Rate | Notes |
|---------|------|-------|
| Initial (Nov) | 0% | All tools broken |
| Update 1 | 62.5% | Basic SQL/Command/Path |
| Update 2 | 89% | Added line numbers |
| Update 3 | 100% | Added Flask XSS, SSTI, XXE |
| **v1.5.1** | **100%** | **Production-ready** |

---

## [PREVIEW] Future Roadmap

- **v1.6.0:** Multi-language support (JavaScript, TypeScript)
- **v1.7.0:** IDE integration (VS Code extension)
- **v2.0.0:** Full polyglot analysis (Java, Go, Rust)

---

## [NOTE] Changelog

### v1.5.1 (December 13, 2025)

**Added:**
- `ImportResolver` class for building import dependency graphs
- `CrossFileExtractor` class for extracting code with cross-file dependencies
- `CrossFileTaintTracker` class for detecting cross-file vulnerabilities
- `get_cross_file_dependencies` MCP tool
- `cross_file_security_scan` MCP tool
- 142 new tests for all v1.5.1 features
- 10 integration tests for end-to-end workflows

**Changed:**
- Updated `ast_tools/__init__.py` with new exports
- Updated `symbolic_execution_tools/__init__.py` with new exports
- Enhanced `mcp/server.py` with 2 new MCP tools

**Fixed:**
- No bug fixes in this release (new features only)

---

## [DOCUMENTATION] Documentation

- [API Reference](../api_reference.md)
- [Getting Started Guide](../getting_started.md)
- [Agent Integration](../agent_integration.md)
- [Cross-File Analysis Guide](../guides/cross_file_analysis.md) (new)

---

## [THANKS] Credits

Built with the Code Scalpel team's commitment to surgical precision in code analysis.

**Total MCP Tools:** 15  
**Total Test Suite:** 2,258 tests  
**Production Ready:** [COMPLETE]
