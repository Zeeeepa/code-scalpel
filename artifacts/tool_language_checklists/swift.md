# Swift Tool Adoption Checklist

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
  Depends on: Swift app/server source-sink model
  Local order: 11
  Requirements: Define Foundation/UIKit/server-side Swift sources and sinks; add sanitizer recognition; keep unresolved dynamic dispatch unsupported.
  Why hard: dynamic dispatch and platform diversity make Swift security modeling expensive

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
  Depends on: unified patcher plus Swift symbol model
  Local order: 5
  Requirements: Support modules, extensions, protocols, and conformances; preserve member references across files; exclude selector and reflection-based cases; add SourceKit-backed fixtures.
  Why hard: protocols, extensions, and selectors complicate rename safety

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus Swift symbol/range logic
  Local order: 5
  Requirements: Support function, method, and type replacement with extension awareness; preserve imports; add protocol/conformance fixtures and rollback validation.
  Why hard: extensions and protocol conformances complicate safe replacement scopes

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
  Local order: 11
  Requirements: Add Swift lowering for functions, methods, optionals, and a minimal safe subset before protocol-heavy features.
  Why hard: optionals, protocols, and value/reference semantics complicate modeling

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Swift symbolic frontend plus test emitter
  Local order: 11
  Requirements: Add Swift path extraction plus XCTest emitter and optionals-aware assertions.
  Why hard: Swift needs both frontend and assertion strategy work

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: Swift parser and validation logic
  Local order: 11
  Requirements: Add Swift AST diffing, protocol/extension awareness, and typed validation for safe subset refactors.
  Why hard: protocols and extensions complicate impact analysis

- [ ] `get_file_context`
  Status: U
  Difficulty: medium
  Target: high-quality file summaries
  Depends on: language-specific structure extraction
  Local order: 12
  Requirements: Add module/type/function summaries with extension/protocol awareness.
  Why hard: extensions and protocols alter how symbols should be summarized

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: Swift graph/runtime parity
  Local order: 8
  Requirements: Add module/type/member symbol IDs and categorized reference tests.
  Why hard: protocol and extension references complicate stable categorization

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus Swift symbol model
  Local order: 8
  Requirements: Promote Swift local parity, add module/type/member normalization, import-aware cross-file resolution, and extension/protocol-safe unsupported-case policy.
  Why hard: protocols and extensions complicate high-confidence dispatch

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: Swift get_call_graph parity
  Local order: 8
  Requirements: Add Swift canonical node IDs and neighborhood extraction after call-graph parity lands.
  Why hard: extensions and protocols complicate neighborhood semantics

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: Swift get_call_graph parity
  Local order: 8
  Requirements: Add Swift chain assembly after graph parity lands with module/type/member resolution.
  Why hard: protocol/extension complexity propagates into chains

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: Swift graph/runtime parity
  Local order: 8
  Requirements: Add Swift module/type discovery and graph-derived relationships after graph parity lands.
  Why hard: protocol and extension relations need careful handling

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

