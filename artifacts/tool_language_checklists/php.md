# Php Tool Adoption Checklist

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
  Depends on: PHP runtime and framework taint models
  Local order: 9
  Requirements: Model superglobals as sources; add SQL, template, file, and command sinks; recognize common framework sanitizers; add fixture coverage.
  Why hard: superglobals and dynamic patterns create many false-positive traps

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
  Local order: 5
  Requirements: Add namespace/class/function summaries and import/use handling; add fixture tests.
  Why hard: namespace-aware summaries matter more than raw file metadata

## Unsupported / Add

- [ ] `rename_symbol`
  Status: U
  Difficulty: medium
  Target: definition plus cross-file rename parity
  Depends on: unified patcher plus PHP namespace model
  Local order: 3
  Requirements: Implement namespace and use-alias handling; support class/static members; exclude dynamic variable-function cases; add conservative unresolved-reference behavior.
  Why hard: PHP symbol resolution becomes unsafe once dynamic invocation enters the picture

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus PHP namespace handling
  Local order: 3
  Requirements: Support namespace-aware replacement; preserve use imports and class/static members; define unsupported dynamic cases; add rollback tests.
  Why hard: unsafe dynamic constructs must fail closed rather than patch guessed ranges

- [ ] `cross_file_security_scan`
  Status: U
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: PHP graph/runtime parity
  Local order: 6
  Requirements: Add namespace/import-aware graph support; then add framework request flow, sink models, and conservative dynamic-call exclusions.
  Why hard: namespace graphs are tractable, but dynamic invocation must stay unsupported

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 9
  Requirements: Add PHP lowering for functions, methods, arrays, and dynamic features with a strict unsupported subset.
  Why hard: dynamic runtime behavior must be kept out of the trusted subset

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: PHP symbolic frontend plus test emitter
  Local order: 9
  Requirements: Add PHP path extraction plus PHPUnit emitter and safe subset fixtures.
  Why hard: dynamic runtime semantics make automated expectations harder

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: PHP parser and validation logic
  Local order: 9
  Requirements: Add PHP AST diffing, namespace and dynamic-feature policy, and fixture coverage for safe subset refactors.
  Why hard: dynamic features require a strict fail-closed policy

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: PHP graph/runtime parity
  Local order: 6
  Requirements: Add namespace/use-aware symbol identity, reference categorization, and dynamic-call exclusions.
  Why hard: dynamic invocation must remain unsupported

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus PHP namespace model
  Local order: 6
  Requirements: Promote PHP local parity, add namespace/module normalization, import/use resolution, cross-file symbol-chain fixtures, confidence metadata, and unsupported dynamic-call policy.
  Why hard: namespace resolution is feasible, but dynamic invocation must fail closed

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: PHP get_call_graph parity
  Local order: 6
  Requirements: Add PHP canonical node IDs and neighborhood extraction after call-graph parity lands; preserve conservative dynamic exclusions.
  Why hard: dynamic-call uncertainty propagates directly into neighborhoods

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: PHP get_call_graph parity
  Local order: 6
  Requirements: Add PHP chain assembly after graph parity lands with namespace/use handling and conservative dynamic exclusions.
  Why hard: namespace resolution must be right before chains are useful

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: PHP graph/runtime parity
  Local order: 6
  Requirements: Add PHP namespace/module discovery and graph-derived relationships after graph parity lands.
  Why hard: namespace maps need graph support to be useful

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

