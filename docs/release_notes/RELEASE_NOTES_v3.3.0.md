# Release Notes - v3.3.0

**Release Date:** December 25, 2025  
**Version:** 3.3.0 "Project Reorganization"  
**Release Type:** Minor (Non-Breaking)

---

## Executive Summary

Version 3.3.0 completes the comprehensive project reorganization (Phases 1-4) that restructures the codebase for better maintainability, discoverability, and modularity. All changes maintain **full backward compatibility** through deprecation warning stubs, allowing existing code to continue working while encouraging migration to new import paths.

---

## Key Features

### 1. Module Reorganization (Phases 1-4)

**Phase 1: Core Module Creation**
- **quality_assurance/** - Error scanning and fixing tools
  - `error_scanner.py` - Code error detection
  - `error_fixer.py` - Automated error correction
- **surgery/** - Surgical code modification tools
  - `surgical_extractor.py` - Precise code extraction
  - `surgical_patcher.py` - Safe code patching
  - `unified_extractor.py` - Universal polyglot extraction
- **analysis/** - Code analysis tools
  - `code_analyzer.py` - AST-based analysis
  - `project_crawler.py` - Project-wide scanning
  - `core.py` - Analysis toolkit core

**Phase 2: Security & Licensing Modules**
- **licensing/** - License tier management
  - `tier_detector.py` - Tier detection
  - `license_manager.py` - License validation
  - `validator.py` - Validation logic
  - `cache.py` - License caching
- **tiers/** - Tier enforcement
  - `decorators.py` - @requires_tier decorator
  - `feature_registry.py` - Feature tier mapping
  - `tool_registry.py` - MCP tool tier mapping
- **security/** - Security analysis (6 subdirectories)
  - `analyzers/` - Security analyzers
  - `type_safety/` - Type evaporation detection
  - `dependencies/` - Dependency scanning
  - `sanitization/` - Input sanitization analysis
  - `secrets/` - Secret detection
  - `ml/` - ML vulnerability prediction

**Phase 3: Protocol Analyzers**
- **integrations/protocol_analyzers/** - Protocol analysis tools
  - `graphql/schema_tracker.py` - GraphQL schema tracking
  - `grpc/contract_analyzer.py` - gRPC contract analysis
  - `kafka/taint_tracker.py` - Kafka message taint tracking
  - `schema/drift_detector.py` - Protocol buffer drift detection
  - `frontend/input_tracker.py` - Frontend input tracking (React/Vue/Angular)

**Phase 4: Remaining File Moves**
- `governance_config.py` → `governance/governance_config.py`
- `osv_client.py` → `security/dependencies/osv_client.py`

### 2. Backward Compatibility System

All reorganized modules include backward compatibility stubs with deprecation warnings:

```python
# Old import (still works, shows deprecation warning):
from code_scalpel.code_analyzer import CodeAnalyzer

# New import (recommended):
from code_scalpel.analysis import CodeAnalyzer
```

### 3. Fixed Issues

- **langchain.py** - Fixed incomplete module stub (missing closing docstring)
- **decorators.py** - Fixed Pyright type error for tier enum handling
- **Test imports** - Updated test imports for private functions to use canonical locations

---

## Statistics

### Test Results
| Metric | Value |
|--------|-------|
| Total Tests | 4,431 |
| Passed | 4,431 |
| Skipped | 17 |
| Pass Rate | 100% |

### Quality Gates
| Check | Status |
|-------|--------|
| Black Formatting | ✅ PASSED |
| Ruff Linting | ✅ PASSED (32 E402 expected in compat stubs) |
| Pyright Type Checking | ✅ PASSED (0 errors) |
| Bandit Security Scan | ✅ PASSED (No Medium/High issues) |
| pip-audit Dependencies | ✅ PASSED (No vulnerabilities) |
| Package Build | ✅ PASSED |
| twine check | ✅ PASSED |

### Package Size
| Artifact | Size |
|----------|------|
| Wheel | code_scalpel-3.3.0-py3-none-any.whl |
| Source | code_scalpel-3.3.0.tar.gz |

### Lines of Code
| Category | Count |
|----------|-------|
| Lines Scanned (Bandit) | 102,972 |
| Files | 520 |

---

## Migration Guide

### Import Path Changes

| Old Path | New Path |
|----------|----------|
| `code_scalpel.code_analyzer` | `code_scalpel.analysis` |
| `code_scalpel.project_crawler` | `code_scalpel.analysis` |
| `code_scalpel.surgical_extractor` | `code_scalpel.surgery` |
| `code_scalpel.unified_extractor` | `code_scalpel.surgery` |
| `code_scalpel.surgical_patcher` | `code_scalpel.surgery` |
| `code_scalpel.symbolic_execution_tools.taint_tracker` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.security_analyzer` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.unified_sink_detector` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.type_evaporation_detector` | `code_scalpel.security.type_safety` |
| `code_scalpel.symbolic_execution_tools.vulnerability_scanner` | `code_scalpel.security.dependencies` |
| `code_scalpel.symbolic_execution_tools.graphql_schema_tracker` | `code_scalpel.integrations.protocol_analyzers.graphql` |
| `code_scalpel.symbolic_execution_tools.grpc_contract_analyzer` | `code_scalpel.integrations.protocol_analyzers.grpc` |
| `code_scalpel.symbolic_execution_tools.kafka_taint_tracker` | `code_scalpel.integrations.protocol_analyzers.kafka` |
| `code_scalpel.symbolic_execution_tools.schema_drift_detector` | `code_scalpel.integrations.protocol_analyzers.schema` |
| `code_scalpel.symbolic_execution_tools.frontend_input_tracker` | `code_scalpel.integrations.protocol_analyzers.frontend` |
| `code_scalpel.config.governance_config` | `code_scalpel.governance` |
| `code_scalpel.ast_tools.osv_client` | `code_scalpel.security.dependencies` |

### Deprecation Timeline

- **v3.3.0** - Deprecation warnings added
- **v4.0.0** - Old import paths will be removed

---

## Known Issues

- 1 Pyright warning (invalid escape sequence in path_resolver.py) - cosmetic only

---

## Contributors

- Tim Escolopio (@tescolopio)

---

## Upgrade Instructions

```bash
# Upgrade from PyPI (when published)
pip install --upgrade code-scalpel==3.3.0

# Or install from source
git checkout v3.3.0
pip install -e .
```

---

## Full Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for complete history.
