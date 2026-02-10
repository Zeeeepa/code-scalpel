# Oracle Resilience MCP Inspector Test Cases

This document contains test cases to validate oracle resilience functionality across all pilot tools. Run these tests using the MCP Inspector.

**Command**: `npx @modelcontextprotocol/inspector python3 -m code_scalpel.mcp.server`

---

## Test Setup

Before running tests, create a test file with sample code:

**File**: `/tmp/test_code.py`
```python
def process_data(x):
    """Process numeric data."""
    return x * 2

def process_item(y):
    """Process item data."""
    return y + 1

def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def calculate_product(x, y):
    """Calculate product of two numbers."""
    return x * y

class DataProcessor:
    """Process various data types."""

    def __init__(self, name):
        self.name = name

    def execute(self, data):
        """Execute processing."""
        return process_data(data)

def main():
    """Main entry point."""
    result = process_data(5)
    return result
```

---

## Tool 1: extract_code - ✅ Symbol Typo Test

**Scenario**: Extract code with a symbol name typo. Oracle should suggest similar functions.

**Test Case 1.1 - Typo: process_dta (should suggest process_data)**

```json
{
  "tool": "extract_code",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "process_dta"
  }
}
```

**Expected Result**:
- ❌ Error should occur (symbol not found)
- 🔧 `error_code` should be: `"correction_needed"`
- 💡 `error_details.suggestions` should contain:
  - `{ "symbol": "process_data", "score": >0.9 }`
  - `{ "symbol": "process_item", "score": >0.8 }`
  - `{ "symbol": "calculate_sum", "score": >0.6 }`

**Test Case 1.2 - Typo: proccess_data (extra c)**

