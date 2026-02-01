# Release Notes: Code Scalpel v1.3.0

**Release Date:** February 1, 2026  
**Codename:** Oracle Resilience

---

## Executive Summary

Version 1.3.0 introduces the **Oracle Resilience Middleware** - an automatic error recovery system that helps AI agents recover from common mistakes like typos, path errors, and symbol mismatches. This release significantly improves the developer experience when using Code Scalpel with AI assistants like Claude, GitHub Copilot, and Cursor.

---

## Highlights

### 🔮 Oracle Resilience Middleware

The Oracle middleware automatically detects and recovers from common AI agent errors:

| Error Type | Example | Recovery |
|------------|---------|----------|
| Symbol typos | `procss_data` | Suggests `process_data` (fuzzy match) |
| Path errors | `/wrong/path/file.py` | Suggests workspace-relative paths |
| Method format | `calculate` | Suggests `Calculator.calculate` |
| Node ID format | `process_order` | Suggests `python::module::function::process_order` |

**Key Features:**
- **`@with_oracle_resilience`** decorator for MCP tools
- **Symbol fuzzy matching** using Levenshtein distance
- **Path resolution** with workspace-aware suggestions
- **Composable strategies** for complex recovery scenarios
- **Zero configuration** - works out of the box

### 📚 Documentation Reorganization

All documentation has been reorganized for better discoverability:

| Category | Location |
|----------|----------|
| Oracle docs | `docs/oracle/` |
| API reference | `docs/reference/` |
| Architecture | `docs/architecture/` |
| Getting started | `docs/getting_started/` |

---

## What's New

### Added
- **Oracle Resilience Middleware** (`src/code_scalpel/mcp/oracle_middleware.py`)
  - `@with_oracle_resilience` decorator
  - `SymbolStrategy` - fuzzy symbol matching
  - `PathStrategy` - intelligent path resolution
  - `SafetyStrategy` - refactoring validation
  - `NodeIdFormatStrategy` - node ID format recovery
  - `MethodNameFormatStrategy` - method name format recovery
  - `CompositeStrategy` - strategy chaining

- **Stage 2 Error Enhancement**
  - `_enhance_error_envelope()` - top-level error processing
  - `_enhance_data_error()` - nested error processing
  - Consistent error enhancement across all error locations

- **Test Coverage**
  - 61 Oracle middleware tests (100% pass rate)
  - Tier isolation tests (Community/Pro/Enterprise)
  - Stage 2 before/after example tests

### Changed
- Test suite updated to handle Oracle-enhanced `ToolError` objects
- Documentation reorganized into logical subdirectories
- Root directory cleaned up (10+ files moved to proper locations)

### Fixed
- Black formatting exclusion for intentionally broken test files
- Unused imports cleaned up across test suite
- `envelope.error` check now uses `model_dump()` for Pydantic v2 compatibility

---

## Migration Guide

### No Breaking Changes

Version 1.3.0 is fully backward compatible. The Oracle middleware is opt-in and does not affect existing tool behavior.

### Enabling Oracle Resilience

Oracle resilience is automatically enabled for all MCP tools. No configuration required.

To see Oracle suggestions in action:

```python
# Intentional typo - Oracle will suggest correction
result = await extract_code(
    file_path="/path/to/file.py",
    target_type="function",
    target_name="procss_data"  # Typo!
)

# Result includes suggestion:
# error="Function 'procss_data' not found. Did you mean: process_data?"
```

---

## Documentation

- **Quick Start**: [Oracle Resilience Quickstart](../oracle/ORACLE_RESILIENCE_QUICKSTART.md)
- **Integration Guide**: [Oracle Integration Guide](../oracle/ORACLE_INTEGRATION_GUIDE.md)
- **Implementation**: [Oracle Implementation Details](../ORACLE_RESILIENCE_IMPLEMENTATION.md)
- **Test Cases**: [Oracle Test Cases](../ORACLE_RESILIENCE_TEST_CASES.md)

---

## Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 4,100+ |
| Oracle Tests | 61 |
| Pass Rate | 100% |
| Coverage | 94.86% |

---

## Contributors

- Oracle Resilience Middleware implementation
- Documentation reorganization
- Test suite improvements

---

## Upgrade Instructions

```bash
# From PyPI
pip install --upgrade codescalpel

# Verify version
python -c "import code_scalpel; print(code_scalpel.__version__)"
# Output: 1.3.0
```

---

## Known Issues

None at this time.

---

## Next Release Preview (v1.4.0)

Planned features:
- Cache invalidation strategies (TTL-based)
- Parallel file scanning for large projects
- Incremental project updates
- Custom language profile support
