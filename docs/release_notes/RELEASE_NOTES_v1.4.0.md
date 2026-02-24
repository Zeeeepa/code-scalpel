# Release Notes: Code Scalpel v1.4.0

**Release Date:** February 20, 2026
**Type:** Minor release (new features + bug fixes)

---

## Executive Summary

Version 1.4.0 delivers full response configuration coverage and resolves a class
of cross-test tier contamination bugs that caused intermittent failures in the
test suite. The response filtering pipeline now covers all 22 MCP tools uniformly,
hot reload works without requiring a server restart, and the `.code-scalpel/`
directory is automatically scaffolded with `response_config.json` and
`response_config.schema.json` on first boot.

---

## New Features

### `response_config.json` and Schema Auto-Created on MCP Boot

**Before:** The MCP server auto-init created governance files but left
`response_config.json` and `response_config.schema.json` absent. Users who
wanted to tune output verbosity had to create these files manually.

**After:** `init_config_dir()` now writes both files during the `templates_only`
boot phase (before full governance init). Files are skipped if they already exist,
so existing configurations are never overwritten.

Default `response_config.json` written to `.code-scalpel/response_config.json`:

```json
{
  "$schema": "./response_config.schema.json",
  "version": "1.4.0",
  "description": "MCP response configuration for token efficiency",
  "global": {
    "profile": "standard",
    "exclude_empty_arrays": true,
    "exclude_empty_objects": true,
    "exclude_null_values": true,
    "exclude_default_values": true
  },
  "tool_overrides": {}
}
```

### `exclude_when_tier` Feature Documented and Schema-Validated

The `exclude_when_tier` per-field directive was previously undocumented and
absent from `response_config.schema.json`. It is now:

- Added to the JSON schema as a formal property of `tool_overrides.additionalProperties`
- Documented with a comment in the default `response_config.json` template
- Validated by schema-aware editors (VS Code, etc.)

Example `tool_overrides` entry using `exclude_when_tier`:

```json
"tool_overrides": {
  "get_call_graph": {
    "fields": {
      "mermaid": {
        "exclude_when_tier": ["community", "pro"]
      }
    }
  }
}
```

---

## Bug Fixes

### Graph Tools Bypassed `filter_tool_response` Entirely

**Problem:** Five graph tools (`get_call_graph`, `get_graph_neighborhood`,
`get_project_map`, `get_cross_file_dependencies`, `cross_file_security_scan`)
used `envelop_tool_function` from `contract.py` to build their response
envelopes. This path called `make_envelope` → `ToolResponseEnvelope` directly
without ever calling `filter_tool_response`, so all `response_config.json`
settings (profile, per-field overrides, `exclude_when_tier`) were silently
ignored for these tools.

**Fix:** `envelop_tool_function._wrapped` now:
1. Normalizes the raw result to a dict
2. Calls `_cfg._check_reload()` (hot reload)
3. Calls `filter_tool_response(result_dict, tool_name, tier)` before building `ToolResponseEnvelope`

**Impact:** All 22 MCP tools now pass through the response filter uniformly.
649 graph-tool tests confirmed 0 failures after the fix.

### Hot Reload (`_check_reload`) Never Triggered from `filter_response`

**Problem:** `ResponseConfig.filter_response()` had a `_check_reload()` method
that compared the config file's mtime and reloaded if changed. However,
`filter_response()` never called `_check_reload()`, so changes to
`response_config.json` on disk required a server restart to take effect.

**Fix:** `filter_response()` now calls `self._check_reload()` as its first
statement. Config changes now take effect within the reload interval (default: 5 s).

### `DEFAULT_CONFIG` Profile Mismatch (`"minimal"` vs `"standard"`)

**Problem:** `ResponseConfig.DEFAULT_CONFIG["global"]["profile"]` was `"minimal"`,
but `RESPONSE_CONFIG_JSON_TEMPLATE` defaulted to `"standard"`. This meant:

- New users who relied on the auto-written file got `"standard"` behavior
- Code that fell back to `DEFAULT_CONFIG` (when no file exists) got `"minimal"` behavior

Behavior differed depending on whether `.code-scalpel/response_config.json` was
present.

**Fix:** `DEFAULT_CONFIG["global"]["profile"]` is now `"standard"` in both
`response_config.py` and the template. Behavior is consistent regardless of
whether the file exists.

### Cross-Test Tier Contamination (141 failures → 0)

**Problem:** `tests/conftest.py`'s `_clear_tier_cache_globally` autouse fixture
cleared in-memory JWT and config caches between tests but did not snapshot or
restore tier-related environment variables. The session-scoped
`set_default_license_path` fixture set `CODE_SCALPEL_LICENSE_PATH` to an
enterprise license at session start; tests that called `_get_current_tier()`
directly (without a `community_tier` / `pro_tier` / `enterprise_tier` fixture)
received enterprise tier unexpectedly.