```json
{
  "tool": "extract_code",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "proccess_data"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Top suggestion should be `process_data` with score > 0.85

**Test Case 1.3 - Class extraction with typo: DataProccesor**

```json
{
  "tool": "extract_code",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "class",
    "target_name": "DataProccesor"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `DataProcessor` with high score

---

## Tool 2: rename_symbol - ✅ Symbol Typo Test

**Scenario**: Try to rename a symbol that doesn't exist (typo). Oracle should suggest the correct name.

**Test Case 2.1 - Rename non-existent: procces_data → processed_data**

```json
{
  "tool": "rename_symbol",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "procces_data",
    "new_name": "processed_data",
    "create_backup": true
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 `error_details.suggestions` should suggest `process_data`

**Test Case 2.2 - Another typo: calculte_sum → calculate_sum_total**

```json
{
  "tool": "rename_symbol",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "calculte_sum",
    "new_name": "calculate_sum_total",
    "create_backup": true
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `calculate_sum` with high score

---

## Tool 3: update_symbol - ✅ Symbol Typo Test

**Scenario**: Try to update a symbol that doesn't exist (typo). Oracle should suggest similar symbol.

**Test Case 3.1 - Update non-existent: proces_item**

```json
{
  "tool": "update_symbol",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "proces_item",
    "new_code": "def process_item(y):\n    \"\"\"Updated version.\"\"\"\n    return y + 2",
    "operation": "replace",
    "create_backup": true
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `process_item` with high score

**Test Case 3.2 - Update main function with typo: main_func**

```json
{
  "tool": "update_symbol",
  "arguments": {
    "file_path": "/tmp/test_code.py",
    "target_type": "function",
    "target_name": "main_func",
    "new_code": "def main():\n    return 'updated'",
    "operation": "replace"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `main` with high score

---

## Tool 4: get_symbol_references - ✅ Symbol Typo Test

**Scenario**: Find references to a symbol that doesn't exist (typo). Oracle should suggest similar symbols.

**Test Case 4.1 - Find refs to: proces_data**

```json
{
  "tool": "get_symbol_references",
  "arguments": {
    "symbol_name": "proces_data",
    "project_root": "/tmp"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `process_data`, `process_item`, etc.

**Test Case 4.2 - Find refs to: DataProce (incomplete name)**

```json
{
  "tool": "get_symbol_references",
  "arguments": {
    "symbol_name": "DataProce",
    "project_root": "/tmp"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `DataProcessor` with score > 0.8

---

## Tool 5: get_call_graph - ✅ Entry Point Typo Test

**Scenario**: Build call graph with a non-existent entry point (typo). Oracle should suggest similar functions.

**Test Case 5.1 - Entry point with typo: main_func**

```json
{
  "tool": "get_call_graph",
  "arguments": {
    "project_root": "/tmp",
    "entry_point": "main_func",
    "depth": 3
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `main` with high score

**Test Case 5.2 - Entry point typo: proccess_data**

```json
{
  "tool": "get_call_graph",
  "arguments": {
    "project_root": "/tmp",
    "entry_point": "proccess_data",
    "depth": 2
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `process_data`, `process_item`, etc.

---

## Tool 6: get_graph_neighborhood - ✅ Node ID Typo Test

**Scenario**: Query neighborhood around a node with typo in ID. Oracle should suggest similar symbols.

**Test Case 6.1 - Node ID with typo: proccess_data**

```json
{
  "tool": "get_graph_neighborhood",
  "arguments": {
    "center_node_id": "python::test_code::function::proccess_data",
    "k": 2,
    "direction": "both"
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `process_data`

---

## Tool 7: get_cross_file_dependencies - ✅ Symbol Typo Test

**Scenario**: Get dependencies for a symbol with typo. Oracle should suggest similar symbols.

**Test Case 7.1 - Symbol typo: proces_data**

```json
{
  "tool": "get_cross_file_dependencies",
  "arguments": {
    "target_file": "test_code.py",
    "target_symbol": "proces_data",
    "project_root": "/tmp",
    "max_depth": 2
  }
}
```

**Expected Result**:
- 🔧 `error_code`: `"correction_needed"`
- 💡 Should suggest `process_data` with high score

---

## Validation Checklist

For each test, verify:

- ✅ `error_code` is exactly `"correction_needed"`
- ✅ `error_details` contains `"suggestions"` array
- ✅ Each suggestion has `"symbol"` or `"path"`, `"score"`, and `"reason"`
- ✅ Suggestions are ranked by score (highest first)
- ✅ Scores are between 0.0 and 1.0
- ✅ Error message includes "Did you mean: X?" hint
- ✅ `data` is `null` when error occurs
- ✅ Response structure matches ToolResponseEnvelope

---

## Success Metrics

🎯 **All tests should:**
- Return `error_code: "correction_needed"`
- Provide relevant suggestions with scores > 0.6
- Include helpful "Did you mean?" messages
- Maintain backward compatibility (clients see it as an error)

---

## Notes for MCP Inspector Testing

1. **Paste test cases one at a time** into the MCP Inspector
2. **Look for the error response** with `"correction_needed"` code
3. **Check error_details** for suggestions array
4. **Verify suggestion ranking** (highest scores first)
5. **Test with both typos and partial names** to see fuzzy matching quality

---

## Example Success Response

When `extract_code` is called with `target_name: "process_dta"`:

```json
{
  "error": {
    "error": "Symbol 'process_dta' not found. Did you mean: process_data?",
    "error_code": "correction_needed",
    "error_details": {
      "suggestions": [
        {
          "symbol": "process_data",
          "score": 0.95,
          "reason": "fuzzy_match"
        },
        {
          "symbol": "process_item",
          "score": 0.82,
          "reason": "fuzzy_match"
        },
        {
          "symbol": "calculate_sum",
          "score": 0.61,
          "reason": "fuzzy_match"
        }
      ],
      "hint": "Symbol 'process_dta' not found. Did you mean: process_data?"
    }
  },
  "data": null
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No suggestions returned | Check if file path is correct and file exists |
| All suggestions have low scores | Try a different typo (closer to real symbols) |
| Error code is "internal_error" | Check file permissions and Python syntax |
| Decorator not applied | Verify imports are correct in tool file |

---

## Next Steps After Validation

✅ All pilot tools working with oracle resilience
→ Phase 4: Expand to remaining 15 tools (crawl_project, analyze_code, etc.)
→ Phase 5: Create user documentation and update docstrings
→ Phase 6: Add oracle metrics/telemetry for acceptance tracking
