# Release Notes v3.2.3

**Release Date:** December 23, 2025  
**Status:** Stable  
**Type:** Patch Release (CI Gates + Type Safety)

---

## Summary

v3.2.3 tightens release gates and fixes a type-safety edge case uncovered by CI.

## What's Changed

### CI / Release

- Updated the release-confidence dependency audit to use `requirements-secure.txt` (keeps the gate focused on the secure/pinned set).

### Type Safety

- Hardened XML parsing in the dependency/vulnerability scanner to avoid optional-member typing issues when XML root parsing fails.

## Notes

- No intended behavioral changes to MCP tool outputs; this release is primarily CI/release hardening.
