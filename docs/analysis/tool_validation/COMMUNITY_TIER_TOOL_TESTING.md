# Community Tier MCP Tool Testing (22 tools)

**Date**: December 30, 2025  
**Goal**: Confirm (MCP-first) that Community tier:
- Advertises all 22 canonical tools
- Allows Community features/limits
- Blocks Pro/Enterprise-only features and higher limits

## Test Setup (MCP-first)
- Run MCP server with **no paid license** present.
- Set `CODE_SCALPEL_TIER=community` (or omit; should default to Community).
- Recommended logging: `SCALPEL_MCP_INFO=DEBUG`

### Canonical Tool Registry (must be stable)
Expected `list_tools()` returns exactly these 22 tool names:
- `analyze_code`
- `code_policy_check`
- `crawl_project`
- `cross_file_security_scan`
- `extract_code`
- `generate_unit_tests`
- `get_call_graph`
- `get_cross_file_dependencies`
- `get_file_context`
- `get_graph_neighborhood`
- `get_project_map`
- `get_symbol_references`
- `rename_symbol`
- `scan_dependencies`
- `security_scan`
- `simulate_refactor`
- `symbolic_execute`
- `type_evaporation_scan`
- `unified_sink_detect`
- `update_symbol`
- `validate_paths`
- `verify_policy_integrity`

**Recorded Result**:
- Tool registry matches expected: ☑ PASS / ☐ FAIL  
- Notes: Confirmed via MCP-first probe: `list_tools()` returned 22 tools (including `rename_symbol`).

---

## Tool-by-Tool Community Expectations + Test Checklist

> For each tool below:
> - **Expected (Community)** is the authoritative expected behavior.
> - **Negative tests** explicitly check Pro/Enterprise features are blocked.
> - Fill in the **Recorded Result** section after running the MCP calls.

### 1) analyze_code
**Expected (Community)**
- Capabilities: `basic_ast`, `function_inventory`, `class_inventory`, `imports`, `complexity_metrics`
- Limits: `max_file_size_mb=1`

**MCP Test**
- Call `analyze_code` with a small Python snippet.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Returned `functions=["f"]`, `complexity=2` on a small snippet.

### 2) security_scan
**Expected (Community)**
- Capabilities: OWASP-focused detection (SQLi/XSS/command injection + AST patterns)
- Limits: `max_findings=50`, `max_file_size_kb=500`, `vulnerability_types=owasp_top_10`

**MCP Test**
- Call `security_scan` with a small snippet containing a known sink.

**Negative Test (no Pro features)**
- Confirm output is bounded (does not exceed `max_findings`).

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Detected SQL Injection (`CWE-89`) in a small f-string SQL snippet.

### 3) extract_code
**Expected (Community)**
- Capabilities: `single_file_extraction`, `basic_symbols`
- Limits: `include_cross_file_deps=False`, `max_depth=0`, `max_extraction_size_mb=1`

**MCP Test**
- Call `extract_code` with inline `code` containing the target symbol.

**Negative Tests (blocked)**
- Request any Pro/Enterprise advanced flags (e.g. variable promotion / closure detection / org-wide) → expect an error indicating tier requirement.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Extracted `divide()` from `stage1-qualifying-round/08-version-variance.py` successfully.

### 4) symbolic_execute
**Expected (Community)**
- Capabilities: `basic_symbolic_execution`, `simple_constraints`
- Limits: `max_paths=3`, `max_depth=5`, `constraint_types=[int,bool]`

**MCP Test**
- Call `symbolic_execute` on a small pure function.

**Negative Test (limits enforced)**
- Request `max_paths>3` → should be rejected or clamped.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Requested `max_paths=10`; tool returned `paths_explored=3` (Community limit/clamp behavior).

### 5) generate_unit_tests
**Expected (Community)**
- Capabilities: `basic_test_generation`
- Limits: `max_test_cases=5`, `test_frameworks=[pytest]`

**MCP Test**
- Call `generate_unit_tests` on a small function.

