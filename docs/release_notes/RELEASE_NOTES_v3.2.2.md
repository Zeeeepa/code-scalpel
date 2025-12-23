# Release Notes v3.2.2

**Release Date:** December 23, 2025  
**Status:** Stable  
**Type:** Patch Release (CI/Release Hardening)

---

## Summary

v3.2.2 focuses on release pipeline reliability and CI hygiene.

## What's Changed

### CI / Release

- Added PyPI publishing via GitHub Trusted Publishing (OIDC): automated publish on `v*` tags.
- General release packaging metadata updated for v3.2.2.

### Quality

- Resolved a Ruff `F841` lint issue in the cross-file taint tooling.

## Notes

- No public API changes intended in this release.
