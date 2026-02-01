# Comprehensive Oracle Resilience Test Report

**Total Tests**: 8
**Passed**: 3
**Failed**: 5
**Pass Rate**: 37.5%

---

## By Strategy

### PathStrategy
**0/3 passed**

**Missing File - Extract Code** - ❌ FAIL
- Tool: extract_code
- Error Code: None
- Suggestions: 0
- Issues:
  - 'error' field is null

**Missing File - Get Context** - ❌ FAIL
- Tool: get_file_context
- Error Code: None
- Suggestions: 0
- Issues:
  - 'error' field is null

**Wrong Directory Path - Crawl** - ❌ FAIL
- Tool: crawl_project
- Error Code: None
- Suggestions: 0
- Issues:
  - 'error' field is null

### SafetyStrategy
**1/1 passed**

**Rename to Existing Name** - ✅ PASS
- Tool: rename_symbol
- Error Code: correction_needed
- Suggestions: 2
- Top: process_item

### SymbolStrategy
**2/4 passed**

**Function Typo - Extract** - ✅ PASS
- Tool: extract_code
- Error Code: correction_needed
- Suggestions: 2
- Top: process_item

**Function Typo - Rename** - ✅ PASS
- Tool: rename_symbol
- Error Code: correction_needed
- Suggestions: 2
- Top: process_item

**Function Typo - Get References** - ❌ FAIL
- Tool: get_symbol_references
- Error Code: None
- Suggestions: 0
- Issues:
  - 'error' field is null

**Entry Point Typo - Call Graph** - ❌ FAIL
- Tool: get_call_graph
- Error Code: None
- Suggestions: 0
- Issues:
  - 'error' field is null
