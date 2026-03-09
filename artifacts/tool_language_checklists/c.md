# C Tool Adoption Checklist

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
  Depends on: C API source/sink model
  Local order: 4
  Requirements: Define conservative source/sink taxonomy for process, file, network, and memory APIs; add sanitizer rules; avoid guessed dataflow across unresolved pointers.
  Why hard: pointer-heavy code makes taint propagation easy to overstate

- [ ] `generate_unit_tests`
  Status: C
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: C symbolic frontend plus Catch2 emitter
  Local order: 3
  Requirements: Add C path extraction, assertion rendering, and Catch2-oriented output; define supported subset and fixtures.
  Why hard: metadata claims framework support, but no runtime path engine exists

- [ ] `simulate_refactor`
  Status: P
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: language-aware diff and validation
  Local order: 4
  Requirements: Add C-aware structural diffing, function/global analysis, and conservative pointer-related warnings; add parser-backed fixtures.
  Why hard: C changes can alter behavior through globals and pointer use

- [ ] `crawl_project`
  Status: C
  Difficulty: medium
  Target: convert claimed/coarse support into runtime-backed support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: Align feature metadata with actual runtime behavior, implement missing execution path(s), add fixture coverage, and define explicit unsupported cases.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

## Unsupported / Add

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
  Depends on: new symbolic execution frontend plus memory model
  Local order: 4
  Requirements: Add C control-flow lowering, pointer/memory model policy, arithmetic semantics, and conservative unsupported-case handling.
  Why hard: memory and pointer semantics make C symbolic execution non-trivial

- [ ] `get_file_context`
  Status: U
  Difficulty: medium
  Target: high-quality file summaries
  Depends on: language-specific structure extraction
  Local order: 8
  Requirements: Add C function/struct/include summaries, preprocessor-aware fallbacks, and conservative complexity heuristics.
  Why hard: preprocessor noise makes useful summarization harder

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: add new language support
  Graph parity: Level 0: unsupported
  Depends on: shared graph runtime plus import resolution plus symbol indexing
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: reference quality depends on symbol identity, import handling, and call categorization

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: canonical node scheme plus C-specific policy
  Local order: 11
  Requirements: Define advanced parity scope for C, add same-file static/internal function distinction, header/source de-duplication, conservative function-pointer handling, multi-file include fixtures, and explicit unsupported-case docs.
  Why hard: C has fewer abstractions, but headers and function pointers create their own pitfalls

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: add new language support
  Graph parity: Level 0: unsupported
  Depends on: get_call_graph parity plus canonical node IDs plus neighborhood extraction
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: best ROI comes after call-graph expansion because neighborhood quality inherits node quality

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: add new language support
  Graph parity: Level 0: unsupported
  Depends on: graph runtime plus import resolution plus dependency chain assembly
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: runtime is relatively simple only after call-graph and confidence scoring are solid

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Graph parity: Level 0: unsupported
  Depends on: module discovery plus graph-derived relationships
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: language totals are easy; relationship maps need graph/runtime parity

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

