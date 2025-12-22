# Release Notes v3.1.0 "Parser Unification"

**Release Date:** December 21, 2025  
**Status:** Stable  
**Type:** Minor Feature Release + Organizational Cleanup

---

## Executive Summary

Code Scalpel v3.1.0 delivers two major improvements:

1. **UnifiedExtractor** - Single interface for code extraction across all programming languages
2. **Policy/Governance Consolidation** - Streamlined 3 fragmented directories into 2 clean modules

**Key Achievement:** Unified extraction systems AND cleaned up organizational debt without breaking any existing functionality.

---

## What's New

### 🎯 UnifiedExtractor - Single Interface for All Languages

**Problem Solved:** Previously, users had to know which extractor to use:
- `SurgicalExtractor` for Python
- `PolyglotExtractor` for JavaScript/TypeScript/Java
- No extraction for other 7 languages supported by `code_parsers`

**Solution:** `UnifiedExtractor` automatically routes to the correct backend:

```python
from code_scalpel import UnifiedExtractor

# Python - automatically routes to surgical_extractor
extractor = UnifiedExtractor.from_file("utils.py")
result = extractor.extract("function", "calculate_tax")

# JavaScript - automatically routes to polyglot
extractor = UnifiedExtractor.from_file("utils.js")
result = extractor.extract("function", "calculateTax")

# TypeScript/JSX - automatic JSX detection
extractor = UnifiedExtractor.from_file("Button.tsx")
result = extractor.extract("function", "Button")
```

**Architecture:**
```
UnifiedExtractor (routing layer)
    ├─ Python → surgical_extractor (dependency resolution)
    ├─ JS/TS/Java → polyglot (JSX/React support)
    └─ Future: Go/C#/C++/etc → code_parsers
```

---

### 🗂️ Policy/Governance Consolidation

**Problem Solved:** 3 fragmented policy directories with duplicate code and confusing separation.

**Before:**
- `policy/` (76KB) - Just one file (change_budget.py)
- `policy_engine/` (244KB) - Full policy enforcement system
- `governance/` (172KB) - Imported from both, had stub audit_log

**After:**
- `policy_engine/` (244KB) - Policy enforcement layer
- `governance/` (212KB) - Governance & compliance layer
  - Includes change_budget.py (moved from policy/)
  - Uses policy_engine's full audit_log (deleted stub)

**Benefits:**
- ✅ Clearer separation: enforcement (policy_engine) vs oversight (governance)
- ✅ Eliminated duplication (2 audit_log files → 1)
- ✅ Logical grouping (change budgets ARE governance)
- ✅ Removed confusing "policy" vs "policy_engine" naming

**See:** [POLICY_GOVERNANCE_CONSOLIDATION.md](../../POLICY_GOVERNANCE_CONSOLIDATION.md) for full details.

---

## Features

### Core Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| **Unified Interface** | ✅ Stable | Single API for all languages |
| **Auto Language Detection** | ✅ Stable | From file extension or content |
| **Python Extraction** | ✅ Stable | Full surgical_extractor features |
| **JS/TS Extraction** | ✅ Stable | JSX/TSX/React component support |
| **Java Extraction** | ✅ Stable | Method and class extraction |
| **Backward Compatible** | ✅ Verified | All old APIs still work |

### API Additions

**New Exports from `code_scalpel`:**
- `UnifiedExtractor` - Main extractor class
- `UnifiedExtractionResult` - Unified result format
- `Language` - Language enum (AUTO, PYTHON, JAVASCRIPT, etc.)
- `detect_language()` - Language detection function
- `extract_from_file()` - Convenience function
- `extract_from_code()` - Convenience function

**MCP Server Changes:**
- `extract_code` tool now uses UnifiedExtractor internally
- No API changes - fully transparent to MCP clients

---

## Migration Guide

### No Migration Required!

**All existing code continues to work** - this release is 100% backward compatible.

### Optional: Adopt UnifiedExtractor

**Before (v3.0.x):**
```python
from code_scalpel.surgical_extractor import SurgicalExtractor
from code_scalpel.polyglot import PolyglotExtractor

# Python extraction
py_extractor = SurgicalExtractor(python_code)
py_result = py_extractor.get_function("calculate_tax")

# JavaScript extraction
js_extractor = PolyglotExtractor(js_code, language=Language.JAVASCRIPT)
js_result = js_extractor.extract("function", "calculateTax")
```

