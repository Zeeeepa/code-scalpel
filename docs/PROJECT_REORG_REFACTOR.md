# Project Reorganization & Refactoring Document

**Status:** In Progress (Phases 1-4 COMPLETE - Issues 1-5, 8-10, 19, 23, 32, Protocol Analyzers)  
**Last Updated:** December 25, 2025 (Phase 4 COMPLETE - governance_config, osv_client moved)  
**Document Version:** 2.6 (Phase 4 Complete)  
**Created:** December 24, 2025  
**Target Completion:** Post v3.0.5 (Phase 2 of V1.0 fork strategy)

---

## Document Organization Summary

This document has been comprehensively reorganized (v2.0) for proper alignment and consistency:

✅ **Consolidated Summary Tables** - Single comprehensive table covering all 31 issues with priority (P0-P4), tier impact, breaking changes, and cross-references

✅ **Added Dependency Graph** - Clear visualization of issue dependencies and execution order with critical path analysis identifying sequential vs. parallel opportunities

✅ **Standardized Headers** - Consistent format across all 31 issues showing Priority, Tier Impact, Status (KEEP/MOVE/SPLIT/CREATE/REMOVE), and Cross-References

✅ **Corrected Structure Errors** - Removed non-existent modules (code_parser/, parsers/, policy/) from documentation and updated folder count from "11" to actual "18 subdirectories"

✅ **Expanded Roadmap** - 6 comprehensive phases covering all 31 issues with dependency-ordered execution sequence, parallel opportunities identified, estimated 37-54 hours total effort

✅ **Enhanced Statistics** - Summary metrics: 11 breaking changes (35%), 15 modules kept in place (48%), 7 file moves (23%), 2 new modules (6%), 3 document corrections (10%), 1 rejected recommendation (Issue 11)

✅ **Phase Summary Table** - Week-by-week breakdown with effort estimates, dependencies, and critical path identification (Phase 1 → Phase 2 sequential → Phases 3+4 parallel → Phase 5 → Phase 6)

**Key Architectural Decisions:**
- **Issue 11 (Integration Consolidation): REJECTED** - integrations/, agents/, autonomy/ remain separate with distinct architectural concerns
- **Issues 24, 25, 26: APPROVED** - Three modules serve fundamentally different purposes and should not be consolidated
- **Issues 29-31: CORRECTED** - Non-existent modules removed from documentation (code_parser/, parsers/, policy/)
- **Issue 19 → 27: VALIDATED** - governance/ module ready for governance_config.py migration

**Next Steps:** Phase 4 COMPLETE. Begin Phase 5 implementation (documentation & cleanup) - estimated 2-3 hours

**✅ Phase 1 Completed (December 25, 2025):**
- Issue 1: quality_assurance/ created with error_scanner.py, error_fixer.py
- Issue 2: surgery/ created with surgical_extractor.py, surgical_patcher.py, unified_extractor.py
- Issue 3: analysis/ created with code_analyzer.py, project_crawler.py, core.py
- Issue 32: polyglot/ absorbed into code_parsers/ with typescript_parsers/ subdirectory
- All backward-compat aliases in place with deprecation warnings
- 4,431 tests passing

**✅ Phase 2 Completed (December 25, 2025):**
- Issue 4: licensing/ created with tier_detector.py, license_manager.py, validator.py, cache.py
- Issue 5: tiers/ created with decorators.py, feature_registry.py, tool_registry.py
- Issues 8-10: security/ populated with 6 subdirectories:
  - analyzers/ (security_analyzer.py, taint_tracker.py, unified_sink_detector.py, cross_file_taint.py)
  - type_safety/ (type_evaporation_detector.py)
  - dependencies/ (vulnerability_scanner.py)
  - sanitization/ (sanitizer_analyzer.py)
  - secrets/ (secret_scanner.py)
  - ml/ (ml_vulnerability_predictor.py)
- All backward-compat stubs in symbolic_execution_tools/ with deprecation warnings
- 4,431 tests passing

**✅ Phase 3 Completed (December 25, 2025):**
- Protocol analyzers split from symbolic_execution_tools/ to integrations/protocol_analyzers/:
  - graphql/ (schema_tracker.py - GraphQL schema tracking)
  - grpc/ (contract_analyzer.py - gRPC contract analysis)
  - kafka/ (taint_tracker.py - Kafka message taint tracking)
  - schema/ (drift_detector.py - Protocol buffer schema drift)
  - frontend/ (input_tracker.py - Frontend input tracking for React/Vue/Angular)
- All backward-compat stubs in symbolic_execution_tools/ with deprecation warnings
- 4,431 tests passing

**✅ Phase 4 Completed (December 25, 2025):**
- Issue 19: governance_config.py moved from config/ to governance/
- Issue 23: osv_client.py moved from ast_tools/ to security/dependencies/
- All backward-compat stubs in original locations with deprecation warnings
- 4,431 tests passing

---

## Executive Summary

Code Scalpel's source organization has organically grown as new capabilities were added. This document identifies structural improvements needed to support the three-tier product strategy (COMMUNITY/PRO/ENTERPRISE) and improve maintainability.

**Key Finding:** Several top-level modules should be reorganized into logical subdirectories, licensing infrastructure needs new location, and tier-aware feature separation requires architectural clarity.

**Latest Analysis (Issues 26-31):** Comprehensive gap analysis completed:
- **Issue 26 (integrations/):** Framework integration adapters confirmed as distinct from agents/autonomy. **CRITICAL:** Clarifies that Issue 11's original recommendation to consolidate modules should be REJECTED. integrations/, agents/, and autonomy/ serve three distinct architectural concerns.
- **Issue 27 (governance/):** Enterprise compliance infrastructure validated. Confirms governance/ is ready to receive governance_config.py per Issue 19 recommendation.
- **Issue 28 (generators/):** Code generation tools (test generation, refactor simulation) confirmed as cohesive module. Needs TODO expansion for refactor_simulator.py.
- **Issues 29-31 (code_parser/, parsers/, policy/):** Three non-existent modules identified in document. These are documentation errors and should be removed from structure listings.

**Previous Analysis (Issue 25):** Agents module analysis confirms it should remain as a standalone top-level module, NOT moved to integrations/. The module provides Code Scalpel's own specialized AI agent implementations built on the OODA loop pattern, which are distinct from framework integration adapters.

**Previous Analysis (Issue 24):** Autonomy module analysis confirms it should remain as a standalone top-level module, NOT moved to surgery/ or integrations/. The module provides supervised autonomous code repair with safety guarantees, which is architecturally distinct from direct code surgery operations.

**Previous Analysis (Issue 23):** AST Tools module analysis reveals one file (osv_client.py) should move to security/ module. All other 16 files are correctly placed.

---

## Current Source Structure Analysis

### Current Layout
```
src/code_scalpel/
├── Top-level modules (10 files):
│   ├── __init__.py
│   ├── py.typed
│   ├── cli.py (missing from analysis)
│   ├── code_analyzer.py
│   ├── core.py
│   ├── error_fixer.py
│   ├── error_scanner.py
│   ├── project_crawler.py
│   ├── surgical_extractor.py
│   ├── surgical_patcher.py
│   └── unified_extractor.py
│
├── Feature subdirectories (18 folders):
│   ├── ast_tools/
│   ├── pdg_tools/
│   ├── symbolic_execution_tools/
│   ├── polyglot/
│   ├── ir/
│   ├── security/
│   ├── policy_engine/
│   ├── governance/
│   ├── generators/
│   ├── cache/
│   ├── utilities/
│   ├── config/
│   ├── graph_engine/
│   ├── mcp/
│   ├── integrations/
│   ├── agents/
│   └── autonomy/
```

**Note:** Previous versions of this document incorrectly listed `polyglot/`, `parsers/`, and `policy/` directories. These modules do not exist in the codebase. Parsing functionality is consolidated in `code_parsers/`, and policy functionality is distributed between `policy_engine/` (enforcement) and `governance/` (compliance).

**Problem:** Top-level modules lack organizational grouping. Related functionality is scattered across hierarchy levels.

---

## Identified Reorganization Needs

### TIER 1: COMMUNITY (High Priority - Current Release)

#### Issue 1: Error Analysis Tools Need Dedicated Subdirectory
**Files:** `error_fixer.py`, `error_scanner.py`  
**Current Location:** Top-level (`src/code_scalpel/`)  
**Recommendation:** Move to `src/code_scalpel/quality_assurance/`

**Rationale:**
- Both files are quality-focused tools
- Should be grouped with linting, formatting, and code quality
- Reduces top-level clutter
- Enables future additions (linters, formatters, coverage tools)

**Proposed Structure:**
```
src/code_scalpel/quality_assurance/
├── __init__.py
├── error_scanner.py    # Error detection
├── error_fixer.py      # Error fixing
├── (future) formatter.py
├── (future) linter_integration.py
└── README.md
```

**Migration Steps:**
1. Create `src/code_scalpel/quality_assurance/` directory
2. Move `error_scanner.py` and `error_fixer.py`
3. Create `__init__.py` with appropriate exports
4. Update imports in `__init__.py` and `cli.py`
5. Update test paths in `tests/`
6. Update documentation references

**Breaking Changes:** Yes - imports change from `from code_scalpel.error_scanner` to `from code_scalpel.quality_assurance.error_scanner`

---

#### Issue 2: Code Extraction/Modification Tools Need Dedicated Subdirectory
**Files:** `surgical_extractor.py`, `surgical_patcher.py`, `unified_extractor.py`  
**Current Location:** Top-level (`src/code_scalpel/`)  
**Recommendation:** Move to `src/code_scalpel/surgery/`

**Rationale:**
- All three are surgical code extraction/modification tools
- Conceptually distinct from analysis
- Logical grouping for token-efficient LLM interactions
- Enables future surgical operations (insert, delete, refactor)

**Proposed Structure:**
```
src/code_scalpel/surgery/
├── __init__.py
├── extractor.py           # Unified extractor (rename from unified_extractor.py)
├── surgical_extractor.py  # Python-specific (legacy, for backward compat)
├── patcher.py             # Unified patcher (new wrapper)
├── surgical_patcher.py    # Python-specific implementation
├── constants.py           # Shared extraction/patching constants
├── exceptions.py          # Custom exceptions
└── README.md
```

**Migration Steps:**
1. Create `src/code_scalpel/surgery/` directory
2. Move extraction/patcher files
3. Create unified interface (`__init__.py`)
4. Add `constants.py` for shared configuration (e.g., DEFAULT_COMPLEXITY_THRESHOLD)
5. Update all imports across codebase
6. Update MCP tools to use new import paths
7. Update `surgical_extractor.py` and `surgical_patcher.py` module docstrings

**Breaking Changes:** Yes - imports change

---

#### Issue 3: Core Analysis Tools Need Reorganization
**Files:** `code_analyzer.py`, `project_crawler.py`, `core.py`  
**Current Location:** Top-level (`src/code_scalpel/`)  
**Recommendation:** Move to `src/code_scalpel/analysis/`

**Rationale:**
- `code_analyzer.py` and `project_crawler.py` are analysis-specific
- `core.py` is generic (PDGBuilder, etc.) but analysis-focused
- Clarifies distinction: `analysis/` (code inspection) vs `surgery/` (code modification)
- Aligns with architecture: Analysis → Security → Surgery pipeline

**Proposed Structure:**
```
src/code_scalpel/analysis/
├── __init__.py
├── code_analyzer.py       # Single-file analysis (keep naming)
├── project_crawler.py     # Project-wide analysis
├── core.py                # PDG building and utilities
├── metrics.py             # Shared metric calculations
├── complexity.py          # Cyclomatic, cognitive, Halstead metrics
└── README.md
```

**Migration Steps:**
1. Create `src/code_scalpel/analysis/` directory
2. Move `code_analyzer.py`, `project_crawler.py`, `core.py`
3. Extract metric calculations to `metrics.py` (eliminate duplication)
4. Update imports in `__init__.py`
5. Update CLI imports
6. Update test paths

**Breaking Changes:** Yes - imports change

---

### TIER 2: PRO (Medium Priority - Phase 2)

#### Issue 4: Licensing Infrastructure Missing Directory
**Files:** (To be created) `license_manager.py`, `validator.py`, `server_validator.py`, `license_server/`  
**Current Location:** Designed but not yet created  
**Recommendation:** Create `src/code_scalpel/licensing/`

**Rationale:**
- Licensing is tier-critical for PRO/ENTERPRISE
- Needs isolated, secure implementation
- Server validation separate from client validation
- Future: License portal, revocation, metering

**Proposed Structure:**
```
src/code_scalpel/licensing/
├── __init__.py
├── client/
│   ├── __init__.py
│   ├── license_manager.py    # Load CODE_SCALPEL_LICENSE_PATH
│   ├── validator.py          # Local HMAC verification
│   ├── cache.py              # License cache (24h grace)
│   └── exceptions.py         # LicenseError, ExpiredError, etc.
├── server/
│   ├── __init__.py
│   ├── server_validator.py   # Optional server for Enterprise
│   ├── models.py             # SQLite ORM models
│   ├── routes.py             # FastAPI endpoints
│   └── metering.py           # Usage tracking
└── README.md
```

**Migration Steps:**
1. Create `src/code_scalpel/licensing/` structure
2. Implement licensing system (Phase 1 of V1.0)
3. Wire into `__init__.py` tier detection
4. Add to MCP tool registry

**Breaking Changes:** No (new code)

---

#### Issue 5: Feature Gating Infrastructure Missing
**Files:** (To be created) `tier.py`, `decorators.py`, `feature_registry.py`  
**Current Location:** Designed but not created  
**Recommendation:** Create `src/code_scalpel/tiers/`

**Rationale:**
- Tier system is architectural, deserves its own module
- Feature gating decorators should be reusable
- Tool registry needs central location
- Tier configuration separate from licensing

**Proposed Structure:**
```
src/code_scalpel/tiers/
├── __init__.py
├── models.py              # Tier enum, TierConfig, constants
├── decorators.py          # @requires_tier() decorator
├── feature_registry.py    # Available features per tier
├── tool_registry.py       # MCP tools per tier
└── README.md
```

**Integration Points:**
- Licensing system validates license → returns tier
- Feature registry filters available tools
- Decorators guard PRO/ENTERPRISE-only code

**Breaking Changes:** No (new code)

---

### TIER 3: ENTERPRISE (Lower Priority - Phase 3)

#### Issue 6: CLI Needs Reorganization
**Files:** `cli.py` (assumed at `src/code_scalpel/cli.py`)  
**Current Location:** Likely top-level  
**Recommendation:** Move to `src/code_scalpel/cli/` (if grows beyond single file)

**Rationale:**
- If CLI grows significantly, subdir improves organization
- Can separate: `cli/main.py`, `cli/commands/`, `cli/config.py`
- Future: Language-specific CLI modules
- Tier-aware command availability

**Proposed Structure (Future):**
```
src/code_scalpel/cli/
├── __init__.py           # CLI entry point
├── main.py               # Click/argparse CLI group
├── commands/
│   ├── analyze.py        # analyze command
│   ├── extract.py        # extract command (PRO+)
│   ├── patch.py          # patch command (PRO+)
│   ├── scan.py           # scan command
│   ├── mcp.py            # mcp command (ENTERPRISE)
│   └── config.py         # config command (ENTERPRISE)
├── config.py             # CLI config loading
└── README.md
```

**Decision Point:** Only reorganize if single `cli.py` exceeds 500 lines (currently 755 lines based on summary)

---

#### Issue 7: Utilities Module Placement and Organization
**Files:** `path_resolution.py`  
**Current Location:** `src/code_scalpel/utilities/`  
**Recommendation:** KEEP in `utilities/` (cross-cutting utility, domain-agnostic)

**Rationale:**
- `path_resolution.py` provides generic file system utilities
- Used across multiple subsystems (analysis, surgery, integrations)
- Not specific to any single feature tier
- Cross-cutting concerns belong in utilities layer
- Consistent with established utilities pattern

**Current Structure (Appropriate):**
```
src/code_scalpel/utilities/
├── __init__.py
├── path_resolution.py    # File system path handling
├── cache.py              # (if cache utilities split off)
└── README.md
```

**Future Expansion (Optional - Phase 2+):**
```
src/code_scalpel/utilities/
├── __init__.py
├── path_resolution.py    # File system utilities
├── file_operations.py    # File I/O utilities (if needed)
├── decorators.py         # Reusable decorators
├── logging_config.py     # Logging utilities
├── metrics.py            # Metric calculation utilities
└── README.md
```

**Decision Point:** Keep utilities as generic shared code repository. No reorganization needed.

**Note:** Cache utilities currently in `cache/` directory; consider whether `cache/unified_cache.py` utilities should have helper functions in `utilities/` (Phase 2 cleanup).

---

#### Issue 8: Symbolic Execution Tools Need Subdivision and Reorganization
**Current Location:** `src/code_scalpel/symbolic_execution_tools/` (24 files)  
**Issue:** Module mixes core symbolic execution infrastructure with security analysis tools  
**Recommendation:** Split into focused subdirectories per functionality

**Current State Analysis:**
The symbolic_execution_tools/ directory contains three distinct categories of tools:

1. **Core Symbolic Execution Engine (9 files)** - Should stay:
   - `engine.py` - Main symbolic execution engine
   - `concolic_engine.py` - Concolic execution variant
   - `constraint_solver.py` - Z3 constraint solving
   - `state_manager.py` - Symbolic state management
   - `symbolic_memory.py` - Memory model for symbolic execution
   - `ir_interpreter.py` - IR interpretation
   - `path_prioritization.py` - Path exploration strategy
   - `type_inference.py` - Type inference for symbolic values
   - `__init__.py`

2. **Security Analysis Tools (7 files)** - Should move to `security/`:
   - `security_analyzer.py` - Vulnerability detection
   - `taint_tracker.py` - Taint analysis
   - `unified_sink_detector.py` - Security sink detection
   - `vulnerability_scanner.py` - Dependency vulnerability scanning
   - `sanitizer_analyzer.py` - Sanitizer effectiveness analysis
   - `secret_scanner.py` - Hardcoded secret detection
   - `cross_file_taint.py` - Cross-file taint flow analysis

3. **Type Safety Analysis (2 files)** - Should move to `security/`:
   - `type_evaporation_detector.py` - TypeScript type boundary vulnerabilities
   - (type_inference.py - keep in core, used by engine)

4. **Framework/Protocol-Specific Analyzers (5 files)** - Should move to `integrations/` or `protocol_analyzers/`:
   - `graphql_schema_tracker.py` - GraphQL schema analysis
   - `grpc_contract_analyzer.py` - gRPC contract analysis
   - `kafka_taint_tracker.py` - Kafka message taint tracking
   - `schema_drift_detector.py` - API schema drift detection
   - `frontend_input_tracker.py` - Frontend input tracking

5. **ML-Based Analysis (1 file)** - Could move to `security/` or new `ml/`:
   - `ml_vulnerability_predictor.py` - ML-based vulnerability prediction

**Proposed Reorganization:**