Additionally, `tests/capabilities/test_ci_license_injection.py` ran first in
collection order and set `os.environ["CODE_SCALPEL_LICENSE_PATH"]` directly
(instead of via monkeypatch). Although the tests used `try/finally` to clean up,
cache clearing between tests did not restore the env var, causing persistent
contamination.

**Fix:** `_clear_tier_cache_globally` now snapshots
`CODE_SCALPEL_LICENSE_PATH`, `CODE_SCALPEL_TIER`,
`CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY`, and `CODE_SCALPEL_TEST_FORCE_TIER`
before each test and restores them to their pre-test values afterward. This
ensures every test starts and ends with identical tier environment state,
regardless of how prior tests mutated `os.environ`.

**Impact:** Full test suite failures due to tier contamination dropped from 141
to 0. The fix is backward-compatible with all existing `monkeypatch`-based tier
fixtures.

---

## Changes

### `parsing` Section Removed from `response_config` Template and Schema

The `parsing` block in `RESPONSE_CONFIG_JSON_TEMPLATE` was never consumed by
any code path in `response_config.py` or elsewhere. Exposing undocumented,
non-functional configuration knobs is misleading. The `parsing` section has been
removed from both the JSON template and the JSON schema. Existing
`response_config.json` files with a `parsing` key are not affected (the loader
ignores unknown keys).

### `ResponseFormatter` Marked Deprecated

`src/code_scalpel/mcp/response_formatter.py` contains a `ResponseFormatter`
class that implements a divergent, unused profile system. No code in the MCP
tool pipeline calls `ResponseFormatter`; all filtering goes through
`ResponseConfig.filter_response()`. The module docstring now marks the entire
file as deprecated. The class will be removed in v1.5.0.

---

## Upgrade Guide

### No Breaking Changes

v1.4.0 is backward-compatible. Existing `.code-scalpel/response_config.json`
files are untouched by the auto-init logic.

### Recommended: Update `response_config.json`

If your `response_config.json` has a `"parsing"` section, it is now dead
configuration. You may safely remove it:

```json
// Remove this block:
"parsing": {
  "max_file_size_mb": 10,
  ...
}
```

### Graph Tool Response Filtering Now Active

If you previously configured `tool_overrides` for `get_call_graph`,
`get_graph_neighborhood`, `get_project_map`, `get_cross_file_dependencies`, or
`cross_file_security_scan`, those overrides were silently ignored before v1.4.0.
They now take effect. Review your `tool_overrides` to confirm the configured
filtering is still desirable.

### Hot Reload Behavior Change

Config changes to `response_config.json` now take effect automatically (within
the 5-second reload window). Previously a server restart was required. This is
strictly an improvement, but be aware if you are testing config changes in a
long-running server process.

---

## Modified Files

| File | Change |
|------|--------|
| `src/code_scalpel/__init__.py` | `__version__` → `"1.4.0"` |
| `src/code_scalpel/mcp/contract.py` | `envelop_tool_function` now calls `filter_tool_response` + `_check_reload` |
| `src/code_scalpel/mcp/response_config.py` | `DEFAULT_CONFIG` profile `"minimal"` → `"standard"`; `filter_response` calls `_check_reload` |
| `src/code_scalpel/mcp/response_formatter.py` | Marked deprecated in module docstring |
| `src/code_scalpel/config/templates.py` | Template version `"1.4.0"`; `parsing` section removed; `exclude_when_tier` added to schema |
| `src/code_scalpel/config/init_config.py` | Writes `response_config.json` and `response_config.schema.json` during boot init |
| `src/code_scalpel/licensing/cache.py` | `# nosec B608` moved inline to suppress bandit false positive |
| `tests/conftest.py` | `_clear_tier_cache_globally` now snapshots/restores tier env vars per-test |
| `vscode-extension/package.json` | Version → `"1.4.0"`; `minimatch` override → `"3"` (Node 22 compatibility) |
| `CHANGELOG.md` | Added `[1.4.0]` section |
| `README.md` | Version refs updated to v1.4.0 / February 20, 2026 |
| `.code-scalpel/response_config.json` | Version → `"1.4.0"` |

---

## Test Suite

| Category | Status |
|----------|--------|
| Total collected | 7,354 |
| Passed | 7,103+ |
| Skipped | 111 |
| Failed (post-fix) | 0 |
| Black formatting | Clean (9 files auto-formatted) |
| Ruff lint | Clean (0 issues) |
| Bandit security | Clean (0 medium/high) |

---

## Known Issues

None in this release.

---

## Previous Release

See [RELEASE_NOTES_v1.3.5.md](RELEASE_NOTES_v1.3.5.md) for the previous release.
