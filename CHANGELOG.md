# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Smart path suggestions for file resolution
- Cache invalidation strategies (TTL-based)
- Parallel file scanning for large projects
- Incremental project updates
- Custom language profile support
- Language Server Protocol (LSP) integration

---

## [1.3.3] - 2026-02-02

### Changed
- **Project Structure Migration**: Consolidated scattered cache directories into `.code-scalpel/cache/`
  - Migrated `.scalpel_cache/`, `.code_scalpel_cache/`, `.scalpel_ast_cache/` → `.code-scalpel/cache/`
  - Renamed `.code-scalpel/license/` → `.code-scalpel/licenses/`
  - Cleaned up temporary directories (`.tmp_tier_comm/`, `.tmp_tier_fallback/`)
  - Updated all runtime cache path references in source code
- **verify.sh Step Numbering**: Fixed inconsistent step numbering (was 1/4, 3/8, 5/8... now consistent 1/11 through 11/11)
- **verify.sh Header Documentation**: Added comprehensive header with purpose, runtime, prerequisites, and usage

### Added
- **Version Sync Check**: Pre-check in `verify.sh` detects version mismatches between `pyproject.toml` and `__init__.py`
- **`scripts/verify_version_sync.sh`**: Standalone version consistency checker
- **`--skip-build` Flag**: `verify.sh` now supports `--skip-build` to skip expensive build check during iteration
- **`scripts/migrate_project_structure.sh`**: One-time migration script for project structure consolidation
- **`docs/PIPELINE.md`**: Comprehensive CI/CD pipeline documentation covering all three validation tiers
- **`tests/README.md`**: Test suite organization guide with category descriptions and usage examples
- **Troubleshooting Docs**: Added detect-secrets, version sync, and --skip-build troubleshooting to `docs/DEVELOPMENT.md`
- **Navigation Links**: Updated `docs/README.md` with links to MCP tools reference, pipeline docs, and development workflow

### Fixed
- Version mismatch between `pyproject.toml` (1.3.2) and `src/code_scalpel/__init__.py` (was 1.3.0, now synced)

---

## [1.3.2] - 2026-02-02

### Changed
- **Security Hardening**: Added 40+ `.gitignore` patterns blocking API tokens, credentials, vault files, environment configs, and CI/CD artifacts

### Added
- **detect-secrets Pre-commit Hook**: Yelp/detect-secrets v1.4.0 integration with `.secrets.baseline`
- **`.gitignore` Security Sections**: API tokens, environment variants, vault management, CI/CD artifacts, test credentials

### Fixed
- Redacted exact JWT file paths and vault key names from `docs/GITHUB_SECRETS.md`
- Removed broken license examples from documentation (pointed to licensing team)

---

## [1.3.1] - 2026-02-01

### Changed
- **Black/Ruff Path Alignment**: Fixed `verify_local.sh` to check only `src/ tests/` (matching CI), not entire repo
- **Pre-commit Hook Speed**: Changed pre-commit hook from `verify.sh` (comprehensive) to `verify_local.sh` (fast auto-fix)

### Added
- **Documentation Validation Steps**: Added Steps 9-11 to `verify.sh` for MCP tools reference and docs sync validation
- **Optional Security Checks**: Added Bandit and pip-audit as warning-only checks in `verify_local.sh`

---

## [1.3.0] - 2026-02-01

### Added
- **Oracle Resilience Middleware**: Automatic error recovery for AI agent mistakes
  - `@with_oracle_resilience` decorator for MCP tools
  - Symbol fuzzy matching with Levenshtein distance (typo correction)
  - Path resolution with workspace-aware suggestions
  - `SymbolStrategy`: Recovers from symbol name typos (e.g., "procss_data" → "process_data")
  - `PathStrategy`: Recovers from path errors with intelligent suggestions
  - `SafetyStrategy`: Validates refactoring operations
  - `NodeIdFormatStrategy`: Recovers from node ID format errors
  - `MethodNameFormatStrategy`: Recovers from method name format errors
  - `CompositeStrategy`: Chain multiple strategies for complex recovery
- **Stage 2 Error Enhancement**: Oracle now enhances both `envelope.error` and `data.error` patterns
  - `_enhance_error_envelope()`: Processes top-level envelope errors
  - `_enhance_data_error()`: Processes nested data.error patterns
  - Consistent error enhancement across all error locations
- 61 comprehensive Oracle middleware tests (100% pass rate)
- Tier isolation tests verifying Oracle behavior across Community/Pro/Enterprise

