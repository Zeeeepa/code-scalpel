# Java Tool Adoption Checklist

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

- [ ] `get_file_context`
  Status: Y
  Difficulty: medium
  Target: maintain current support
  Depends on: language-specific structure extraction
  Requirements: No adoption work required beyond regression coverage and documentation accuracy.
  Why hard: useful summaries still depend on keeping Java class/method/import/package extraction stable

## Partial / Stabilize

- [ ] `security_scan`
  Status: P
  Difficulty: high
  Target: full taint-analysis parity
  Depends on: security analyzer generalization plus Java web models
  Local order: 3
  Requirements: Implement servlet and Spring sources, JDBC and templating sinks, serialization risk models, sanitizer recognition, and cross-method taint propagation.
  Why hard: Java parity needs framework-specific models and interprocedural flow

- [ ] `cross_file_security_scan`
  Status: P
  Difficulty: very_high
  Target: cross-file taint parity
  Depends on: Java graph foundations plus taint engine
  Local order: 3
  Requirements: Add Spring and servlet inter-file flows, dependency-injection resolution, source/sink metadata, and conservative unresolved-bean handling.
  Why hard: dependency injection and framework indirection are hard to resolve safely

- [ ] `simulate_refactor`
  Status: P
  Difficulty: very_high
  Target: language-aware safety parity
  Depends on: language-aware diff and validation
  Local order: 3
  Requirements: Add Java-aware AST diffing, typed method/class validation, and conservative OO behavior checks; add fixture coverage.
  Why hard: OO structure and typing drive many real regressions

- [ ] `crawl_project`
  Status: C
  Difficulty: medium
  Target: convert claimed/coarse support into runtime-backed support
  Depends on: discovery helpers plus per-language file summarizers
  Requirements: Align feature metadata with actual runtime behavior, implement missing execution path(s), add fixture coverage, and define explicit unsupported cases.
  Why hard: discovery is easy; meaningful semantic crawl quality is not

- [ ] `get_call_graph`
  Status: P
  Difficulty: medium
  Target: stabilized Java slice
  Graph parity: Level 4: typed/OO dispatch
  Depends on: Java file discovery and canonical node emission already landed
  Local order: 3
    Requirements: Maintain shared-runtime Java callable discovery plus Pro/Enterprise type-import and static-import resolution, typed imported instance calls, superclass dispatch, field-backed instance calls, and the new overload-aware selector flow. Signature-qualified selectors now back overloaded Java call-graph paths and keep non-overloaded IDs stable; remaining hardening should stay focused on stronger argument typing and broader overload edge cases.
    Why hard: Java now has a real typed/OO slice with overload-aware identities, but broader parity still depends on conservative selector resolution staying trustworthy

- [ ] `get_project_map`
  Status: P
  Difficulty: medium_high
  Target: narrow Java module and relationship slice
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: stabilized Java get_call_graph slice
  Local order: 3
  Requirements: Maintain Java module discovery, canonical class/method inventory, and file-level relationships from explicit imports/static imports; keep package-layout hardening and broader ambiguity coverage narrow before broader claims.
  Why hard: explicit file relationships are tractable, but deeper architectural inference is still much harder than counting files

- [ ] `get_graph_neighborhood`
  Status: P
  Difficulty: medium
  Target: narrow Java method-node neighborhood slice
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: stabilized Java get_call_graph slice
  Local order: 3
    Requirements: Maintain canonical and signature-qualified Java method-node acceptance plus local neighborhoods in Community and shared call-graph-backed cross-file neighborhoods in Pro/Enterprise, including override-dispatch behavior. Enterprise query/path-constraint capability metadata is directly covered, and overloaded Java method node IDs like `java::demo/Helper::method::Helper:tool(int)` are now validated explicitly.
    Why hard: the tool is only as trustworthy as the underlying Java node IDs and cross-file call edges it reuses, especially once overload-aware selectors enter the surface

- [ ] `get_cross_file_dependencies`
  Status: P
  Difficulty: high
  Target: narrow Java method dependency slice
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: stabilized Java get_call_graph slice
  Local order: 3
    Requirements: Maintain local Java method dependency extraction in Community plus shared call-graph-backed cross-file chains in Pro/Enterprise, including override-dispatch behavior and overload-aware selector flow. Structured Java selectors like `Helper.tool(int)` and `Helper:tool(int)` are now accepted directly, and graph-backed extraction must keep exact-signature selection conservative.
    Why hard: Java dependency chains remain sensitive to selector identity, overload ambiguity, and argument-type inference

- [ ] `get_symbol_references`
  Status: P
  Difficulty: medium
  Target: narrow Java definition/import/call/reference slice
  Graph parity: Level 3: import-aware cross-file resolution
  Depends on: Java parser-backed definitions plus conservative local reference scanning
  Local order: 3
  Requirements: Maintain parser-backed Java class/method definitions plus conservative import, static-import, call-site, and reference discovery; overload/override ambiguity now returns structured disambiguation candidates instead of warning-only fallback, but broader identity hardening is still required before stronger claims.
  Why hard: Java references are now real and more conservative, but overloads, inheritance, and ambiguous names still need stricter symbol identity before broader parity claims

## Unsupported / Add

- [ ] `symbolic_execute`
  Status: U
  Difficulty: very_high
  Target: language frontend plus path exploration parity
  Depends on: new symbolic execution frontend
  Local order: 3
  Requirements: Add Java IR-to-symbolic lowering, object and method-call semantics, loop limits, and solver-friendly constraint extraction.
  Why hard: object-oriented symbolic execution is a separate engine track

- [ ] `generate_unit_tests`
  Status: U
  Difficulty: very_high
  Target: runtime test generation parity
  Depends on: Java symbolic frontend plus test emitter
  Local order: 6
  Requirements: Add Java path extraction plus JUnit-style emitters, fixture corpus, and object-aware expectation generation.
  Why hard: Java needs both path generation and emitter work

- [ ] `type_evaporation_scan`
  Status: U
  Difficulty: medium_high
  Target: add new language support
  Depends on: TypeScript boundary extraction plus Python backend correlation plus schema generation
  Requirements: Define explicit support scope, add parser/runtime integration, add deterministic and parser-backed tests, and document unsupported cases conservatively.
  Why hard: the tool is intentionally narrow: TS/JS frontend to Python backend contract analysis

