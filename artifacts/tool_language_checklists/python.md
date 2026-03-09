# Python Tool Adoption Checklist

Generated from the per-language planning sheet.

## Legend

- `Y`: implemented
- `P`: partial support
- `U`: unsupported
- `C`: claimed/coarse support only
- `A`: language-agnostic

## Graph Parity Levels

- `L0`: Level 0: unsupported
- `L1`: Level 1: local callable nodes
- `L2`: Level 2: same-file call edges
- `L3`: Level 3: import-aware cross-file resolution
- `L4`: Level 4: typed/OO dispatch
- `L5`: Level 5: path-query and confidence parity
- `COUNT`: count-only / pre-parity support

## Implemented / Maintain

- [ ] `analyze_code`
  Status: Y
  Difficulty: low
  Target: maintain current support
  Depends on: parser/normalizer maintenance only
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: already broad; remaining work is mostly parser quality and test depth

- [ ] `extract_code`
  Status: Y
  Difficulty: low
  Target: maintain current support
  Depends on: polyglot extractor plus normalizers
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: already broad; biggest gap is feature uniformity, not language onboarding

- [ ] `rename_symbol`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: unified patcher language support plus per-language rename semantics
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: rename safety depends on symbol-boundary accuracy and reference updates, not just parsing

- [ ] `update_symbol`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: unified patcher and language-aware replacement semantics
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: safe patching needs robust per-language rewrite semantics and post-save verification

- [ ] `security_scan`
  Status: Y
  Difficulty: high
  Target: maintain current support
  Depends on: language-specific taint/source/sink/sanitizer models
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: real vulnerability analysis becomes expensive once each language/framework needs distinct taint rules

- [ ] `unified_sink_detect`
  Status: Y
  Difficulty: low
  Target: maintain current support
  Depends on: sink pattern packs plus language detection
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: already broad; hardest remaining work is sink quality tuning, not language reach

- [ ] `cross_file_security_scan`
  Status: Y
  Difficulty: very_high
  Target: maintain current support
  Depends on: import/call graph plus taint flow plus framework models
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: cross-file taint is one of the hardest semantic engines to generalize

- [ ] `symbolic_execute`
  Status: Y
  Difficulty: very_high
  Target: maintain current support
  Depends on: new symbolic execution frontend per language
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: current engine is explicitly Python-specific

- [ ] `generate_unit_tests`
  Status: Y
  Difficulty: very_high
  Target: maintain current support
  Depends on: symbolic frontend plus per-language test generators
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: capability metadata claims broader frameworks, but runtime is still Python-specific

- [ ] `simulate_refactor`
  Status: Y
  Difficulty: very_high
  Target: maintain current support
  Depends on: AST diffing plus behavior simulation plus optional type checking per language
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: safe refactor simulation needs language-aware structure, typing, and behavior heuristics

- [ ] `crawl_project`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

- [ ] `get_file_context`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: file summarization helpers plus language-specific structure extraction
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: overview is broad, but good summaries for functions/classes/imports need per-language shape support

- [ ] `get_symbol_references`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Graph parity: Level 5: path-query and confidence parity
  Depends on: shared graph runtime plus import resolution plus symbol indexing
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: reference quality depends on symbol identity, import handling, and call categorization

- [ ] `get_call_graph`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Graph parity: Level 5: path-query and confidence parity
  Depends on: shared call-graph builder plus file discovery plus canonical node IDs
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: local same-file edges are cheap; import-aware and typed cross-file semantics are still costly

- [ ] `get_graph_neighborhood`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Graph parity: Level 5: path-query and confidence parity
  Depends on: get_call_graph parity plus canonical node IDs plus neighborhood extraction
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: best ROI comes after call-graph expansion because neighborhood quality inherits node quality

- [ ] `get_cross_file_dependencies`
  Status: Y
  Difficulty: high
  Target: maintain current support
  Graph parity: Level 5: path-query and confidence parity
  Depends on: graph runtime plus import resolution plus dependency chain assembly
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: runtime is relatively simple only after call-graph and confidence scoring are solid

- [ ] `get_project_map`
  Status: Y
  Difficulty: medium_high
  Target: maintain current support
  Graph parity: Level 5: path-query and confidence parity
  Depends on: module discovery plus graph-derived relationships
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: language totals are easy; relationship maps need graph/runtime parity

- [ ] `scan_dependencies`
  Status: A
  Difficulty: low
  Target: maintain current support
  Depends on: manifest parser coverage by ecosystem
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: source language matters less than package-manager support

- [ ] `validate_paths`
  Status: A
  Difficulty: low
  Target: maintain current support
  Depends on: none
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: language-agnostic path validation

- [ ] `verify_policy_integrity`
  Status: A
  Difficulty: low
  Target: maintain current support
  Depends on: none
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: language-agnostic cryptographic verification

- [ ] `code_policy_check`
  Status: A
  Difficulty: medium
  Target: maintain current support
  Depends on: policy rule libraries and language-specific rule packs where deeper parity is desired
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: the engine is generic, but meaningful parity depends on per-language rules

- [ ] `type_evaporation_scan`
  Status: Y
  Difficulty: medium_high
  Target: maintain supported Python backend role
  Depends on: TS/JS frontend boundary extraction plus Python backend endpoint model
  Requirements: No Python adoption work required beyond regression coverage and documentation accuracy for the backend side of the contract.
  Why hard: Python is complete as the backend half of the tool, but the overall workflow is intentionally narrow to TS/JS frontend to Python backend analysis rather than general Python-frontend parity