### Changed
- Updated test suite to handle Oracle-enhanced `ToolError` objects
  - Added `get_error_message()` helper for backward-compatible error checking
  - Tests now work with both string errors and `ToolError` objects
- Moved documentation to organized subdirectories:
  - Oracle docs → `docs/oracle/`
  - Docstring analysis → `docs/reference/`
  - Architecture docs → `docs/architecture/`
- Cleaned up root directory (removed 10+ markdown files to proper locations)

### Fixed
- Black formatting exclusion for `tests/mcp_tool_verification/` (intentionally broken test files)
- Unused imports in test files cleaned up
- `envelope.error` check now uses `model_dump()` for proper Pydantic v2 handling

### Documentation
- Added Oracle Resilience documentation suite:
  - `docs/oracle/ORACLE_INTEGRATION_GUIDE.md` - Complete integration guide
  - `docs/oracle/ORACLE_RESILIENCE_QUICKSTART.md` - Quick start guide
  - `docs/oracle/ORACLE_COMPREHENSIVE_ANALYSIS.md` - Deep dive analysis
  - `docs/ORACLE_RESILIENCE_IMPLEMENTATION.md` - Implementation details
  - `docs/ORACLE_RESILIENCE_TEST_CASES.md` - Test case documentation

---

## [1.2.1] - 2026-01-26

### Fixed
- **UVX Entry Point**: Fixed missing `codescalpel` entry point that prevented `uvx codescalpel` from working
  - v1.1.0 regression: package was renamed to `codescalpel` on PyPI but only had `code-scalpel` entry point
  - Both `codescalpel` and `code-scalpel` commands now available and work identically
  - Verified backward compatibility: all CLI tests pass
  - Fixes deployment for MCP via stdio, HTTP(S), and Docker

---

## [1.2.0] - 2026-01-26

