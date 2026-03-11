# Javascript Tool Adoption Checklist

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

- [ ] `get_file_context`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: file summarization helpers plus language-specific structure extraction
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: overview quality still depends on language-aware extraction for functions, classes, imports, and complexity

- [ ] `type_evaporation_scan`
  Status: Y
  Difficulty: medium_high
  Target: maintain supported JavaScript frontend role
  Depends on: TS/JS frontend boundary extraction plus Python backend endpoint model
  Requirements: No JavaScript adoption work required beyond regression coverage and documentation accuracy for the frontend side of the contract.
  Why hard: JavaScript is complete as a supported frontend input, but the overall workflow is intentionally narrow to TS/JS frontend to Python backend analysis rather than general JavaScript-to-anything parity

- [ ] `unified_sink_detect`
  Status: Y
  Difficulty: low
  Target: maintain current support
  Depends on: sink pattern packs plus language detection
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: already broad; hardest remaining work is sink quality tuning, not language reach

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

## Partial / Stabilize

- [ ] `security_scan`
  Status: P
  Difficulty: high
  Target: full taint-analysis parity
  Depends on: security analyzer generalization plus JS framework models
  Local order: 1
  Requirements: Replace sink-only handling with source, sink, sanitizer, and framework-aware taint models for browser and Node patterns; add reachability and remediation tests.
  Why hard: moving from sink detection to taint analysis requires real flow semantics

- [ ] `cross_file_security_scan`
  Status: P
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: JS graph/runtime parity plus taint engine
  Local order: 1
  Requirements: Reuse JS call graph and import resolution; add inter-file taint propagation, framework-aware source-to-sink tracing, confidence metadata, and deterministic fallback tests.
  Why hard: cross-file taint depends on a solid graph/runtime substrate

- [ ] `generate_unit_tests`
  Status: C
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: JS symbolic frontend plus Jest emitter
  Local order: 1
  Requirements: Wire non-Python code parsing into the generation pipeline; emit Jest tests from language-specific execution paths; add fixtures and framework golden tests.
  Why hard: framework capability exists in metadata, but runtime generation is not wired

- [ ] `simulate_refactor`
  Status: P
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: language-aware diff and validation
  Local order: 1
  Requirements: Add JS AST diff fidelity, same-file behavior heuristics, and stronger semantic validation; add regression tests for imports and common refactors.
  Why hard: generic diff is not enough for trustworthy behavior claims

- [ ] `crawl_project`
  Status: C
  Difficulty: medium
  Target: convert claimed/coarse support into runtime-backed support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: Align feature metadata with actual runtime behavior, implement missing execution path(s), add fixture coverage, and define explicit unsupported cases.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

- [ ] `get_symbol_references`
  Status: P
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: graph runtime plus symbol indexing
  Local order: 1
  Requirements: Keep the local JS slice and add stronger categorization, import-edge resolution, canonical node stability, and tier/truncation tests.
  Why hard: reference quality depends on symbol identity and import handling

- [ ] `get_call_graph`
  Status: P
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: shared call-graph builder plus canonical node scheme
  Local order: 1
  Requirements: Stabilize Level 1 through Level 3 parity: canonical node naming, same-file edges, import-aware cross-file resolution, inference_source taxonomy, confidence rules, unsupported-construct policy, and golden tests.
  Why hard: the easy part is local edges; the hard part is precise cross-file semantics

- [ ] `get_graph_neighborhood`
  Status: P
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 2: same-file call edges
  Depends on: get_call_graph canonical node parity
  Local order: 1
  Requirements: Reuse canonical JS node IDs, neighborhood extraction, confidence metadata, and Mermaid stability from get_call_graph; add unsupported-case tests.
  Why hard: neighborhood quality inherits call-graph quality

- [ ] `get_cross_file_dependencies`
  Status: P
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: JS get_call_graph parity
  Local order: 1
  Requirements: Keep the JS graph-backed slice and add confidence metadata, path/focus validation, Mermaid stability, and unsupported-case tests.
  Why hard: dependency-chain quality depends on upstream graph resolution

- [ ] `get_project_map`
  Status: P
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: JS graph/runtime parity
  Local order: 1
  Requirements: Keep the local JS module slice and add stronger relationship derivation, graph-backed summaries, metadata tests, and stable Mermaid/report outputs.
  Why hard: language totals are easy; relationships are the real work

## Unsupported / Add

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 1
  Requirements: Build a JavaScript symbolic frontend, type model, constraint translation, loop handling, and path extraction; add engine fixture coverage.
  Why hard: the current symbolic engine is explicitly Python-shaped

