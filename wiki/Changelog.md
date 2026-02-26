# Changelog

All notable changes to Code Scalpel are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.2] - 2026-02-25

### Added

- `unified_sink_detect`: C and C++ sink detection across all tiers
- `generate_unit_tests`: Catch2 + NUnit (Community+), Google Test + xUnit (Pro+)
- `code_policy_check`: clang-tidy rules (Community+), Roslyn analyzers (Community+), MISRA-C compliance (Enterprise only)
- `scan_dependencies`: Conan, vcpkg (C/C++) and NuGet (C#) package manager scanning — all tiers
- Test suite: `tests/languages/test_v202_capabilities.py`

---

## [2.0.1] - 2026-02-25

### Fixed

- Packaging fix: re-release to correct PyPI upload issue with v2.0.0 artifacts
- Documentation: wiki changelog backfill for v1.1.0 through v1.5.0 releases
- VS Code extension version aligned with Python package

---

## [2.0.0] - 2026-02-24

### Polyglot Expansion — C, C++, and C# Full Support

Code Scalpel now supports 7 languages with production-quality parsers for C, C++, and C#.

#### New Language Support

- **C** — full AST extraction, IR normalization, `extract_code`/`update_symbol` support
- **C++** — full support including templates, namespaces, nested classes
- **C#** — full support including properties, interfaces, generics
- 262 language-specific tests; 39 new real-world pattern tests
- 4 normalizer bugs fixed during development

#### Changes

- 23 MCP tools (added `type_evaporation_scan`)
- 7,575+ total tests passing (100% pass rate)
- Pre-release pipeline: black, ruff, pyright, bandit, pytest, build — all passing

#### Full Release Notes

See [RELEASE_NOTES_v2.0.0](https://github.com/3D-Tech-Solutions/code-scalpel/blob/main/docs/release_notes/RELEASE_NOTES_v2.0.0.md)

---

## [1.5.0] - 2026-02-24

### Comprehensive C and C++ Parsing

- **C and C++ parsing** via new `c_normalizer` and `cpp_normalizer` (tree-sitter)
  - `.c`, `.h` (C); `.cpp`, `.cc`, `.cxx`, `.c++`, `.hpp`, `.hxx`, `.hh`, `.h++`, `.inl` (C++)
  - IR nodes for functions, structs, unions, enums, macros, classes, namespaces, templates
  - Language detection heuristics updated to distinguish C vs C++ by content and extension
  - Integrated into `PolyglotExtractor` abstraction
- New tests in `tests/languages/test_c_cpp_parsers.py` (realistic 3D project patterns)

### Deprecated

- `code_scalpel.polyglot` imports replaced by `code_parsers` canonical import path (removal in v3.3.0)

---

## [1.4.1] - 2026-02-24

### Added

- `codescalpel check` command — inspects an existing `.code-scalpel` directory and reports which configuration files are present, missing-but-recommended, or missing-and-required without modifying anything
  - `--json` / `-j` flag for machine-readable output
  - `--fix` / `-F` flag: fills missing files before reporting (equivalent to `init` + `check`)
  - Integrity checking: files are parsed (JSON/YAML/Rego) and flagged if empty or corrupt
- `codescalpel init` is now safe to re-run on existing configurations — adds only absent files, preserves all existing customizations

---

## [1.4.0] - 2026-02-20

### Added

- `response_config.json` and `response_config.schema.json` auto-created on first MCP server boot / `codescalpel init`

### Changed

- **Tier limit rebalancing** (data-driven recalibration):
  - Community: Raised to cover solo dev projects ≤500 files (scanner 50→500, call_graph depth 3→10, nodes 50→200, extract_code depth 0→1, etc.)
  - Pro: All numeric limits now unlimited — differentiates on features not scale caps
  - Enterprise: Fixed `unified_sink_detect.max_sinks` bug (was 50, now unlimited)

### Fixed

- Graph tools now respect `response_config.json` filtering
- Hot reload: edits to `response_config.json` take effect without server restart

### Deprecated

- `ResponseFormatter` class in `response_formatter.py` (removal in v1.5.0)

---

## [1.3.5] - 2026-02-10

### Fixed

- Windows `UnicodeEncodeError` on `codescalpel init` — all file I/O now uses `encoding='utf-8'`
- MCP server auto-init now creates full configuration scaffolding (20 files) instead of empty directory

### Added

- Startup update check: non-blocking PyPI version query notifies users of available updates
- License setup documentation (`docs/LICENSE_SETUP.md`)

### Changed

- **Architectural refactor**: Moved `limits.toml` and `features.toml` from `.code-scalpel/` to `src/code_scalpel/capabilities/` — packaged automatically, no `force-include` needed
- Enhanced MCP server boot banner: shows license tier and license file path

---

## [1.3.4] - 2026-02-05

### Added

- `features.toml`: Bundled TOML source of truth for capability feature sets (66 sections: 22 tools × 3 tiers) — replaces 1600-line hardcoded dict

### Changed

- `config_loader` now uses two-path lookup (bundled wheel copy, dev-checkout fallback) instead of 7-layer search
- `features.py` rewritten as thin loader (~230 lines, down from ~1600)
- `limits.toml` ownership: tier limits are now fully package-managed

### Fixed

- Sentinel conversion: `-1` in TOML now converts to `None` (unlimited) at runtime

---

## [1.3.3] - 2026-02-02

### Changed

- **Project Structure Migration**: Consolidated cache directories into `.code-scalpel/cache/`
  - Migrated `.scalpel_cache/`, `.code_scalpel_cache/`, `.scalpel_ast_cache/` → `.code-scalpel/cache/`
  - Renamed `.code-scalpel/license/` → `.code-scalpel/licenses/`

### Added

- Version sync check in `verify.sh`
- `scripts/verify_version_sync.sh`: Standalone version consistency checker
- `--skip-build` flag for faster iteration in `verify.sh`
- `docs/PIPELINE.md`: Comprehensive CI/CD pipeline documentation

---

## [1.3.2] - 2026-02-02

### Added

- **detect-secrets pre-commit hook** (Yelp/detect-secrets v1.4.0) with `.secrets.baseline`

### Changed

- Security hardening: Added 40+ `.gitignore` patterns blocking API tokens, credentials, vault files

---

## [1.3.1] - 2026-02-01

### Changed

- Pre-commit hook changed from `verify.sh` (comprehensive) to `verify_local.sh` (fast auto-fix)
- Black/Ruff path alignment: checks only `src/ tests/` (matching CI)

### Added

- Optional Bandit and pip-audit as warning-only checks in `verify_local.sh`

---

## [1.3.0] - 2026-02-01

### Added

- **Oracle Resilience Middleware** — automatic error recovery for AI agent mistakes
  - `@with_oracle_resilience` decorator for MCP tools
  - Symbol fuzzy matching with Levenshtein distance (typo correction, e.g., `"procss_data"` → `"process_data"`)
  - Path resolution with workspace-aware suggestions
  - Multiple recovery strategies: `SymbolStrategy`, `PathStrategy`, `SafetyStrategy`, `CompositeStrategy`
- 61 comprehensive Oracle middleware tests (100% pass rate)

### Changed

- Moved documentation to organized subdirectories (`docs/oracle/`, `docs/reference/`, `docs/architecture/`)

---

## [1.2.1] - 2026-01-26

### Fixed

- **UVX entry point**: Fixed missing `codescalpel` entry point that prevented `uvx codescalpel` from working
  - v1.1.0 regression: package was renamed to `codescalpel` on PyPI but only had `code-scalpel` entry point
  - Both `codescalpel` and `code-scalpel` commands now available

---

## [1.2.0] - 2026-01-26

### Added

- **Project Awareness Engine**: Intelligent codebase analysis subsystem
  - `ProjectWalker`: Fast file discovery with smart filtering (9+ languages, 19 default exclusions)
  - `ProjectContext`: Metadata storage with in-memory and optional SQLite caching
  - `ParallelCrawler`: Parallel file scanning via `ThreadPoolExecutor` (batch size 100, supports 100k+ files; Pro/Enterprise)
  - `IncrementalIndex`: Incremental project updates with dependency-aware cascading invalidation
- 39 comprehensive tests for Project Awareness Engine

---

## [1.1.0] - 2026-01-26

### Added

- Phase 6 Kernel Integration for `analyze_code` tool
- `SourceContext` model for unified input handling
- `SemanticValidator` for pre-analysis input validation
- `ResponseEnvelope` with metadata and tier information
- `UpgradeHints` for tier-based feature suggestions

### Fixed

- Package name corrected in `pyproject.toml` (`code-scalpel` → `codescalpel`) for PyPI compatibility

---

## [1.0.1] - 2025-01-25

### Added

- Tier-based request/response governance (Community/Pro/Enterprise)
- Parameter clamping with applied limits metadata
- Installation guide for Claude Desktop (`INSTALLING_FOR_CLAUDE.md`)

### Fixed

- Version synchronization: `__init__.py` now matches `pyproject.toml`
- Deprecated `datetime.datetime.now()` → `datetime.now(timezone.utc)` in licensing module

---

## [1.0.0] - 2026-01-17

### Initial Public Release 🎉

Code Scalpel is an MCP server toolkit that enables AI assistants to perform surgical code operations through AST parsing, taint analysis, and symbolic execution.

### Features

#### Code Extraction & Modification (3 tools)

- **`extract_code`** - Surgically extract functions/classes (99% token reduction)
  - File path-based extraction (server reads file)
  - Support for Python, JavaScript/TypeScript, Java
  - Optional cross-file dependency resolution
  - Token count estimates
- **`update_symbol`** - Safe, atomic symbol replacement
  - Automatic backup creation
  - Syntax validation
  - Preserves surrounding code
- **`rename_symbol`** - Consistent renaming across references
  - Updates definition and all call sites
  - Multi-file support

#### Code Analysis (6 tools)

- **`analyze_code`** - Parse structure: functions, classes, imports, complexity
  - Multi-language support
  - Cyclomatic complexity calculation
  - Import analysis
- **`get_file_context`** - Quick overview without full read
  - Lists functions, classes, imports
  - Complexity score
  - Security warnings
- **`crawl_project`** - Comprehensive project-wide analysis
  - All files scan
  - Metrics aggregation
  - Complexity hotspot detection
- **`get_project_map`** - Multi-language project structure
  - Directory tree mapping
  - Entry point detection
  - Language distribution
- **`scan_dependencies`** - Dependency analysis and CVE checking
  - Python (pip), JavaScript (npm), Java (Maven/Gradle)
  - Known vulnerability detection
  - Version checking
- **`get_graph_neighborhood`** - Extract k-hop subgraphs
  - Prevents graph explosion on large codebases
  - Configurable hop distance
  - Mermaid diagram generation

#### Code Navigation (3 tools)

- **`get_call_graph`** - Function relationships and dependencies
  - Intra-file call tracking
  - Entry point detection
  - Circular import detection
  - Mermaid diagram visualization
- **`get_cross_file_dependencies`** - Import resolution across files
  - Direct and transitive dependencies
  - Dependency graph generation
  - Circular dependency detection
- **`get_symbol_references`** - Find all usages of symbols
  - Definition location
  - All reference sites with context
  - Line and column numbers

#### Security Analysis (4 tools)

- **`security_scan`** - Taint-based vulnerability detection
  - Detects 12+ CWE types:
    - CWE-89: SQL Injection
    - CWE-78: Command Injection
    - CWE-79: Cross-Site Scripting (XSS)
    - CWE-22: Path Traversal
    - CWE-94: Code Injection
    - CWE-90: LDAP Injection
    - CWE-611: XML External Entity (XXE)
    - CWE-918: SSRF
    - CWE-601: Open Redirect
    - CWE-502: Insecure Deserialization
    - CWE-798: Hardcoded Credentials
    - CWE-327: Weak Cryptography
  - Taint flow tracing
  - Confidence scoring
- **`cross_file_security_scan`** - Track taint across modules
  - Multi-file vulnerability detection
  - Cross-boundary taint tracking
  - Defense against split-code attacks
- **`unified_sink_detect`** - Polyglot dangerous function detection
  - Multi-language sink identification
  - CWE mapping
  - Confidence scoring
- **`type_evaporation_scan`** - TypeScript/Python type boundary issues
  - Detects type system evaporation at serialization
  - Frontend/backend correlation
  - JSON boundary analysis

#### Testing & Verification (4 tools)

- **`generate_unit_tests`** - Auto-generate tests from symbolic execution
  - pytest and unittest framework support
  - Path-based test generation
  - Edge case coverage
- **`symbolic_execute`** - Z3-based path exploration
  - All execution paths discovery
  - Constraint solving
  - Loop unrolling
- **`simulate_refactor`** - Verify changes before applying
  - Security impact analysis
  - Structural change detection
  - Behavior preservation check
- **`code_policy_check`** - Compliance and style checking
  - Basic anti-patterns (Community)
  - Security patterns (Pro)
  - Compliance standards: HIPAA, SOC2, GDPR, PCI-DSS (Enterprise)

#### Utilities (2 tools)

- **`validate_paths`** - Security boundary enforcement
  - Path traversal protection
  - Symbolic link restriction
  - Docker volume boundary enforcement
- **`verify_policy_integrity`** - Cryptographic verification
  - HMAC-SHA256 signatures
  - Tamper detection
  - Fail-closed security model

### Tier System

- **Community** (MIT License, Free)
  - All 22 tools available
  - Baseline limits (50 findings, 100 refs, 500 nodes)
  - Full AST + PDG + symbolic execution
  
- **Pro** (Commercial)
  - Unlimited findings
  - Cross-file security scanning
  - Advanced metrics
  - Custom rules
  
- **Enterprise** (Commercial)
  - All Pro features
  - Compliance reporting (HIPAA, SOC2, GDPR, PCI-DSS)
  - PDF certificates
  - Audit trails
  - SLA support

### Supported Languages

- **Python** - Full support (AST + PDG + symbolic execution + taint analysis)
- **JavaScript/TypeScript** - Full AST + call graphs + extraction + type evaporation detection
- **Java** - AST parsing + method extraction + Maven/Gradle dependency parsing
- **Go** - AST parsing via tree-sitter
- **Rust** - AST parsing via tree-sitter
- **Ruby** - AST parsing via tree-sitter
- **PHP** - AST parsing via tree-sitter

### MCP Transports

- **stdio** - VS Code, GitHub Copilot, Claude Desktop, Cursor
- **HTTP** - Remote servers, team deployments
- **SSE** - Web-based AI assistants
- **Docker** - Containerized environments

### Infrastructure

- **FastMCP** - MCP protocol implementation
- **tree-sitter** - Multi-language parsing
- **esprima** - JavaScript/TypeScript parsing
- **Z3 theorem prover** - Symbolic execution
- **Sigstore/Cosign** - Release artifact signing

### Documentation

- Complete GitHub Wiki
- 22 tool reference pages
- Security policy
- Architecture documentation
- 20+ code examples
- Troubleshooting guide
- Contributing guide

### Testing

- **7,100+ tests** across:
  - Unit tests
  - Integration tests
  - Per-tool tests
  - Security tests
  - MCP protocol tests
- **≥90% code coverage**
- Mutation testing
- Fuzz testing

### Quality Gates

- ✅ Ruff linting (100% pass)
- ✅ Black formatting (88 char line length)
- ✅ Pyright type checking (strict mode)
- ✅ SBOM generation
- ✅ Dependency vulnerability scanning (OSV/pip-audit)
- ✅ Release artifact signing

---

## [0.3.0] - 2025-12-18 (Pre-Release)

### Added

- Policy integrity verification with HMAC-SHA256
- Cryptographic manifest signing
- Sandbox execution mode
- Tier-based limits enforcement
- JWT license validation
- Cross-file dependency resolver
- React component extraction (JSX/TSX)

### Changed

- Refactored security analyzers to new directory structure
- Improved taint analysis accuracy
- Enhanced error messages

### Fixed

- Circular import detection
- Memory leaks in AST caching
- Type checking errors with external libraries

---

## [0.2.0] - 2025-11-15 (Pre-Release)

### Added

- Symbolic execution engine with Z3
- Unit test generation from execution paths
- Type evaporation scanner for TypeScript/Python
- Call graph visualization with Mermaid
- Cross-file security scanning

### Changed

- Optimized AST parsing performance (60% faster)
- Improved token efficiency in extraction

### Fixed

- False positives in SQL injection detection
- Path traversal on Windows
- Unicode handling in code extraction

---

## [0.1.0] - 2025-10-01 (Pre-Release)

### Added

- Initial MCP server implementation
- Basic extraction tools (extract_code, update_symbol, rename_symbol)
- Security scanning with taint analysis
- Python AST parsing
- JavaScript/TypeScript support via esprima
- Basic tier system

---

## Future Roadmap

### v2.1.0 (Planned)

- [ ] Enhanced Java support (PDG + taint analysis)
- [ ] Go language support (AST + basic analysis)
- [ ] Kotlin and Swift language support
- [ ] GraphQL API support
- [ ] Enhanced compliance reporting
- [ ] Custom sink/source definitions

### v3.0.0 (Planned)

- [ ] Multi-repository analysis
- [ ] Distributed scanning
- [ ] Team collaboration features
- [ ] Advanced IDE integrations
- [ ] Remove deprecated `code_scalpel.polyglot` module

---

## Version History

| Version | Date | Key Features |
|---------|------|--------------|
| **2.0.0** | 2026-02-24 | C, C++, C# support; 23 tools; 7,575+ tests |
| 1.5.0 | 2026-02-24 | C/C++ parsing foundation |
| 1.4.1 | 2026-02-24 | `codescalpel check` command |
| 1.4.0 | 2026-02-20 | Response config, tier rebalancing |
| 1.3.x | 2026-02-01–10 | Oracle resilience, security hardening, Windows fixes |
| 1.2.x | 2026-01-26 | Project awareness engine, UVX entry point fix |
| 1.1.0 | 2026-01-26 | Kernel integration, package name fix |
| 1.0.1 | 2025-01-25 | Tier governance, Claude Desktop guide |
| **1.0.0** | 2026-01-17 | Initial public release, 22 tools |
| 0.3.0 | 2025-12-18 | Policy enforcement, tier system |
| 0.2.0 | 2025-11-15 | Symbolic execution, test generation |
| 0.1.0 | 2025-10-01 | Initial pre-release |

---

## Upgrade Guide

### From 0.3.0 to 1.0.0

**Breaking Changes:**
- None (backward compatible)

**New Features:**
- All 23 tools now publicly available
- Enhanced documentation (GitHub Wiki)
- Improved error messages

**Migration:**
```bash
pip install --upgrade code-scalpel
```

**Configuration Changes:**
No configuration changes required. Existing `.env` files compatible.

---

## Release Notes Archive

Detailed release notes and changelogs are available at:
- **GitHub Releases:** https://github.com/3D-Tech-Solutions/code-scalpel/releases
- **Release Artifacts:** `release_artifacts/vX.Y.Z/`

---

**For support:** time@3dtechsolutions.us  
**Security issues:** See [Security Policy](Security)

