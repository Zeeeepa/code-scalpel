# Oracle Resilience Pilot Testing Plan

**Status**: Ready for MCP Inspector Testing
**Tools Ready**: 7 pilot tools (Group B + C)
**Date**: January 30, 2026

---

## Test Environment Setup

### 1. Start MCP Server with Inspector
```bash
cd /mnt/k/backup/Develop/code-scalpel
npx @modelcontextprotocol/inspector python3 -m code_scalpel.mcp.server
```

### 2. Test Data Location
Use the ninja warrior repo test files:
```
tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/
```

Or use the simple test file:
```
tests/mcp_tool_verification/mcp_inspector/test_code.py
```

---

## ✅ Pilot Tools to Test (7 Total)

### Group B: Symbol Extraction & Graph (5 tools)
1. ✅ extract_code - Symbol extraction with typo recovery
2. ✅ get_symbol_references - Find symbol references with suggestions
3. ✅ get_call_graph - Build call graphs with entry point recovery
4. ✅ get_graph_neighborhood - Graph neighborhood with node suggestions
5. ✅ get_cross_file_dependencies - Cross-file analysis with recovery

### Group C: Surgery/Modification (2 tools)
6. ✅ rename_symbol - Rename with typo recovery
7. ✅ update_symbol - Update with typo recovery

---

## Test Cases for Each Tool

### Test 1: extract_code - Symbol Typo Recovery

**Test File**: `tests/mcp_tool_verification/mcp_inspector/test_code.py`

**Test Case 1.1 - Basic Typo**
```json
{
  "tool": "extract_code",
  "arguments": {
    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "target_type": "function",
    "target_name": "proces_data"
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 suggestions include "process_data"

**Test Case 1.2 - Using Ninja Warrior**
```json
{
  "tool": "extract_code",
  "arguments": {
    "file_path": "tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-surgical-ops/challenges/02_legacy_nightmare/legacy_chaos.py",
    "target_type": "function",
    "target_name": "proces_order"
  }
}
```

**Expected**:
- 💡 Should suggest "process_order" or similar functions

---

### Test 2: rename_symbol - Typo in Source Symbol

**Test Case 2.1 - Rename non-existent function**
```json
{
  "tool": "rename_symbol",
  "arguments": {
    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "target_type": "function",
    "target_name": "proces_data",
    "new_name": "process_input",
    "create_backup": true
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest "process_data"

---

### Test 3: update_symbol - Typo in Target

**Test Case 3.1 - Update non-existent function**
```json
{
  "tool": "update_symbol",
  "arguments": {
    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "target_type": "function",
    "target_name": "proces_item",
    "new_code": "def process_item(y):\\n    return y + 2",
    "operation": "replace",
    "create_backup": true
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest "process_item"

---

### Test 4: get_symbol_references - Missing Symbol

**Test Case 4.1 - Find refs to non-existent symbol**
```json
{
  "tool": "get_symbol_references",
  "arguments": {
    "symbol_name": "proces_data",
    "project_root": "tests/mcp_tool_verification/mcp_inspector"
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest "process_data" or similar

---

### Test 5: get_call_graph - Wrong Entry Point

**Test Case 5.1 - Entry point typo**
```json
{
  "tool": "get_call_graph",
  "arguments": {
    "project_root": "tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-structural/stage1-qualifying-round",
    "entry_point": "proces_request",
    "depth": 3
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest similar function names in the project

---

### Test 6: get_graph_neighborhood - Node ID Typo

**Test Case 6.1 - Wrong node identifier**
```json
{
  "tool": "get_graph_neighborhood",
  "arguments": {
    "center_node_id": "python::test_code::function::proces_data",
    "k": 2,
    "direction": "both",
    "project_root": "tests/mcp_tool_verification/mcp_inspector"
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest "process_data"

---

### Test 7: get_cross_file_dependencies - Symbol Typo

**Test Case 7.1 - Wrong symbol in cross-file analysis**
```json
{
  "tool": "get_cross_file_dependencies",
  "arguments": {
    "target_file": "test_code.py",
    "target_symbol": "proces_data",
    "project_root": "tests/mcp_tool_verification/mcp_inspector",
    "max_depth": 2
  }
}
```

**Expected**:
- ❌ error_code: "correction_needed"
- 💡 Suggest "process_data"

---

## Validation Checklist

For each test, verify:

- [ ] Response has `error` object (not null)
- [ ] `error.error_code` equals `"correction_needed"`
- [ ] `error.error_details` exists
- [ ] `error.error_details.suggestions` is an array
- [ ] Each suggestion has: `symbol` or `path`, `score`, `reason`
- [ ] Suggestions are ranked by score (highest first)
- [ ] Error message includes "Did you mean: X?" hint
- [ ] Scores are between 0.0 and 1.0
- [ ] Top suggestion score > 0.6

---

## Success Criteria

✅ **All 7 tools return "correction_needed" for typos**
✅ **Top suggestion is correct in >80% of cases**
✅ **Suggestions include confidence scores**
✅ **"Did you mean?" hints are helpful**
✅ **No false positives on correct inputs**

---

## Testing Workflow

### Step 1: Quick Smoke Test (15 min)
Run one test case per tool to verify basic oracle functionality

### Step 2: Comprehensive Test (30 min)
Run all test cases with various typos and edge cases

### Step 3: Ninja Warrior Integration (45 min)
Test with real ninja warrior files:
- Stage 1: Parsing challenges
- Stage 4: Confidence crisis (adversarial naming)
- Challenge 02: Legacy nightmare (complex extraction)

### Step 4: Document Results
Record findings in `ORACLE_PILOT_TEST_RESULTS.md`

---

## Test Results Template

```markdown
# Oracle Resilience Pilot Test Results

**Date**:
**Tester**:
**MCP Server Version**:

## Test Summary

| Tool | Tests Run | Passed | Failed | Notes |
|------|-----------|--------|--------|-------|
| extract_code | 2 | | | |
| rename_symbol | 1 | | | |
| update_symbol | 1 | | | |
| get_symbol_references | 1 | | | |
| get_call_graph | 1 | | | |
| get_graph_neighborhood | 1 | | | |
| get_cross_file_dependencies | 1 | | | |

## Detailed Results

### extract_code

**Test 1.1**:
- Input: `target_name: "proces_data"`
- Expected: Suggest "process_data"
- Result: ✅/❌
- Suggestion Score:
- Notes:

### rename_symbol

[Fill in results...]

## Issues Found

1.
2.

## Recommendations

1.
2.
```

---

## Next Steps After Testing

1. ✅ Validate all 7 pilot tools work correctly
2. 📝 Document any issues or edge cases found
3. 🔧 Fix any bugs discovered
4. 🚀 Proceed to Phase 4: Expand to Group A tools (PathStrategy)

---

## Quick Reference

**Start Testing**:
```bash
npx @modelcontextprotocol/inspector python3 -m code_scalpel.mcp.server
```

**Test File**:
```
tests/mcp_tool_verification/mcp_inspector/test_code.py
```

**Documentation**:
- Full implementation: `docs/ORACLE_RESILIENCE_IMPLEMENTATION.md`
- All test cases: `docs/ORACLE_RESILIENCE_TEST_CASES.md`
- Quick start: `ORACLE_RESILIENCE_QUICKSTART.md`
