# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v1.2.0
- Project Awareness Engine (ProjectWalker + ProjectContext)
- Smart codebase scanning for large projects
- Symlink loop detection and handling
- Performance optimizations for agent context windows

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
