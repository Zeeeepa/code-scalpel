# Typescript Tool Adoption Checklist

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

- [ ] `unified_sink_detect`
  Status: Y
  Difficulty: low
  Target: maintain current support
  Depends on: sink pattern packs plus language detection
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: already broad; hardest remaining work is sink quality tuning, not language reach

- [ ] `type_evaporation_scan`
  Status: Y
  Difficulty: medium_high
  Target: maintain current support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

- [ ] `get_file_context`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: file summarization helpers plus language-specific structure extraction
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: overview quality still depends on language-aware extraction for functions, interfaces, imports, and complexity

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
  Depends on: JS security parity plus TS type surface
  Local order: 2
  Requirements: Add type-aware taint propagation, TS framework models, sanitizer recognition, and tighter integration with type-evaporation findings; add regression fixtures.
  Why hard: TypeScript adds type-only forms and framework conventions on top of JS flow

- [ ] `cross_file_security_scan`
  Status: P
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: JS cross-file parity plus TS import model
  Local order: 2
  Requirements: Extend JS cross-file taint with TS path aliases, type-only imports, and framework metadata; add tier and truncation tests.
  Why hard: type-only constructs and aliasing increase graph ambiguity

- [ ] `generate_unit_tests`
  Status: C
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: TS symbolic frontend plus Jest emitter
  Local order: 2
  Requirements: Wire TS analysis into the pipeline; emit Jest tests with TS-friendly assertions and module handling; add fixture coverage.
  Why hard: claimed framework support is not the same as path generation support

- [ ] `simulate_refactor`
  Status: P
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: JS refactor parity plus TS type checks
  Local order: 2
  Requirements: Extend JS simulation with TS-aware type-error detection, import/alias handling, and stronger semantic validation.
  Why hard: type-aware validation is required to make TS results credible

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
  Depends on: JS reference parity plus TS import model
  Local order: 2
  Requirements: Extend JS parity with TS path aliases, type-only imports, and stable reference categorization.
  Why hard: type-only constructs and aliases add ambiguity

- [ ] `get_call_graph`
  Status: P
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: JS call-graph parity plus TS import model
  Local order: 2
  Requirements: Do the JavaScript work plus TS path aliases, type-only imports, and method parity coverage where advanced resolution is enabled.
  Why hard: TypeScript adds extra import and type-system surface area

- [ ] `get_graph_neighborhood`
  Status: P
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 2: same-file call edges
  Depends on: get_call_graph TS parity
  Local order: 2
  Requirements: Extend JS neighborhood parity with TS method-node and alias-aware validation where advanced resolution exists.
  Why hard: method-node parity depends on upstream TS node stability

- [ ] `get_cross_file_dependencies`
  Status: P
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: TS get_call_graph parity
  Local order: 2
  Requirements: Extend JS parity with TS alias and type-only import handling plus metadata-limit tests.
  Why hard: type-only and alias constructs affect chain assembly

- [ ] `get_project_map`
  Status: P
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: TS graph/runtime parity
  Local order: 2
  Requirements: Extend JS parity with TS alias-aware module relationships, symbol summaries, and graph-derived edges.
  Why hard: relationship accuracy depends on TS import normalization

## Unsupported / Add

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: JS symbolic frontend plus TS types
  Local order: 2
  Requirements: Add TS parser frontend, type-aware symbolic variables, constraint lowering, and framework-free core fixtures before any frontend extras.
  Why hard: type-rich TS still needs runtime-semantics modeling