**Negative Test (no Pro frameworks)**
- Request `unittest` (if supported by API) → should be rejected or ignored.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Fixed JSON-serialization crash; returns valid result for trivial functions and is MCP-serializable.

### 6) crawl_project
**Expected (Community)**
- Capabilities: file tree indexing + basic stats + entrypoint detection, respects `.gitignore`
- Limits: `max_files=500`, `max_depth=10`

**MCP Test**
- Call `crawl_project` on a small project root.

**Negative Test (no Enterprise custom pattern extraction)**
- If the tool exposes pattern/custom extraction params: request them → should be rejected (Enterprise-only).

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: On `stage8-advanced-taint/crossfile-hard`, discovery crawl now detects `routes.py` as an entrypoint (supports Flask `@app.get`).

### 7) get_call_graph
**Expected (Community)**
- Capabilities: static call graph + mermaid generation
- Limits: `max_depth=3`, `max_nodes=50`

**MCP Test**
- Call `get_call_graph` on a small module.

**Negative Test (limits enforced)**
- Request deep depth (e.g. 10+) → should be rejected or clamped.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Requested `depth=6`; response reported `depth_limit=3` (Community clamp) and returned mermaid output.

### 8) get_graph_neighborhood
**Expected (Community)**
- Capabilities: `basic_neighborhood`
- Limits: `max_k=1`, `max_nodes=20`

**MCP Test**
- Call with a valid `center_node_id` and default k.

**Negative Test (limits enforced)**
- Request `k>1` → should be rejected or clamped.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Requested `k=2`; response clamped to `k=1` and returned `truncated=true`.

### 9) get_symbol_references
**Expected (Community)**
- Capabilities: AST-based references + definition location
- Limits: `max_files_searched=100`, `max_references=100`

**MCP Test**
- Call on a small project symbol.

**Negative Test (limits enforced)**
- Confirm bounded output and bounded scan.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: On `stage8-advanced-taint/crossfile-hard`, found definition + 2 references for `search_users`.

### 10) simulate_refactor
**Expected (Community)**
- Capabilities: `basic_simulation`, `structural_diff`
- Limits: `max_file_size_mb=1`, `analysis_depth=basic`

**MCP Test**
- Call with small `original_code` and `new_code`.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Flagged `eval()` introduction as unsafe (`is_safe=false`, CWE-94).

### 11) scan_dependencies
**Expected (Community)**
- Capabilities: `basic_dependency_scan`
- Limits: `max_dependencies=50`, `osv_lookup=True`

**MCP Test**
- Call on a small dependency list (or a small project manifest).

**Negative Test (limits enforced)**
- Provide >50 deps → should be rejected or truncated.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Scanned `frontend/package.json` with `scan_vulnerabilities=false`; returned 4 dependencies.

### 12) get_cross_file_dependencies
**Expected (Community)**
- Capabilities: direct import mapping + circular detection + import graph
- Limits: `max_depth=1`, `max_files=50`

**MCP Test**
- Call on a small project root.

**Negative Test (no deep/transitive mapping)**
- Request depth >1 → should be rejected or clamped.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: With `project_root` set to Ninja Warrior repo, resolved `routes.py:search_route` → `services.py:search_users` (include_code disabled).

### 13) cross_file_security_scan
**Expected (Community)**
- Capabilities: basic cross-file scan, single-module taint tracking
- Limits: `max_modules=10`, `max_depth=3`

**MCP Test**
- Call on a small project with a source→sink path.

**Negative Test (limits enforced)**
- Request `max_modules>10` or deep traversal → should be rejected or clamped.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: On `stage8-advanced-taint/crossfile-hard`, detected cross-file SQL injection flows (2 vulnerabilities).

### 14) verify_policy_integrity
**Expected (Community)**
- Capabilities: `basic_verification`
- Limits: `signature_validation=False`, `tamper_detection=False`

**MCP Test**
- Call in a workspace with `.code-scalpel` policies present.

