# Archived Parsers

This directory contains parser implementations that have been deprecated and archived.

---

## `legacy_parsers/` - Deprecated v3.0.x

**Archived:** December 21, 2025 (v3.1.0)  
**Reason:** Superseded by `code_parsers/` multi-language system

### What was `parsers/`?

A minimal Python-only parser implementation that was kept for backward compatibility with old tests. It was NOT used in production.

**Contents:**
- `base_parser.py` - Minimal base parser interface
- `python_parser.py` - Basic Python AST parser
- `factory.py` - Simple parser factory

**Size:** 32KB

### Why Archived?

1. **Superseded:** `code_parsers/` provides:
   - 10 programming languages (vs Python only)
   - 40+ parser strategies per language
   - Unified factory pattern with auto-detection
   - Production-grade implementations

2. **Not Used:** Zero imports in production code:
   ```bash
   grep -r "from code_scalpel.parsers import" src/ → 0 results
   ```

3. **Confusing Naming:** 
   - `parsers/` - Legacy minimal
   - `code_parsers/` - Production (correct name)

### Migration

**Old (deprecated):**
```python
from code_scalpel.parsers import BaseParser, PythonParser
```

**New (v3.1.0+):**
```python
from code_scalpel.code_parsers import BaseParser, PythonParser
```

### Can I Delete This?

**Not yet.** While archived, we're keeping these files temporarily in case:
- External projects still reference them
- Old tests need updating
- Historical reference needed

**Target for deletion:** v4.0.0 (major version bump)

---

## Archive History

| Directory | Archived | Size | Reason |
|-----------|----------|------|--------|
| `legacy_parsers/` | 2025-12-21 | 32KB | Superseded by code_parsers/ |

---

**See also:**
- [../code_parsers/](../code_parsers/) - Current production parsers
- [PARSER_CONSOLIDATION_PLAN.md](../../../../PARSER_CONSOLIDATION_PLAN.md) - Full consolidation strategy
