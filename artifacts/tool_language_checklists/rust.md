# Rust Tool Adoption Checklist

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
  Depends on: Rust API source-sink model
  Local order: 12
  Requirements: Define web framework sources, unsafe/process/file sinks, sanitizer patterns, and conservative macro handling; add cargo-backed fixtures.
  Why hard: macros and ownership-aware APIs complicate flow tracking

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
  Local order: 7
  Requirements: Add module/function/impl summaries and use-tree handling with fixture tests.
  Why hard: Rust structure extraction needs to respect modules and impl blocks

## Unsupported / Add

- [ ] `rename_symbol`
  Status: U
  Difficulty: medium
  Target: definition plus cross-file rename parity
  Depends on: unified patcher plus Rust path model
  Local order: 6
  Requirements: Handle modules and use-aliases; support impl methods, trait items, and associated functions conservatively; define macro exclusions; add cargo fixture tests.
  Why hard: traits, modules, and macros make precise rename boundaries easy to overclaim

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus Rust item model
  Local order: 6
  Requirements: Support module, impl, and trait-item replacement; preserve use statements and formatting; define macro exclusions; add cargo fixture tests.
  Why hard: impls, traits, and macros require conservative range selection

- [ ] `cross_file_security_scan`
  Status: U
  Difficulty: very_high
  Target: add new language support
  Depends on: import/call graph plus taint flow plus framework models
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: cross-file taint is one of the hardest semantic engines to generalize

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 12
  Requirements: Add Rust lowering with ownership-aware semantics, pattern matching, and explicit macro exclusions.
  Why hard: ownership and borrowing need dedicated semantics

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Rust symbolic frontend plus test emitter
  Local order: 12
  Requirements: Add Rust path extraction plus cargo test emitter and ownership-aware assertion generation.
  Why hard: ownership semantics affect how generated tests must be structured

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: Rust parser and validation logic
  Local order: 12
  Requirements: Add Rust AST diffing, module/trait awareness, and ownership-related validation heuristics.
  Why hard: ownership and trait behavior alter how code changes should be judged

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: Rust graph/runtime parity
  Local order: 9
  Requirements: Add module/use/trait-aware symbol IDs and categorized reference tests.
  Why hard: traits and modules affect what counts as the same symbol

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus Rust path model
  Local order: 9
  Requirements: Promote Rust local parity, add module/use normalization, trait/impl-safe local and cross-file resolution, confidence metadata, and macro exclusions.
  Why hard: traits and macros need conservative treatment

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: Rust get_call_graph parity
  Local order: 9
  Requirements: Add Rust canonical node IDs and neighborhood extraction after call-graph parity lands; preserve macro exclusions.
  Why hard: macro and trait boundaries affect neighborhood correctness

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: Rust get_call_graph parity
  Local order: 9
  Requirements: Add Rust chain assembly after graph parity lands with module/use/trait-safe rules and macro exclusions.
  Why hard: trait and macro handling affects chain determinism

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: Rust graph/runtime parity
  Local order: 9
  Requirements: Add Rust module/use discovery and graph-derived relationships after graph parity lands.
  Why hard: module and trait relationships need stable node IDs first

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

