# Code Scalpel v1.5.4 Release Notes (FINAL)

**Release Date:** December 14, 2025
**Version:** 1.5.4
**Status:** READY FOR RELEASE <!-- [20251214_DOCS] Gate passed with full-suite coverage 95.00% -->
**Tag:** v1.5.4

## Executive Summary

v1.5.4 "DynamicImports" introduces the capability to detect and resolve dynamic imports in Python codebases. This allows Code Scalpel to understand dependencies created via `importlib`, `__import__`, and framework-specific patterns like Django's `INSTALLED_APPS`.

## New Features

### Dynamic Import Detection
- **`importlib.import_module()` Support:** Now tracks modules imported programmatically.
- **`__import__()` Support:** Detects low-level dynamic imports.
- **Lazy Import Tracking:** Identifies imports that are conditional or deferred (marked as `ImportType.LAZY`).

### Framework Intelligence
- **Django:** Parses `INSTALLED_APPS` to discover project dependencies.
- **Flask:** Detects Blueprint registrations to understand application structure.

## Testing

- `python -m pytest --maxfail=1 --disable-warnings --cov=src --cov-report=xml:release_artifacts/v1.5.4/coverage_20251214.xml` (2530 passed, 1 skipped, 1 xfailed, 175 warnings; line coverage 95.00%, branch coverage 88.41%).

Full suite includes dynamic import scenarios; detailed log resides in `release_artifacts/v1.5.4/dynamic_import_tests.log`.

## Verification (Release Gate)

- [20251214_DOCS] `python -m ruff check .` (pass).
- [20251214_DOCS] `python -m black --check .` (pass).
- [20251214_DOCS] `python -m pytest --maxfail=1 --disable-warnings --cov=src --cov-report=xml:release_artifacts/v1.5.4/coverage_20251214.xml` (2530 passed, 1 skipped, 1 xfailed, 175 warnings; line coverage 95.00%, branch coverage 88.41%).
- Evidence: [release_artifacts/v1.5.4/v1.5.4_verification_evidence_20251214.json](release_artifacts/v1.5.4/v1.5.4_verification_evidence_20251214.json); coverage report [release_artifacts/v1.5.4/coverage_20251214.xml](release_artifacts/v1.5.4/coverage_20251214.xml).
- [20251214_SECURITY] Artifacts signed and verified with cosign 3.0.2 using bundle + pubkey (no detached .sig required). Verification commands:
	- `cosign verify-blob --key release_artifacts/v1.5.4/cosign.pub --bundle release_artifacts/v1.5.4/code_scalpel-1.5.4-py3-none-any.whl.bundle dist/code_scalpel-1.5.4-py3-none-any.whl`
	- `cosign verify-blob --key release_artifacts/v1.5.4/cosign.pub --bundle release_artifacts/v1.5.4/code_scalpel-1.5.4.tar.gz.bundle dist/code_scalpel-1.5.4.tar.gz`
	Bundles live in `release_artifacts/v1.5.4/`; signatures are embedded per cosign’s new bundle format.

## Evidence

- Dynamic Import Evidence: `release_artifacts/v1.5.4/v1.5.4_dynamic_import_evidence.json`
- Test Results: `release_artifacts/v1.5.4/dynamic_import_tests.log`
- Framework Integration: `release_artifacts/v1.5.4/framework_integration_results.json`
- Static vs Dynamic Comparison: `release_artifacts/v1.5.4/import_resolution_comparison.json`
- Edge Case Coverage: `release_artifacts/v1.5.4/edge_case_coverage.json`

## Technical Details

### ImportResolver Updates
- Added `ImportType.DYNAMIC` and `ImportType.DUNDER`.
- Enhanced AST traversal to recognize import call patterns.

## Migration Guide

No breaking changes. The `ImportGraphResult` will now simply contain more edges representing dynamic dependencies.
