# Release Notes: Code Scalpel v1.3.5

**Release Date:** February 10, 2026
**Type:** Patch release (bug fixes + quality-of-life improvements)

---

## Executive Summary

Version 1.3.5 fixes two bugs affecting first-run experience — a Windows `UnicodeEncodeError` during `codescalpel init` and an incomplete auto-init on `codescalpel mcp` first boot — and adds a non-blocking startup update check so users know when a newer version is available.

---

## Bug Fixes

### Windows UnicodeEncodeError on `codescalpel init`

**Problem:** On Windows systems with non-UTF-8 default encodings (e.g., `cp1252`), running `codescalpel init` would crash with `UnicodeEncodeError` when writing configuration files containing Unicode characters.

**Root Cause:** Several `Path.write_text()` and `Path.read_text()` calls in `config/init_config.py` did not specify `encoding='utf-8'`, causing Python to use the platform default encoding.

**Fix:** All `write_text()` and `read_text()` calls in the init pipeline now explicitly specify `encoding='utf-8'`.

### MCP Server Auto-Init Created Empty Directory

**Problem:** When running `codescalpel mcp` for the first time, the auto-init created the `.code-scalpel/` directory but left it empty instead of scaffolding all 20 configuration files.

**Root Cause:** `governance.auto_init_config_dir()` was creating the directory directly instead of delegating to `init_config_dir()` which generates the full scaffolding.

**Fix:** `auto_init_config_dir()` now delegates to `init_config_dir()` for the actual directory creation and file scaffolding.

---

## Improvements

### Enhanced MCP Server Boot Banner

The MCP server startup banner now displays:
- License tier (COMMUNITY, PRO, ENTERPRISE)
- License file path (relative when inside the project)
- Visual separators for better readability

### Non-Blocking Startup Update Check

The MCP server now checks PyPI for a newer version on startup:
- Runs in a background thread with a 3-second timeout
- Prints a notification if a newer version is available:
  ```
  Update available: v1.3.5 -> v1.4.0. Run: pip install --upgrade codescalpel  (or: uvx codescalpel@latest)
  ```
- Silently skips on any failure (no network, timeout, parse error)
- Opt out by setting `CODE_SCALPEL_UPDATE_CHECK=0`

### Documentation Cleanup

Removed references to internal-only configuration files (`limits.toml`, `features.toml`) from the public website documentation. These files are package-managed and should not be edited by users.

---

## New Files

| File | Purpose |
|------|---------|
| `scripts/validate_encoding.py` | CI script to detect missing `encoding=` in `write_text()`/`read_text()` calls |
| `docs/LICENSE_SETUP.md` | Guide for setting up and managing Code Scalpel licenses |
| `docs/ENCODING_VALIDATION.md` | Documentation for the encoding validation CI job |

---

## Upgrade Instructions

```bash
# pip
pip install --upgrade codescalpel

# uvx (runs latest without install)
uvx codescalpel@latest

# Verify
codescalpel --version
# Expected: 1.3.5
```

---

## Compatibility

- **Python:** 3.10+
- **Breaking changes:** None
- **Sub-packages:** `codescalpel-agents` and `codescalpel-web` remain at v1.0.2 (no changes)
