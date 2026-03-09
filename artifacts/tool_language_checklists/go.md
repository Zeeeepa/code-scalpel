# Go Tool Adoption Checklist

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
  Depends on: security analyzer generalization plus Go package models
  Local order: 7
  Requirements: Add net/http, template, database, and os/exec source-sink models; support package and method flows conservatively; add context-aware fixtures.
  Why hard: interface calls and package-level helpers complicate flow precision

- [ ] `crawl_project`
  Status: C
  Difficulty: medium
  Target: convert claimed/coarse support into runtime-backed support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: Align feature metadata with actual runtime behavior, implement missing execution path(s), add fixture coverage, and define explicit unsupported cases.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

- [ ] `get_file_context`
  Status: P
  Difficulty: medium
  Target: high-quality file summaries
  Depends on: language-specific structure extraction
  Local order: 4
  Requirements: Add Go package/function/method summaries and import grouping with fixture coverage.
  Why hard: Go needs package-aware summaries to be useful

## Unsupported / Add

- [ ] `rename_symbol`
  Status: U
  Difficulty: medium
  Target: definition plus cross-file rename parity
  Depends on: unified patcher plus Go symbol model
  Local order: 1
  Requirements: Add parser-backed symbol span extraction; support package/import scope renames; preserve receiver-method boundaries; add golden rename and rollback tests.
  Why hard: rename correctness depends on exact symbol ownership and conservative reference updates

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus Go formatter/import logic
  Local order: 1
  Requirements: Add Go-aware function and method replacement; preserve imports and formatting; validate receiver methods and package scopes; add semantic-validation tests.
  Why hard: rewrites must preserve imports, formatting, and symbol ownership

- [ ] `cross_file_security_scan`
  Status: U
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: Go graph/runtime parity
  Local order: 4
  Requirements: First land import-aware call-graph/runtime support; then add package-level taint propagation, framework models, and dependency-chain fixtures.
  Why hard: without graph parity, taint flow across files will be too lossy

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 7
  Requirements: Add Go lowering, function/method semantics, loop/fuel policy, and conservative interface-call handling.
  Why hard: interfaces and concurrency semantics need careful scoping

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Go symbolic frontend plus test emitter
  Local order: 7
  Requirements: Add Go path extraction plus standard Go test emitter and assertion conventions.
  Why hard: the whole stack is missing, not just the emitter

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: Go parser and validation logic
  Local order: 7
  Requirements: Add Go AST diffing, import and receiver-method awareness, and typed validation before claiming safe refactor support.
  Why hard: without Go-specific structure, safety results would be superficial

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: Go graph/runtime parity
  Local order: 4
  Requirements: Add Go canonical symbols, package/import resolution, and categorized reference fixtures.
  Why hard: reference precision needs import-aware symbol identity

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus import-aware resolution
  Local order: 4
  Requirements: Audit IR output quality; ensure top-level functions, methods, and call expressions are usable; add local parity, import-aware cross-file resolution, alias handling, confidence metadata, path/focus tests, Mermaid stability, and roadmap parity level.
  Why hard: Go is a good next cohort because imports and package structure are tractable

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: Go get_call_graph parity
  Local order: 4
  Requirements: Reuse Go canonical node IDs after get_call_graph parity reaches import-aware support; add predictable unsupported behavior until then.
  Why hard: neighborhood expansion before graph parity would duplicate work

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: Go get_call_graph parity
  Local order: 4
  Requirements: Add Go chain assembly after import-aware graph parity lands; validate paths_from, paths_to, and focus behavior.
  Why hard: dependency chains are downstream of import-aware graph resolution

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: Go graph/runtime parity
  Local order: 4
  Requirements: Add Go module discovery, graph-derived relationships, hotspots, and stable summaries after graph parity lands.
  Why hard: project maps are only valuable once relationships are trustworthy

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