```
src/code_scalpel/symbolic_execution_tools/
├── __init__.py (exports core engine only)
├── engine.py
├── concolic_engine.py
├── constraint_solver.py
├── state_manager.py
├── symbolic_memory.py
├── ir_interpreter.py
├── path_prioritization.py
├── type_inference.py
└── README.md (focused on symbolic execution)

src/code_scalpel/security/
├── __init__.py
├── analyzers/
│   ├── __init__.py
│   ├── security_analyzer.py
│   ├── taint_tracker.py
│   ├── unified_sink_detector.py
│   └── README.md
├── type_safety/
│   ├── __init__.py
│   ├── type_evaporation_detector.py
│   └── README.md
├── dependencies/
│   ├── __init__.py
│   ├── vulnerability_scanner.py
│   └── README.md
├── sanitization/
│   ├── __init__.py
│   ├── sanitizer_analyzer.py
│   └── README.md
├── secrets/
│   ├── __init__.py
│   ├── secret_scanner.py
│   └── README.md
├── ml/
│   ├── __init__.py
│   ├── ml_vulnerability_predictor.py
│   └── README.md
└── README.md (overall security module)

src/code_scalpel/integrations/protocol_analyzers/
├── __init__.py
├── graphql/
│   ├── __init__.py
│   ├── schema_tracker.py (renamed from graphql_schema_tracker.py)
│   └── README.md
├── grpc/
│   ├── __init__.py
│   ├── contract_analyzer.py (renamed from grpc_contract_analyzer.py)
│   └── README.md
├── kafka/
│   ├── __init__.py
│   ├── taint_tracker.py (renamed from kafka_taint_tracker.py)
│   └── README.md
├── schema/
│   ├── __init__.py
│   ├── drift_detector.py (renamed from schema_drift_detector.py)
│   └── README.md
├── frontend/
│   ├── __init__.py
│   ├── input_tracker.py (renamed from frontend_input_tracker.py)
│   └── README.md
└── README.md
```

**Rationale:**
1. **Clarity:** Separates core engine from analysis tools
2. **Maintainability:** Security tools grouped by concern (analyzers, type safety, dependencies, secrets, ML)
3. **Feature Gating:** Security tools can be PRO/ENTERPRISE; core engine is COMMUNITY
4. **Framework Integration:** Protocol-specific tools organized by framework
5. **Cross-File Taint:** Move to `security/` as cross-cutting security concern

**Migration Steps:**
1. Create new subdirectories in `security/` and `integrations/protocol_analyzers/`
2. Move security analysis tools to `security/analyzers/`
3. Move type safety tools to `security/type_safety/`
4. Move protocol-specific analyzers to `integrations/protocol_analyzers/{protocol}/`
5. Move `cross_file_taint.py` to `security/analyzers/`
6. Update `symbolic_execution_tools/__init__.py` to export only core engine
7. Create new `__init__.py` files in all new subdirectories
8. Update all imports across codebase (core imports from symbolic_execution_tools, security imports from security/)
9. Update MCP tool registry to reflect new locations
10. Create README.md for each new subdirectory

**Breaking Changes:** Yes - imports change significantly

**Tier Implications:**
- Core symbolic execution (COMMUNITY): `symbolic_execution_tools/`
- Security analysis (PRO/ENTERPRISE): `security/` with tier gating
- Protocol analyzers (PRO/ENTERPRISE): `integrations/protocol_analyzers/`

---

#### Issue 9: Security Module Exists But Needs Population
**Current Location:** `src/code_scalpel/security/`  
**Current State:** Folder exists with only README files (README.md, README_DEVELOPER_GUIDE.md)  
**Issue:** Security folder is a placeholder; actual security tools are still in symbolic_execution_tools/  
**Recommendation:** Use existing security/ folder structure, populate with tools from symbolic_execution_tools/

**Current Structure:**
```
src/code_scalpel/security/
├── README.md                    # High-level security module guide
├── README_DEVELOPER_GUIDE.md    # Developer documentation
└── (no subdirectories yet)
```

**Rationale:**
- Security folder already exists as intended destination
- Good architectural decision to have it ready
- Needs to be populated with security analysis tools in Phase 2
- Existing README files provide guidance for structure and implementation
- No reorganization needed for security/ itself; just needs tool migration from symbolic_execution_tools/

**Next Steps (Phase 2):**
1. Review existing README.md and README_DEVELOPER_GUIDE.md for architectural guidance
2. Create subdirectories: analyzers/, type_safety/, dependencies/, sanitization/, secrets/, ml/
3. Move tools from symbolic_execution_tools/ according to reorganization plan
4. Update README files to document new structure
5. Wire into tier system and MCP registry

**Decision Point:** Verify existing security/ README files align with proposed subdirectory structure. If not, update them to guide Phase 2 implementation.

---

#### Issue 10: Polyglot Module Analysis and Reorganization
**Files in polyglot/:** `alias_resolver.py`, `contract_breach_detector.py`, `extractor.py`, `tsx_analyzer.py`, and `typescript/` subdirectory  
**Current Location:** `src/code_scalpel/polyglot/`  
**Issue:** Some polyglot files are framework/library-specific while others are language-agnostic  
**Recommendation:** Consolidate core extraction in polyglot; move specialized analyzers to appropriate locations

**Current State Analysis:**

The polyglot module contains:
1. **Core Multi-Language Extraction (3 files)** - Should STAY in polyglot:
   - `extractor.py` - Multi-language code extraction (core)
   - `alias_resolver.py` - Module alias resolution (tsconfig.json, webpack, vite)
   - `typescript/` - TypeScript/JavaScript parser and analysis

2. **Contract Analysis (1 file)** - Should move to security:
   - `contract_breach_detector.py` - Cross-language API contract violation detection

3. **Framework-Specific Analysis (1 file)** - Could move to integrations:
   - `tsx_analyzer.py` - React/TSX component detection (framework-specific, PRO feature)

**Proposed Reorganization:**

Option 1 (Recommended for Phase 2):
```
src/code_scalpel/polyglot/
├── __init__.py
├── extractor.py              # Multi-language extraction (STAY)
├── alias_resolver.py         # Import alias resolution (STAY)
├── typescript/
│   ├── __init__.py
│   ├── parser.py             # TypeScript parser (STAY)
│   ├── analyzer.py           # TypeScript analysis (STAY)
│   ├── decorator_analyzer.py # TypeScript decorators (STAY)
│   ├── type_narrowing.py     # Type narrowing analysis (STAY)
│   └── README.md
└── README.md

src/code_scalpel/security/
├── cross_language/
│   ├── __init__.py
│   ├── contract_breach_detector.py  # (MOVE from polyglot/)
│   └── README.md

src/code_scalpel/integrations/frameworks/
├── react/
│   ├── __init__.py
│   ├── tsx_analyzer.py       # (MOVE from polyglot/)
│   └── README.md
```

**Rationale:**
1. **Keep in polyglot:** Core extraction and language support are fundamental to polyglot functionality
2. **Move contract_breach_detector to security:** Contract violation detection is a security/compatibility concern, not core extraction
3. **Move tsx_analyzer to integrations:** React/TSX analysis is framework-specific, belongs with other framework integrations (PRO/ENTERPRISE)

**Migration Steps:**
1. Create `src/code_scalpel/security/cross_language/` directory
2. Move `contract_breach_detector.py` to `security/cross_language/`
3. Create `src/code_scalpel/integrations/frameworks/react/` directory
4. Move `tsx_analyzer.py` to `integrations/frameworks/react/`
5. Update imports in `polyglot/__init__.py`
6. Update security module `__init__.py` to export cross_language tools
7. Update integrations module to include react framework directory
8. Update MCP tool registry

**Breaking Changes:** Yes - imports change for contract_breach_detector and tsx_analyzer

**Tier Implications:**
- Core polyglot extraction (COMMUNITY): `polyglot/`
- Cross-language security analysis (PRO/ENTERPRISE): `security/cross_language/`
- Framework-specific analysis (PRO/ENTERPRISE): `integrations/frameworks/react/`

**Decision Point:** Should tsx_analyzer stay in polyglot for COMMUNITY tier or move to integrations/frameworks/react for PRO tier feature gating?

---

#### Issue 11: Integration Layer Needs Reorganization (**REJECTED - See Issues 24, 25, 26**)
**Files:** Integrations split across `integrations/`, `agents/`, `autonomy/`  
**Current Location:** Three separate directories  
**Original Recommendation:** Partial consolidation  
**UPDATED RECOMMENDATION:** ❌ **REJECT consolidation - Keep all three modules separate**

