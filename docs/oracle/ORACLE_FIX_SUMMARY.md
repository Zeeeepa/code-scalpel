# Oracle Resilience - Issue Found & Fixed

## The Problem You Discovered ✅

Your testing revealed that the oracle middleware was **NOT working** because:

1. **Test showed**: Error messages had available functions listed, but NOT as structured suggestions
2. **Error code**: Was not `"correction_needed"`
3. **No confidence scores**: Suggestions lacked ranking

## Root Cause 🔍

The decorator was applied outside the tool's try/catch block:

```python
@mcp.tool()
@with_oracle_resilience(...)  # ← Decorator here
async def extract_code(...):
    try:
        result = await _extract_code(...)  # ← Exception raised
        return make_envelope(data=result)
    except Exception as exc:  # ← Caught HERE first!
        return make_envelope(error=ToolError(...))  # ← Oracle never sees it
```

**Flow Problem**:
1. Tool raises ValidationError inside try/catch
2. Tool catches it and returns envelope with error
3. Decorator receives the envelope (not the exception)
4. Decorator has no post-processing logic, so it just returns it as-is
5. Oracle never enhances the error with suggestions

## The Solution 🔧

Updated `oracle_middleware.py` to do **two-stage error processing**:

### Stage 1: Direct Exception Catching (Unchanged)
If exception bubbles up to decorator, catch it (for direct raises)

### Stage 2: NEW - Error Envelope Post-Processing
After tool returns envelope, check if it contains a correctable error

```python
async def wrapper(*args, **kwargs):
    try:
        result = await func(*args, **kwargs)

        # NEW: Post-process error envelopes
        if isinstance(result, ToolResponseEnvelope) and result.error:
            enhanced = _enhance_error_envelope(
                result, tool_id, strategy, kwargs, started
            )
            if enhanced:
                return enhanced  # Return enhanced version with suggestions

        return result
```

### New Helper Function: `_enhance_error_envelope()`

```python
def _enhance_error_envelope(envelope, tool_id, strategy, kwargs, started):
    """
    Checks if error looks correctable (missing symbol/file)
    If so, generates suggestions and returns enhanced envelope
    """
    # 1. Check error message for "not found" + symbol/function/class
    # 2. If match, use strategy to generate suggestions
    # 3. Update error code to "correction_needed"
    # 4. Add suggestions to error_details
    # 5. Return new envelope with enhanced error
```

---

## What Changed in oracle_middleware.py

### Added Function
- `_enhance_error_envelope()` - Post-processes error envelopes to add suggestions

### Modified Function
- `with_oracle_resilience()` wrapper now:
  1. Calls tool function
  2. Checks if result is error envelope
  3. If so, calls `_enhance_error_envelope()` to add suggestions
  4. Returns enhanced envelope or original

---

## Impact on All 7 Pilot Tools

This fix applies to ALL tools using `@with_oracle_resilience`:

1. ✅ extract_code
2. ✅ rename_symbol
3. ✅ update_symbol
4. ✅ get_symbol_references
5. ✅ get_call_graph
6. ✅ get_graph_neighborhood
7. ✅ get_cross_file_dependencies

---

## Testing the Fix

### Before Fix
```bash
# Typo: "proces_data"
Error: "Function 'proces_data' not found. Available: [...]"
(No structured suggestions, no error_code change)
```

### After Fix
```bash
# Typo: "proces_data"
Error: "Function 'proces_data' not found. Did you mean: process_data?"
error_code: "correction_needed"
error_details: {
  "suggestions": [
    {"symbol": "process_data", "score": 0.95, "reason": "fuzzy_match"}
  ]
}
```

---

## Next Steps

1. **Re-run your MCP Inspector tests** with the fix
2. **Update test results** in `ORACLE_PILOT_TEST_RESULTS.md`
3. **Verify all 7 tools** now return proper suggestions
4. If tests pass, proceed to **Phase 4** expansion (Group A tools)

---

## Files Modified

- `src/code_scalpel/mcp/oracle_middleware.py`
  - Added `_enhance_error_envelope()` function
  - Updated wrapper to post-process envelopes
  - Added comment explaining two-stage processing

No other files needed to change - the fix is purely in the oracle middleware!