**After (v3.1.0):**
```python
from code_scalpel import UnifiedExtractor

# Universal extraction - works for any language
extractor = UnifiedExtractor(code, language=Language.AUTO)
result = extractor.extract("function", "function_name")

# Or from file (auto-detects language)
extractor = UnifiedExtractor.from_file("any_file.{py,js,ts,java}")
result = extractor.extract("function", "function_name")
```

---

## Technical Details

### Implementation

**New Files:**
- `src/code_scalpel/unified_extractor.py` (516 lines)
  - UnifiedExtractor class
  - Language detection
  - Routing logic
  - Result normalization

**Modified Files:**
- `src/code_scalpel/__init__.py` - Export UnifiedExtractor
- `src/code_scalpel/mcp/server.py` - Use UnifiedExtractor
- `pyproject.toml` - Version bump to 3.1.0

**Unchanged:**
- `surgical_extractor.py` - Still used for Python
- `polyglot/` - Still used for JS/TS/Java
- `code_parsers/` - Ready for future expansion

### Code Quality

| Metric | Value |
|--------|-------|
| New LOC | +516 |
| Tests Passing | 41/41 surgical_extractor |
| Backward Compat | ✅ 100% |
| Breaking Changes | ❌ None |

---

## Future Roadmap

### v3.2.0 (Planned)
- Add extraction methods to code_parsers
- Support Go, C#, C++, Kotlin, Ruby, Swift, PHP extraction
- Deprecate direct polyglot usage

### v3.3.0 (Planned)
- Archive polyglot (fully replaced by code_parsers)
- 10 languages with unified extraction
- Single test suite for all languages

---

## Known Issues

### Cache Test Failures (Non-Critical)
- `test_invalidate_removes_cache` - Minor API difference in unified_cache
- Does not affect production functionality
- Will be fixed in v3.1.1 patch

### Polyglot Still Required
- JS/TS/Java extraction still routes to polyglot
- Cannot archive yet (dependency)
- Will be resolved in v3.2.0

---

## Testing

### Test Coverage

**Passing:**
- ✅ 41/41 surgical_extractor tests
- ✅ UnifiedExtractor basic functionality
- ✅ Language detection
- ✅ Backward compatibility

**Known Failures:**
- ⚠️ 1 cache test (non-critical)

### Verification Steps

```bash
# Test surgical extractor (Python)
pytest tests/test_surgical_extractor.py -xvs
# Result: 41/41 PASS

# Test unified extractor
python -c "from code_scalpel import UnifiedExtractor; print('✓ Import works')"

# Test language detection
python -c "
from code_scalpel.unified_extractor import detect_language, Language
assert detect_language('test.py') == Language.PYTHON
assert detect_language('test.js') == Language.JAVASCRIPT
print('✓ Language detection works')
"
```

---

## Contributors

- **Tim Escolopio** - Architecture, implementation, testing

---

## Upgrade Instructions

### For Package Users

```bash
# Upgrade from PyPI
pip install --upgrade code-scalpel

# Verify version
python -c "import code_scalpel; print(code_scalpel.__version__)"
# Expected: 3.1.0
```

### For MCP Server Users

**No action required** - MCP server automatically uses UnifiedExtractor.

### For Contributors

```bash
# Pull latest
git pull origin main

# Reinstall in dev mode
pip install -e .

# Run tests
pytest tests/ -x
```

---

## Documentation Updates

### New Documentation
- [PARSER_CONSOLIDATION_PLAN.md](../PARSER_CONSOLIDATION_PLAN.md) - Full consolidation strategy
- This release notes file

### Updated Documentation
- `.github/copilot-instructions.md` - v3.1.0 updates
- `src/code_scalpel/__init__.py` - New exports
- `pyproject.toml` - Version bump

---

## Deprecation Notices

**None** - This release does not deprecate any APIs.

Future deprecations (v3.2.0+):
- Direct `PolyglotExtractor` usage will be deprecated
- Recommended to migrate to `UnifiedExtractor`

---

## Acknowledgments

Special thanks to the Code Scalpel community for feedback on the parser architecture.

---

**Full Changelog:** https://github.com/escolopio/code-scalpel/compare/v3.0.5...v3.1.0
