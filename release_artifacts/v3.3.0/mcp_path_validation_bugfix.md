# Section 2.1: Root Cause Analysis - MCP Path Validation Bug

**Date:** 2025-12-26
**Issue:** 6 failing tests in TestUpdateSymbolTool
**Root Cause:** MCP server path validation doesn't respect SCALPEL_ROOT environment variable

## Problem Analysis

### Failure Pattern
All 6 failures have the same error:
```
PermissionError: Access denied: /tmp/pytest-of-xbyooki/pytest-551/test_update_function_in_file0/test.py is outside allowed roots.
Allowed roots: /mnt/k/backup/Develop/code-scalpel
```

### Root Cause
The MCP server validates file paths against `ALLOWED_ROOTS` during `update_symbol` execution:

1. **Test Setup** (correct):
   - Tests set `SCALPEL_ROOT` environment variable to `tmp_path`
   - `monkeypatch.setenv("SCALPEL_ROOT", str(tmp_path))`

2. **MCP Server Issue** (incorrect):
   - `PROJECT_ROOT` is set at module import time: `PROJECT_ROOT = Path.cwd()`
   - `_validate_path_security()` checks `ALLOWED_ROOTS` which starts empty: `ALLOWED_ROOTS: list[Path] = []`
   - When `ALLOWED_ROOTS` is empty, defaults to `PROJECT_ROOT` (which is the git repo root)
   - The path validation never checks the `SCALPEL_ROOT` environment variable

### Evidence
From [src/code_scalpel/mcp/server.py](src/code_scalpel/mcp/server.py#L1528):

```python
def _validate_path_security(path: Path) -> Path:
    resolved = path.resolve()
    
    if not _is_path_allowed(resolved):
        roots_str = ", ".join(str(r) for r in (ALLOWED_ROOTS or [PROJECT_ROOT]))
        raise PermissionError(
            f"Access denied: {path} is outside allowed roots.\n"
            f"Allowed roots: {roots_str}\n"
            f"Set roots via the roots/list capability or SCALPEL_ROOT environment variable."
        )
```

**The bug:** The error message says "Set roots via... SCALPEL_ROOT environment variable" but the code never actually checks `SCALPEL_ROOT`!

## Solution

The MCP server needs to respect the `SCALPEL_ROOT` environment variable at runtime. Current code:

```python
ALLOWED_ROOTS: list[Path] = []
PROJECT_ROOT = Path.cwd()

def _validate_path_security(path: Path) -> Path:
    resolved = path.resolve()
    if not _is_path_allowed(resolved):
        roots_str = ", ".join(str(r) for r in (ALLOWED_ROOTS or [PROJECT_ROOT]))
        raise PermissionError(...)
```

Should be:

```python
def _validate_path_security(path: Path) -> Path:
    resolved = path.resolve()
    
    # Check SCALPEL_ROOT from environment at runtime
    scalpel_root = os.environ.get("SCALPEL_ROOT")
    allowed_roots = ALLOWED_ROOTS or [PROJECT_ROOT]
    if scalpel_root:
        allowed_roots = [Path(scalpel_root)] + allowed_roots
    
    if not any(is_path_within(resolved, root) for root in allowed_roots):
        roots_str = ", ".join(str(r) for r in allowed_roots)
        raise PermissionError(...)
```

## Fix Strategy

**Option A: Check SCALPEL_ROOT in path validation** (RECOMMENDED)
- Modify `_validate_path_security()` to check `SCALPEL_ROOT` environment variable
- Add SCALPEL_ROOT to allowed roots before validation
- Estimated fix time: 5-10 minutes
- Risk: Low (just adds an environment variable check)
- Test impact: All 6 failing tests should pass

**Option B: Modify tests to change working directory**
- Not recommended - MCP server should handle test environments properly
- Tests correctly use pytest tmp_path fixture and monkeypatch

## Recommendation

Implement **Option A** - fix the MCP server path validation to respect SCALPEL_ROOT at runtime. This is a clear bug: the error message tells users to set SCALPEL_ROOT, but the code doesn't actually check it.

## Testing After Fix

After implementing the fix, run:
```bash
pytest tests/mcp/test_mcp.py::TestUpdateSymbolTool -v
```

All 6 tests should pass:
- test_update_function_in_file
- test_update_class_in_file
- test_update_method_in_file
- test_update_function_not_found
- test_update_no_backup
- test_update_lines_delta
- test_extract_modify_update_workflow
