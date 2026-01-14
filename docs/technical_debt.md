# Technical Debt Register

**Version:** 3.3.0  
**Last Updated:** January 12, 2026

---

## File Length Violations

The following files exceed the recommended 1000 LOC threshold. These have been granted temporary waivers for v3.3.0 due to the risk of refactoring core infrastructure late in the release cycle.

| File | Lines | Priority | Target Version | Notes |
|------|-------|----------|----------------|-------|
| `src/code_scalpel/mcp/server.py` | 21,696 | P2 | v3.4.0 | MCP server with 22 tools - candidate for tool extraction into separate modules |
| `src/code_scalpel/code_parsers/python_parsers/python_parsers_ast.py` | 4,049 | P3 | v3.5.0 | AST parsing logic - consider splitting by visitor pattern |
| `src/code_scalpel/surgery/surgical_extractor.py` | 3,691 | P2 | v3.4.0 | Core extraction tool - split by language support |
| `src/code_scalpel/surgery/surgical_patcher.py` | 3,018 | P2 | v3.4.0 | Core patching tool - split by operation type |
| `src/code_scalpel/security/analyzers/taint_tracker.py` | 2,516 | P3 | v3.5.0 | Security taint analysis - complex state machine |

### Remediation Strategy

1. **server.py** (P2): Extract each MCP tool handler into `src/code_scalpel/mcp/tools/<tool_name>.py`
2. **surgical_extractor.py** (P2): Split into language-specific extractors
3. **surgical_patcher.py** (P2): Split into operation-specific patchers
4. **Parser files** (P3): Group AST visitors by purpose (analysis, extraction, security)

---

## Test Infrastructure Issues

### Hanging Tests (v3.3.0)

The following test files contain integration tests that spawn MCP server processes and may hang in CI environments:

| File | Issue | Workaround |
|------|-------|------------|
| `tests/mcp/test_tier_boundary_limits.py` | Spawns stdio MCP server | Run with explicit timeout or skip in CI |
| `tests/mcp/test_mcp_http_sse_all_tools_end_to_end.py` | Requires running HTTP server | Skip in basic CI, run in integration suite |

**Resolution:** These tests should be tagged with `@pytest.mark.slow` and excluded from default CI runs.

---

## Unused Variable Warnings (F841)

64 F841 warnings remain in test files. These are **intentional** - the tests verify that operations complete without exceptions. The assigned variables demonstrate the operation was performed.

Example pattern:
```python
result = await some_operation()  # F841: assigned but not used
# Test passes if no exception was raised
```

**Decision:** Accept as-is. The test pattern is valid for integration testing.

---

## Print Statement Usage

377 `print()` calls exist in `src/`:
- **170** in `cli.py` - CLI output (allowed)
- **~200** in docstrings as examples (allowed)
- **~7** in server startup banner (allowed)

**Decision:** No action required. These are legitimate uses, not debug statements.
