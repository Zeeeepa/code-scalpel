# Oracle Resilience Pilot Tests - Automated Results

**Date**: 2026-01-30T20:22:39.073426
**Total Tests**: 7
**Passed**: 2
**Failed**: 5
**Pass Rate**: 28.6%

---

## Summary Table

| Test | Tool | Status | Error Code | Suggestions | Top Suggestion |
|------|------|--------|-----------|-------------|-----------------|
| Test 1.1: extract_code - Symbol Typo | extract_code | ✅ PASS | correction_needed | 2 | process_data (0.95) |
| Test 2.1: rename_symbol - Missing Symbol | rename_symbol | ✅ PASS | correction_needed | 2 | process_data (0.95) |
| Test 3.1: update_symbol - Missing Symbol | update_symbol | ❌ FAIL | N/A | 0 | N/A |
| Test 4.1: get_symbol_references - Missing Symbol | get_symbol_references | ❌ FAIL | N/A | 0 | N/A |
| Test 5.1: get_call_graph - Entry Point Typo | get_call_graph | ❌ FAIL | N/A | 0 | N/A |
| Test 6.1: get_graph_neighborhood - Node Typo | get_graph_neighborhood | ❌ FAIL | N/A | 0 | N/A |
| Test 7.1: get_cross_file_dependencies - Symbol Typo | get_cross_file_dependencies | ❌ FAIL | N/A | 0 | N/A |

---

## Detailed Results

### Test 1.1: extract_code - Symbol Typo

**Status**: ✅ PASS
**Tool**: extract_code
**Error Code**: correction_needed
**Suggestions Count**: 2
**Top Suggestion**: process_data
**Score**: 0.95

**Raw Response**:
```json
{
  "tier": null,
  "tool_version": null,
  "tool_id": null,
  "request_id": null,
  "capabilities": null,
  "duration_ms": null,
  "error": {
    "error": "Function 'proces_data' not found. Available: ['process_data', 'process_item', 'calculate_sum', 'calculate_product', 'main'] Did you mean: process_data, process_item?",
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
          "score": 0.8999999999999999,
          "reason": "fuzzy_match"
        }
      ],
      "hint": "Function 'proces_data' not found. Available: ['process_data', 'process_item', 'calculate_sum', 'calculate_product', 'main'] Did you mean: process_data, process_item?"
    }
  },
  "upgrade_hints": null,
  "warnings": [],
  "data": {
    "success": false,
    "target_name": "proces_data",
    "target_code": "",
    "context_code": "",
    "full_code": "",
    "total_lines": 0,
    "line_start": 0,
    "line_end": 0,
    "token_estimate": 0,
    "error": "Function 'proces_data' not found. Available: ['process_data', 'process_item', 'calculate_sum', 'calculate_product', 'main']",
    "tier_applied": "community",
    "cross_file_deps_enabled": false,
    "jsx_normalized": false,
    "is_server_component": false,
    "is_server_action": false
  }
}
```

### Test 2.1: rename_symbol - Missing Symbol

**Status**: ✅ PASS
**Tool**: rename_symbol
**Error Code**: correction_needed
**Suggestions Count**: 2
**Top Suggestion**: process_data
**Score**: 0.95

**Raw Response**:
```json
{
  "tier": null,
  "tool_version": null,
  "tool_id": null,
  "request_id": null,
  "capabilities": null,
  "duration_ms": null,
  "error": {
    "error": "Function 'proces_data' not found Did you mean: process_data, process_item?",
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
          "score": 0.8999999999999999,
          "reason": "fuzzy_match"
        }
      ],
      "hint": "Function 'proces_data' not found Did you mean: process_data, process_item?"
    }
  },
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
```

### Test 3.1: update_symbol - Missing Symbol

**Status**: ❌ FAIL
**Tool**: update_symbol
**Error Code**: N/A
**Suggestions Count**: 0
**Issues**:
- 'error' field is null (should be error object)

**Raw Response**:
```json
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
    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "target_name": "proces_item",
    "target_type": "function",
    "lines_before": 0,
    "lines_after": 0,
    "lines_delta": 0,
    "backup_path": null,
    "error_code": "UPDATE_SYMBOL_SEMANTIC_VALIDATION_FAILED",
    "batch_truncated": false,
    "error": "Replacement function name 'process_item' does not match target 'proces_item'."
  }
}
```

### Test 4.1: get_symbol_references - Missing Symbol

**Status**: ❌ FAIL
**Tool**: get_symbol_references
**Error Code**: N/A
**Suggestions Count**: 0
**Issues**:
- 'error' field is null (should be error object)

**Raw Response**:
```json
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
    "success": true,
    "tier_applied": "community",
    "max_files_applied": 10,
    "max_references_applied": 50,
    "symbol_name": "proces_data",
    "total_references": 0,
    "files_scanned": 10,
    "total_files": 156,
    "files_truncated": true,
    "file_truncation_warning": "File scan truncated: scanned 10 of 156 files.",
    "references_truncated": false
  }
}
```

### Test 5.1: get_call_graph - Entry Point Typo

