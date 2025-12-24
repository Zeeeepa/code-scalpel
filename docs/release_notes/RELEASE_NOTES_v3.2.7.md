# Release Notes v3.2.7 "Tiered Registry Hotfix"

**Release Date:** December 23, 2025  
**Status:** Stable  
**Type:** Patch / Hotfix Release

---

## Executive Summary

Code Scalpel v3.2.7 is a patch release that finalizes the **tiered MCP tool registry** rollout and ensures the **Release Confidence** gates (format/lint/type/security/tests/contracts) pass cleanly for the current release.

This release also formalizes the docs-as-contract approach for MCP tool inventory and tier matrices.

---

## Highlights

### Tiered MCP Tool Exposure (Community / Pro / Enterprise)

- MCP server now supports tier-based tool exposure across transports.
- Tier selection supported via CLI and environment variables.
- Enterprise-only tools are excluded from Community/Pro surfaces as configured.

### Docs-as-Contract for Tool Inventory

- Generated reference docs are treated as contract artifacts:
  - `docs/reference/mcp_tools_current.md`
  - `docs/reference/mcp_tools_by_tier.md`
- CI enforces that generated docs are present and up-to-date.

### Cross-Transport Contract Coverage

- Contract tests validate tool surfaces across:
  - stdio
  - SSE
  - streamable HTTP

---

## Fixes

- Fix Release Confidence formatting/lint gate failures for the tagged release series.
- Ensure version bump and generated artifacts align with the release tag workflow expectations.

---

## Compatibility / Migration

- No breaking API changes.
- No migration required.

---

## Notes for Release Management

- Release notes are expected at: `docs/release_notes/RELEASE_NOTES_v3.2.7.md`.
- The GitHub Release pipeline should use this file as the release body for tag `v3.2.7`.
