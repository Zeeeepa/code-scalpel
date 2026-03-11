# Ruby Tool Adoption Checklist

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
  Depends on: Ruby/Rails taint models
  Local order: 10
  Requirements: Model Rails params and request sources, ActiveRecord/ERB/process sinks, sanitizer helpers, and cross-method flows conservatively.
  Why hard: Ruby metaprogramming and Rails conventions make static flow analysis difficult

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
  Local order: 6
  Requirements: Add module/class/method summaries and require/include awareness with fixture coverage.
  Why hard: Ruby files need semantic grouping, not just plain text inspection

## Unsupported / Add

- [ ] `rename_symbol`
  Status: U
  Difficulty: medium
  Target: definition plus cross-file rename parity
  Depends on: unified patcher plus Ruby constant model
  Local order: 4
  Requirements: Support module and class scopes; model mixins and reopen semantics conservatively; exclude metaprogrammed dynamic references; add fixture coverage.
  Why hard: Ruby allows many runtime-bound references that should not be guessed

- [ ] `update_symbol`
  Status: U
  Difficulty: medium
  Target: safe replace/update parity
  Depends on: unified patcher plus Ruby formatter/range logic
  Local order: 4
  Requirements: Support class and module body replacement; preserve reopen semantics where safe; define metaprogramming exclusions; add fixture coverage.
  Why hard: Ruby rewrites are easy to get syntactically valid but semantically wrong

- [ ] `cross_file_security_scan`
  Status: U
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: Ruby graph/runtime parity
  Local order: 7
  Requirements: Add module/class graph support; then model Rails controller-to-view/db flows conservatively and exclude metaprogrammed edges.
  Why hard: Rails-style flow is useful, but Ruby dynamism makes safe resolution hard

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 10
  Requirements: Add Ruby lowering with a narrow safe subset; exclude metaprogramming and dynamic dispatch until proven tractable.
  Why hard: Ruby dynamism makes bounded symbolic execution especially hard

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Ruby symbolic frontend plus test emitter
  Local order: 10
  Requirements: Add Ruby path extraction plus RSpec/Minitest emitter and conservative safe subset.
  Why hard: Ruby dynamism complicates stable auto-generated expectations

- [ ] `simulate_refactor`
  Status: U
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: Ruby parser and validation logic
  Local order: 10
  Requirements: Add Ruby AST diffing for a narrow safe subset and exclude metaprogrammed behavior from safety claims.
  Why hard: metaprogramming makes static behavior-preservation claims risky

- [ ] `get_symbol_references`
  Status: U
  Difficulty: medium
  Target: reference parity
  Graph parity: Level 0: unsupported
  Depends on: Ruby graph/runtime parity
  Local order: 7
  Requirements: Add module/class symbol IDs and conservative reference categorization with metaprogramming exclusions.
  Why hard: Ruby reference analysis must stay conservative around dynamic behavior

- [ ] `get_call_graph`
  Status: U
  Difficulty: medium
  Target: advanced call-graph parity
  Graph parity: Level 0: unsupported
  Depends on: local parity promotion plus Ruby module model
  Local order: 7
  Requirements: Promote Ruby local parity, add module/class normalization, require/include awareness, conservative cross-file resolution, and dynamic exclusion tests.
  Why hard: Ruby needs strict unsupported-case policy around metaprogramming

- [ ] `get_graph_neighborhood`
  Status: U
  Difficulty: medium
  Target: neighborhood parity
  Graph parity: Level 0: unsupported
  Depends on: Ruby get_call_graph parity
  Local order: 7
  Requirements: Add Ruby canonical node IDs and neighborhood extraction after call-graph parity lands; exclude metaprogrammed edges.
  Why hard: unsafe dynamic edges would pollute neighborhood output

- [ ] `get_cross_file_dependencies`
  Status: U
  Difficulty: high
  Target: dependency-chain parity
  Graph parity: Level 0: unsupported
  Depends on: Ruby get_call_graph parity
  Local order: 7
  Requirements: Add Ruby chain assembly after graph parity lands with module/class resolution and metaprogramming exclusions.
  Why hard: dynamic behavior makes chain assembly easy to overclaim

- [ ] `get_project_map`
  Status: U
  Difficulty: medium_high
  Target: module and relationship parity
  Graph parity: Level 0: unsupported
  Depends on: Ruby graph/runtime parity
  Local order: 7
  Requirements: Add Ruby module/class discovery and graph-derived relationships after graph parity lands.
  Why hard: dynamic features make relationship extraction easy to overstate

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

