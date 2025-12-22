# Code Scalpel - Source Code

**Version:** 3.0.5 "Ninja Consolidation"  
**Release Date:** December 23, 2025

## Overview

This is the main source directory for Code Scalpel, an MCP server toolkit for AI-driven surgical code analysis and modification.

## Module Organization

### Core Analysis
- **ast_tools/** - AST parsing and analysis
- **pdg_tools/** - Program Dependence Graph construction and analysis
- **symbolic_execution_tools/** - Symbolic execution engine and security analysis (500K+ LOC)

### Language Support
- **polyglot/** - Modern multi-language parsing (tree-sitter based)
- **code_parser/** - Legacy language-specific parsers
- **ir/** - Unified Intermediate Representation for cross-language analysis
- **parsers/** - Lightweight parser factory

### Security & Governance
- **security/** - Security analysis tools and vulnerability detection
- **policy_engine/** - Policy enforcement and semantic analysis
- **policy/** - Change budget and modification limits
- **governance/** - Compliance reporting and audit logging

### Code Modification
- **generators/** - Test generation and refactoring simulation
- **surgical_extractor.py** - Precise code extraction
- **surgical_patcher.py** - Safe code modification
- **code_analyzer.py** - Single-file code analysis
- **project_crawler.py** - Project-wide analysis

### Infrastructure
- **cache/** - Unified caching layer (v3.0.5 consolidation)
- **utilities/** - Path resolution and shared utilities
- **config/** - Configuration management
- **graph_engine/** - Dependency graph construction

### Integrations
- **mcp/** - MCP server with 20 tools
- **integrations/** - REST API, AutoGen, CrewAI integrations
- **agents/** - AI agent implementations
- **autonomy/** - Error-to-diff autonomous fixing engine

## Quick Start

```python
# Import core functionality
from code_scalpel import (
    CodeAnalyzer,
    AnalysisResult,
    extract_function,
    update_function_in_file,
)

# Analyze code
analyzer = CodeAnalyzer()
result = analyzer.analyze("def foo(): return 1")
print(result.metrics.num_functions)

# Extract function
from code_scalpel import extract_function
func_code = extract_function(file_path, "function_name")

# Start MCP server
from code_scalpel import run_server
run_server(port=8080)
```

## Module Statistics (v3.0.5)

| Module | LOC | Status | Coverage |
|--------|-----|--------|----------|
| symbolic_execution_tools | 500K+ | Stable | 95%+ |
| ir | 180K+ | Stable | 95%+ |
| code_parser | 150K+ | Legacy | 90%+ |
| polyglot | 80K+ | Stable | 90%+ |
| pdg_tools | 120K+ | Stable | 100% |
| mcp | 4K+ | Stable | 100% |
| **Total** | **~1.2M LOC** | | **94.86%** |

## Key Features (v3.0.5)

✅ **Cache Consolidation** - Unified cache implementation (eliminated 277 LOC redundancy)  
✅ **20 MCP Tools** - Full toolkit for AI agents  
✅ **Multi-Language** - Python, Java, JavaScript, TypeScript support  
✅ **Security Analysis** - OWASP Top 10 vulnerability detection  
✅ **Symbolic Execution** - Path exploration with Z3 solver  
✅ **Cross-File Analysis** - Dependency tracking across modules  
✅ **Test Generation** - Automated unit test creation  
✅ **Autonomy Engine** - Error-to-diff automatic fixing  

## Documentation

- **Architecture:** `docs/architecture/`
- **Guides:** `docs/guides/`
- **API Reference:** `docs/modules/`
- **Release Notes:** `docs/release_notes/RELEASE_NOTES_v3.0.5.md`
- **Organizational Analysis:** `ORGANIZATIONAL_ANALYSIS.md`

## Testing

```bash
# Run all tests
pytest tests/

# Run specific module tests
pytest tests/test_cache/
pytest tests/test_symbolic_execution/

# Coverage report
pytest --cov=src/code_scalpel --cov-report=html
```

## Development

```bash
# Install in development mode
pip install -e .

# Format code
black src/code_scalpel
ruff check src/code_scalpel --fix

# Type checking
mypy src/code_scalpel
```

## Module READMEs

Every subdirectory contains a README.md with detailed module documentation:
- Purpose and overview
- Key components and APIs
- Usage examples
- Integration points
- Version status

## v3.0.5 Changes

**Cache Consolidation:**
- Merged `cache/analysis_cache.py` + `utilities/cache.py` → `cache/unified_cache.py`
- Eliminated 277 lines of redundancy
- Preserved all features from both implementations
- Backward compatible imports

**Documentation:**
- Fixed MCP tool count (19 → 20)
- Created READMEs for all 33 directories
- Archived old cache implementations with explanation

## Contact

- **Author:** Tim Escolopio
- **Email:** 3dtsus@gmail.com
- **License:** MIT
- **Repository:** [code-scalpel](https://github.com/yourusername/code-scalpel)
