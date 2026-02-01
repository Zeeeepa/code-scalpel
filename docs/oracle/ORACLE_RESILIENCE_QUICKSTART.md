# Oracle Resilience - Quick Start Guide

## ✅ What's Done

**7 Pilot Tools with Oracle Resilience**:
1. ✅ extract_code
2. ✅ rename_symbol
3. ✅ update_symbol
4. ✅ get_symbol_references
5. ✅ get_call_graph
6. ✅ get_graph_neighborhood
7. ✅ get_cross_file_dependencies

**Test Status**: 18/18 ✅ (100% passing)

---

## 🧪 Test with MCP Inspector

### Start MCP Inspector
```bash
npx @modelcontextprotocol/inspector python3 -m code_scalpel.mcp.server
```

### Run a Quick Test
Paste this into Inspector:

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

### Expected Response
```json
{
  "error": {
    "error": "Symbol 'process_dta' not found. Did you mean: process_data?",
    "error_code": "correction_needed",
    "error_details": {
      "suggestions": [
        {"symbol": "process_data", "score": 0.95, "reason": "fuzzy_match"},
        {"symbol": "process_item", "score": 0.85, "reason": "fuzzy_match"}
      ]
    }
  }
}
```

---

## 📋 Quick Test File

Create `/tmp/test_code.py`:
```python
def process_data(x):
    return x * 2

def process_item(y):
    return y + 1

def calculate_sum(a, b):
    return a + b

def main():
    return process_data(5)
```

---

## 📚 Full Documentation

- **Implementation Details**: `docs/ORACLE_RESILIENCE_IMPLEMENTATION.md`
- **All Test Cases**: `docs/ORACLE_RESILIENCE_TEST_CASES.md`
- **Source Code**: `src/code_scalpel/mcp/oracle_middleware.py`

---

## 🎯 Key Features

✅ **Intelligent Suggestions** - Typo recovery using fuzzy matching
✅ **Backward Compatible** - error_code overload, no breaking changes
✅ **LLM Friendly** - Structured suggestions in error_details
✅ **Zero Overhead** - Only active when errors occur
✅ **Production Ready** - 18/18 tests passing

---

## 🚀 Next Steps

**Phase 4: Expand to 15 More Tools**
- Group A (6 tools): Context & Navigation
- Group D (6 tools): Security & Analysis
- Group E (2 tools): Simulation & Testing

**Estimated Effort**: 8-12 hours

---

## 💡 How It Works

**Before Oracle**:
```
Tool Error → "Symbol not found" → LLM guesses
```

**With Oracle**:
```
Tool Error → "Did you mean: X, Y, Z?" → LLM corrects
```

---

## 🔍 Validation Checklist

Run through these when testing:

- [ ] extract_code with typo → correction_needed ✅
- [ ] rename_symbol with typo → correction_needed ✅
- [ ] update_symbol with typo → correction_needed ✅
- [ ] get_symbol_references with typo → correction_needed ✅
- [ ] get_call_graph with typo → correction_needed ✅
- [ ] get_graph_neighborhood with typo → correction_needed ✅
- [ ] get_cross_file_dependencies with typo → correction_needed ✅

---

## 📊 Implementation Stats

| Metric | Value |
|--------|-------|
| New Files | 3 |
| Modified Files | 5 |
| Lines of Code | ~1,700 |
| Tests | 18/18 ✅ |
| Pilot Tools | 7 |
| Error Codes | 1 new |
| Strategies | 3 |

---

## 🎓 Learning Resources

### For Understanding the Design:
1. Read: `src/code_scalpel/mcp/oracle_middleware.py` (well-commented)
2. Look at: How `@with_oracle_resilience` decorator works
3. Study: Recovery strategies (SymbolStrategy, PathStrategy, SafetyStrategy)

### For Using It:
1. See: `docs/ORACLE_RESILIENCE_TEST_CASES.md` for examples
2. Run: Tests with MCP Inspector
3. Check: Response format in examples

### For Extending It:
1. Create new Recovery Strategy class
2. Implement `suggest(error, context) -> list[dict]`
3. Apply decorator with `strategy=CustomStrategy`

---

**Status**: Production Ready ✅
**Ready for Phase 4**: Yes ✅
**Last Updated**: January 30, 2026
