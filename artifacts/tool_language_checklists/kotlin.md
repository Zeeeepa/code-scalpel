# Kotlin Tool Adoption Checklist

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
  Depends on: Java web parity plus Kotlin coroutine model
  Local order: 8
  Requirements: Add Spring, Ktor, and Android source/sink models; handle coroutine boundaries conservatively; add sanitizer and framework fixtures.
  Why hard: coroutines and mixed JVM frameworks need dedicated flow handling

- [ ] `crawl_project`
  Status: C
  Difficulty: medium
  Target: convert claimed/coarse support into runtime-backed support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: Align feature metadata with actual runtime behavior, implement missing execution path(s), add fixture coverage, and define explicit unsupported cases.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

## Unsupported / Add

- [ ] `rename_symbol`
  Status: U
  Difficulty: medium
  Target: definition plus cross-file rename parity
  Depends on: unified patcher plus Kotlin symbol model
  Local order: 2
  Requirements: Support package and import-alias renames; handle class, object, companion, and extension members; add overload-safe fixture coverage.
  Why hard: Kotlin scoping and alias forms make symbol identity non-trivial

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus Kotlin formatter/import logic
  Local order: 2
  Requirements: Implement Kotlin-aware block replacement; preserve imports and companion/object semantics; validate extension functions and overloaded members.
  Why hard: replacement is harder once extension and companion members are involved

- [ ] `cross_file_security_scan`
  Status: U
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: Kotlin graph/runtime parity
  Local order: 5
  Requirements: First add graph/runtime support for packages and imports; then add Spring/Ktor coroutine-aware taint propagation and DI handling.
  Why hard: Kotlin inherits JVM framework complexity plus coroutine boundaries

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 8
  Requirements: Add Kotlin lowering for functions, methods, nullability, and coroutine exclusions or semantics; define a minimal safe subset first.
  Why hard: nullability plus coroutine features expand the design space

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Kotlin symbolic frontend plus test emitter
  Local order: 8
  Requirements: Add Kotlin path extraction plus JUnit/Kotest-style emitter and JVM fixture coverage.
  Why hard: Kotlin requires both language and framework wiring

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: Kotlin parser and validation logic
  Local order: 8
  Requirements: Add Kotlin AST diffing, nullability/type checks, and object/companion awareness.
  Why hard: nullability and companion/object semantics affect behavior

- [ ] `get_file_context`
  Status: U
  Difficulty: medium
  Target: high-quality file summaries
  Depends on: language-specific structure extraction
  Local order: 11
  Requirements: Add package/class/object/function summaries and import handling with fixture coverage.
  Why hard: Kotlin files often mix multiple symbol kinds that need grouping

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: Kotlin graph/runtime parity
  Local order: 5
  Requirements: Add package/import-aware symbol identity and categorized reference tests.
  Why hard: package and member scopes need consistent symbol IDs

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus Kotlin package/import model
  Local order: 5
  Requirements: Promote Kotlin to method-aware local parity, then implement import-aware cross-file resolution, alias handling, path/focus behavior, and parity reporting.
  Why hard: Kotlin is promising but mixed JVM patterns still need conservative handling

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: Kotlin get_call_graph parity
  Local order: 5
  Requirements: Add Kotlin canonical node IDs and neighborhood extraction after call-graph parity is stable.
  Why hard: adjacent graph tools should reuse stable node IDs

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: Kotlin get_call_graph parity
  Local order: 5
  Requirements: Add Kotlin chain assembly after graph parity lands; include alias/import fixtures and metadata tests.
  Why hard: chain quality follows graph/runtime quality

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: Kotlin graph/runtime parity
  Local order: 5
  Requirements: Add Kotlin module discovery and graph-derived relationships after graph parity lands.
  Why hard: summary quality depends on relationship derivation

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

