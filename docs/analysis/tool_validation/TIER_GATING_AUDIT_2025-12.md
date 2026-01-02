# Tier Gating Audit (2025-12)

## Scope
This audit checks for **tool-level hard denials** (e.g., Community tier returning an error for the entire tool) outside the intended tier model:

- Policy baseline: *tools are available at all tiers; tiers differ by capabilities/limits*.
- Allowed: gating of **optional parameters/features** by tier (capability/limits).
- Not allowed: blanket **"Community cannot use this tool"** style blocks, unless explicitly documented as an exception.

## What was scanned
- Source: `src/code_scalpel/**/*.py`
- Primary patterns:
  - `tier == "community": return ...` (early returns)
  - strings containing `requires PRO/Enterprise tier`
  - `upgrade_required` usage

## Findings
### 1) Confirmed policy violation (fixed)
- Tool: `update_symbol` (`operation="rename"` path)
- Issue: Legacy Community hard deny with message `"Rename requires PRO tier."` even though `rename_symbol` V1.0 is tier-aware.
- Fix: Delegate rename operation to `rename_symbol` for **all tiers**, letting the tier-aware limits apply.
- Location: `src/code_scalpel/mcp/server.py`
- Regression: Added Community-tier test to confirm rename via `update_symbol` is allowed.

### 2) No additional tool-level Community denials found outside MCP server
- The repo-wide scan did not identify other **non-server** modules hard-denying whole tools by tier.

### 3) Remaining tier checks appear to be capability-level gates
In `src/code_scalpel/mcp/server.py`, remaining `requires PRO/Enterprise tier` checks are tied to **optional feature flags/parameters**, e.g.:
- `extract_code(..., include_cross_file_deps=True)` (Pro)
- advanced extraction features such as closure detection / DI suggestions (Pro)
- microservice/dockerfile generation, org-wide resolution, service boundary detection, custom pattern extraction (Enterprise)
- `generate_unit_tests(data_driven=True)` (Pro), `generate_unit_tests(crash_log=...)` (Enterprise)

These match the intended tier behavior model (feature-level gating rather than tool-level denial).

## Notes / Follow-ups (optional)
- Some advanced feature handlers include explicit upgrade URLs or direct `tier == "community"` checks instead of using `has_capability(...)`/capability matrices consistently. This is a style/consistency issue, not a policy violation.

## Validation
- `pytest -q tests/test_rename.py tests/test_rename_cross_file.py`
- `pytest -q tests/tools/tiers/test_update_symbol_tiers.py`
