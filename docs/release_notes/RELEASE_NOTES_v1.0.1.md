# Release Notes - v1.0.1 (2025-01-25)

## Overview

v1.0.1 is a stabilization and hardening release focusing on proper tier-based governance, comprehensive validation, and production-ready refactoring completion. All 22 MCP tools have been validated to ensure correctness, deprecation handling, and protocol compliance.

---

## Features & Enhancements

### 🎯 Tier-Based Request/Response Governance

Implemented comprehensive tier-aware governance across all 22 MCP tools:

- **Community Tier**: Base functionality with strict numeric limits
  - file_size: 1 MB, depth: 3, max_files: 100, findings: 50
  - Basic language support (Python full, JS/TS/Java basic)
  - No advanced analysis features

- **Pro Tier**: Enhanced capabilities with mid-range limits
  - file_size: 10 MB, depth: 50, max_files: unlimited, findings: unlimited
  - Extended language support with sanitizer recognition
  - Advanced analysis features enabled

- **Enterprise Tier**: Full capabilities with no limits
  - file_size: 100 MB, unlimited depth/files/findings
  - All languages supported with full analysis
  - Custom policies and compliance frameworks

### 📊 Limit Enforcement & Parameter Clamping

- Automatic parameter clamping when requests exceed tier limits
- Applied limits metadata in all tool responses indicating what was clamped
- Neutral upgrade hints without marketing language
- Clear communication of limits via `response_config.json` filtering

### 🔧 MCP Tool Refactoring (v1.0.1 Completion)

All 22 tools follow the correct refactoring pattern:

**Pattern A - make_envelope (17 tools)**:
- `@mcp.tool()` decorator with thin wrapper
- Helper functions in `helpers/*_helpers.py`
- Async/sync separation via `asyncio.to_thread()`
- Returns `ToolResponseEnvelope` with tier, duration_ms, and error handling

**Pattern B - envelop_tool_function (5 graph tools)**:
- Wrapper decorator handles envelope, timing, errors
- Tools: `get_call_graph`, `get_graph_neighborhood`, `get_project_map`, `get_cross_file_dependencies`, `cross_file_security_scan`
- Same response contract and tier enforcement

### 📝 Backward Compatibility

Enhanced stability documentation for all backward-compatible re-exports:
- Explicitly marked as "STABLE PUBLIC API"
- 22 tool re-exports guaranteed through v2.0.0+
- 2+ release deprecation cycle required for removal
- Clear guidance for external users

### ⚠️ Deprecation Roadmap

Clear deprecation timelines for legacy code:
- **polyglot module**: Marked for removal in v3.3.0
  - Migration guide: `code_parsers/` as replacement
  - v3.1.x: Intense warnings
  - v3.2.x: Critical warnings
  - v3.3.0: Removal
- **Shim files** (8 deprecated files): Timeline v2.0.0+ (after migration period)
- **Contract fields**: `upgrade_url` field → removal planned v2.0.0

---

## Bug Fixes

### 🔧 Version Synchronization
- Fixed mismatch between `__init__.py` ("1.0.0") and `pyproject.toml` ("1.0.1")
- Verified `vscode-extension/package.json` in sync
- Implemented automated version syncing in release process

### 🕐 Datetime Timezone Issues
- Fixed deprecated `datetime.datetime.now()` → `datetime.now(timezone.utc)` in licensing module:
  - `licensing/jwt_generator.py:351`
  - `licensing/jwt_validator.py:72,78`
  - `licensing/license_manager.py:39`
  - `licensing/validator.py:52,58`
- All timestamp generation now timezone-aware

### 📋 Refactoring Completion
- Validated all 22 tools pass 13-point compliance criteria (100% pass rate)
- Confirmed zero duplicate implementations (old + new)
- Verified zero deprecated imports in active source code
- Inventory of all deprecated code with clear recommendations

---

## Documentation Improvements

### 📖 New Documentation Files
- **REFACTOR_VALIDATION_REPORT.md** (382 lines)
  - Complete validation of v1.0.1 refactoring
  - Tool compliance matrix showing 100% pass rate
  - Deprecated code inventory with recommendations
  - Cleanup action items for future releases

- **Enhanced polyglot deprecation notice**
  - Clear "REMOVAL SCHEDULED FOR v3.3.0" warning at module top
  - Timeline breakdown: v3.1.x → v3.2.x → v3.3.0
  - Migration guide with old vs new import paths

- **Stability documentation in server.py**
  - "BACKWARD-COMPATIBLE RE-EXPORTS (STABLE PUBLIC API)" section
  - Explicit "DO NOT REMOVE without 2+ release deprecation cycle"
  - Clear communication that external users depend on these

### 📚 Updated Documentation
- Added tier governance details to each tool's documentation
- Documented applied_limits metadata in response envelopes
- Clear examples of tier-based feature availability
- Updated README with clarity on installation methods

---

## Technical Details

### MCP Protocol Enhancements
- All tool responses include `tier` field (community/pro/enterprise)
- All tool responses include `applied_limits` metadata (what was clamped)
- Consistent error handling with `ToolError` wrapping
- Response envelope version tracking via `tool_version`

### Tool Compliance Matrix
**All 22 Tools Status**: ✅ PASS (100%)

**Tool Categories**:
- **Analysis & Understanding** (4 tools): analyze_code, get_file_context, get_symbol_references, crawl_project
- **Code Extraction** (3 tools): extract_code, rename_symbol, update_symbol
- **Graph & Architecture** (5 tools): get_call_graph, get_cross_file_dependencies, get_graph_neighborhood, get_project_map, scan_dependencies
- **Security & Safety** (5 tools): security_scan, cross_file_security_scan, unified_sink_detect, type_evaporation_scan, code_policy_check
- **Surgical Refactoring** (4 tools): simulate_refactor, symbolic_execute, generate_unit_tests
- **Policy & Infrastructure** (2 tools): verify_policy_integrity, validate_paths

### Configuration Files
- **.code-scalpel/limits.toml**: All 22 tools configured with Community/Pro/Enterprise limits
- **licensing/features.py**: Capability definitions aligned with tier governance
- **.code-scalpel/response_config.json**: Field filtering configured per tool

---

## Breaking Changes

**None** - v1.0.1 is fully backward compatible with v1.0.0

---

## Known Issues

None at this time. All identified issues have been resolved.

---

## Contributors

Code Scalpel Team

---

## Installation

### From PyPI
```bash
pip install codescalpel==1.0.1
```

### From GitHub
```bash
pip install git+https://github.com/3D-Tech-Solutions/code-scalpel.git@v1.0.1
```

### Via UVX (Recommended for Claude Desktop)
```bash
uvx codescalpel mcp
```

---

## Support

For issues, questions, or feature requests, please visit:
- GitHub Issues: https://github.com/3D-Tech-Solutions/code-scalpel/issues
- Documentation: https://github.com/3D-Tech-Solutions/code-scalpel#documentation

---

## Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for complete version history.
