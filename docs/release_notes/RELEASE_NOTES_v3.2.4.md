# Release Notes v3.2.4

**Release Date:** December 23, 2025  
**Status:** Stable  
**Type:** Patch Release (CI Reliability)

---

## Summary

v3.2.4 fixes CI/release reliability issues in the legacy regression runner and MCP contract suite.

## What's Changed

### CI / Testing

- Ensures the MCP contract test suite is present in the source distribution and can be executed by CI workflows.
- Makes `scripts/regression_test.py` resilient when executed directly (adds a fallback to import `code_scalpel` from `src/` when the package is not installed).

## Notes

- No intended behavioral changes to MCP tool outputs.
