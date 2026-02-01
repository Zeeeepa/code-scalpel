# Oracle Resilience Pilot Test Results

**Date**: 1/30/2026
**Tester**: TEscolopio
**MCP Server Version**: Code Scalpel MCP Server v1.2.1
**License Tier**: Community Tier

---

## Summary

| Metric | Value |
|--------|-------|
| Tools Tested | 7 |
| Total Test Cases | 7+ |
| Passed | |
| Failed | |
| Success Rate | % |

---

## Test Results by Tool

### ✅ 1. extract_code

**Test 1.1 - Basic Typo: "proces_data"**
- Input file: `test_code.py`
- Target: `proces_data` (typo)
- Expected suggestion: `process_data`
- Result: X PASS / ⬜ FAIL
- Error code: error:
"Function 'proces_data' not found. Available: ['process_data', 'process_item', 'calculate_sum', 'calculate_product', 'main']"
- Top suggestion: _______________
- Suggestion score: No Score presented
- Notes: Did not rank "process_data" as top suggestion.

**Test 1.2 - Ninja Warrior Legacy**
- Result: ⬜ PASS / X FAIL
- Notes:
Tool Result: Success
{
  "tier": null,
  "tool_version": null,
  "tool_id": null,
  "request_id": null,
  "capabilities": null,
  "duration_ms": null,
  "error": null,
  "upgrade_hints": null,
  "warnings": [],
  "data": {
    "success": false,
    "target_name": "proces_order",
    "target_code": "",
    "context_code": "",
    "full_code": "",
    "total_lines": 0,
    "line_start": 0,
    "line_end": 0,
    "token_estimate": 0,
    "error": "Cannot access file: tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py (not found)\n\nAttempted locations (6):\n  [FAIL] tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py\n  [FAIL] /mnt/k/backup/Develop/code-scalpel/tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py\n  [FAIL] /mnt/k/backup/Develop/code-scalpel/tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py\n  [FAIL] /home/xbyooki/projects/tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py\n  [FAIL] /mnt/k/backup/Develop/code-scalpel/tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py\n  ... and 1 more\n\nSuggestion:\nEnsure the file exists and use an absolute path, or place it in:\n\n  - /mnt/k/backup/Develop/code-scalpel\n  - /home/xbyooki/projects\n\nCurrent workspace roots: /mnt/k/backup/Develop/code-scalpel, /home/xbyooki/projects\nSet WORKSPACE_ROOT environment variable to specify custom root.",
    "tier_applied": "community",
    "cross_file_deps_enabled": false,
    "jsx_normalized": false,
    "is_server_component": false,
    "is_server_action": false
  }
}
---


### ✅ 2. rename_symbol

**Test 2.1 - Rename Non-existent Function**
- Input: `target_name: "proces_data"`, `new_name: "process_input"`
- Expected: Suggest "process_data"
- Result: ⬜ PASS / X FAIL
- Error code: _______________{
  "tier": null,
  "tool_version": null,
  "tool_id": null,
  "request_id": null,
  "capabilities": null,
  "duration_ms": null,
  "error": null,
  "upgrade_hints": null,
  "warnings": [],
  "data": {
    "success": false,
    "file_path": "/mnt/k/backup/Develop/code-scalpel/tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "target_name": "proces_data",
    "target_type": "function",
    "lines_before": 0,
    "lines_after": 0,
    "lines_delta": 0,
    "backup_path": null,
    "batch_truncated": false,
    "error": "Function 'proces_data' not found"
  }
}
- Top suggestion: N/A
- Suggestion score: N/A
- Notes:
I even tried to put in the wrong filename to see what would happen (as it should suggest filenames/paths if they are wrong as well). However, no suggesteions were provided at all.

---

### ✅ 3. update_symbol

**Test 3.1 - Update Non-existent Function**
- Input: `target_name: "proces_item"`
- Expected: Suggest "process_item"
- Result: ⬜ PASS / ⬜ FAIL
- Error code: _______________
- Top suggestion: _______________
- Suggestion score: _______________
- Notes:

---

### ✅ 4. get_symbol_references

**Test 4.1 - Find Refs to Non-existent Symbol**
- Input: `symbol_name: "proces_data"`
- Expected: Suggest "process_data"
- Result: ⬜ PASS / ⬜ FAIL
- Error code: _______________
- Top suggestion: _______________
- Suggestion score: _______________
- Notes:

---

### ✅ 5. get_call_graph

**Test 5.1 - Entry Point Typo**
- Input: `entry_point: "proces_request"`
- Expected: Suggest similar functions
- Result: ⬜ PASS / ⬜ FAIL
- Error code: _______________
- Top suggestion: _______________
- Suggestion score: _______________
- Notes:

---

### ✅ 6. get_graph_neighborhood

**Test 6.1 - Node ID Typo**
- Input: `center_node_id: "python::test_code::function::proces_data"`
- Expected: Suggest "process_data"
- Result: ⬜ PASS / ⬜ FAIL
- Error code: _______________
- Top suggestion: _______________
- Suggestion score: _______________
- Notes:

---

### ✅ 7. get_cross_file_dependencies

**Test 7.1 - Symbol Typo in Cross-file**
- Input: `target_symbol: "proces_data"`
- Expected: Suggest "process_data"
- Result: ⬜ PASS / ⬜ FAIL
- Error code: _______________
- Top suggestion: _______________
- Suggestion score: _______________
- Notes:

---

## Response Structure Validation

Check that all error responses have:

- [ ] `error` object is not null
- [ ] `error.error_code` equals `"correction_needed"`
- [ ] `error.error_details` exists
- [ ] `error.error_details.suggestions` is an array
- [ ] Each suggestion has:
  - [ ] `symbol` or `path` field
  - [ ] `score` field (0.0-1.0)
  - [ ] `reason` field
- [ ] Suggestions ranked by score (descending)
- [ ] Error message includes "Did you mean?" hint
- [ ] `data` field is null when error occurs

---

## Issues Discovered

### Issue 1
**Tool**: _______________
**Description**:


**Severity**: ⬜ Critical / ⬜ Major / ⬜ Minor
**Workaround**:


### Issue 2
**Tool**: _______________
**Description**:


**Severity**: ⬜ Critical / ⬜ Major / ⬜ Minor
**Workaround**:


---

## Edge Cases Tested

### Good Catches (Oracle worked well)
1.
2.

### Missed Opportunities (Oracle didn't suggest)
1.
2.

### False Positives (Oracle suggested when it shouldn't)
1.
2.

---

## Performance Notes

| Tool | Avg Response Time | Notes |
|------|-------------------|-------|
| extract_code | ms | |
| rename_symbol | ms | |
| update_symbol | ms | |
| get_symbol_references | ms | |
| get_call_graph | ms | |
| get_graph_neighborhood | ms | |
| get_cross_file_dependencies | ms | |

---

## Recommendation

⬜ **APPROVED** - Ready for Phase 4 expansion to Group A tools
⬜ **NEEDS WORK** - Issues must be addressed before expanding
⬜ **BLOCKED** - Critical issues prevent expansion

**Justification**:


---

## Next Steps

1. [ ] Fix any critical issues found
2. [ ] Document edge cases in code
3. [ ] Proceed to Phase 4 (Group A tools with PathStrategy)
4. [ ] Update oracle middleware based on findings

---

## Additional Notes