**Original Rationale (Now Rejected):**
- `agents/`, `autonomy/`, `integrations/` are all integration-related
- Current split is unclear (what's the difference?)
- ENTERPRISE feature that can be organized together
- Easier maintenance for integrations team

**Comprehensive Analysis (Issues 24, 25, 26) - RECOMMENDATION REJECTED:**

After thorough analysis of all three modules, the original recommendation to consolidate is **REJECTED**. The three modules serve **distinct architectural concerns** and should remain separate:

**Issue 26 (integrations/) - Framework Integration Adapters:**
- **Purpose:** External framework adapters (how other frameworks USE Code Scalpel)
- **Contents:** AutoGen, CrewAI, LangChain, Claude adapters + REST API server
- **Scope:** Wrappers around Code Scalpel for external consumption
- **Tier:** COMMUNITY (base adapters), PRO (advanced features), ENTERPRISE (multi-tenancy)

**Issue 25 (agents/) - Internal Agent Implementations:**
- **Purpose:** Code Scalpel's own AI agent implementations (OODA loop pattern)
- **Contents:** CodeReviewAgent, SecurityAgent, OptimizationAgent, etc.
- **Scope:** Internal tooling built on Code Scalpel's analysis capabilities
- **Tier:** COMMUNITY (base agents), PRO (advanced agents), ENTERPRISE (federation)

**Issue 24 (autonomy/) - Supervised Autonomous Repair:**
- **Purpose:** Supervised autonomous code repair with safety guarantees
- **Contents:** Error-to-diff engine, fix loops, mutation gates, sandboxing
- **Scope:** Autonomous repair workflows with error budgets and rollback
- **Tier:** ENTERPRISE-focused (safety-critical autonomous operations)

**Three Distinct Concerns:**

```
integrations/     # "How external frameworks use Code Scalpel"
                 # Example: AutoGen framework calls Code Scalpel tools via adapter
                 
agents/           # "Code Scalpel's own AI agents"
                 # Example: CodeReviewAgent uses Code Scalpel to review code
                 
autonomy/         # "Supervised autonomous repair"
                 # Example: Error-to-diff engine auto-fixes bugs with safety gates
```

**Why Consolidation Would Be Wrong:**

1. **Blurs architectural boundaries** - Three modules serve fundamentally different purposes
2. **Confuses consumers** - Users need Code Scalpel agents (agents/), framework adapters (integrations/), or autonomous repair (autonomy/) for different use cases
3. **Complicates maintenance** - Mixing external adapters, internal tools, and autonomous systems in one module creates cognitive overhead
4. **Violates separation of concerns** - External integration ≠ Internal agent ≠ Autonomous repair

**Relationship Between Modules:**

```
User/Framework
    │
    ├── Uses integrations/ to call Code Scalpel from AutoGen/CrewAI/etc.
    ├── Uses agents/ to leverage Code Scalpel's built-in AI agents
    └── Uses autonomy/ for supervised autonomous repair workflows
```

**rest_api_server.py Deprecation (Correct):**
- Current location: `integrations/rest_api_server.py`
- Status: Legacy, non-MCP-compliant HTTP API
- Recommendation: ✅ Mark as deprecated, favor `mcp/` (true MCP protocol)
- Action: Deprecation can happen in-place with warnings, no file movement needed

**Updated Proposed Structure (No Changes - All Stay in Place):**

```
src/code_scalpel/
├── integrations/             # Framework integration adapters (KEEP)
│   ├── __init__.py
│   ├── autogen.py           # AutoGen adapter
│   ├── crewai.py            # CrewAI adapter
│   ├── langchain.py         # LangChain adapter
│   ├── claude.py            # Claude adapter
│   ├── rest_api_server.py   # (Deprecated - favor mcp/)
│   └── README.md
│
├── agents/                   # Internal agent implementations (KEEP)
│   ├── __init__.py
│   ├── base_agent.py        # OODA loop framework
│   ├── code_review_agent.py # Code review agent
│   ├── security_agent.py    # Security analysis agent
│   ├── optimization_agent.py # (Fixed typo from optimazation_agent.py)
│   └── README.md
│
└── autonomy/                 # Supervised autonomous repair (KEEP)
    ├── __init__.py
    ├── engine.py            # Autonomous repair engine
    ├── fix_loop.py          # Fix loop implementation
    ├── error_to_diff.py     # Error-to-diff converter
    ├── mutation_gate.py     # Safety gate
    ├── sandbox.py           # Sandboxed execution
    └── integrations/        # Autonomy-specific framework integrations
        ├── autogen.py       # AutoGen fix loop workflows
        ├── crewai.py        # CrewAI fix loop workflows
        └── langgraph.py     # LangGraph fix loop state machines
```
**Migration Steps:**
1. ✅ **NO MIGRATION REQUIRED** - All modules stay in place
2. Mark rest_api_server.py as deprecated (favor mcp/)
3. Add deprecation warnings to rest_api_server.py
4. Update documentation to clarify architectural boundaries:
   - integrations/ = External framework adapters
   - agents/ = Internal agent implementations
   - autonomy/ = Supervised autonomous repair
5. Document REST API deprecation timeline

**Breaking Changes:** None - All modules stay in current locations

**Decision Point (RESOLVED):** ❌ **REJECT consolidation** - Issues 24, 25, 26 confirm all three modules should remain separate with clear architectural boundaries.

**Summary:**
- ❌ Original recommendation to consolidate is **REJECTED**
- ✅ Keep integrations/, agents/, autonomy/ as separate top-level modules
- ✅ Deprecate rest_api_server.py in favor of mcp/
- ✅ Document architectural boundaries clearly

---

#### Issue 13: PDG Tools Module Analysis and Reorganization
**Files in pdg_tools/:** `__init__.py`, `builder.py`, `analyzer.py`, `slicer.py`, `transformer.py`, `utils.py`, `visualizer.py`, `README.md`  
**Current Location:** `src/code_scalpel/pdg_tools/`  
**Issue:** Determine if PDG module components are appropriately grouped or if any should be moved  
**Recommendation:** KEEP pdg_tools together - cohesive module, no reorganization needed

**Current State Analysis:**

The pdg_tools module is a cohesive set of interdependent analysis and transformation tools:

1. **Core PDG Infrastructure (4 files)** - STAY:
   - `builder.py` - Constructs PDG from AST, computes control/data dependencies
   - `analyzer.py` - Analyzes PDG for anomalies, vulnerabilities, and data flow
   - `slicer.py` - Performs program slicing on PDG (backward/forward)
   - `transformer.py` - Applies correctness-preserving transformations to PDG

2. **Support Files (3 files)** - STAY:
   - `utils.py` - PDG-specific utilities (serialization, diffing, statistics)
   - `visualizer.py` - PDG visualization (Graphviz, interactive UI)
   - `__init__.py` - Module exports and public API

3. **Documentation (1 file)**:
   - `README.md` - Module documentation

**Architectural Rationale:**

1. **Tight Coupling:** All components depend on each other:
   - `analyzer` and `slicer` depend on PDGs built by `builder`
   - `transformer` modifies PDGs analyzed by `analyzer`
   - `visualizer` displays PDGs from any component
   - `utils` supports all other modules

2. **Specialized Domain:** PDG operations are distinct from:
   - General security analysis (belongs in `security/`)
   - Code surgery (belongs in `surgery/`)
   - General utilities (belongs in `utilities/`)

3. **Tier Alignment:**
   - Core builder/analyzer/slicer: COMMUNITY (fundamental analysis)
   - Advanced features (distributed, polyglot): PRO/ENTERPRISE
   - All tiers use the same core PDG infrastructure

4. **Not Cross-Cutting:** Unlike `utilities/path_resolution.py`:
   - PDG tools are specific to PDG operations
   - Not used by unrelated modules
   - Should stay together as a unit

5. **Feature Gating:** PDG tools support tier features at the capability level (e.g., distributed PDG is ENTERPRISE), not at the file level

**Proposed Structure (Current is Optimal):**

```
src/code_scalpel/pdg_tools/
├── __init__.py              # Module exports
├── builder.py               # PDG construction (STAY)
├── analyzer.py              # PDG analysis (STAY)
├── slicer.py                # Program slicing (STAY)
├── transformer.py           # PDG transformation (STAY)
├── utils.py                 # PDG utilities (STAY)
├── visualizer.py            # PDG visualization (STAY)
├── README.md                # Documentation
└── (no subdirectories needed - cohesive module)
```

**Considerations for Phase 2+:**

If PDG tools expand significantly (>7,000 LOC total), could consider optional structure:
- Keep all files at top level (current - recommended)
- OR split by concern (only if 50%+ growth):
  - `analysis/` - analyzer, transformer subfolder
  - `visualization/` - visualizer subfolder
  - Core in pdg_tools root

**Decision Point:** None - keep pdg_tools as cohesive module. No reorganization needed.

**Tier Implications:**
- All PDG operations (COMMUNITY core)
- Advanced features (PRO/ENTERPRISE) gated at feature level, not file level

---

#### Issue 14: MCP Module Analysis and Reorganization
**Files in mcp/:** `__init__.py`, `server.py`, `contract.py`, `logging.py`, `module_resolver.py`, `path_resolver.py`, `README.md`  
**Current Location:** `src/code_scalpel/mcp/`  
**Issue:** Determine if MCP module components are appropriately grouped or if any should be moved to general utilities/integrations  
**Recommendation:** KEEP mcp together - cohesive MCP integration module, no reorganization needed

**Current State Analysis:**

The MCP module is a cohesive set of interdependent MCP server implementation tools:

1. **Core MCP Server Infrastructure (2 files)** - STAY:
   - `server.py` - FastMCP server implementation, tool registration, transport handling
   - `__init__.py` - Module exports and initialization

2. **MCP Protocol Contract (1 file)** - STAY:
   - `contract.py` - Universal response envelope, error codes, machine-parseable contracts

3. **MCP-Specific Support Tools (3 files)** - STAY:
   - `logging.py` - Structured MCP logging with metrics and analytics
   - `module_resolver.py` - Maps language module names to file paths for code:/// URI support
   - `path_resolver.py` - Intelligent path resolution across Docker/WSL/Windows/local environments

4. **Documentation (1 file)** - STAY:
   - `README.md` - MCP module documentation

**Architectural Rationale:**

1. **MCP-Specific Domain:** All files are tightly integrated with MCP operations:
   - Server implementation depends on contract definitions
   - Logging tracks MCP tool invocations specifically
   - Module/path resolvers support code:/// URI resource templates for MCP
   - Not general-purpose utilities (too MCP-specific)

2. **Not Duplicate Utilities:** Despite similar names:
   - `path_resolver.py` in MCP is Docker/deployment-specific for MCP servers (not same as `utilities/path_resolution.py`)
   - `module_resolver.py` is for code:/// URIs (polyglot module access) - specific to MCP features
   - Both are MCP protocol concerns, not generic file system utilities

3. **Tight Coupling:** All components work together:
   - Server invokes tools and uses logging
   - Module/path resolvers support tool I/O
   - Contract defines response format for all tools
   - Cannot function independently

4. **Isolation from Other Modules:** Unlike shared utilities:
   - MCP tools are not imported by security analysis, PDG tools, or other modules
   - MCP is an integration layer (inbound connection), not a foundation layer
   - Pure MCP concern with clear boundaries

5. **Feature Gating:** MCP tools support tier features at capability level:
   - Core server: COMMUNITY (20 MCP tools)
   - Advanced features (HTTP, auth, monitoring): PRO
   - Distributed, federated, OpenTelemetry: ENTERPRISE
   - All tiers use same core MCP infrastructure

6. **Consistent with Similar Modules:**
   - Like `pdg_tools/` (cohesive), `policy_engine/` (cohesive), `polyglot/` (cohesive)
   - Unlike scattered utilities in `utilities/`

**Proposed Structure (Current is Optimal):**

```
src/code_scalpel/mcp/
├── __init__.py              # Module exports
├── server.py                # FastMCP server (STAY)
├── contract.py              # Response envelopes (STAY)
├── logging.py               # MCP metrics (STAY)
├── module_resolver.py       # Module resolution for URIs (STAY)
├── path_resolver.py         # Path resolution for deployment (STAY)
├── README.md                # Documentation
└── (no subdirectories needed - cohesive module)
```

**Considerations for Phase 2+:**

If MCP tools expand significantly (>10,000 LOC total across all 6 files), could consider optional structure:
- Keep all files at top level (current - recommended)
- OR split by concern (only if 50%+ growth):
  - `transports/` - HTTP, gRPC, WebSocket transport implementations
  - `auth/` - Authentication and authorization for MCP
  - `tools/` - Tool-specific implementations
  - Core (server, contract, logging, resolvers) in mcp root

**Decision Point:** None - keep mcp as cohesive module. No reorganization needed.

**Tier Implications:**
- Core MCP server (COMMUNITY): stdio transport, 20 tools, basic logging
- Enhanced MCP (PRO): HTTP transport, auth, tier gating, metrics, request queuing
- Advanced MCP (ENTERPRISE): Distributed, federated, multi-protocol, OpenTelemetry, AI optimization

---

#### Issue 12: Policy Engine Module Analysis and Reorganization
**Files in policy_engine/:** `__init__.py`, `audit_log.py`, `crypto_verify.py`, `exceptions.py`, `models.py`, `policy_engine.py`, `semantic_analyzer.py`, `tamper_resistance.py`  
**Current Location:** `src/code_scalpel/policy_engine/`  
**Issue:** Semantic analyzer provides security pattern detection that could be shared with general security analysis  
**Recommendation:** Keep core policy governance in policy_engine; move semantic_analyzer to security for cross-module reuse

**Current State Analysis:**

The policy_engine module contains policy governance infrastructure plus security pattern detection:

1. **Core Policy Governance (7 files)** - Should STAY in policy_engine:
   - `policy_engine.py` - Main policy evaluation engine
   - `__init__.py` - Module exports
   - `audit_log.py` - Audit trail for policy decisions
   - `crypto_verify.py` - HMAC/cryptographic verification
   - `exceptions.py` - Policy-specific exceptions
   - `models.py` - Policy data models
   - `tamper_resistance.py` - File integrity and override protection

2. **Security Pattern Detection (1 file)** - Should move to security:
   - `semantic_analyzer.py` - SQL injection, XSS, command injection, LDAP injection, NoSQL injection detection

**Proposed Reorganization:**

```
src/code_scalpel/policy_engine/
├── __init__.py              # Policy engine exports
├── audit_log.py             # Audit trail (STAY)
├── crypto_verify.py         # Cryptographic verification (STAY)
├── exceptions.py            # Policy exceptions (STAY)
├── models.py                # Data models (STAY)
├── policy_engine.py         # Core engine (STAY)
├── tamper_resistance.py     # File integrity (STAY)
└── README.md

src/code_scalpel/security/analyzers/
├── __init__.py
├── security_analyzer.py     # General security analysis
├── semantic_analyzer.py     # (MOVE from policy_engine/)
├── taint_tracker.py         # Taint flow analysis
├── unified_sink_detector.py # Dangerous sinks detection
├── sanitizer_analyzer.py    # Sanitizer detection
├── secret_scanner.py        # Secret/credential detection
└── README.md
```

**Rationale:**
1. **Separation of Concerns:** Policy governance (COMMUNITY) vs. security pattern detection (PRO/ENTERPRISE)
2. **Code Reuse:** Semantic analyzer patterns can be used by other security modules, not just policy engine
3. **Architectural Clarity:** Policy engine focuses on policy evaluation and enforcement; security patterns are detection tools
4. **Tier Alignment:** 
   - Policy governance COMMUNITY (all policy engine files except semantic_analyzer)
   - Security patterns PRO/ENTERPRISE (semantic_analyzer with security/analyzers)
5. **Future Extensibility:** Other modules can import semantic patterns independently

**Migration Steps:**
1. Identify semantic_analyzer usage in policy_engine.py
2. Create import bridge: `from code_scalpel.security.analyzers import SemanticAnalyzer`
3. Move `semantic_analyzer.py` to `security/analyzers/`
4. Update `policy_engine/__init__.py` to import from new location if needed
5. Update `security/analyzers/__init__.py` to export `SemanticAnalyzer`
6. Update any direct imports of `policy_engine.semantic_analyzer`
7. Update documentation and READMEs
8. Run tests to verify cross-module dependencies work

**Breaking Changes:** Minimal if semantic_analyzer is used only internally within policy_engine. Potentially breaking if external code imports from policy_engine directly.

**Tier Implications:**
- Policy governance (COMMUNITY): `policy_engine/` - Core policy evaluation
- Security patterns (PRO/ENTERPRISE): `security/analyzers/` - Pattern-based vulnerability detection

**Decision Point:** Should semantic_analyzer move to security/analyzers for code reuse across security modules?

---

#### Issue 15: Normalizers Module Analysis and Reorganization
**Files in normalizers/:** `__init__.py`, `base.py`, `python_normalizer.py`, `java_normalizer.py`, `javascript_normalizer.py`, `typescript_normalizer.py`, `tree_sitter_visitor.py`  
**Current Location:** `src/code_scalpel/ir/normalizers/`  
**Issue:** Should normalizers module remain cohesive or split by language?  
**Recommendation:** Keep normalizers as cohesive module - tightly coupled, shared interface, unified IR output

**Current State Analysis:**

The normalizers module converts language-specific AST/CST to Unified IR across polyglot languages:

1. **Architecture:**
   - `base.py` - Abstract `BaseNormalizer` interface for all normalizers
   - `tree_sitter_visitor.py` - Base class for tree-sitter based visitors (generic AST traversal)
   - Language-specific normalizers:
     - `python_normalizer.py` - Python AST (ast module) to IR normalization
     - `java_normalizer.py` - Java CST (tree-sitter-java) to IR normalization
     - `javascript_normalizer.py` - JavaScript CST (tree-sitter-javascript) to IR normalization
     - `typescript_normalizer.py` - TypeScript CST (tree-sitter-typescript) to IR normalization
   - `__init__.py` - Module exports and normalizer factory function

2. **Dependencies (Cohesion Analysis):**
   - All normalizers inherit from `BaseNormalizer` (base.py)
   - Tree-sitter normalizers inherit from `VisitorContext` (tree_sitter_visitor.py)
   - Each normalizer is independent implementation but follows shared interface
   - `__init__.py` provides factory function to select normalizer by language
   - No cross-normalizer dependencies (python_normalizer doesn't call java_normalizer, etc.)

3. **Polyglot Context:**
   - Normalizers are called by polyglot/extractor to convert ASTs to Unified IR
   - Unified IR is consumed by downstream analysis (symbolic execution, security analysis, PDG building)
   - Currently in `ir/` directory (appropriate - part of IR infrastructure)
   - Not in `polyglot/` (normalizers are IR-specific, not general polyglot extraction)

**Proposed Reorganization: KEEP COHESIVE**

```
src/code_scalpel/ir/normalizers/
├── __init__.py                    # Factory and exports (KEEP)
├── base.py                        # Base normalizer interface (KEEP)
├── tree_sitter_visitor.py         # Base visitor (KEEP)
├── python_normalizer.py           # Python AST→IR (KEEP)
├── java_normalizer.py             # Java CST→IR (KEEP)
├── javascript_normalizer.py       # JavaScript CST→IR (KEEP)
├── typescript_normalizer.py       # TypeScript CST→IR (KEEP)
└── README.md

# NOT splitting into language-specific subdirectories
# NOT moving to polyglot/
# NOT splitting base classes to utilities/
```

**Rationale for KEEP Decision:**

1. **Tightly Coupled Interface:** All normalizers share `BaseNormalizer` interface. Cannot split without duplicating interface.
2. **Shared Visitor Base:** Tree-sitter normalizers share `VisitorContext` base. Splitting would require moving this to shared location.
3. **Factory Pattern:** `__init__.py` factory function selects normalizer by language. Requires all normalizers in one module.
4. **Single Responsibility:** Module has one clear job: convert language AST/CST to Unified IR.
5. **Cohesive Domain:** Normalizers are IR infrastructure, not polyglot utilities. Belong in ir/, not polyglot/.
6. **Independent Implementations:** Each normalizer is independent (no python_normalizer calls java_normalizer). Can extend without affecting others.
7. **Balanced Module Size:** 7 files, ~1,500 LOC total (appropriate size for cohesive module).

**Comparison with Similar Modules:**

| Module | Structure | Decision | Reason |
|--------|-----------|----------|--------|
| `pdg_tools/` | builder, analyzer, slicer, transformer, utils, visualizer (7 files) | KEEP | Tightly coupled PDG operations, shared data structures |
| `polyglot/` | extractor, alias_resolver, typescript/ (core extraction) | KEEP | Core multi-language extraction, shared patterns |
| `mcp/` | server, contract, logging, module_resolver, path_resolver, __init__ (6 files) | KEEP | Cohesive MCP protocol integration |
| `normalizers/` | base, tree_sitter_visitor, python, java, js, ts, __init__ (7 files) | KEEP | Cohesive IR normalization, shared interface |

**Not a Candidate for Splitting:**

- **NOT into polyglot/** - Normalizers convert AST→IR, not extraction (extraction is polyglot's job)
- **NOT into language-specific dirs** - Would require duplicating `base.py` and `tree_sitter_visitor.py`
- **NOT into utilities/** - Normalizers are IR-specific, not general utilities
- **NOT split by tree-sitter vs Python AST** - Would obscure domain (IR normalization)

**Tier Implications:**
- All normalizers (COMMUNITY): Core IR normalization infrastructure
- No tier-specific normalizers (all languages normalized the same way)
- Future tier features: Normalizer caching (PRO), distributed normalization (ENTERPRISE), ML optimization (ENTERPRISE)

**Breaking Changes:** None - no reorganization planned

**Decision Point:** Keep normalizers module cohesive in ir/normalizers/

---

#### Issue 16: IR Module Analysis and Reorganization
**Files in ir/:** `__init__.py`, `nodes.py`, `operators.py`, `semantics.py`, `README.md`, `normalizers/` (subdirectory)  
**Current Location:** `src/code_scalpel/ir/`  
**Issue:** Should IR module remain cohesive or split into logical submodules?  
**Recommendation:** Keep IR as cohesive module - foundational infrastructure with clear purpose

**Current State Analysis:**

The IR (Intermediate Representation) module provides language-agnostic code representation:

1. **Core IR Infrastructure (5 files):**
   - `__init__.py` - Module exports and utility functions
   - `nodes.py` - IR node definitions (IRModule, IRFunctionDef, IRCall, etc.)
   - `operators.py` - Operator enums (BinaryOperator, CompareOperator, etc.)
   - `semantics.py` - Language-specific behavioral semantics
   - `README.md` - Module documentation

2. **Subdirectory (Cohesive):**
   - `normalizers/` - Language-specific normalizers (Python, Java, JS, TS)

3. **Dependencies (Cohesion Analysis):**
   - All normalizers depend on nodes.py (IRNode base classes)
   - operators.py used by both nodes.py and semantics.py
   - semantics.py interprets IR nodes with language-specific behavior
   - __init__.py exports unified public API
   - normalizers/ converts language AST/CST → IR nodes
   - No circular dependencies between submodules

4. **Role in Architecture:**
   - Foundation layer: AST/CST → IR conversion
   - Used by: polyglot, pdg_tools, symbolic_execution_tools, security modules
   - Provides unified structure for multi-language analysis
   - Separates STRUCTURE (nodes, operators) from BEHAVIOR (semantics)

**Proposed Reorganization: KEEP COHESIVE**

```
src/code_scalpel/ir/
├── __init__.py                    # Module exports and utilities (KEEP)
├── nodes.py                       # IR node definitions (KEEP)
├── operators.py                   # Operator enums (KEEP)
├── semantics.py                   # Language semantics (KEEP)
├── README.md                       # Module documentation (KEEP)
└── normalizers/                   # Language-specific normalizers (KEEP)
    ├── __init__.py
    ├── base.py
    ├── python_normalizer.py
    ├── java_normalizer.py
    ├── javascript_normalizer.py
    ├── typescript_normalizer.py
    ├── tree_sitter_visitor.py
    └── README.md

# NOT splitting into submodules like ir/core/, ir/schema/, ir/types/
# NOT moving semantics.py to language-specific directories
# NOT scattering IR concerns across other modules
```

**Rationale for KEEP Decision:**

1. **Single Responsibility:** IR module has one clear domain - provide language-agnostic code representation
2. **Foundation Layer:** Used as base by multiple analysis tools, needs to stay unified
3. **Clear API Boundary:** Public API in `__init__.py` is clean and well-defined
4. **Appropriate Granularity:** 5 core files + normalizers subdirectory is good size
5. **No Circular Dependencies:** All files have clear dependency direction
6. **Semantic Coupling:** nodes.py → operators.py → semantics.py form coherent abstraction
7. **Normalizers Subdirectory:** Already well-organized, keeps language-specific implementations separated

**NOT a Candidate for Splitting:**

- **NOT into submodules** - Would obscure unified IR concept (nodes + operators + semantics form one system)
- **NOT into ir/core/ and ir/schema/** - Would unnecessarily fragment foundational layer
- **NOT moving semantics.py elsewhere** - Semantics are IR-specific, not language-specific utilities
- **NOT moving nodes.py to ir/types/** - Nodes represent structure, not just types
- **NOT moving normalizers out of ir/** - Normalizers output unified IR, belong with IR module

**Tier Implications:**
- All IR infrastructure (COMMUNITY): Core language-agnostic representation
- Type inference and semantic analysis (PRO): Advanced analysis features
- Distributed and ML features (ENTERPRISE): Polyglot analysis, federated IR, ML optimization

**Breaking Changes:** None - no reorganization planned

**Decision Point:** Keep IR module cohesive in src/code_scalpel/ir/

---

#### Issue 17: Graph Engine Module Analysis and Reorganization

**Files in graph_engine/:** `__init__.py`, `confidence.py`, `graph.py`, `http_detector.py`, `node_id.py`, `README.md`  
**Current Location:** `src/code_scalpel/graph_engine/`  
**Issue:** Should Graph Engine module remain cohesive or split by concern (graph operations vs. confidence vs. HTTP)?  
**Recommendation:** Keep Graph Engine as cohesive module - unified cross-language analysis framework

**Current State Analysis:**

The Graph Engine module provides unified graph representation and analysis for cross-language code:

1. **Core Graph Infrastructure (5 files):**
   - `__init__.py` - Module exports and factory functions
   - `graph.py` - Core graph construction and traversal algorithms (598 LOC)
   - `confidence.py` - Confidence scoring system for edges (363 LOC)
   - `http_detector.py` - Frontend/backend HTTP link detection (466 LOC)
   - `node_id.py` - Universal node ID system across languages (219 LOC)

2. **Documentation (1 file):**
   - `README.md` - Module documentation and API reference (97 LOC)

3. **Dependencies (Cohesion Analysis):**
   - `graph.py` depends on `confidence.py` for edge scoring
   - `http_detector.py` depends on `graph.py` for node/edge creation
   - `node_id.py` used by all modules for universal node identification
   - All modules work together to build unified cross-language graphs
   - No circular dependencies between modules

4. **Role in Architecture:**
   - Core analysis layer: Unified code graph with confidence scoring
   - Used by: polyglot parsers, PDG tools, symbolic execution, security analysis
   - Provides cross-language dependency tracking
   - Enables HTTP link detection between frontend and backend
   - Powers universal node identification across languages

**Proposed Reorganization: KEEP COHESIVE**

```
src/code_scalpel/graph_engine/
├── __init__.py                    # Module exports and utilities (KEEP)
├── graph.py                       # Core graph construction (KEEP)
├── confidence.py                  # Confidence scoring engine (KEEP)
├── http_detector.py               # HTTP link detection (KEEP)
├── node_id.py                     # Universal node ID system (KEEP)
└── README.md                       # Module documentation (KEEP)

# NOT splitting into submodules like graph_engine/core/, graph_engine/confidence/, etc.
# NOT moving confidence scoring to separate module
# NOT moving HTTP detection to integrations/
# NOT moving node ID system to utilities/
```

**Rationale for KEEP Decision:**

1. **Unified Framework:** All components work together to build and analyze cross-language graphs
2. **Cohesive Domain:** Graph Engine is a single concern - unified code representation with confidence
3. **Shared Dependencies:** `node_id.py` used by all modules, `confidence.py` used by `graph.py` and `http_detector.py`
4. **Clear API Boundary:** Public API in `__init__.py` provides clean factory methods
5. **Appropriate Granularity:** 5 core files is optimal size (not too small, not too large)
6. **Multi-language Support:** All components work together for cross-language analysis
7. **Confidence Integration:** Confidence scoring is fundamental to graph edges, not separable

**NOT a Candidate for Splitting:**

- **NOT into submodules** - Would obscure unified graph framework concept
- **NOT into graph_engine/core/ and graph_engine/confidence/** - Would unnecessarily fragment
- **NOT moving confidence.py elsewhere** - Confidence is core to graph edges, not generic utility
- **NOT moving http_detector.py to integrations/** - HTTP detection is core graph feature
- **NOT moving node_id.py to utilities/** - Node IDs are graph-specific, not generic utility
- **NOT moving to polyglot/** - Graph Engine is analysis layer above polyglot parsers

**Tier Implications:**
- Core graph construction (COMMUNITY): Universal node IDs, basic graph building, traversal
- Advanced analysis (PRO): K-hop neighborhoods, confidence optimization, pattern detection
- Distributed graph (ENTERPRISE): Sharding, replication, federated analysis, ML integration

**Breaking Changes:** None - no reorganization planned

**Decision Point:** Keep Graph Engine module cohesive in src/code_scalpel/graph_engine/

---

## Comprehensive Summary Table (All 31 Issues)

**Legend:**
- **Priority:** P0 (Critical) → P4 (Low)
- **Status:** KEEP (no change), MOVE (relocate files), SPLIT (divide module), CREATE (new code), REMOVE (document correction)
- **Tier Impact:** COMMUNITY (free), PRO (commercial), ENTERPRISE (commercial+)

| # | Module/Topic | Files | Current Location | Recommendation | Priority | Tier | Breaking | Cross-Refs |
|---|--------------|-------|------------------|----------------|----------|------|----------|------------|
| 1 | Error Analysis Tools | 2 | Top-level | **✅ COMPLETE** to `quality_assurance/` | P1 | COMMUNITY | Yes | - |
| 2 | Code Extraction/Modification | 3 | Top-level | **✅ COMPLETE** to `surgery/` | P1 | COMMUNITY | Yes | - |
| 3 | Core Analysis Tools | 3 | Top-level | **✅ COMPLETE** to `analysis/` | P1 | COMMUNITY | Yes | - |
| 4 | Licensing Infrastructure | 0 | N/A | **CREATE** `licensing/` | P2 | PRO | No | - |
| 5 | Feature Gating | 0 | N/A | **CREATE** `tiers/` | P2 | PRO | No | - |
| 6 | CLI Reorganization | 1 | Top-level | **MOVE** to `cli/` (conditional) | P4 | ENTERPRISE | Conditional | - |
| 7 | Utilities Module | 1 | `utilities/` | **KEEP** | P4 | COMMUNITY | No | - |
| 8 | Symbolic Execution Tools | 24 | `symbolic_execution_tools/` | **SPLIT** security tools | P2 | COMMUNITY/PRO | Yes | → 9, 23 |
| 9 | Security Module | 0 | `security/` (empty) | **POPULATE** with tools | P2 | PRO/ENT | No | ← 8, 10, 12 |
| 10 | Polyglot Module | 5 | `polyglot/` | **SPLIT** (move 2 files) | P2 | COMMUNITY/PRO | Yes | → 9 |
| 11 | Integration Layer | 3 dirs | 3 separate dirs | **REJECTED** (keep separate) | P0 | ALL | No | ← 24, 25, 26 |
| 12 | Policy Engine | 8 | `policy_engine/` | **MOVE** semantic_analyzer | P2 | COMMUNITY/PRO | Minimal | → 9, 27 |
| 13 | PDG Tools | 8 | `pdg_tools/` | **KEEP** | P4 | COMMUNITY | No | - |
| 14 | MCP Module | 7 | `mcp/` | **KEEP** | P4 | ALL | No | - |
| 15 | Normalizers | 7 | `ir/normalizers/` | **KEEP** | P4 | COMMUNITY | No | - |
| 16 | IR Module | 5 | `ir/` | **KEEP** | P4 | ALL | No | - |
| 17 | Graph Engine | 6 | `graph_engine/` | **KEEP** | P4 | ALL | No | - |
| 18 | Generators (First Analysis) | 4 | `generators/` | **KEEP** | P4 | ALL | No | → 28 |
| 19 | Config Module | 3 | `config/` | **MOVE** governance_config | P1 | ALL | Yes | → 27 |
| 20 | Config Module (Revised) | - | - | Confirmed governance_config move | - | - | - | → 19, 27 |
| 21 | Cache Module | 4 | `cache/` | **KEEP** | P4 | ALL | No | - |
| 22 | Cache Module (Revised) | - | - | Keep unified_cache in cache/ | - | - | - | → 21 |
| 23 | AST Tools Module | 17 | `ast_tools/` | **MOVE** osv_client.py to security/ | P2 | COMMUNITY/PRO | Yes | → 9 |
| 24 | Autonomy Module | 12 | `autonomy/` | **KEEP** | P4 | PRO/ENT | No | → 11 |
| 25 | Agents Module | 10 | `agents/` | **KEEP** (fix typo) | P4 | ALL | No | → 11 |
| 26 | Integrations Module | 8 | `integrations/` | **KEEP** (deprecate REST API) | P0 | ALL | No | → 11 |
| 27 | Governance Module | 5 | `governance/` | **KEEP** | P1 | ENT | No | ← 19, 20 |
| 28 | Generators (Detailed) | 3 | `generators/` | **KEEP** | P2 | ALL | No | ← 18 |
| 29 | code_parser/ | 0 | **DOESN'T EXIST** | **REMOVE** from docs | P3 | N/A | No | - |
| 30 | parsers/ | 0 | **DOESN'T EXIST** | **REMOVE** from docs | P3 | N/A | No | - |
| 31 | policy/ | 0 | **DOESN'T EXIST** | **REMOVE** from docs | P3 | N/A | No | - |

**Summary Statistics:**
- **Total Issues:** 31
- **Breaking Changes:** 11 issues (35%)
- **Keep in Place:** 15 modules (48%)
- **Move Files:** 7 issues (23%)
- **Create New:** 2 modules (6%)
- **Document Corrections:** 3 issues (10%)
- **Rejected Recommendations:** 1 (Issue 11)

---

## Issue Dependencies and Execution Order

**Critical Dependencies:**

```
Issue 11 (Integration Consolidation - REJECTED)
  ← BLOCKED BY: Issue 24 (Autonomy stays separate)
  ← BLOCKED BY: Issue 25 (Agents stays separate)  
  ← BLOCKED BY: Issue 26 (Integrations stays separate)
  → DECISION: Keep all three modules separate

Issue 9 (Security Module Population)
  ← REQUIRES: Issue 8 (Split symbolic_execution_tools)
  ← REQUIRES: Issue 10 (Move polyglot security tools)
  ← REQUIRES: Issue 12 (Move policy_engine semantic_analyzer)
  ← REQUIRES: Issue 23 (Move ast_tools osv_client.py)

Issue 27 (Governance Module Ready)
  ← VALIDATES: Issue 19 (governance_config.py → governance/)
  ← VALIDATES: Issue 20 (governance_config migration confirmed)

Issue 28 (Generators Detailed Analysis)
  ← SUPERSEDES: Issue 18 (Generators initial analysis)
```

**Recommended Execution Sequence:**

1. **Phase 1 (Quick Wins - No Dependencies):**
   - Issues 1, 2, 3: Move top-level files to subdirectories
   - Issues 29, 30, 31: Document corrections
   - Issue 25: Fix agents typo (optimazation → optimization)

2. **Phase 2 (Security Infrastructure - Sequential):**
   - Issue 8: Split symbolic_execution_tools (FIRST)
   - Issue 9: Populate security/ with moved tools (SECOND)
   - Issue 10: Move polyglot security tools (feeds into 9)
   - Issue 12: Move policy_engine semantic_analyzer (feeds into 9)
   - Issue 23: Move ast_tools osv_client.py (feeds into 9)

3. **Phase 3 (Governance & Config):**
   - Issue 19/20: Move governance_config.py
   - Issue 27: Validate governance/ module (confirms 19/20)

4. **Phase 4 (New Infrastructure):**
   - Issue 4: Create licensing/
   - Issue 5: Create tiers/

5. **Phase 5 (Validation & Documentation):**
   - Issues 7, 13, 14, 15, 16, 17, 21, 22, 24, 26, 28: Validate modules (KEEP decisions)
   - Issue 11: Document architectural boundaries (REJECTED consolidation)
   - Issue 6: Conditional CLI reorganization (if needed)

**Parallel Execution Opportunities:**
- Phase 1 can run fully parallel (no dependencies)
- Phase 2 must be sequential (9 depends on 8, 10, 12, 23)
- Phase 3 and Phase 4 can run in parallel with each other

---

## Implementation Roadmap

**Timeline:** 6 phases over 4-6 weeks post v3.0.5
**Approach:** Dependency-ordered execution with parallel opportunities

### Phase 1: Quick Wins & Document Corrections (Week 1, v3.1.0 Alpha) - ✅ COMPLETE
- [x] **UTILITIES:** Verify `utilities/` structure is clean and documented
  - [x] Review `path_resolution.py` for clarity
  - [x] Confirm no cross-dependencies from other reorganized modules
  - [x] Update `utilities/README.md` with usage guidelines
  - [x] No file moves needed (already well-organized)
- [x] **SYMBOLIC EXECUTION TOOLS:** Keep core engine, reorganize security tools
  - [x] Verify core engine files (engine, concolic, constraint_solver, state, memory, ir, path_priority)
  - [x] Update `symbolic_execution_tools/__init__.py` to export only core
  - [x] Create placeholder structure for security/ migration (Phase 2)
  - [x] Update module docstrings to reflect split
- [x] Create `quality_assurance/` and move error tools (Issue 1 - December 25, 2025)
- [x] Create `surgery/` and move extraction/patching tools (Issue 2 - December 25, 2025)
- [x] Create `analysis/` and move analysis tools (Issue 3 - December 25, 2025)
- [x] Update all imports and documentation
- [x] Run full test suite (4,431 tests passing)
- [x] Update `__init__.py` exports
- [x] Verify backward compatibility considerations (deprecation warnings added)
- [x] Issue 32: polyglot/ → code_parsers/ absorption (December 24, 2025)

**Completed:** December 25, 2025  
**Actual Effort:** ~4 hours  
**Test Results:** 4,431 passed, 17 skipped

**Decision Gate:** ✅ APPROVED - Breaking changes to imports implemented with backward-compat aliases

### Phase 2: PRO (Week 2-3, v3.2.0)
- [ ] **SYMBOLIC EXECUTION TOOLS SECURITY SPLIT:**
  - [ ] Create `security/` module structure
  - [ ] Move security analysis tools: security_analyzer, taint_tracker, unified_sink_detector, vulnerability_scanner, sanitizer_analyzer, secret_scanner, cross_file_taint
  - [ ] Move type safety tools: type_evaporation_detector
  - [ ] Move ML vulnerability predictor: ml_vulnerability_predictor
  - [ ] Update all imports
  - [ ] Update MCP tool registry
  - [ ] Run tests
- [ ] **PROTOCOL ANALYZERS SPLIT:**
  - [ ] Create `integrations/protocol_analyzers/` structure
  - [ ] Move framework-specific tools: graphql_schema_tracker, grpc_contract_analyzer, kafka_taint_tracker, schema_drift_detector, frontend_input_tracker
  - [ ] Update all imports
  - [ ] Run tests
- [ ] Create `licensing/` infrastructure
- [ ] Create `tiers/` feature gating system
- [ ] Implement license validation
- [ ] Wire into MCP tool registry
- [ ] Add to `__init__.py` initialization

**Estimated Effort:** 12-16 hours (new structure + security tool migration)

### Phase 3: Governance & Configuration (Week 3, v3.1.0 RC1)
**Issues:** 19, 20, 27
**Dependencies:** None (parallel with Phase 4)
**Breaking Changes:** Yes (Issue 19)
**Estimated Effort:** 3-4 hours

- [ ] **Issue 19/20:** Move governance configuration
  - [ ] Move `governance_config.py` from `config/` → `governance/`
  - [ ] Update imports in governance module
  - [ ] Update config module exports
  - [ ] Run governance tests

- [ ] **Issue 27:** Validate governance module
  - [ ] Confirm module ready for governance_config.py
  - [ ] Expand README.md with comprehensive examples
  - [ ] Add governance architecture diagram
  - [ ] Document relationship to policy_engine/
  - [ ] Add 75-150 TODO items per file
  - [ ] Run validation tests

**Decision Gate:** Confirm governance/ structure is complete?

---

### Phase 4: New Infrastructure (Week 3, v3.2.0 Alpha)
**Issues:** 4, 5
**Dependencies:** None (parallel with Phase 3)
**Breaking Changes:** No (new code)
**Estimated Effort:** 8-12 hours

- [ ] **Issue 4:** Create licensing infrastructure
  - [ ] Create `src/code_scalpel/licensing/` structure
  - [ ] Implement `client/license_manager.py`
  - [ ] Implement `client/validator.py`
  - [ ] Implement `client/cache.py`
  - [ ] Implement `server/` components (optional)
  - [ ] Wire into `__init__.py` tier detection
  - [ ] Add to MCP tool registry
  - [ ] Create comprehensive tests

- [ ] **Issue 5:** Create feature gating system
  - [ ] Create `src/code_scalpel/tiers/` structure
  - [ ] Implement `models.py` (Tier enum, TierConfig)
  - [ ] Implement `decorators.py` (@requires_tier)
  - [ ] Implement `feature_registry.py`
  - [ ] Implement `tool_registry.py`
  - [ ] Integrate with licensing system
  - [ ] Create comprehensive tests

**Decision Gate:** Approve tier gating implementation?

---

### Phase 5: Module Validation & Documentation (Week 4, v3.2.0 Beta)
**Issues:** 6, 7, 11, 13-18, 21-22, 24, 26, 28
**Dependencies:** None (validation only)
**Breaking Changes:** Conditional (Issue 6 only)
**Estimated Effort:** 6-10 hours

- [ ] **Validation Issues (No Code Changes):**
  - [ ] Issue 7: Document utilities/ module architecture
  - [ ] Issue 13: Document PDG tools cohesion rationale
  - [ ] Issue 14: Document MCP module cohesion rationale
  - [ ] Issue 15: Document normalizers cohesion rationale
  - [ ] Issue 16: Document IR module architecture
  - [ ] Issue 17: Document graph engine architecture
  - [ ] Issue 18/28: Consolidate generators documentation
  - [ ] Issue 21/22: Document cache module decisions
  - [ ] Issue 24: Document autonomy module boundaries
  - [ ] Issue 26: Document integrations module boundaries

- [ ] **Issue 11:** Document architectural boundaries (REJECTED consolidation)
  - [ ] Create architecture diagram showing 3 separate modules
  - [ ] Document rejection rationale clearly
  - [ ] Clarify integrations/ = external framework adapters
  - [ ] Clarify agents/ = internal agent implementations
  - [ ] Clarify autonomy/ = supervised autonomous repair
  - [ ] Deprecate rest_api_server.py with timeline
  - [ ] Add migration guide from REST API to MCP

- [ ] **Issue 6:** Reorganize CLI (conditional - if >500 lines)
  - [ ] Check if `cli.py` exceeds 500 lines (currently 755 - YES)
  - [ ] Create `cli/` subdirectory structure
  - [ ] Split into `main.py` and `commands/`
  - [ ] Add tier-aware command availability
  - [ ] Update entry points
  - [ ] Run CLI tests

**Decision Gate:** Architecture documentation complete?

---

### Phase 6: Final Integration & Release (Week 4, v3.2.0 Release)
**Dependencies:** All previous phases complete
**Breaking Changes:** None (integration only)
**Estimated Effort:** 2-4 hours

- [ ] **Final Integration:**
  - [ ] Update all documentation (README, docs/INDEX.md)
  - [ ] Run full test suite (all modules)
  - [ ] Verify coverage ≥90%
  - [ ] Update CHANGELOG.md with all 31 issues
  - [ ] Create comprehensive migration guide
  - [ ] Update all examples/ files
  - [ ] Review CI/CD paths
  - [ ] Create release notes v3.2.0
  - [ ] Tag release: `git tag v3.2.0`

**Decision Gate:** Ready for v3.2.0 release?

---

## Phase Summary

| Phase | Week | Issues | Breaking | Effort | Dependencies |
|-------|------|--------|----------|--------|----------------|
| 1 | Week 1 | 1-3, 25, 29-31 | Yes | 6-8h | None (parallel) |
| 2 | Week 2 | 8-10, 12, 23 | Yes | 12-16h | Sequential |
| 3 | Week 3 | 19-20, 27 | Yes | 3-4h | None (parallel w/4) |
| 4 | Week 3 | 4-5 | No | 8-12h | None (parallel w/3) |
| 5 | Week 4 | 6-7, 11, 13-18, 21-22, 24, 26, 28 | Conditional | 6-10h | None (validation) |
| 6 | Week 4 | Final Integration | No | 2-4h | All phases |
| **Total** | **4 weeks** | **31 issues** | **11 breaking** | **37-54h** | - |

**Critical Path:** Phase 1 → Phase 2 (sequential within phase) → Phases 3+4 (parallel) → Phase 5 → Phase 6

**Key Decision:** Issue 11 (Integration Layer Consolidation) recommendation is **REJECTED** per Issues 24, 25, 26 analysis. All three modules (integrations/, agents/, autonomy/) remain separate with clear architectural boundaries.

---

## Migration Impact Analysis

### Breaking Changes
- **Import Paths Change:** Code using `from code_scalpel.error_scanner` must update to `from code_scalpel.quality_assurance.error_scanner`
- **Module Docstrings:** Update examples in module docstrings
- **Test Imports:** Update all test file imports
- **MCP Tools:** Update MCP tools that reference these modules

### Backward Compatibility Options

**Option A: No Compatibility Layer** (Recommended for v3.1.0)
- Clean break, document migration in CHANGELOG
- Force users to update imports
- Simpler codebase

**Option B: Deprecation Shims** (If needed)
- Add compatibility imports at old locations
- Import from new locations internally
- Emit deprecation warnings
- Removes in v4.0.0

**Example:**
```python
# src/code_scalpel/error_scanner.py (shim)
"""
DEPRECATED: Use src/code_scalpel/quality_assurance/error_scanner instead.
This module will be removed in v4.0.0.
"""
import warnings
from code_scalpel.quality_assurance.error_scanner import *

warnings.warn(
    "error_scanner moved to quality_assurance.error_scanner",
    DeprecationWarning
)
```

---

## Testing Strategy

### Unit Tests
- Update import paths in all test files
- Verify module exports work from new locations
- Check circular import issues

### Integration Tests
- Verify CLI still works after reorganization
- Test MCP server tool loading
- Verify example scripts still run

### Smoke Tests
```bash
# Test imports
python -c "from code_scalpel.quality_assurance import ErrorScanner"
python -c "from code_scalpel.surgery import SurgicalExtractor"
python -c "from code_scalpel.analysis import CodeAnalyzer"

# Test CLI
code-scalpel analyze --help
code-scalpel scan --help

# Test MCP server
code-scalpel mcp --help
```

---

## Documentation Updates

### Files to Update
1. **docs/INDEX.md** - Update module navigation
2. **docs/modules/** - Create new module READMEs for each subdir
3. **docs/architecture/** - Update architecture diagrams
4. **README.md (root)** - Update quick start imports
5. **examples/** - Update import statements
6. **CHANGELOG.md** - Document reorganization

### New Documentation
- `src/code_scalpel/quality_assurance/README.md`
- `src/code_scalpel/surgery/README.md`
- `src/code_scalpel/analysis/README.md`
- `src/code_scalpel/licensing/README.md`
- `src/code_scalpel/tiers/README.md`

---

## Decision Checklist

- [ ] **Approve Phase 1 breaking changes?** (YES/NO)
  - Affects: error_scanner, error_fixer, surgical_*, code_analyzer, project_crawler, core
  - Timeline: v3.1.0 (next release)

- [ ] **Keep polyglot core extraction in polyglot/?** (YES/NO)
  - YES: Keep extractor, alias_resolver, typescript/ in polyglot (core multi-language support)
  - NO: Reorganize each language into language-specific subdirs
  - **Recommended:** YES - polyglot is the right home for core extraction

- [ ] **Move contract_breach_detector to security/?** (YES/NO)
  - YES: Move to security/cross_language/ (cross-language security analysis, PRO/ENT)
  - NO: Keep in polyglot (multi-language concern)
  - **Recommended:** YES for Phase 2 - enables security feature gating

- [ ] **Move tsx_analyzer to integrations/frameworks/react/?** (YES/NO)
  - YES: Move to integrations/frameworks/react/ (framework-specific, PRO/ENT)
  - NO: Keep in polyglot (language analysis)
  - **Recommended:** YES for Phase 2 - enables framework-specific feature gating

- [ ] **Verify security/ folder README alignment?** (YES/NO)
  - Review README.md and README_DEVELOPER_GUIDE.md for guidance
  - Ensure proposed subdirectory structure (analyzers/, type_safety/, cross_language/, etc.) aligns with documentation
  - **Recommended:** YES before Phase 2

- [ ] **Split symbolic_execution_tools security analysis tools?** (YES/NO)
  - YES: Move security analysis to security/ (cleaner architecture, enables PRO/ENT feature gating)
  - NO: Keep all tools in symbolic_execution_tools/ (simpler, but larger module)

- [ ] **Move semantic_analyzer from policy_engine to security/?** (YES/NO)
  - YES: Move to security/analyzers/ (code reuse across security modules, PRO/ENT pattern detection)
  - NO: Keep in policy_engine/ (policy-specific pattern detection)
  - **Recommended:** YES for Phase 2 - enables pattern sharing with general security analyzers

- [ ] **Keep PDG tools cohesive in pdg_tools/?** (YES/NO)
  - YES: Keep all PDG components together (tightly coupled, specialized domain, COMMUNITY core)
  - NO: Split by concern (builder/analyzer/slicer to different locations)
  - **Recommended:** YES - PDG tools are interdependent and should remain cohesive module

- [ ] **Keep MCP module cohesive in mcp/?** (YES/NO)
  - YES: Keep all MCP components together (tightly coupled, MCP-specific, all tiers use same core)
  - NO: Split utilities (path_resolver, module_resolver) to utilities/ or integrations/
  - **Recommended:** YES - MCP module is cohesive integration with clear boundaries, no reorganization needed

- [ ] **Keep normalizers module cohesive in ir/normalizers/?** (YES/NO)
  - YES: Keep all normalizer components together (shared BaseNormalizer interface, unified IR output, factory pattern)
  - NO: Split by language to language-specific dirs or move to polyglot/
  - **Recommended:** YES - Normalizers module is cohesive IR infrastructure with clear domain, no reorganization needed

- [ ] **Keep IR module cohesive in ir/?** (YES/NO)
  - YES: Keep nodes, operators, semantics, normalizers together (foundational layer, clear API boundary)
  - NO: Split into submodules (ir/core/, ir/schema/) or scatter to other locations
  - **Recommended:** YES - IR is unified language-agnostic representation layer, no reorganization needed

- [ ] **Keep Graph Engine module cohesive in graph_engine/?** (YES/NO)
  - YES: Keep graph, confidence, http_detector, node_id together (unified cross-language framework)
  - NO: Split into submodules (graph_engine/core/, graph_engine/confidence/) or scatter to utilities/
  - **Recommended:** YES - Graph Engine is cohesive analysis framework, no reorganization needed

- [ ] **Keep Generators module cohesive in generators/?** (YES/NO)
  - YES: Keep test_generator and refactor_simulator together (unified code generation framework)
  - NO: Split into generators/test/ and generators/refactor/ or scatter to other modules
  - **Recommended:** YES - Generators is cohesive code generation framework, no reorganization needed

- [ ] **Keep Config module cohesive in config/?** (YES/NO) - REVISED
  - Previous: YES (Issue 19) - assumed unified configuration system
  - Current: **NO** (Issue 20) - governance_config is governance-specific
  - **Recommended:** Move governance_config.py to governance/ module, keep init_config + templates in config/

- [ ] **Keep Cache module cohesive in cache/?** (YES/NO)
  - YES: Keep all cache components together (unified performance optimization domain)
  - NO: Split by concern (unified_cache to utilities, ast_cache to parsers, etc.)
  - **Recommended:** YES - Cache module is well-organized with clear domain separation

- [ ] **Move unified_cache.py to utilities/?** (YES/NO) - REVISED
  - Previous: Phase 2 note suggested considering helper functions in utilities
  - Current: **NO** (Issue 22) - unified_cache is core infrastructure, not a utility helper
  - **Recommended:** KEEP in cache/ module - DO NOT move to utilities

- [ ] **Move protocol-specific analyzers to integrations/?** (YES/NO)
  - YES: Create integrations/protocol_analyzers/ (grouped by framework, cleaner)
  - NO: Keep in symbolic_execution_tools/ (simpler, but mixes concerns)
  - **Recommended:** YES for Phase 2

- [ ] **Implement deprecation shims or clean break?** (SHIMS/CLEAN)
  - SHIMS: Easier user migration, larger codebase
  - CLEAN: Simpler code, breaking change documented

- [ ] **Consolidate CLI into `cli/` subdir?** (YES/NO)
  - Only if file grows beyond 500 lines
  - Current: ~750 lines → recommends YES for Phase 3

- [ ] **Move autonomy to `surgery/` instead of `integrations/`?** (YES/NO)
  - autonomy is code modification (surgery) not integration
  - Could be `src/code_scalpel/surgery/autonomy.py`

- [ ] **Coordinate with v3.1.0 licensing implementation?** (YES/NO)
  - Licensing lives in `src/code_scalpel/licensing/`
  - Phase 2 timeline alignment needed

---

## Appendix A: Full Migration Checklist

### Quality Assurance Reorganization
- [ ] Create `src/code_scalpel/quality_assurance/` directory
- [ ] Create `__init__.py` with exports
- [ ] Move `error_scanner.py`
- [ ] Move `error_fixer.py`
- [ ] Create `README.md`
- [ ] Update `src/code_scalpel/__init__.py` imports
- [ ] Update `cli.py` imports
- [ ] Update test imports in `tests/test_error_scanner.py`
- [ ] Update test imports in `tests/test_error_fixer.py`
- [ ] Update example files
- [ ] Run tests: `pytest tests/test_error_*.py`
- [ ] Update docs/

### Surgery Reorganization
- [ ] Create `src/code_scalpel/surgery/` directory
- [ ] Create `__init__.py` with unified interface
- [ ] Move `surgical_extractor.py`
- [ ] Move `surgical_patcher.py`
- [ ] Move `unified_extractor.py` (rename to `extractor.py`?)
- [ ] Create `constants.py` for shared config
- [ ] Create `README.md`
- [ ] Update `src/code_scalpel/__init__.py` imports
- [ ] Update MCP tools
- [ ] Update test imports
- [ ] Run tests: `pytest tests/test_surgical_*.py`
- [ ] Update docs/

### Analysis Reorganization
- [ ] Create `src/code_scalpel/analysis/` directory
- [ ] Create `__init__.py` with exports
- [ ] Move `code_analyzer.py`
- [ ] Move `project_crawler.py`
- [ ] Move `core.py`
- [ ] Extract metrics to `metrics.py`
- [ ] Create `README.md`
- [ ] Update `src/code_scalpel/__init__.py` imports
- [ ] Update CLI imports
- [ ] Update test imports
- [ ] Run tests: `pytest tests/test_code_analyzer.py`
- [ ] Update docs/

### Symbolic Execution Tools Security Analysis Reorganization (Phase 2)
- [ ] Create `src/code_scalpel/security/` directory structure
- [ ] Create `src/code_scalpel/security/analyzers/` subdirectory
  - [ ] Move `security_analyzer.py`
  - [ ] Move `taint_tracker.py`
  - [ ] Move `unified_sink_detector.py`
  - [ ] Move `vulnerability_scanner.py`
  - [ ] Move `sanitizer_analyzer.py`
  - [ ] Move `secret_scanner.py`
  - [ ] Move `cross_file_taint.py`
  - [ ] Create `__init__.py` with exports
  - [ ] Create `README.md`
- [ ] Create `src/code_scalpel/security/type_safety/` subdirectory
  - [ ] Move `type_evaporation_detector.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Create `src/code_scalpel/security/ml/` subdirectory
  - [ ] Move `ml_vulnerability_predictor.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Update `symbolic_execution_tools/__init__.py` to remove moved tools
- [ ] Update all imports across codebase (search for `from code_scalpel.symbolic_execution_tools import security_analyzer` etc.)
- [ ] Update MCP tool registry to reference new locations
- [ ] Update test imports: `tests/test_security_analyzer.py`, etc.
- [ ] Update example files that import security tools
- [ ] Run tests: `pytest tests/test_security_analyzer.py tests/test_taint_tracker.py tests/test_vulnerability_scanner.py`
- [ ] Update docs/

### Polyglot Module Reorganization (Phase 2)

#### Contract Breach Detector Reorganization
- [ ] Create `src/code_scalpel/security/cross_language/` directory
- [ ] Create `__init__.py` with exports
- [ ] Move `polyglot/contract_breach_detector.py` to `security/cross_language/contract_breach_detector.py`
- [ ] Create `README.md` for cross_language module
- [ ] Update `polyglot/__init__.py` to remove contract_breach_detector export
- [ ] Update `security/__init__.py` to export cross_language tools
- [ ] Update all imports across codebase (search for `from code_scalpel.polyglot import contract_breach_detector`)
- [ ] Update MCP tool registry to reference new location
- [ ] Update test imports: `tests/test_contract_breach_detector.py`
- [ ] Update example files that import contract detector
- [ ] Run tests: `pytest tests/test_contract_breach_detector.py`
- [ ] Update docs/ and architecture diagrams

#### TSX/React Analyzer Reorganization
- [ ] Create `src/code_scalpel/integrations/frameworks/react/` directory
- [ ] Create `__init__.py` with exports
- [ ] Move `polyglot/tsx_analyzer.py` to `integrations/frameworks/react/tsx_analyzer.py`
- [ ] Create `README.md` for react framework module
- [ ] Update `polyglot/__init__.py` to remove tsx_analyzer export
- [ ] Update `integrations/frameworks/__init__.py` to export react tools
- [ ] Update all imports across codebase (search for `from code_scalpel.polyglot import tsx_analyzer`)
- [ ] Update MCP tool registry to reference new location
- [ ] Update test imports: `tests/test_tsx_analyzer.py`
- [ ] Update example files that import tsx analyzer
- [ ] Update polyglot extractor if it depends on tsx_analyzer (may need cross-reference)
- [ ] Run tests: `pytest tests/test_tsx_analyzer.py`
- [ ] Update docs/ and architecture diagrams


### Symbolic Execution Tools Protocol Analyzers Reorganization (Phase 2)
- [ ] Create `src/code_scalpel/integrations/protocol_analyzers/` directory
- [ ] Create GraphQL subdirectory
  - [ ] Create `src/code_scalpel/integrations/protocol_analyzers/graphql/`
  - [ ] Move `graphql_schema_tracker.py` → `schema_tracker.py`
  - [ ] Create `__init__.py` with exports
  - [ ] Create `README.md`
- [ ] Create gRPC subdirectory
  - [ ] Create `src/code_scalpel/integrations/protocol_analyzers/grpc/`
  - [ ] Move `grpc_contract_analyzer.py` → `contract_analyzer.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Create Kafka subdirectory
  - [ ] Create `src/code_scalpel/integrations/protocol_analyzers/kafka/`
  - [ ] Move `kafka_taint_tracker.py` → `taint_tracker.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Create Schema subdirectory
  - [ ] Create `src/code_scalpel/integrations/protocol_analyzers/schema/`
  - [ ] Move `schema_drift_detector.py` → `drift_detector.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Create Frontend subdirectory
  - [ ] Create `src/code_scalpel/integrations/protocol_analyzers/frontend/`
  - [ ] Move `frontend_input_tracker.py` → `input_tracker.py`
  - [ ] Create `__init__.py`
  - [ ] Create `README.md`
- [ ] Create `src/code_scalpel/integrations/protocol_analyzers/__init__.py` with exports
- [ ] Create `src/code_scalpel/integrations/protocol_analyzers/README.md`
- [ ] Update `symbolic_execution_tools/__init__.py` to remove moved tools
- [ ] Update all imports across codebase
- [ ] Update MCP tool registry
- [ ] Update test imports
- [ ] Run tests: `pytest tests/test_graphql_schema_tracker.py tests/test_grpc_contract_analyzer.py tests/test_kafka_taint_tracker.py tests/test_schema_drift_detector.py tests/test_frontend_input_tracker.py`
- [ ] Update docs/

### Policy Engine Semantic Analyzer Reorganization (Phase 2)
- [ ] Verify semantic_analyzer usage in policy_engine.py
  - [ ] Check if imports are internal only or external
  - [ ] Identify all call sites
- [ ] Create `src/code_scalpel/security/analyzers/__init__.py` (if not exists)
- [ ] Move `semantic_analyzer.py` from `policy_engine/` to `security/analyzers/`
  - [ ] Copy file to new location
  - [ ] Remove file from policy_engine/
- [ ] Update `security/analyzers/__init__.py` to export `SemanticAnalyzer`
- [ ] Update `policy_engine/__init__.py` if semantic_analyzer was re-exported
  - [ ] Option A: Import from new location `from code_scalpel.security.analyzers import SemanticAnalyzer`
  - [ ] Option B: Remove from policy_engine if not needed in public API
- [ ] Update all imports across codebase
  - [ ] Find: `from code_scalpel.policy_engine import SemanticAnalyzer`
  - [ ] Replace: `from code_scalpel.security.analyzers import SemanticAnalyzer`
  - [ ] Find: `from code_scalpel.policy_engine.semantic_analyzer import`
  - [ ] Replace: `from code_scalpel.security.analyzers.semantic_analyzer import`
- [ ] Update MCP tool registry if semantic_analyzer is exposed as MCP tool
- [ ] Update test imports
  - [ ] Find: `tests/test_policy_engine/test_semantic_analyzer.py` (if exists)
  - [ ] Move to: `tests/test_security/test_analyzers/test_semantic_analyzer.py`
  - [ ] Update imports in test file
- [ ] Run tests: `pytest tests/test_policy_engine/ tests/test_security/test_analyzers/test_semantic_analyzer.py`
- [ ] Update docs/
  - [ ] Update `docs/modules/policy_engine.md` to remove semantic_analyzer reference
  - [ ] Update `docs/modules/security.md` to include semantic_analyzer
  - [ ] Update `docs/architecture/` diagrams showing new semantic_analyzer location

---

## Issue 18: Generators Module Analysis and Reorganization

**Date:** December 24, 2025  
**Scope:** 4 files analyzed (test_generator.py, refactor_simulator.py, __init__.py, README.md)  
**Issue:** Should generators module remain cohesive or split by type (test vs. refactor)?  
**Recommendation:** Keep generators as cohesive module - unified code generation framework

### Current State

The generators module provides code generation capabilities:

```
src/code_scalpel/generators/
├── __init__.py (16 lines → 88 lines with TODOs)
├── test_generator.py (1054 lines, 7 classes)
├── refactor_simulator.py (642 lines, 3 classes)
└── README.md (86 lines → 160 lines with TODOs)
```

**Existing Implementation:**
- `TestGenerator` - Converts symbolic execution paths to unit tests
- `RefactorSimulator` - Verifies code changes before applying
- `TestCase`, `GeneratedTestSuite` - Test data structures
- `RefactorResult`, `SecurityIssue` - Refactor verification results

### Analysis

#### 1. **Unified Framework**
Both test generation and refactor simulation are code generation tasks:
- Both use AST analysis for code parsing
- Both generate code artifacts
- Both need formatting, validation, serialization
- Both integrate with symbolic execution engine

#### 2. **Cohesive Domain**
Single concern: **Code generation and verification**
- Not separable into test-specific and refactor-specific modules
- Shared infrastructure (AST parsing, formatting, validation)
- Both needed for complete "AI agent safe code modification" workflow

#### 3. **Shared Dependencies**
- Both import: `ast`, `dataclasses`, `enum`, `typing`
- Both depend on: `symbolic_execution_tools/engine.py`
- Both depend on: `ast_tools/analyzer.py`
- Both used by: `mcp/server.py` (MCP tools)
- Both used by: `autonomy/` workflows

#### 4. **Clear API Boundary**
Module exports cohesive API:
```python
__all__ = [
    "TestGenerator",
    "GeneratedTestSuite",
    "RefactorSimulator",
    "RefactorResult",
]
```

#### 5. **Appropriate Granularity**
- Current: 4 files (test_generator, refactor_simulator, __init__, README)
- Optimal size for unified code generation service
- Not sprawling, not fragmented

### Why NOT Splitting

**Option: Split into generators/test_gen/ and generators/refactor/**
- ❌ Would duplicate shared infrastructure
- ❌ Would obscure unified code generation concept
- ❌ Would require complex inter-module imports
- ❌ Test generation and refactor simulation are co-dependent patterns

**Option: Move test_generator to symbolic_execution_tools/**
- ❌ Test generation is not core symbolic execution
- ❌ Belongs in generation/output layer, not analysis layer
- ❌ Would tightly couple user-facing code with internal engine

**Option: Move refactor_simulator to utilities/**
- ❌ Not a utility function; sophisticated analysis tool
- ❌ Belongs with other code generators
- ❌ Not appropriate for general-purpose utilities

### Tier Implications

**COMMUNITY Tier:**
- Basic test generation from execution paths
- Basic refactor simulation with security checks
- Pytest and unittest format support
- Structural change detection

**PRO Tier:**
- Property-based test generation (Hypothesis)
- Advanced equivalence checking
- Performance impact prediction
- Custom assertion generation
- Fixture and mock generation

**ENTERPRISE Tier:**
- Distributed test generation across agents
- Federated test generation across organizations
- Test/refactor compliance checking (SOC2/HIPAA/GDPR)
- ML-based test prioritization
- Cost tracking and SLA monitoring
- Audit logging and access control

### Breaking Changes

**None** - No reorganization planned, no imports affected

### Decision Point

**✅ Keep generators module cohesive in src/code_scalpel/generators/**

**Rationale:** Generators is a unified code generation framework. Test generation and refactor simulation are complementary capabilities that share infrastructure, dependencies, and API boundaries. No reorganization needed.

---

## Appendix B: References

- **Related Issue:** V1.0 fork strategy → three-tier product
- **Related Phase:** Phase 1-2 of implementation roadmap
- **Related Document:** `DEVELOPMENT_ROADMAP.md` (tier architecture)
- **Testing Framework:** pytest
- **Breaking Change Policy:** Document in CHANGELOG, consider v3.1.0 milestone

---

## Issue 23: AST Tools Module Analysis and Reorganization

**Module:** `src/code_scalpel/ast_tools/`  
**Status:** Analysis Complete - Partial Reorganization Recommended  
**Tier Impact:** TIER 2 (PRO) - Security scanning reorganization  
**Files:** 17 Python files + 1 README

### Current Structure
```
src/code_scalpel/ast_tools/
├── __init__.py                 # Module initialization
├── README.md                   # Comprehensive documentation (3,000+ lines)
│
├── Core AST Analysis (3 files):
│   ├── analyzer.py            # AST analysis and metrics
│   ├── builder.py             # AST construction from source
│   └── utils.py               # AST utility functions
│
├── Transformation & Validation (3 files):
│   ├── transformer.py         # Safe AST transformations
│   ├── validator.py           # Code validation and style checks
│   └── visualizer.py          # AST visualization (Graphviz)
│
├── Cross-File Analysis (4 files):
│   ├── import_resolver.py     # Import resolution across files
│   ├── call_graph.py          # Call relationship analysis
│   ├── cross_file_extractor.py # Symbol extraction with deps
│   └── dependency_parser.py   # Dependency file parsing (pyproject, package.json, pom.xml)
│
├── Advanced Analysis (4 files):
│   ├── type_inference.py      # Type hint inference engine
│   ├── control_flow.py        # Control flow graph builder
│   ├── data_flow.py           # Data flow analysis
│   └── ast_refactoring.py     # Refactoring pattern detection
│
├── Security/Dependency Scanning (1 file):
│   └── osv_client.py          # OSV vulnerability database client
│
└── __pycache__/               # Python bytecode cache
```

### Analysis

#### Strengths
1. **Comprehensive Functionality:** 17 modules covering full AST lifecycle (parse → analyze → transform → validate → visualize)
2. **Well-Documented:** Each file has extensive TIER 1/2/3 TODO roadmaps (1,750+ TODOs, 2,250+ test specifications)
3. **Logical Grouping:** Files naturally cluster into functional groups
4. **Feature Completeness:** Covers parsing, analysis, transformation, validation, visualization, and security
5. **Tier-Aware:** All modules documented with COMMUNITY/PRO/ENTERPRISE feature roadmaps

#### Identified Issues

**ISSUE 23A: Security Scanning Module Misplaced**

**File:** `osv_client.py` (OSV vulnerability database client)  
**Current Location:** `src/code_scalpel/ast_tools/`  
**Problem:** Security scanning is **not an AST operation**

**Rationale:**
- OSV client queries external vulnerability databases (OSV.dev API)
- Works with dependency files (requirements.txt, package.json, pom.xml)
- **Does NOT** parse or manipulate AST structures
- Functionality is orthogonal to AST analysis
- Should be grouped with other security/scanning tools

**Recommended Location:** `src/code_scalpel/security/`

**Proposed Structure:**
```
src/code_scalpel/security/
├── __init__.py
├── osv_client.py              # Move from ast_tools/
├── vulnerability_scanner.py   # (future) Aggregate scanner
├── dependency_analyzer.py     # (future) Dependency risk analysis
└── README.md
```

**Migration Steps:**
1. Move `ast_tools/osv_client.py` → `security/osv_client.py`
2. Update `security/__init__.py` to export OSVClient
3. Update imports in:
   - `mcp/tools/scan_dependencies.py` (uses OSVClient)
   - Any other modules importing OSVClient
4. Update `ast_tools/__init__.py` to remove OSVClient export
5. Update `ast_tools/README.md` to remove OSV client documentation
6. Create/update `security/README.md` with vulnerability scanning documentation
7. Update test paths: `tests/ast_tools/test_osv_client.py` → `tests/security/test_osv_client.py`

**Breaking Changes:** Yes
- Import changes: `from code_scalpel.ast_tools import OSVClient` → `from code_scalpel.security import OSVClient`
- However, MCP tools are primary consumers and can be updated atomically

**Benefits:**
- ✅ Logical grouping: Security tools in security module
- ✅ Clearer module boundaries: AST tools focus on AST operations only
- ✅ Future-proof: Natural home for other security scanning tools
- ✅ Reduced confusion: Developers won't look in ast_tools for security features

**Tier Impact:** TIER 2 (PRO) - Vulnerability scanning is a PRO/ENTERPRISE feature

---

**ISSUE 23B: Dependency Parser Ambiguous Placement**

**File:** `dependency_parser.py`  
**Current Location:** `src/code_scalpel/ast_tools/`  
**Problem:** Partially misplaced - parses **dependency files**, not AST

**Analysis:**
- **Function:** Parses `pyproject.toml`, `requirements.txt`, `package.json`, `pom.xml`
- **AST Usage:** Minimal - only uses defusedxml for XML parsing (not Python AST)
- **Dependencies:** Works with osv_client.py for vulnerability scanning
- **Use Case:** Cross-file dependency analysis, security scanning

**Recommendation:** **KEEP in ast_tools/** (but with caveat)

**Rationale:**
- Used by `call_graph.py` and `cross_file_extractor.py` (both in ast_tools)
- Part of broader "code analysis" context (understanding project dependencies)
- Moving would break more integrations than it fixes
- Name is somewhat misleading but functionality is adjacent to AST cross-file analysis

**Alternative (Not Recommended):** Move to `utilities/` or `security/`
- Would separate from cross-file analysis tools
- Less discoverable for developers working on call graphs/extraction

**Decision:** **Keep in ast_tools/** but document clearly in README

**Documentation Update Required:**
```markdown
### dependency_parser.py - Dependency File Parsing

**Note:** Despite the name, this module parses **dependency files** 
(requirements.txt, package.json, pom.xml), NOT Python AST. It supports 
cross-file dependency analysis and security vulnerability scanning.

**Key Features:**
- Parse Python dependencies (pip, poetry, setup.py)
- Parse JavaScript dependencies (npm, yarn)
- Parse Java dependencies (Maven, Gradle)
- Integrate with OSVClient for vulnerability scanning
- Support lock file parsing (poetry.lock, package-lock.json)
```

---

**ISSUE 23C: No Further Reorganization Needed**

**Remaining Files:** 15 files (excluding osv_client.py and dependency_parser.py)

**Analysis:** All remaining files are **correctly placed**

**Core AST Analysis:**
- ✅ analyzer.py - AST metrics and analysis
- ✅ builder.py - AST construction
- ✅ utils.py - AST utilities

**Transformation & Validation:**
- ✅ transformer.py - AST transformation
- ✅ validator.py - AST validation
- ✅ visualizer.py - AST visualization

**Cross-File Analysis:**
- ✅ import_resolver.py - Uses AST to resolve imports
- ✅ call_graph.py - Uses AST to build call graphs
- ✅ cross_file_extractor.py - Uses AST to extract symbols
- ✅ dependency_parser.py - (Keep in ast_tools per 23B)

**Advanced Analysis:**
- ✅ type_inference.py - AST-based type inference
- ✅ control_flow.py - AST-based CFG construction
- ✅ data_flow.py - AST-based data flow analysis
- ✅ ast_refactoring.py - AST-based refactoring detection

**Rationale:**
- All files perform **AST-based operations**
- Natural functional grouping maintained
- Cross-references within module are appropriate
- No circular dependencies identified
- Documentation is comprehensive and tier-organized

---

### Reorganization Summary

| File | Current Location | Recommended Action | Priority |
|------|------------------|-------------------|----------|
| osv_client.py | ast_tools/ | Move to security/ | P1 (High) |
| dependency_parser.py | ast_tools/ | Keep (document clearly) | P2 (Medium) |
| All others (15 files) | ast_tools/ | Keep as-is | - |

### Implementation Priority

**Phase 1 (Current Release - v3.0.6):**
- ✅ Document dependency_parser.py placement rationale in README
- ✅ Add clarity about "AST operations only" in module docstring

**Phase 2 (Next Minor Release - v3.1.0):**
- 🔄 Move osv_client.py to security/
- 🔄 Update all imports and tests
- 🔄 Update documentation and MCP tool references

**Phase 3 (Future):**
- ⏳ Populate security/ with additional scanning tools
- ⏳ Consider renaming dependency_parser.py to dependency_file_parser.py for clarity

### Breaking Changes

**v3.1.0 Migration (osv_client.py move):**

**Before:**
```python
from code_scalpel.ast_tools import OSVClient

client = OSVClient()
vulns = client.query_package("requests", "2.25.0", "PyPI")
```

**After:**
```python
from code_scalpel.security import OSVClient

client = OSVClient()
vulns = client.query_package("requests", "2.25.0", "PyPI")
```

**Affected Components:**
- `src/code_scalpel/mcp/tools/scan_dependencies.py` (primary consumer)
- `examples/security_analysis_example.py` (if exists)
- Documentation referencing OSVClient
- Test files in `tests/ast_tools/test_osv_client.py`

### Decision Points

**✅ APPROVED: Move osv_client.py to security/**

**Rationale:** 
- Security scanning is not AST analysis
- Natural home in dedicated security module
- Improves discoverability
- Minimal breaking changes (primarily MCP tools)

**✅ APPROVED: Keep dependency_parser.py in ast_tools/**

**Rationale:**
- Tightly integrated with cross-file analysis tools
- Used by call_graph.py and cross_file_extractor.py
- Moving would cause more disruption than benefit
- Document placement rationale clearly

**✅ APPROVED: No other reorganization needed**

**Rationale:**
- All remaining 15 files perform AST-based operations
- Logical grouping is maintained
- Comprehensive tier-organized documentation
- No circular dependencies or architectural issues

### Tier-Aware Feature Distribution

**COMMUNITY Tier (Free):**
- Basic AST parsing, analysis, validation
- Simple transformations and visualization
- Core cross-file analysis
- **Total:** 70+ TIER 1 features across all ast_tools modules

**PRO Tier (Commercial):**
- Advanced analysis (type inference, data flow, control flow)
- Pattern matching transformations
- Interactive visualization
- Framework-specific analysis
- **Vulnerability scanning (osv_client.py - moving to security/)**
- **Total:** 140+ TIER 2 features

**ENTERPRISE Tier (Commercial):**
- ML-based analysis and predictions
- IDE integration (LSP)
- Advanced optimization
- 3D visualization
- **Total:** 100+ TIER 3 features

### Documentation Quality

**Current State:** ✅ Excellent
- Each file has comprehensive TIER 1/2/3 TODOs
- 1,750+ TODO items documented
- 2,250+ test specifications defined
- README.md is comprehensive (3,000+ lines)
- All modules have clear feature roadmaps

**No additional documentation changes needed** beyond Issue 23A/23B updates.

---

## Issue 24: Autonomy Module Analysis and Reorganization

**Module:** `src/code_scalpel/autonomy/`  
**Status:** Analysis Complete - Keep Autonomy as Standalone Module  
**Tier Impact:** TIER 2 (PRO), TIER 3 (ENTERPRISE)  
**Files:** 8 core files + 4 integration files + 2 README

### Current Structure
```
src/code_scalpel/autonomy/
├── __init__.py                    # Module initialization with exports
├── README.md                      # Comprehensive autonomy documentation (673 lines)
│
├── Core Autonomy Engine (3 files):
│   ├── engine.py                 # Main orchestration for autonomous operations
│   ├── fix_loop.py               # Supervised fix loop with safety guarantees
│   └── audit.py                  # Cryptographically-hashed audit trail
│
├── Safety & Validation (2 files):
│   ├── mutation_gate.py          # Hollow fix detection via mutation testing
│   └── sandbox.py                # Speculative execution in isolated environment
│
├── Analysis & Transformation (1 file):
│   ├── error_to_diff.py          # Convert errors to actionable diffs
│
├── Support Infrastructure (2 files):
│   ├── stubs.py                  # Placeholder stubs for dependencies
│   └── (utils/helpers planned)
│
└── integrations/                 # Framework-specific integrations
    ├── __init__.py
    ├── README.md
    ├── autogen.py                # AutoGen AssistantAgent integration
    ├── crewai.py                 # CrewAI Crew integration
    └── langgraph.py              # LangGraph StateGraph integration
```

### Analysis Summary

**Question from Issue 11:** Should `autonomy/` (Error-to-Diff engine) move to `surgery/` instead? It's code modification, not integration.

**Answer:** **NO - Keep autonomy/ as standalone module**

### Detailed Analysis

#### Core Functionality Assessment

The autonomy module provides **supervised autonomous code repair** with the following components:

1. **Error-to-Diff Engine (error_to_diff.py)**
   - Converts compiler errors, linter warnings, test failures → actionable diffs
   - Multi-language error parsing (Python, TypeScript, Java)
   - Confidence-scored fix generation
   - AST-based validation
   - **NOT just code modification** - includes error analysis, fix ranking, validation

2. **Fix Loop (fix_loop.py)**
   - Supervised fix loop with safety guarantees
   - Hard limits on retry attempts
   - Timeout enforcement
   - Repeated error detection
   - Human escalation on failure
   - **Orchestration logic** - coordinates multiple operations

3. **Mutation Test Gate (mutation_gate.py)**
   - Prevents "hollow fixes" (tests pass due to deleted functionality)
   - Mutation score calculation
   - Weak test identification
   - **Quality assurance** - not code surgery

4. **Sandbox Executor (sandbox.py)**
   - Speculative execution in isolated environment
   - Resource limits (CPU, memory, disk)
   - Network isolation
   - Process/container-level isolation
   - **Safety infrastructure** - not code modification

5. **Audit Trail (audit.py)**
   - Cryptographically-hashed immutable logs
   - Parent-child operation tracking
   - Compliance-ready audit records
   - **Governance infrastructure** - not code surgery

6. **Autonomy Engine (engine.py)**
   - Main orchestration layer
   - Configuration-driven governance
   - Change budget tracking
   - Blast radius calculation
   - **Orchestration** - coordinates all autonomy components

### Rationale for Keeping Autonomy Separate

**1. Architectural Distinctness:**
- **surgery/** is about **direct code manipulation** (extract, patch, modify)
- **autonomy/** is about **supervised intelligent repair** (analyze error → generate fix → validate → apply)
- Mixing these would blur architectural boundaries

**2. Different Concerns:**
| Concern | surgery/ | autonomy/ |
|---------|----------|-----------|
| **Primary Goal** | Token-efficient extraction/modification | Safe autonomous code repair |
| **Intelligence** | AST-based surgical operations | Error analysis → Fix generation → Validation |
| **Safety** | Assumes human oversight | Built-in safety gates (mutation testing, sandbox) |
| **Scope** | Single operation (extract/patch) | Multi-step workflow (analyze → fix → test → apply) |
| **Audit** | No audit trail | Cryptographic audit logging |
| **Integration** | Direct API calls | Framework integrations (AutoGen, CrewAI, LangGraph) |

**3. Feature Tier Alignment:**
- **surgery/**: COMMUNITY tier (core surgical operations available to all)
- **autonomy/**: PRO/ENTERPRISE tier (supervised autonomy is commercial feature)
- Keeping separate enables clear tier gating

**4. Framework Integrations:**
- `autonomy/integrations/` contains AutoGen, CrewAI, LangGraph integrations
- These are **autonomy-specific** (fix loop workflows, error analysis nodes)
- NOT general framework integrations (which belong in `integrations/frameworks/`)
- Moving autonomy to surgery would split these integrations awkwardly

**5. Cohesive Module:**
- All 8 files work together as a unified system
- Fix loop coordinates error-to-diff, mutation gate, sandbox, audit
- Strong interdependencies (engine → fix_loop → sandbox → audit)
- Splitting would create unnecessary import complexity

**6. Governance Integration:**
- Autonomy module integrates with policy_engine/ for governance
- Implements change budgets, blast radius calculation
- Natural architectural layer distinct from code surgery

### Comparison to Other Modules

**Similar Cohesive Modules (Keep Separate):**
- `pdg_tools/` - cohesive PDG analysis suite (Issue 13: KEEP)
- `mcp/` - cohesive MCP server infrastructure (Issue 14: KEEP)
- `policy_engine/` - cohesive policy governance (Issue 12: KEEP)

**Autonomy is similar:** Tightly integrated components serving unified purpose.

### Proposed Structure (Current is Optimal)

**✅ KEEP: All autonomy/ files in current location**

```
src/code_scalpel/autonomy/
├── __init__.py                    # (KEEP - exports all components)
├── README.md                      # (KEEP - comprehensive docs)
├── engine.py                      # (KEEP - orchestration)
├── fix_loop.py                    # (KEEP - supervised loop)
├── audit.py                       # (KEEP - audit trail)
├── mutation_gate.py               # (KEEP - hollow fix detection)
├── sandbox.py                     # (KEEP - safe execution)
├── error_to_diff.py               # (KEEP - error analysis & fix generation)
├── stubs.py                       # (KEEP - dependency stubs)
└── integrations/                  # (KEEP - autonomy-specific integrations)
    ├── __init__.py
    ├── README.md
    ├── autogen.py
    ├── crewai.py
    └── langgraph.py
```

**No reorganization needed.**

### Relationship to Issue 11 (Integration Layer)

**Issue 11 Recommendation:** Consolidate `integrations/`, `agents/`, `autonomy/` into single `integrations/` tree.

**Updated Recommendation after Issue 24 Analysis:**

**DO NOT move autonomy/ to integrations/**

Rationale:
- `autonomy/integrations/` contains **autonomy-specific** framework integrations (fix loop workflows)
- General `integrations/frameworks/` contains **general-purpose** framework integrations
- Moving autonomy would create confusion: "Is autonomy a framework integration or does it have framework integrations?"
- Keep autonomy as first-class module with its own integration subdirectory

**Updated Issue 11 Structure:**
```
src/code_scalpel/
├── autonomy/                      # (KEEP as top-level - Issue 24)
│   ├── integrations/              # Autonomy-specific (AutoGen fix loops, etc.)
│   └── ... (all autonomy files)
│
├── integrations/                  # General integrations
│   ├── frameworks/                # General framework integrations
│   │   ├── autogen_general.py
│   │   ├── crewai_general.py
│   │   └── ...
│   ├── protocol_analyzers/       # (from symbolic_execution_tools/)
│   ├── rest_api/
│   └── mcp_server/
│
└── agents/                        # (Consider merging to integrations/agents/ - Issue 11)
```

**Key Distinction:**
- `autonomy/integrations/autogen.py` - AutoGen agents for **autonomous fix loops**
- `integrations/frameworks/autogen.py` - General AutoGen integration for **Code Scalpel tools**

### Tier-Aware Feature Distribution

**COMMUNITY Tier (Free):**
- Basic error analysis (error-to-diff parsing)
- Simple fix suggestions
- Manual fix application
- **Total:** 25 TIER 1 features per file (175 total)

**PRO Tier (Commercial):**
- Supervised fix loop (bounded retries)
- Sandbox execution (process-level)
- Mutation testing (hollow fix detection)
- Audit trail (basic logging)
- Framework integrations (AutoGen, CrewAI, LangGraph)
- **Total:** 25 TIER 2 features per file (175 total)

**ENTERPRISE Tier (Commercial):**
- Distributed orchestration
- Container-level isolation
- Advanced mutation analysis
- Compliance-ready audit (SIEM integration)
- Multi-agent coordination
- **Total:** 25 TIER 3 features per file (175 total)

### Documentation Quality

**Current State:** ✅ Excellent
- Each file has comprehensive TIER 1/2/3 TODOs
- 525+ TODO items documented across 8 core files + 4 integration files
- 600+ test specifications defined (25 per TODO)
- README.md is comprehensive (673 lines)
- Clear module boundaries and responsibilities

**No additional documentation changes needed.**

### Migration Steps

**No migration required** - autonomy/ stays in current location.

**Recommendation for Issue 11 Update:**
- Update Issue 11 to reflect autonomy/ should remain separate
- Clarify distinction between `autonomy/integrations/` (autonomy-specific) vs `integrations/frameworks/` (general)
- Document architectural reasoning for separation

### Breaking Changes

**None** - no reorganization, no import changes.

### Priority Assessment

**Priority:** P3 (Documentation Only)
- No code changes needed
- Document decision rationale
- Update Issue 11 to reflect analysis
- Clarify architectural boundaries

### Summary

**✅ APPROVED: Keep autonomy/ as standalone top-level module**

**Rationale:**
- Architecturally distinct from surgery/ (supervised repair vs direct manipulation)
- Cohesive module with strong interdependencies
- Clear tier alignment (PRO/ENTERPRISE features)
- Framework integrations are autonomy-specific, not general-purpose
- Consistent with other cohesive modules (pdg_tools, mcp, policy_engine)

**✅ APPROVED: Keep autonomy/integrations/ subdirectory**

**Rationale:**
- Autonomy-specific framework integrations (fix loop workflows)
- Distinct from general framework integrations
- Natural organization within autonomy module

**✅ APPROVED: Update Issue 11 recommendation**

**Rationale:**
- Original Issue 11 suggested moving autonomy to integrations
- Analysis reveals autonomy should stay separate
- Document architectural reasoning

---

## Issue 25: Agents Module Analysis and Reorganization

**Module:** `src/code_scalpel/agents/`  
**Status:** Analysis Complete - Keep Agents as Standalone Module  
**Tier Impact:** COMMUNITY (Core Agents), PRO/ENTERPRISE (Advanced Features)  
**Files:** 10 Python files + 1 README

### Current Structure
```
src/code_scalpel/agents/
├── __init__.py                    # Module initialization with exports
├── README.md                      # Comprehensive agent documentation (500+ lines)
│
├── Core Framework (2 files):
│   ├── base_agent.py             # OODA loop framework (BaseCodeAnalysisAgent, AgentContext)
│   └── (interfaces/protocols planned)
│
├── Implemented Agents (3 files):
│   ├── code_review_agent.py      # Code quality and security review
│   ├── security_agent.py         # Security vulnerability detection
│   └── optimazation_agent.py     # Performance optimization (typo in filename)
│
└── Stub Agents (5 files):
    ├── refactoring_agent.py      # Code restructuring and design patterns
    ├── testing_agent.py          # Test generation and coverage
    ├── documentation_agent.py    # Documentation generation
    ├── metrics_agent.py          # Code metrics and analytics
    └── (additional agents planned)
```

### Analysis Summary

**Question:** Should `agents/` be moved to `integrations/agents/` per Issue 11?

**Answer:** **NO - Keep agents/ as standalone module**

### Detailed Analysis

#### Core Functionality Assessment

The agents module provides **specialized AI agents for code analysis** built on the OODA loop pattern (Observe → Orient → Decide → Act).

**Key Components:**

1. **BaseCodeAnalysisAgent (base_agent.py)**
   - Abstract base class for all agents
   - OODA loop implementation
   - MCP tool integration layer
   - Context management (AgentContext class)
   - **Framework infrastructure** - not integration code

2. **AgentContext (base_agent.py)**
   - Operation history tracking
   - Knowledge base for learning
   - Workspace state management
   - **Core framework component**

3. **Specialized Agents (3 implemented + 5 stubs)**
   - CodeReviewAgent - Quality and security review
   - SecurityAgent - Vulnerability detection
   - OptimizationAgent - Performance analysis
   - RefactoringAgent (stub) - Code restructuring
   - TestingAgent (stub) - Test generation
   - DocumentationAgent (stub) - Documentation generation
   - MetricsAgent (stub) - Code metrics
   - **Tool implementations** - not framework integrations

### Rationale for Keeping Agents Separate

**1. Architectural Distinctness:**
- **integrations/frameworks/** is for **external framework adapters** (AutoGen, CrewAI, LangGraph)
- **agents/** is for **Code Scalpel's own agent implementations**
- Mixing these would blur the distinction between "our tools" vs "integration layer"

**2. Different Concerns:**

| Concern | integrations/frameworks/ | agents/ |
|---------|--------------------------|---------|
| **Primary Goal** | Adapt Code Scalpel tools for external frameworks | Provide specialized analysis agents |
| **Ownership** | Integration adapters | Core Code Scalpel functionality |
| **Dependencies** | External frameworks (AutoGen, CrewAI, etc.) | Internal MCP tools only |
| **Usage** | By external AI frameworks | Directly by users or via MCP |
| **Evolution** | Driven by framework changes | Driven by Code Scalpel features |

**3. Similar to Autonomy Module:**
- Just as `autonomy/integrations/` contains autonomy-specific framework integrations
- And `integrations/frameworks/` contains general framework integrations
- **agents/** contains Code Scalpel's agent implementations
- **integrations/frameworks/** would contain adapters to use agents in external frameworks

**4. Module Independence:**
- Agents can be used standalone via MCP protocol
- Agents don't require external frameworks
- External frameworks integrate WITH agents, not vice versa
- Clear architectural boundary

**5. Tier Alignment:**
- Core agents (COMMUNITY): CodeReview, Security, Optimization
- Advanced agents (PRO/ENTERPRISE): Refactoring, Testing, Documentation, Metrics
- Keeping separate enables clear tier gating at agent level

### Comparison to Other Modules

**Similar Standalone Modules (Keep Separate):**
- `pdg_tools/` - Code Scalpel's PDG analysis suite (Issue 13: KEEP)
- `mcp/` - Code Scalpel's MCP server infrastructure (Issue 14: KEEP)
- `policy_engine/` - Code Scalpel's policy governance (Issue 12: KEEP)
- `autonomy/` - Code Scalpel's autonomous repair system (Issue 24: KEEP)

**Agents is similar:** Internal tooling that other parts of the system can integrate with.

### Proposed Structure (Current is Optimal)

**✅ KEEP: All agents/ files in current location**

```
src/code_scalpel/agents/
├── __init__.py                    # (KEEP - module exports)
├── README.md                      # (KEEP - agent documentation)
├── base_agent.py                  # (KEEP - OODA loop framework)
├── code_review_agent.py           # (KEEP - quality review)
├── security_agent.py              # (KEEP - security analysis)
├── optimazation_agent.py          # (KEEP - but rename to optimization_agent.py)
├── refactoring_agent.py           # (KEEP - code restructuring)
├── testing_agent.py               # (KEEP - test generation)
├── documentation_agent.py         # (KEEP - doc generation)
├── metrics_agent.py               # (KEEP - code metrics)
└── (future agents here)
```

**No reorganization needed** except filename typo fix.

### Relationship to Issue 11 (Integration Layer)

**Issue 11 Recommendation:** Consolidate `integrations/`, `agents/`, `autonomy/`

**Updated Recommendation after Issues 24 & 25:**

**DO NOT move agents/ to integrations/**

Rationale:
- `agents/` contains Code Scalpel's own agent implementations
- `integrations/frameworks/` contains external framework adapters
- `autonomy/` contains autonomous repair system with its own integrations
- Each serves distinct purpose with clear boundaries

**Updated Architecture:**
```
src/code_scalpel/
├── agents/                        # (KEEP as top-level - Issue 25)
│   ├── base_agent.py              # OODA loop framework
│   ├── code_review_agent.py       # Code Scalpel's code review agent
│   ├── security_agent.py          # Code Scalpel's security agent
│   └── ... (other Code Scalpel agents)
│
├── autonomy/                      # (KEEP as top-level - Issue 24)
│   ├── integrations/              # Autonomy-specific framework integrations
│   │   ├── autogen.py             # AutoGen fix loop workflows
│   │   ├── crewai.py              # CrewAI fix loop workflows
│   │   └── langgraph.py           # LangGraph fix loop state machines
│   └── ... (autonomy core files)
│
└── integrations/                  # General framework integrations
    ├── frameworks/                # General framework adapters
    │   ├── autogen.py             # Use Code Scalpel agents in AutoGen
    │   ├── crewai.py              # Use Code Scalpel agents in CrewAI
    │   ├── langgraph.py           # Use Code Scalpel agents in LangGraph
    │   └── ... (other framework adapters)
    └── ...
```

**Key Distinction:**
- `agents/code_review_agent.py` - Code Scalpel's code review agent implementation
- `integrations/frameworks/autogen.py` - Adapter to use Code Scalpel agents in AutoGen
- `autonomy/integrations/autogen.py` - AutoGen workflows for autonomous fix loops

### Tier-Aware Feature Distribution

**COMMUNITY Tier (Free):**
- Base agent framework (OODA loop, context management)
- Core agents (CodeReview, Security, Optimization)
- Basic agent capabilities
- **Total:** 75 TIER 1 features across framework and 3 core agents

**PRO Tier (Commercial):**
- Advanced agents (Refactoring, Testing, Documentation, Metrics)
- Multi-agent coordination
- Agent learning and optimization
- Framework integration adapters
- **Total:** 75 TIER 2 features

**ENTERPRISE Tier (Commercial):**
- Agent federation and governance
- Enterprise security and compliance
- Agent marketplace and certification
- Advanced orchestration
- **Total:** 75 TIER 3 features

### Documentation Quality

**Current State:** ✅ Excellent
- README.md comprehensive (500+ lines with usage examples)
- Each agent has detailed docstrings
- OODA loop pattern well-documented
- Clear examples for each agent type
- Now enhanced with 225+ TODO items (75 per tier)

**Updates Made:**
- Organized existing TODOs into tiers
- Added 75 comprehensive TODOs to `__init__.py`
- Added 150 comprehensive TODOs to `base_agent.py` (AgentContext + OODA loop)
- Framework ready for exhaustive feature expansion

### Migration Steps

**No migration required** - agents/ stays in current location.

**Minor Cleanup:**
- Rename `optimazation_agent.py` → `optimization_agent.py` (typo fix)
- Update imports in `__init__.py`
- Update documentation references

### Breaking Changes

**Minor** - filename rename only:
- `from code_scalpel.agents import OptimizationAgent` (import statement unchanged)
- Internal filename change only (typo correction)

### Priority Assessment

**Priority:** P4 (Low - Filename Typo Fix Only)
- No structural changes needed
- Filename typo fix for consistency
- Document decision rationale for agents/ placement

### Summary

**✅ APPROVED: Keep agents/ as standalone top-level module**

**Rationale:**
- Code Scalpel's own agent implementations, not framework integrations
- Architecturally distinct from integrations/ (internal tooling vs external adapters)
- Clear tier alignment with agent-level feature gating
- Consistent with other standalone modules (pdg_tools, mcp, autonomy, policy_engine)
- Can be used independently or integrated into external frameworks

**✅ APPROVED: Filename typo fix**

**Rationale:**
- optimazation_agent.py → optimization_agent.py
- Improves code professionalism
- No breaking changes (import name unchanged)

**✅ APPROVED: Update Issue 11 recommendation**

**Rationale:**
- Original Issue 11 suggested consolidating agents/, autonomy/, integrations/
- Analysis reveals all three should stay separate with clear boundaries
- Document architectural distinction between internal tooling and framework adapters

---

## Issue 26: Integrations Module (8 files) - Framework Integration Adapters

### Current Location
`src/code_scalpel/integrations/`

### Files Inventoried
```
integrations/
├── __init__.py (120 lines)
├── README.md (215 lines)
├── autogen.py
├── claude.py
├── crewai.py
├── langchain.py
├── rest_api_server.py (616 lines, legacy non-MCP API)
└── __pycache__/
```

### Purpose Analysis

**Primary Purpose:** Framework integration adapters for external AI agent frameworks

**Scope:**
- Framework adapters (AutoGen, CrewAI, LangChain, Claude)
- Legacy REST API server (non-MCP, deprecated in favor of mcp/)
- Integration registry and factory patterns (planned)
- Framework compatibility and capability detection (planned)

**Key Distinction (Critical for Issue 11):**
- `integrations/` = **External framework adapters** (how other frameworks use Code Scalpel)
- `agents/` = **Internal agent implementations** (Code Scalpel's own agents)
- `autonomy/` = **Supervised autonomous repair** (fix loops with safety guarantees)

### Cohesion Assessment

**✅ HIGHLY COHESIVE** - All files serve integration purposes:
- `autogen.py`, `crewai.py`, `langchain.py`, `claude.py` - Framework adapters
- `rest_api_server.py` - Legacy HTTP API (being deprecated, see Issue 11 NOTE)
- `__init__.py` - Integration registry and factory (75 TODOs added)
- `README.md` - Integration documentation (75 TODOs added)

**No Outliers:** All files belong in this module.

### Architectural Clarity

**Boundaries:**
- Does NOT contain Code Scalpel's own agents (those are in agents/)
- Does NOT contain autonomous repair logic (that's in autonomy/)
- Does NOT contain MCP server (that's in mcp/)
- ONLY contains adapters for external frameworks to use Code Scalpel tools

**Relationship to Issue 11:**
Issue 11 originally suggested consolidating agents/, autonomy/, integrations/ based on incomplete information. Analysis reveals:
- `integrations/` = Framework adapters (wrappers around Code Scalpel for external use)
- `agents/` = Agent implementations (Code Scalpel's own OODA loop agents)
- `autonomy/` = Autonomous repair (supervised fix loops with safety)

These are **three distinct concerns** that should remain separate.

### Licensing and Tier Strategy

**Current State:** All files are COMMUNITY tier (no tier markers found)

**Proposed Tier Distribution:**

**COMMUNITY Tier (Free):**
- Base integration framework (registry, factory, config)
- Core framework adapters (AutoGen, LangChain, CrewAI, Claude)
- Integration health checks and status
- Basic documentation and examples
- **Total:** ~25 TIER 1 features (already in __init__.py TODOs)

**PRO Tier (Commercial):**
- Advanced caching, rate limiting, batching
- Middleware and hook systems
- Response filtering and customization
- Monitoring and metrics collection
- **Total:** ~25 TIER 2 features (already in __init__.py TODOs)

**ENTERPRISE Tier (Commercial):**
- Multi-tenancy and isolation
- Enterprise authentication (SAML/SSO)
- Audit logging and compliance
- Distributed coordination
- **Total:** ~25 TIER 3 features (already in __init__.py TODOs)

### Documentation Quality

**Current State:** ✅ Excellent
- README.md comprehensive (215 lines)
- __init__.py has 75 TODOs organized by tier
- Each framework adapter has inline documentation
- REST API server has 75 TODOs for deprecation path

**Enhancement Opportunities:**
- Add README.md TODOs (75 items for documentation expansion)
- Add framework comparison matrix
- Add migration guides between frameworks
- Document REST API deprecation path (favor mcp/)

### rest_api_server.py - Legacy API Deprecation

**Status:** Legacy, non-MCP-compliant HTTP API  
**Future:** Being deprecated in favor of `mcp/` (true MCP protocol)

**Issue 11 Update:** Issue 11 recommends deprecating `rest_api_server.py` in favor of MCP. This is correct. The REST API is a legacy artifact and should be:
1. Marked as deprecated in documentation
2. Maintained for backward compatibility (COMMUNITY tier)
3. Eventually removed in favor of full MCP adoption

**No file movement needed** - deprecation can happen in-place with proper warnings.

### Migration Steps

**No migration required** - integrations/ stays in current location.

**Documentation Updates:**
- Clarify architectural boundaries between integrations/, agents/, autonomy/
- Document REST API deprecation path
- Add tier markers to framework adapters
- Expand README.md with framework comparison

### Breaking Changes

**None** - All files stay in current location.

### Priority Assessment

**Priority:** P0 (Critical - Clarifies Issue 11)

**Rationale:**
- Issue 11's original recommendation to consolidate modules was based on incomplete analysis
- integrations/ analysis reveals distinct architectural concerns
- This clarification prevents incorrect module consolidation
- Preserves clear separation of concerns

### Summary

**✅ APPROVED: Keep integrations/ as standalone top-level module**

**Rationale:**
- Framework integration adapters are distinct from internal agents
- Highly cohesive module with clear boundaries
- Issue 11 recommendation to consolidate modules is **rejected** based on this analysis
- rest_api_server.py deprecation can happen in-place

**✅ APPROVED: Document architectural boundaries**

**Rationale:**
- Clarify integrations/ = external framework adapters
- Clarify agents/ = internal agent implementations
- Clarify autonomy/ = supervised autonomous repair
- Prevents future consolidation confusion

**✅ APPROVED: REST API deprecation strategy**

**Rationale:**
- Mark rest_api_server.py as deprecated
- Favor mcp/ for true MCP protocol
- Maintain for backward compatibility
- Remove in future major version

---

## Issue 27: Governance Module (5 files) - Compliance and Policy Infrastructure

### Current Location
`src/code_scalpel/governance/`

### Files Inventoried
```
governance/
├── __init__.py (69 lines, v3.1.0 unified governance)
├── README.md
├── audit_log.py
├── change_budget.py
├── compliance_reporter.py
└── unified_governance.py (759 lines, v3.1.0 feature)
```

### Purpose Analysis

**Primary Purpose:** Enterprise-grade compliance reporting and unified governance

**Scope:**
- Compliance reporting (v2.5.0 feature)
- Change budgeting (quantitative constraints)
- Unified governance (v3.1.0 - integrates policy + budget + semantic analysis)
- Audit logging (imports from policy_engine.audit_log, not local)
- Role-based policy hierarchy

**Key Feature:** `UnifiedGovernance` (v3.1.0)
- Bridges PolicyEngine + ChangeBudget + SemanticAnalyzer
- FAIL CLOSED security model (errors = DENY)
- Combined violation reporting across policy/budget/semantic
- Support for justified overrides

### Cohesion Assessment

**✅ HIGHLY COHESIVE** - All files serve governance purposes:
- `unified_governance.py` - Main coordination system (v3.1.0)
- `change_budget.py` - Quantitative constraint enforcement
- `compliance_reporter.py` - Compliance metrics and reporting (v2.5.0)
- `audit_log.py` - Imported from policy_engine (not local file)
- `__init__.py` - Exports and coordination

**No Outliers:** All files belong in this module.

### Relationship to Policy Engine

**Important Distinction:**
- `policy_engine/` = Policy definition, OPA/Rego evaluation, semantic analysis
- `governance/` = Compliance reporting, budget enforcement, unified coordination

**Cross-Module Dependencies:**
```python
# governance/ imports from policy_engine/
from code_scalpel.policy_engine.audit_log import AuditLog
from code_scalpel.policy_engine import PolicyEngine
from code_scalpel.policy_engine.semantic_analyzer import SemanticAnalyzer
```

**Architecture:**
- `policy_engine/` = Low-level enforcement mechanisms
- `governance/` = High-level enterprise coordination and reporting

### Verification of Issue 19

**Issue 19 Status:** `config/governance_config.py` → `governance/`

**Current State:** Files in governance/:
- `unified_governance.py` (759 lines)
- `change_budget.py`
- `compliance_reporter.py`

**Question:** Is governance/ ready to receive governance_config.py?

**Answer:** ✅ YES - governance/ is the correct location
- unified_governance.py already handles configuration
- Module is cohesive and well-structured
- Moving governance_config.py here makes architectural sense

**Recommendation:** Proceed with Issue 19 migration as planned.

### Licensing and Tier Strategy

**Current State:** Governance is ENTERPRISE-focused (compliance, audit, budgets)

**Proposed Tier Distribution:**

**COMMUNITY Tier (Free):**
- Basic change budget enforcement
- Simple compliance checks
- Basic audit logging
- **Total:** ~20 TIER 1 features

**PRO Tier (Commercial):**
- Advanced budget strategies
- Role-based policy hierarchy
- Custom compliance rules
- Semantic security integration
- **Total:** ~25 TIER 2 features

**ENTERPRISE Tier (Commercial):**
- Unified governance (full PolicyEngine + Budget + Semantic)
- Multi-tenant isolation
- Compliance reporting (SOC2, HIPAA, GDPR)
- Executive dashboards
- Federated governance
- **Total:** ~30 TIER 3 features

### Documentation Quality

**Current State:** ⚠️ Needs Enhancement
- __init__.py has clear docstring
- unified_governance.py has comprehensive docstring (759 lines)
- README.md exists but needs expansion

**Enhancement Opportunities:**
- Add comprehensive README.md with examples
- Add governance architecture diagram
- Document relationship to policy_engine/
- Add compliance reporting examples
- Create governance configuration guide

### Migration Steps

**No migration required** - governance/ stays in current location.

**Enhancement Tasks:**
1. Add TODO items to governance/ files (75-150 per file)
2. Expand README.md documentation
3. Confirm Issue 19 migration (governance_config.py → governance/)
4. Add tier markers to governance features

### Breaking Changes

**None** - All files stay in current location.

### Priority Assessment

**Priority:** P1 (High - Validates Issue 19)

**Rationale:**
- Confirms governance/ is ready for governance_config.py
- Validates Issue 19 migration recommendation
- Governance is enterprise-critical feature
- Needs documentation expansion

### Summary

**✅ APPROVED: Keep governance/ as standalone top-level module**

**Rationale:**
- Enterprise-grade compliance and governance infrastructure
- Highly cohesive with clear boundaries
- Distinct from policy_engine/ (high-level coordination vs low-level enforcement)
- Ready to receive governance_config.py per Issue 19

**✅ APPROVED: Proceed with Issue 19 migration**

**Rationale:**
- governance/ is architecturally correct location for governance_config.py
- Module structure supports configuration files
- Maintains clear separation from policy_engine/

**⚠️ ENHANCEMENT NEEDED: Expand documentation**

**Rationale:**
- README.md needs comprehensive examples
- Governance architecture needs diagram
- Tier strategy needs documentation
- Add TODO items for feature expansion

---

## Issue 28: Generators Module (3 files) - Code Generation Tools

### Current Location
`src/code_scalpel/generators/`

### Files Inventoried
```
generators/
├── __init__.py (105 lines with 75 TODOs)
├── README.md
├── refactor_simulator.py
└── test_generator.py (1,143 lines with 75 TODOs)
```

### Purpose Analysis

**Primary Purpose:** Code generation capabilities for tests and refactoring

**Scope:**
- Test generation from symbolic execution paths
- Refactor simulation and safety verification
- Code generation templates and registries (planned)
- Multi-language code generation (planned)

**Key Features:**
- `TestGenerator` - Convert Z3 symbolic execution to pytest/unittest
- `RefactorSimulator` - Simulate code changes and verify safety
- Generator factory patterns (planned, 75 TODOs in __init__.py)

### Cohesion Assessment

**✅ HIGHLY COHESIVE** - All files serve code generation purposes:
- `test_generator.py` - Generate unit tests from symbolic paths (1,143 lines)
- `refactor_simulator.py` - Simulate and verify refactoring safety
- `__init__.py` - Generator registry, factory, and infrastructure (75 TODOs)

**No Outliers:** All files belong in this module.

### Architectural Clarity

**Boundaries:**
- Does NOT contain symbolic execution (that's in symbolic_execution_tools/)
- Does NOT contain AST manipulation (that's in ast_tools/)
- ONLY contains code generation from analysis results

**Relationship to Other Modules:**
- Consumes symbolic execution results from `symbolic_execution_tools/`
- Generates code that uses structures from `ast_tools/`
- Coordinates with `security/` for security-focused test generation

### Licensing and Tier Strategy

**Current State:** __init__.py and test_generator.py have 75 TODOs each organized by tier

**Proposed Tier Distribution (from TODO analysis):**

**COMMUNITY Tier (Free):**
- Basic test generation from symbolic paths
- pytest/unittest formatting
- Simple refactor simulation
- Test case validation
- **Total:** 25 TIER 1 features (in __init__.py and test_generator.py)

**PRO Tier (Commercial):**
- Property-based test generation (Hypothesis)
- Mutation testing integration
- Performance regression tests
- Security-focused test generation
- ML-based test prioritization
- **Total:** 25 TIER 2 features

**ENTERPRISE Tier (Commercial):**
- Distributed test generation across agents
- Federated test generation across organizations
- Test generation work queue and load balancing
- Multi-region coordination
- Compliance and audit logging
- **Total:** 25 TIER 3 features

### Documentation Quality

**Current State:** ✅ Good
- __init__.py has comprehensive docstring with 75 TODOs
- test_generator.py has detailed docstring with 75 TODOs
- README.md exists for module overview

**Enhancement Opportunities:**
- Expand README.md with examples
- Add refactor_simulator.py TODO items (currently missing)
- Add code generation patterns guide
- Document symbolic execution integration

### Completeness Analysis

**test_generator.py Analysis:**
- **Comprehensive:** 1,143 lines with full implementation
- **TODOs:** 75 items organized by tier (25 per tier)
- **Coverage:** Likely high given file size and maturity

**refactor_simulator.py Analysis:**
- **Status:** Implementation exists, TODO analysis needed
- **Enhancement:** Add 75 TODOs organized by tier
- **Priority:** P2 (Medium - complete TODO expansion)

### Migration Steps

**No migration required** - generators/ stays in current location.

**Enhancement Tasks:**
1. Add TODO items to refactor_simulator.py (75 items, 25 per tier)
2. Expand README.md with usage examples
3. Add code generation patterns documentation
4. Document integration with symbolic_execution_tools/

### Breaking Changes

**None** - All files stay in current location.

### Priority Assessment

**Priority:** P2 (Medium - Documentation Enhancement)

**Rationale:**
- Module is well-structured and cohesive
- test_generator.py already has comprehensive TODOs
- refactor_simulator.py needs TODO expansion
- Documentation needs enhancement but functionality is complete

### Summary

**✅ APPROVED: Keep generators/ as standalone top-level module**

**Rationale:**
- Code generation is distinct concern from analysis
- Highly cohesive with clear boundaries
- Consistent with other specialized modules
- Well-organized with tier-aware feature planning

**⚠️ ENHANCEMENT NEEDED: Complete TODO expansion**

**Rationale:**
- refactor_simulator.py needs 75 TODOs (25 per tier)
- README.md needs usage examples
- Document integration patterns with symbolic execution

**✅ APPROVED: Tier strategy**

**Rationale:**
- Clear progression from basic (COMMUNITY) to distributed (ENTERPRISE)
- Aligns with product strategy
- Test generation is valuable PRO/ENTERPRISE feature

---

## Issue 29: code_parser/ - Non-Existent Module (Document Error)

### Current Location
**DOES NOT EXIST**

### Discovery
Attempted directory scan: `list_dir("/mnt/k/backup/Develop/code-scalpel/src/code_scalpel/code_parser")`  
Result: `ERROR - ENOENT: no such file or directory`

### Document Error Analysis

**Source of Error:** Listed in "Current Source Structure Analysis" section:
```markdown
├── Feature subdirectories (11 folders):
│   ├── code_parser/
```

**Actual State:** This directory does not exist in the codebase.

### Possible Confusion

**Similar Modules That DO Exist:**
- `polyglot/` - Polyglot parsing infrastructure (TreeSitter-based)
- `ast_tools/` - AST manipulation and analysis
- `parsers/` - **Also doesn't exist** (see Issue 30)

**Hypothesis:** Documentation may have listed planned modules that were never created, or modules that were renamed/consolidated into `polyglot/`.

### Correction Required

**Action:** Remove `code_parser/` from "Current Source Structure Analysis"

**Reasoning:**
- Module does not exist in filesystem
- Listing non-existent modules creates confusion
- Document should reflect actual codebase structure

### Migration Steps

**Document Correction:**
1. Remove `code_parser/` from structure listing
2. Add note that parsing is handled by `polyglot/`
3. Update module count (11 folders → 10 folders)

### Summary

**❌ REJECTED: Module does not exist**

**Rationale:**
- Filesystem confirms directory does not exist
- Document lists non-existent module
- Correction needed for accuracy

**✅ APPROVED: Remove from document**

**Rationale:**
- Document should reflect actual structure
- Parsing functionality exists in polyglot/
- No migration needed (module never existed)

---

## Issue 30: parsers/ - Non-Existent Module (Document Error)

### Current Location
**DOES NOT EXIST**

### Discovery
Attempted directory scan: `list_dir("/mnt/k/backup/Develop/code-scalpel/src/code_scalpel/parsers")`  
Result: `ERROR - ENOENT: no such file or directory`

### Document Error Analysis

**Source of Error:** Listed in "Current Source Structure Analysis" section:
```markdown
├── Feature subdirectories (11 folders):
│   ├── parsers/
```

**Actual State:** This directory does not exist in the codebase.

### Possible Confusion

**Similar Modules That DO Exist:**
- `polyglot/` - Unified polyglot parsing (TreeSitter-based)
- `ast_tools/` - AST manipulation (Python-specific)

**Hypothesis:** parsers/ may have been planned as a generic parsing layer but was consolidated into polyglot/ during development.

### Correction Required

**Action:** Remove `parsers/` from "Current Source Structure Analysis"

**Reasoning:**
- Module does not exist in filesystem
- Parsing functionality consolidated in polyglot/
- Document should reflect actual architecture

### Migration Steps

**Document Correction:**
1. Remove `parsers/` from structure listing
2. Add note that parsing is handled by `polyglot/`
3. Update module count (10 folders → 9 folders after code_parser removal)

### Summary

**❌ REJECTED: Module does not exist**

**Rationale:**
- Filesystem confirms directory does not exist
- Document lists non-existent module
- Parsing handled by polyglot/

**✅ APPROVED: Remove from document**

**Rationale:**
- Document should reflect actual structure
- Functionality exists in polyglot/
- No migration needed (module never existed)

---

## Issue 31: policy/ - Non-Existent Module (Document Error)

### Current Location
**DOES NOT EXIST**

### Discovery
Attempted directory scan: `list_dir("/mnt/k/backup/Develop/code-scalpel/src/code_scalpel/policy")`  
Result: `ERROR - ENOENT: no such file or directory`

### Document Error Analysis

**Source of Error:** Listed in "Current Source Structure Analysis" section:
```markdown
├── Feature subdirectories (11 folders):
│   ├── policy/
```

**Actual State:** This directory does not exist in the codebase.

### Possible Confusion

**Similar Modules That DO Exist:**
- `policy_engine/` - Policy definition, OPA/Rego evaluation, semantic analysis
- `governance/` - Compliance reporting, unified governance

**Hypothesis:** policy/ was likely confused with policy_engine/, or was a planned separation that never materialized.

### Architectural Clarity

**Current Architecture:**
- `policy_engine/` - Low-level policy enforcement (OPA/Rego, semantic analysis)
- `governance/` - High-level enterprise coordination (compliance, budgets, unified governance)

**No need for policy/** - Functionality is properly distributed between policy_engine/ and governance/.

### Correction Required

**Action:** Remove `policy/` from "Current Source Structure Analysis"

**Reasoning:**
- Module does not exist in filesystem
- Policy functionality exists in policy_engine/
- Document should reflect actual architecture

### Migration Steps

**Document Correction:**
1. Remove `policy/` from structure listing
2. Clarify that policy enforcement is in policy_engine/
3. Update module count (9 folders → 8 folders after parsers removal)

### Summary

**❌ REJECTED: Module does not exist**

**Rationale:**
- Filesystem confirms directory does not exist
- Document lists non-existent module
- Policy functionality properly distributed

**✅ APPROVED: Remove from document**

**Rationale:**
- Document should reflect actual structure
- Functionality exists in policy_engine/ and governance/
- No migration needed (module never existed)

---

## Issue 32: polyglot/ → code_parsers/ Absorption

### Header
**Priority:** P1 | **Tier Impact:** ALL TIERS | **Breaking Changes:** Yes (with deprecation)
**Status:** ✅ COMPLETE (Dec 24, 2025) | **Cross-References:** → Issue 1 (parsers deprecation), → Issue 30 (parsers removal)

### Implementation Summary (Completed)
- Created `code_parsers/typescript_parsers/` with 6 files migrated from `polyglot/typescript/`
- Moved `polyglot/extractor.py` → `code_parsers/extractor.py`
- Moved `polyglot/contract_breach_detector.py` → `security/contract_breach_detector.py`
- Added deprecation warnings to `polyglot/__init__.py` with backward-compat aliases
- Updated `code_parsers/__init__.py` with new exports
- All 4,431 tests pass

### Current Location (DEPRECATED)
`src/code_scalpel/polyglot/`
- `__init__.py` - Module exports
- `extractor.py` - PolyglotExtractor, Language enum, detect_language
- `alias_resolver.py` - Bundler/module alias resolution for TS/JS
- `tsx_analyzer.py` - React component detection, JSX analysis
- `contract_breach_detector.py` - Cross-language API contract detection
- `typescript/` - TypeScript-specific parsing and analysis
  - `__init__.py` - TypeScript module exports
  - `parser.py` - TypeScriptParser (tree-sitter stub)
  - `analyzer.py` - TypeScriptAnalyzer (structural analysis)
  - `type_narrowing.py` - Control-flow type narrowing analysis
  - `decorator_analyzer.py` - TypeScript decorator extraction

### Problem Analysis

**Architectural Redundancy:**
- `code_parsers/` has language-specific subdirectories: `python_parsers/`, `java_parsers/`, `javascript_parsers/`, etc.
- `polyglot/` exists as a separate top-level module doing the same thing (multi-language parsing)
- `polyglot/typescript/` should logically be `code_parsers/typescript_parsers/`
- Two modules with overlapping purpose creates confusion

**Current code_parsers Structure:**
```
code_parsers/
├── python_parsers/     ← Python-specific
├── java_parsers/       ← Java-specific  
├── javascript_parsers/ ← JS-specific
├── kotlin_parsers/     ← Kotlin stubs
├── go_parsers/         ← Go stubs
├── ??? typescript_parsers/ ← MISSING (exists in polyglot/typescript/)
└── adapters/           ← IParser adapters
```

### Recommended Migration

**Phase 1: Create typescript_parsers/**
- Create `code_parsers/typescript_parsers/` with files from `polyglot/typescript/`
- Preserve all TODO items with proper tier organization
- Add `alias_resolver.py` and `tsx_analyzer.py` (TypeScript-specific)

**Phase 2: Move extractor.py**
- Move `polyglot/extractor.py` → `code_parsers/extractor.py`
- Update internal imports to use new locations
- Keep PolyglotExtractor name for consistency

**Phase 3: Relocate contract_breach_detector.py**
- Move to `security/contract_breach_detector.py` (security analysis module)
- Cross-language API contract detection is security-adjacent

**Phase 4: Add backward-compat aliases**
- Update `polyglot/__init__.py` with deprecation warnings
- Re-export from new locations with `DeprecationWarning`

**Phase 5: Remove polyglot/ (v3.3.0)**
- After deprecation period, remove `polyglot/` directory entirely
- Update all external documentation

### Migration File Mapping

| Source (polyglot/) | Destination | Notes |
|-------------------|-------------|-------|
| `extractor.py` | `code_parsers/extractor.py` | Core multi-language extraction |
| `alias_resolver.py` | `code_parsers/typescript_parsers/alias_resolver.py` | TS/JS specific |
| `tsx_analyzer.py` | `code_parsers/typescript_parsers/tsx_analyzer.py` | JSX/TSX specific |
| `contract_breach_detector.py` | `security/contract_breach_detector.py` | Security analysis |
| `typescript/parser.py` | `code_parsers/typescript_parsers/parser.py` | TypeScript parser |
| `typescript/analyzer.py` | `code_parsers/typescript_parsers/analyzer.py` | TypeScript analyzer |
| `typescript/type_narrowing.py` | `code_parsers/typescript_parsers/type_narrowing.py` | Type guards |
| `typescript/decorator_analyzer.py` | `code_parsers/typescript_parsers/decorator_analyzer.py` | Decorator support |
| `typescript/__init__.py` | `code_parsers/typescript_parsers/__init__.py` | Module exports |

### Benefits

1. **Single Source of Truth:** All parsers under `code_parsers/`
2. **Consistent Naming:** `code_parsers/{lang}_parsers/` pattern
3. **Simpler Imports:** `from code_scalpel.code_parsers import PolyglotExtractor`
4. **Unified Factory:** `ParserFactory.create("typescript")` works for all languages
5. **Cleaner Tier Boundaries:** Tier decorators apply uniformly

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Import breakage | Backward-compat aliases with deprecation warnings |
| Test failures | Update test imports, run full suite |
| Documentation | Update all examples and guides |
| External users | Deprecation period (v3.2.0 → v3.3.0) |

### Migration Steps

1. Create `code_parsers/typescript_parsers/` directory structure
2. Copy all files from `polyglot/typescript/` with updated imports
3. Move `extractor.py` to `code_parsers/`
4. Move TypeScript utilities (alias_resolver, tsx_analyzer) to typescript_parsers/
5. Move `contract_breach_detector.py` to `security/`
6. Update `polyglot/__init__.py` with deprecation aliases
7. Update `code_parsers/__init__.py` with new exports
8. Update all internal imports across codebase
9. Update test imports
10. Update documentation

### Estimated Effort

| Task | Hours |
|------|-------|
| Create typescript_parsers/ | 1-2 |
| Move extractor.py | 0.5 |
| Move analysis utilities | 0.5 |
| Add deprecation aliases | 0.5 |
| Update internal imports | 2-3 |
| Update tests | 1-2 |
| Update documentation | 1-2 |
| **Total** | **6-10 hours** |

### Summary

**✅ APPROVED: Absorb polyglot/ into code_parsers/**

**Rationale:**
- Eliminates architectural redundancy
- Aligns with existing `{lang}_parsers/` naming convention
- Simplifies imports and factory patterns
- Enables unified tier enforcement

**Phase:** 2 (after Issue 1 - parsers/ deprecation)
**Dependencies:** Issue 1 should complete first to avoid confusion

---

## Detailed Issue Analysis

The following sections provide comprehensive analysis for each of the 31 issues identified in the reorganization effort. Issues are presented in chronological order (1-31) with standardized headers for consistency.

**Issue Header Format:**
```
### Issue N: [Module Name] - [Brief Description]
**Priority:** P0-P4 | **Tier Impact:** COMMUNITY/PRO/ENTERPRISE | **Breaking Changes:** Yes/No
**Status:** KEEP/MOVE/SPLIT/CREATE/REMOVE | **Cross-References:** → Issue M, ← Issue N
```

---

### Previously Listed Summary Table (Replaced by Comprehensive Table Above)

| Issue | Module | Files | Decision | Priority | Rationale |
|-------|--------|-------|----------|----------|-----------|
| 23 | ast_tools | 17 | PARTIAL MOVE | P2 | Move osv_client.py → security/, keep 16 others |
| 24 | autonomy | 12 | KEEP IN PLACE | P4 | Autonomous repair distinct from surgery/integrations |
| 25 | agents | 10 | KEEP IN PLACE | P4 | Internal agents distinct from framework integrations |
| **26** | **integrations** | **8** | **KEEP IN PLACE** | **P0** | **Framework adapters distinct from agents/autonomy** |
| **27** | **governance** | **5** | **KEEP IN PLACE** | **P1** | **Validates Issue 19, needs doc expansion** |
| **28** | **generators** | **3** | **KEEP IN PLACE** | **P2** | **Code generation cohesive, needs TODO expansion** |
| **29** | **code_parser** | **0** | **N/A (DOESN'T EXIST)** | **P3** | **Remove from document** |
| **30** | **parsers** | **0** | **N/A (DOESN'T EXIST)** | **P3** | **Remove from document** |
| **31** | **policy** | **0** | **N/A (DOESN'T EXIST)** | **P3** | **Remove from document** |
| **32** | **polyglot** | **10** | **✅ COMPLETE** | **P1** | **Absorbed into code_parsers/, typescript_parsers/ created** |

---

**Last Updated:** December 24, 2025 (Issue 32 COMPLETE)