**Negative Test (no crypto verification)**
- Confirm it does not require cryptographic secrets and reports only basic checks.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Malformed `.code-scalpel/budget.yaml` now fails gracefully (returns `success=false` with escaped error text), not an `internal_error`.

### 15) code_policy_check
**Expected (Community)**
- Capabilities: style guide checks + basic patterns
- Limits: `max_files=100`, `max_rules=50`

**MCP Test**
- Call on a small file set.

**Negative Test (no enterprise compliance audit)**
- Confirm it does not attempt HIPAA/SOC2/GDPR reports.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: `code_policy_check` completed successfully (6 files checked; no violations reported).

### 16) type_evaporation_scan
**Expected (Community)**
- Capabilities: explicit-any detection, basic TS scanning
- Limits: `max_files=50`, `frontend_only=True`

**MCP Test**
- Call with simple TS frontend + (optional) backend string.

**Negative Test (frontend_only)**
- Confirm cross-file endpoint correlation is not produced.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Community now respects `frontend_only=True` (no `matched_endpoints`, no backend correlation).

### 17) unified_sink_detect
**Expected (Community)**
- Capabilities: polyglot sink detection (python/js/ts/java)
- Limits: `languages=[python,javascript,typescript,java]`, `max_sinks=50`

**MCP Test**
- Call with a small snippet in one language.

**Negative Test (no extended languages)**
- Use `language=go` → should be rejected or reported unsupported.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Detected `subprocess.run(..., shell=True)` as a command injection sink.

### 18) update_symbol
**Expected (Community)**
- Capabilities: `basic_replacement`
- Limits: backups supported; **replacement must keep the same symbol name**

**MCP Test**
- Replace a function with the same name.

**Negative Tests (blocked)**
- Try to replace `def f(): ...` with `def g(): ...` while targeting `f` → expect failure.
- Try `operation=rename` → expect `Rename requires PRO tier.`

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Replacement with same symbol name succeeded and created `.bak`; rename is blocked (see probes).

### 19) get_file_context
**Expected (Community)**
- Capabilities: AST outlining + line range extraction
- Limits: `max_context_lines=500`

**MCP Test**
- Call with a small file.

**Negative Test (limits enforced)**
- Request huge ranges → should be bounded.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Correctly identified `01-unicode-minefield.js` as JavaScript and returned function inventory.

### 20) get_project_map
**Expected (Community)**
- Capabilities: basic tree + basic mermaid
- Limits: `max_files=100`, `max_modules=50`, `detail_level=basic`

**MCP Test**
- Call on a small project.

**Negative Test (blocked)**
- If `detect_service_boundaries` exists: request it → should be rejected (Enterprise-only).

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: On `stage8-advanced-taint/crossfile-hard`, mapped modules + entrypoints and generated mermaid.

### 21) validate_paths
**Expected (Community)**
- Capabilities: file existence + import path checking + broken reference detection
- Limits: `max_paths=100`

**MCP Test**
- Validate a small set of paths.

**Negative Test (blocked)**
- Confirm it does not do alias/dynamic import resolution.

**Recorded Result**: ☐ PASS / ☐ FAIL
**Recorded Result**: ☑ PASS / ☐ FAIL
- Notes: Validated a set of Ninja Warrior fixture paths successfully.

### 22) rename_symbol
**Expected (Community)**
- Renames the symbol **definition only** in the target file.
- Creates a backup when `create_backup=True`.
- Does **not** update references/imports in other files.

**MCP Test**
- Call `rename_symbol` on a sample symbol.

**Negative Test (no cross-file)**
- Create a second file that references the symbol and confirm it is unchanged.

**Recorded Result**: ☐ PASS / ☐ FAIL

---

## MCP-First Community Gating Probes (recommended quick proof)
Record the results of these probes to confirm you are not getting paid-tier behavior accidentally.

1) `extract_code(variable_promotion=True)` returns tier error  ☑ PASS / ☐ FAIL
2) `get_graph_neighborhood(k=2)` is rejected/clamped to k=1  ☑ PASS / ☐ FAIL

Notes:
