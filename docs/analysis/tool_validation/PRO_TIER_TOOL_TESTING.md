# Pro Tier MCP Tool Testing (22 tools)

**Date**: December 30, 2025  
**Goal**: Confirm (MCP-first) that Pro tier:
- Advertises all 22 canonical tools
- Enables Pro features/limits
- Blocks Enterprise-only features where applicable

## Test Setup (MCP-first)
- Install a **valid Pro (or higher) license** and point `CODE_SCALPEL_LICENSE_PATH` at it.
- Set `CODE_SCALPEL_TIER=pro`.
- Recommended logging: `SCALPEL_MCP_INFO=DEBUG`

> If you see `Invalid license signature - token may be tampered`, you are NOT running Pro.
> In that case, the server will clamp to Community behavior and this document cannot be validated.

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
- Tool registry matches expected: [x] PASS / [ ] FAIL
- Effective tier is Pro (not Community): [x] PASS / [ ] FAIL

**Automated Run (recorded)**
- Command: `CODE_SCALPEL_TIER=pro CODE_SCALPEL_LICENSE_PATH=/mnt/k/backup/Develop/.code-scalpel/license/license.jwt python scripts/mcp_validate_pro_tier.py --verbose`
- Outcome: PASS (25/25 checks)

---

## Tool-by-Tool Pro Expectations + Test Checklist

> For each tool below:
> - **Expected (Pro)** is the authoritative expected behavior.
> - **Negative tests** explicitly check Enterprise-only features are blocked.
> - Fill in the **Recorded Result** section after running the MCP calls.

### 1) analyze_code
**Expected (Pro)**
- Capabilities (adds vs Community): `code_smells`, `halstead_metrics`, `cognitive_complexity`, `duplicate_code_detection`, `dependency_graph`
- Limits: `max_file_size_mb=10`

**MCP Tests**
- Call `analyze_code` on a medium snippet and confirm output includes Pro fields where available.

**Recorded Result**: [x] PASS / [ ] FAIL

### 2) security_scan
**Expected (Pro)**
- Capabilities (adds vs Community): `context_aware_scanning`, `sanitizer_recognition`, `data_flow_sensitive_analysis`, `false_positive_reduction`, `remediation_suggestions`, `full_vulnerability_list`
- Limits: no `max_findings` cap; `vulnerability_types=all`

**MCP Tests**
- Provide code with a sink plus a sanitizer; confirm sanitizer recognition / remediation hints appear when applicable.

**Recorded Result**: [x] PASS / [ ] FAIL

### 3) extract_code
**Expected (Pro)**
- Capabilities (adds vs Community): `cross_file_deps`, `context_extraction`, `variable_promotion`, `closure_detection`, `dependency_injection_suggestions`
- Limits: `include_cross_file_deps=True`, `max_depth=1`, `max_extraction_size_mb=10`

**MCP Tests**
- Call `extract_code` with `include_cross_file_deps=True` and confirm direct imports are resolved.

**Negative Test (Enterprise-only)**
- Request Enterprise-only behaviors (e.g., org-wide resolution / Dockerfile generation flags if present) → expect tier/feature error.

**Recorded Result**: [x] PASS / [ ] FAIL

### 4) symbolic_execute
**Expected (Pro)**
- Limits: `max_paths=10`, `max_depth=10`, supports `string` + `float` constraint types

**MCP Tests**
- Request `max_paths=10` and confirm more than 3 paths are explored (where code permits).

**Recorded Result**: [x] PASS / [ ] FAIL

### 5) generate_unit_tests
**Expected (Pro)**
- Capabilities (adds vs Community): `data_driven_tests`, `bug_reproduction` (if supported by tool output)
- Limits: higher `max_test_cases` than Community (per runtime caps)

**MCP Tests**
- Call `generate_unit_tests` with a branching function; confirm output is MCP-serializable and includes richer test variants.

**Recorded Result**: [x] PASS / [ ] FAIL

### 6) crawl_project
**Expected (Pro)**
- Discovery + parsing enabled: `parsing_enabled=true`, `complexity_analysis=true`
- Limits: `max_files=1000`

**MCP Tests**
- Call `crawl_project` and confirm functions/classes inventories are populated (not discovery-only).

**Recorded Result**: [x] PASS / [ ] FAIL

### 7) get_call_graph
**Expected (Pro)**
- Limits: `max_depth=50`, `max_nodes=500`

**MCP Tests**
- Request a deeper call graph than Community (`depth>3`) and confirm it is not clamped to 3.

**Recorded Result**: [x] PASS / [ ] FAIL

