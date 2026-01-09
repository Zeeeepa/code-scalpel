# Release Notes - v3.3.1

> [20260104_DOCS] Release notes capturing get_project_map hardening and multi-language validation.

## Overview

- **Focus**: Finalize `get_project_map` for production with multi-language coverage and tier enforcement tests.
- **Status**: ✅ Production ready; all gates passing.
- **Date**: 2026-01-04

## Highlights

- Validated multi-language detection (Python, Java, JavaScript/TypeScript, YAML, Markdown, HTML, CSS, JSON) with 8 dedicated tests.
- Hardened tier enforcement for Community, Pro, and Enterprise via 57 tests (limits, gating, feature access).
- Confirmed 100/100 tests passing (43 functional + 57 tier enforcement) in 5.24s.
- Documented performance evidence: enterprise 5000-file scenario executes within acceptable limits.

## Changes

### Added / Testing
- [20260104_TEST] Expanded test coverage to 100 total cases for `get_project_map`, including language breakdown, tier enforcement, licensing, and feature gating.

### Documentation
- [20260104_DOCS] Updated assessment to mark multi-language support as fully implemented (not deferred) and to record latest test evidence.
- [20260104_DOCS] Clarified tier behaviors and limits in assessment and release materials.

## Compatibility
- **Breaking Changes**: None.
- **Migration**: No action required; existing integrations continue to work. Multi-language support is already active across tiers.

## Testing Summary

- **Functional**: 43/43 passing.
- **Tier Enforcement**: 57/57 passing.
- **Overall**: 100/100 tests passing in 5.24s (2026-01-04 run).

## Known Issues / Limitations

- Complexity hotspot threshold tuning remains an acceptable P3 deferral; detection is functional, tuning is planned for v3.5.0.

## Next Steps

- Update root `CHANGELOG.md` (completed).
- Update `README.md` with current `get_project_map` example and language coverage (completed hereafter).
- Tag release as `v3.3.1` once code review sign-off is done.