**Status**: ❌ FAIL
**Tool**: get_call_graph
**Error Code**: N/A
**Suggestions Count**: 0
**Issues**:
- 'error' field is null (should be error object)

**Raw Response**:
```json
{
  "tier": "community",
  "tool_version": "1.2.1",
  "tool_id": "get_call_graph",
  "request_id": "dd658a9a7a134fe5af1a32ff0140055f",
  "capabilities": [
    "envelope-v1"
  ],
  "duration_ms": 8313,
  "error": null,
  "upgrade_hints": [],
  "warnings": [],
  "data": {
    "success": true,
    "server_version": "1.2.1",
    "nodes": [
      {
        "name": "proces_data",
        "file": "<external>",
        "line": 0,
        "end_line": null,
        "is_entry_point": false,
        "source_uri": null,
        "in_degree": null,
        "out_degree": null
      }
    ],
    "edges": [],
    "entry_point": "proces_data",
    "depth_limit": 2,
    "mermaid": "graph TD\n    N0(proces_data)",
    "circular_imports": [],
    "paths": [],
    "focus_functions": null,
    "total_nodes": 1,
    "total_edges": 0,
    "nodes_truncated": false,
    "edges_truncated": false,
    "truncation_warning": null,
    "hot_nodes": [],
    "dead_code_candidates": [],
    "tier_applied": "community",
    "max_depth_applied": 3,
    "max_nodes_applied": 50,
    "advanced_resolution_enabled": false,
    "enterprise_metrics_enabled": false,
    "error": null
  }
}
```

### Test 6.1: get_graph_neighborhood - Node Typo

**Status**: ❌ FAIL
**Tool**: get_graph_neighborhood
**Error Code**: N/A
**Suggestions Count**: 0
**Issues**:
- argument of type 'NoneType' is not iterable

**Raw Response**:
```json
{
  "tier": "community",
  "tool_version": "1.2.1",
  "tool_id": "get_graph_neighborhood",
  "request_id": "38a1f00704f641779095196baa936ea4",
  "capabilities": [
    "envelope-v1"
  ],
  "duration_ms": 32,
  "error": {
    "error": "Center node function 'proces_data' not found in tests/mcp_tool_verification/mcp_inspector/test_code.py",
    "error_code": "internal_error",
    "error_details": null
  },
  "upgrade_hints": [],
  "warnings": [],
  "data": {
    "success": false,
    "server_version": "1.2.1",
    "center_node_id": "",
    "k": 0,
    "nodes": [],
    "edges": [],
    "total_nodes": 0,
    "total_edges": 0,
    "max_depth_reached": 0,
    "truncated": false,
    "truncation_warning": null,
    "mermaid": "",
    "semantic_neighbors": [],
    "logical_relationships": [],
    "query_supported": false,
    "traversal_rules_available": false,
    "path_constraints_supported": false,
    "hot_nodes": [],
    "error": "Center node function 'proces_data' not found in tests/mcp_tool_verification/mcp_inspector/test_code.py"
  }
}
```

### Test 7.1: get_cross_file_dependencies - Symbol Typo

**Status**: ❌ FAIL
**Tool**: get_cross_file_dependencies
**Error Code**: N/A
**Suggestions Count**: 0
**Issues**:
- argument of type 'NoneType' is not iterable

**Raw Response**:
```json
{
  "tier": "community",
  "tool_version": "1.2.1",
  "tool_id": "get_cross_file_dependencies",
  "request_id": "05f6b9762e91480d88f9b42aefb051dd",
  "capabilities": [
    "envelope-v1"
  ],
  "duration_ms": 6963,
  "error": {
    "error": "Extraction failed: File not found: tests/mcp_tool_verification/mcp_inspector/test_code.py.",
    "error_code": "not_found",
    "error_details": null
  },
  "upgrade_hints": [],
  "warnings": [],
  "data": {
    "success": false,
    "server_version": "1.2.1",
    "target_name": "",
    "target_file": "",
    "extracted_symbols": [],
    "total_dependencies": 0,
    "unresolved_imports": [],
    "import_graph": {},
    "circular_imports": [],
    "combined_code": "",
    "token_estimate": 0,
    "transitive_depth": 0,
    "alias_resolutions": [],
    "wildcard_expansions": [],
    "reexport_chains": [],
    "chained_alias_resolutions": [],
    "coupling_score": null,
    "coupling_violations": [],
    "dependency_chains": [],
    "boundary_violations": [],
    "layer_violations": [],
    "architectural_alerts": [],
    "architectural_violations": [],
    "boundary_alerts": [],
    "layer_mapping": {},
    "rules_applied": [],
    "architectural_rules_applied": [],
    "exempted_files": [],
    "files_scanned": 0,
    "files_truncated": 0,
    "truncation_warning": null,
    "truncated": false,
    "files_analyzed": 0,
    "max_depth_reached": 0,
    "mermaid": "",
    "confidence_decay_factor": 0.9,
    "low_confidence_count": 0,
    "low_confidence_warning": null,
    "error": "Extraction failed: File not found: tests/mcp_tool_verification/mcp_inspector/test_code.py."
  }
}
```