### 8) get_graph_neighborhood
**Expected (Pro)**
- Limits: `max_k=5`, `max_nodes=100`

**MCP Tests**
- Request `k=2` and confirm it is accepted (not clamped to 1).

**Recorded Result**: [x] PASS / [ ] FAIL

### 9) get_symbol_references
**Expected (Pro)**
- Limits: effectively unlimited (no `max_files_searched` / `max_references` caps)

**MCP Tests**
- Call on a symbol with multiple refs; confirm results exceed Community caps when appropriate.

**Recorded Result**: [x] PASS / [ ] FAIL

### 10) simulate_refactor
**Expected (Pro)**
- Capabilities: same surface, but more robust structural + security checks.

**MCP Tests**
- Introduce `eval()` and confirm it is flagged unsafe.

**Recorded Result**: [x] PASS / [ ] FAIL

### 11) scan_dependencies
**Expected (Pro)**
- Limits: unlimited dependency counts; `osv_lookup=true`

**MCP Tests**
- Call on a manifest or dependency list; confirm the tool runs without the Community truncation limit.

**Recorded Result**: [x] PASS / [ ] FAIL

### 12) get_cross_file_dependencies
**Expected (Pro)**
- Limits: `max_depth=5`, `max_files=500`

**MCP Tests**
- Request `max_depth=3` and confirm transitive dependency resolution occurs.

**Recorded Result**: [x] PASS / [ ] FAIL

### 13) cross_file_security_scan
**Expected (Pro)**
- Limits: `max_modules=100`, `max_depth=10`

**MCP Tests**
- Request `max_depth=5` and confirm no Community clamp to 3.

**Recorded Result**: [x] PASS / [ ] FAIL

### 14) verify_policy_integrity
**Expected (Pro)**
- Capabilities: signature validation + tamper detection (requires `SCALPEL_MANIFEST_SECRET`)
- Limits: `max_rules=200`

**MCP Tests**
- Provide a policy dir with a signed manifest; confirm signature verification runs.

**Recorded Result**: [x] PASS / [ ] FAIL

### 15) code_policy_check
**Expected (Pro)**
- Capabilities: best-practice + security rules; `custom_rules_enabled=true`
- Limits: `max_files=1000`, `max_rules=200`

**MCP Tests**
- Call with a `rules` list including both style and security codes (e.g., `SEC001`).

**Negative Test (Enterprise-only)**
- Request `compliance_standards` (HIPAA/SOC2/etc) → expect not supported or upgrade-required.

**Recorded Result**: [x] PASS / [ ] FAIL

### 16) type_evaporation_scan
**Expected (Pro)**
- Capabilities: includes network boundary analysis and implicit-any detection
- Limits: `max_files=500`

**MCP Tests**
- Provide frontend code that consumes `.json()` without runtime validation and confirm implicit-any issues are surfaced.

**Recorded Result**: [x] PASS / [ ] FAIL

### 17) unified_sink_detect
**Expected (Pro)**
- Supports additional languages (Go/Rust) vs Community.

**MCP Tests**
- Call with `language=javascript` and with `language=go` and confirm Go is accepted.

**Recorded Result**: [x] PASS / [ ] FAIL

### 18) validate_paths
**Expected (Pro)**
- Limits: effectively unlimited

**MCP Tests**
- Provide a larger path list than Community’s cap and confirm it is accepted.

**Recorded Result**: [x] PASS / [ ] FAIL

### 19) update_symbol
**Expected (Pro)**
- Same behavior; should remain safe + atomic replacement.

**MCP Tests**
- Update a small function and confirm the backup file is created.

**Recorded Result**: [x] PASS / [ ] FAIL

### 20) rename_symbol
**Expected (Pro)**
- Renames the symbol definition in the target file.
- Additionally updates **references/imports** in other files where resolvable (project scope).
- Limits enforced via `limits.toml` (bounded cross-file search/update).

**MCP Tests**
- Rename a simple function and confirm success + backup creation.

**Cross-file Test**
- Add a second file that imports/calls the symbol and confirm it is updated.

**Recorded Result**: [x] PASS / [ ] FAIL

### 21) get_project_map
**Expected (Pro)**
- Limits: `max_files=1000`, `detail_level=detailed`

**MCP Tests**
- Run on a medium project and confirm enhanced detail vs Community.

**Recorded Result**: [x] PASS / [ ] FAIL

### 22) get_file_context
**Expected (Pro)**
- Same surface; may include additional metadata in richer tiers.

**MCP Tests**
- Call on a file and confirm results are returned.

**Recorded Result**: [x] PASS / [ ] FAIL