### Added
- **Project Awareness Engine**: New subsystem for intelligent codebase analysis
  - `ProjectWalker`: Fast file discovery with smart filtering (530 lines)
    - 9+ language detection (Python, JS, TS, Java, C++, C#, Ruby, Go, Rust)
    - 19 default exclusion patterns with custom override support
    - Symlink cycle detection using inode tracking
    - Optional .gitignore support
    - Token estimation for context sizing
  - `ProjectContext`: Metadata storage and intelligent caching (514 lines)
    - Directory classification (source, test, build, docs, vendor, config)
    - File importance scoring (0.0-1.0 scale)
    - In-memory and optional SQLite caching
    - Change detection via MD5 hashing
  - `FileInfo`, `DirectoryInfo`, `ProjectMap` data classes
  - `DirectoryType` enum for semantic directory classification
  - All language extension constants exported from analysis module
- Comprehensive documentation: `docs/PROJECT_AWARENESS_ENGINE.md` (473 lines)
  - Quick start guide with 3+ code examples
  - Complete API reference
  - Performance benchmarks
  - 5+ real-world use cases
  - Integration patterns

### Changed
- **ProjectCrawler Refactoring**: Now uses ProjectWalker for file discovery
  - Eliminated 51 lines of duplicate gitignore handling
  - Single source of truth for file discovery
  - 100% backward compatible with existing code

### Testing
- Added 39 comprehensive tests for Project Awareness Engine (100% pass rate)
- All 31 existing ProjectCrawler tests continue to pass
- Performance benchmarking for large project structures
- Symlink cycle handling verification

### Documentation
- Added PROJECT_AWARENESS_ENGINE.md with complete feature documentation
- Updated ARCHITECTURE_IMPLEMENTATION.md references
- Added code examples for all major use cases
- Performance characteristics and scaling notes

### Performance
- File discovery time for 1,000 files: ~50ms
- Memory consumption: ~2MB per 1,000 files
- Symlink cycle detection: O(1) per traversal

---

## [1.1.0] - 2026-01-26

### Added
- Phase 6 Kernel Integration for `analyze_code` tool
- SourceContext model for unified input handling
- SemanticValidator for pre-analysis input validation
- ResponseEnvelope with metadata and tier information
- UpgradeHints for tier-based feature suggestions
- Self-correction support for AI agents

### Changed
- `analyze_code` now uses hybrid kernel architecture
- Enhanced response metadata with version tracking and duration metrics
- Improved error handling with structured error responses

### Fixed
- Package name corrected in pyproject.toml (code-scalpel → codescalpel) for PyPI compatibility
- All documentation updated to reflect correct package name

### Security
- Backward compatible with all existing tools (no breaking changes)
- Hybrid architecture allows gradual kernel adoption across tool suite

---

## [1.0.2] - TBD

### Planned Release Improvements
- Enhanced publication automation
- Streamlined release process documentation
- Multi-platform release verification
- Release notes best practices

**Status**: Planning phase

---

## [1.0.1] - 2025-01-25

### Added
- Tier-based request/response governance (Community/Pro/Enterprise)
- Parameter clamping with applied limits metadata
- Comprehensive refactor validation report
- Installation guide for Claude Desktop (INSTALLING_FOR_CLAUDE.md)
- Release guide documentation (RELEASING.md)
- Release notes template for future releases (RELEASE_NOTES_TEMPLATE.md)
- Enhanced backward compatibility documentation (STABLE PUBLIC API designation)

### Fixed
- Version synchronization: __init__.py now matches pyproject.toml (1.0.1)
- Deprecated datetime.datetime.now() → datetime.now(timezone.utc) in licensing module (6 locations)
- Removed version mismatch between package version strings

### Changed
- Enhanced polyglot module deprecation notice with v3.3.0 timeline
- Improved error handling consistency across all 22 MCP tools
- Better tier enforcement validation with get_tool_capabilities()

### Documentation
- Added REFACTOR_VALIDATION_REPORT.md with tool compliance matrix (100% pass rate)
- Enhanced stability markers for backward-compatible exports
- Clear deprecation timelines (v2.0.0, v3.3.0)
- Comprehensive MCP protocol compliance documentation

### Verified
- All 22 tools pass 13-point compliance criteria (100%)
- Zero duplicate implementations (old + new)
- Zero deprecated imports in active source code
- All helper functions properly mapped

**Release Date**: 2025-01-25
**See also**: [RELEASE_NOTES_v1.0.1.md](docs/release_notes/RELEASE_NOTES_v1.0.1.md)

---

## [1.0.0] - 2026-01-17

### Initial Public Release

Code Scalpel is an MCP server toolkit that enables AI assistants to perform surgical code operations through AST parsing, taint analysis, and symbolic execution.

### Features

#### Code Analysis (6 tools)
- **`analyze_code`** - Parse code structure: functions, classes, imports, complexity metrics
- **`get_file_context`** - Quick file overview without reading full content
- **`crawl_project`** - Comprehensive project-wide analysis
- **`get_project_map`** - Multi-language project structure mapping
- **`scan_dependencies`** - Dependency analysis and version checking
- **`get_graph_neighborhood`** - Extract k-hop subgraphs around code symbols

#### Code Navigation (3 tools)
- **`get_call_graph`** - Function call relationships and dependencies
- **`get_cross_file_dependencies`** - Import resolution across files
- **`get_symbol_references`** - Find all usages of functions, classes, variables

#### Security Analysis (4 tools)
- **`security_scan`** - Taint-based vulnerability detection (SQL injection, XSS, etc.)
- **`cross_file_security_scan`** - Track taint flow across module boundaries
- **`unified_sink_detect`** - Polyglot dangerous function detection with CWE mapping
- **`type_evaporation_scan`** - Detect TypeScript/Python type boundary vulnerabilities

#### Code Extraction & Modification (3 tools)
- **`extract_code`** - Surgically extract functions/classes (99% token reduction)
- **`update_symbol`** - Safe, atomic symbol replacement with backup
- **`rename_symbol`** - Consistent renaming across definition and references

#### Testing & Verification (4 tools)
- **`generate_unit_tests`** - Symbolic execution generates tests for all paths
- **`symbolic_execute`** - Z3-based path exploration and constraint solving
- **`simulate_refactor`** - Verify code changes are safe before applying
- **`code_policy_check`** - Automated compliance and style checking

#### Utilities (2 tools)
- **`validate_paths`** - Security boundary enforcement for file access
- **`verify_policy_integrity`** - Cryptographic policy file verification

### Tier System

- **Community** - Free access to all 22 tools with baseline capabilities
- **Pro** - Unlimited findings, cross-file analysis, advanced features
- **Enterprise** - Compliance reporting, custom policies, audit trails

### Supported Languages

- Python (full AST + PDG + symbolic execution)
- JavaScript/TypeScript (AST + basic analysis)
- Java (AST parsing)
- Go, Rust, Ruby, PHP (AST parsing via tree-sitter)

### MCP Transports

- **stdio** - VS Code, GitHub Copilot, Claude Desktop
- **HTTP/SSE** - Remote servers, team deployments
- **Docker** - Isolated environments, CI/CD pipelines
