# Code Scalpel v3.2.8 — Release Notes

## Summary

v3.2.8 advances the V1.0 production-ready architecture by introducing (1) real per-tier feature splitting for project-wide tools, (2) a universal response envelope + error-code contract for all MCP tools, and (3) open-core distribution separation with runtime tier enforcement.

## Highlights

- Per-tier behavior splitting for expensive/project-wide tools (Community vs Pro/Enterprise)
- Universal response envelope for all MCP tool responses with structured error codes
- Standardized, machine-parseable error codes (11 codes) + upgrade hints
- Open-core distribution separation with runtime tier enforcement (single MIT-licensed package)
- GitHub Releases use versioned release notes from the tag

## Compatibility

- API/Contract: Tool responses now use a universal envelope; update any downstream clients expecting tool-specific root models.
- Tiering: Some tools may now return discovery-only outputs in Community.

## Details

### Per-tier behavior splitting

**`crawl_project` tier behavior:**
- **Community:** Discovery crawl provides:
  - File inventory (all .py files)
  - Entrypoint detection (main blocks, CLI commands, Flask/Django routes)
  - Basic statistics (file count, line count, directory structure)
  - Discovery-mode status ("discovered" vs "error")
  - No complexity analysis, no function/class details, no file contents parsed
  - Markdown report with upgrade hints for Pro/Enterprise features
  
- **Pro/Enterprise:** Deep crawl provides:
  - Full AST parsing and complexity analysis
  - Function and class inventories with line numbers
  - Import statements and dependencies
  - Complexity warnings for functions exceeding threshold
  - Cross-file dependency resolution
  - Detailed markdown report with metrics

**`get_call_graph` tier behavior:**
- **Community:** Limited to 3 hops from entry point
- **Pro/Enterprise:** Configurable depth (up to 50 hops)
- Upgrade hints included when depth limit is enforced

**`get_graph_neighborhood` tier behavior:**
- **Community:** Limited to 1-hop neighborhood (immediate neighbors only)
- **Pro/Enterprise:** Configurable k-hop traversal
- Truncation warning includes upgrade hint when limit is applied

**`get_symbol_references` tier behavior:**
- **Community:** Returns first 10 file references with upgrade hint
- **Pro/Enterprise:** Full project-wide reference search
- Error message indicates when results are truncated

**Implementation:**
- Tier detection: `_get_current_tier()` function checks global CURRENT_TIER
- Discovery crawl: `_crawl_project_discovery()` for Community tier
- Deep crawl: `_crawl_project_sync()` for Pro/Enterprise tiers
- All tools include upgrade hints in response when Community limits are hit

### Response envelope + error codes

All 20 MCP tools return a universal response envelope including:
- `tier`: Current tier (community/pro/enterprise)
- `tool_version`: Code Scalpel version
- `tool_id`: Tool identifier
- `request_id`: Unique request ID for tracking
- `capabilities`: List of supported capabilities (e.g., "envelope-v1")
- `duration_ms`: Execution duration in milliseconds
- `error`: Structured error object with `error_code`, `error`, and optional `error_details`
- `upgrade_hints`: List of upgrade hints when features require higher tier
- `data`: Actual tool response (preserves original tool output structure)

Error responses include standardized error codes:
- `invalid_argument`: Invalid input parameter
- `invalid_path`: Path not found or inaccessible
- `forbidden`: Operation not permitted in current tier
- `not_found`: Requested entity not found
- `timeout`: Operation exceeded time limit
- `too_large`: Input/output exceeds size limit
- `resource_exhausted`: System resources exhausted
- `not_implemented`: Feature not yet implemented
- `upgrade_required`: Feature requires higher tier
- `dependency_unavailable`: External dependency unavailable
- `internal_error`: Internal server error

Implementation:
- Created `src/code_scalpel/mcp/contract.py` with ToolResponseEnvelope and ToolError models
- Intercepts tool registration via monkeypatched `add_tool` to wrap all tool execution
- Captures timing, detects failures, classifies errors, and adds tier metadata
- Reference docs: `docs/reference/mcp_response_envelope.md`, `docs/reference/error_codes.md`

### Distribution separation

**Status**: ✅ Implemented

Code Scalpel v3.2.8 implements an **open-core model with runtime tier enforcement**:

#### Architecture

- **Single Package**: All code ships in one MIT-licensed `code-scalpel` package
- **Runtime Restrictions**: Tier limitations enforced at runtime via tier checks
- **Configuration**: Set `CODE_SCALPEL_TIER=community|pro|enterprise` environment variable
- **Audit Trail**: All tool responses include `tier` field for compliance tracking

#### Design Rationale

Chose runtime enforcement over package separation for:
- **Simplicity**: Single codebase, one PyPI package, one distribution
- **Transparency**: All code visible for auditing and trust
- **Maintainability**: No conditional imports or missing module handling
- **Developer Experience**: Easy to test all tiers locally
- **Licensing Clarity**: MIT license + commercial licenses for Pro/Enterprise

#### Verification

Automated verification via `scripts/verify_distribution_separation.py`:

```bash
$ python scripts/verify_distribution_separation.py
✅ PASS: Distribution separation is correctly implemented
- 5 tier check calls found
- All 4 restricted features have tier checks
- Community/Pro/Enterprise comparisons detected
```

#### Upgrade Path

No code changes needed to upgrade:

```bash
# Community (default)
pip install code-scalpel

# Pro (after purchasing license)
export CODE_SCALPEL_TIER=pro

# Enterprise (after purchasing license)
export CODE_SCALPEL_TIER=enterprise
```

#### Licensing Model

- **Community Edition**: MIT License (free, open source)
- **Pro Edition**: Commercial license required to use Pro tier
- **Enterprise Edition**: Commercial license required to use Enterprise tier

All code ships in the MIT-licensed package. Pro/Enterprise features are licensed separately and activated via environment configuration. This follows the "open core" model used by many successful projects.

#### Documentation

- Architecture: [`docs/architecture/distribution_separation.md`](../architecture/distribution_separation.md)
- Security: Source visibility ≠ usage rights; tier logged for audit

## Security

- No known security regressions introduced.
- Continued CI gates: Bandit + pip-audit artifacts are attached in Release Confidence.

## Upgrade notes

- If you are consuming MCP responses programmatically, update parsing to handle the universal envelope.
- If you rely on deep project-wide behavior in `crawl_project`, use Pro/Enterprise.

## Contributors

(fill)
