# Governance & Compliance Enforcement Status

> [20251231_DOCS] Production-ready governance enforcement documentation for Code Scalpel v3.3.0+.

This document answers: **which `.code-scalpel/` files are actively enforced today**, where that enforcement lives, and how to use each feature.

## Quick Reference: What's Enforced by Tier

| Governance Feature | Community | Pro | Enterprise | Enforcement Point |
|--------------------|-----------|-----|------------|-------------------|
| `response_config.json` | ✅ Auto | ✅ Auto | ✅ Auto | MCP response wrapper |
| `limits.toml` | ✅ Auto | ✅ Auto | ✅ Auto | Tool capability loader |
| `policy.manifest.json` | ❌ | ✅ Auto | ✅ Auto | MCP preflight (all tools) |
| `budget.yaml` | ❌ | ✅ Auto | ✅ Auto | MCP preflight (write tools) |
| `policy.yaml` (evaluation) | ❌ | ✅ Opt-in | ✅ Opt-in | MCP preflight (write tools) |
| `audit.jsonl` | ❌ | ✅ Auto | ✅ Auto | MCP preflight logging |

## Environment Variables Reference

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `SCALPEL_GOVERNANCE_ENFORCEMENT` | `off\|warn\|block` | Community: `off`, Pro/Enterprise: `block` | Global enforcement posture |
| `SCALPEL_GOVERNANCE_FEATURES` | comma-separated | See below | Feature gates |
| `SCALPEL_GOVERNANCE_BREAK_GLASS` | `1` | unset | Pro/Enterprise: allows `warn` to proceed |
| `SCALPEL_GOVERNANCE_AUDIT` | `0\|1` | `1` | Enable audit logging |
| `SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY` | `1` | unset | Only enforce on write tools |
| `SCALPEL_MANIFEST_SECRET` | string | unset | Secret for policy integrity HMAC |
| `SCALPEL_POLICY_DIR` | path | `.code-scalpel` | Override policy directory location |

**Default features by tier (when `SCALPEL_GOVERNANCE_FEATURES` unset):**
- Community: `response_config,limits`
- Pro: `policy_integrity,response_config,limits,budget`
- Enterprise: `policy_integrity,response_config,limits,budget`

**Available feature gates:**
- `policy_integrity` - Verify `.code-scalpel/policy.manifest.json` before tool execution
- `budget` - Enforce `.code-scalpel/budget.yaml` limits on write tools
- `policy_evaluation` - Evaluate `.code-scalpel/policy.yaml` rules (opt-in)
- `response_config` - Apply `.code-scalpel/response_config.json` filtering
- `limits` - Apply `.code-scalpel/limits.toml` capability limits

## Tier source of truth

> [20251231_DOCS] **Tiers are controlled by Authentication/Licensing.** Governance behavior must recognize the current tier as determined by the MCP server (license-derived tier) and apply governance features based on:
>
>- Current tier (Community/Pro/Enterprise)
>- `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block`
>- Explicit feature gating (`SCALPEL_GOVERNANCE_FEATURES`) when applicable

## Enforced automatically at the MCP boundary ("invisible governance")

These run without the user manually invoking any governance tool.

- `policy.manifest.json`
  - **Status:** Enforced (tier-aware)
  - **Enforcement point:** MCP tool wrapper preflight in the server.
  - **Tier:** Pro/Enterprise (Community: no policy integrity preflight)
  - **Behavior:** For Pro/Enterprise, policy integrity is verified before tool execution; enforcement posture is controlled by `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block` (with break-glass constraints).
  - **How to validate:** Run the existing governance tests (see "Validation" below).

- `response_config.json`
  - **Status:** Enforced
  - **Enforcement point:** Response shaping layer used by the server wrapper.
  - **Tier:** Community/Pro/Enterprise
  - **Behavior:** Tool payloads are filtered for token efficiency based on profile/tool overrides; contract-critical fields are preserved.
  - **How to validate:** Run the response config tests (added below).

- `limits.toml` / `limits.local.toml`
  - **Status:** Enforced
  - **Enforcement point:** Tier/tool capability & limit loading; the server enforces `max_*` limits and tools rely on capabilities/limits.
  - **Tier:** Community/Pro/Enterprise
  - **Behavior:** Limits can be loaded from env override, local dev override, project config, user/system config, or package defaults.
  - **How to validate:** Tier tests that assert capabilities/limits, plus a targeted limits-loader test if desired.

- `budget.yaml`
  - **Status:** Enforced (tier-aware, write-tools only)
  - **Enforcement point:** MCP tool wrapper preflight in the server (before filesystem mutation).
  - **Tier:** Pro/Enterprise
  - **Behavior:** For write-capable tools (`update_symbol`, `rename_symbol`), the server simulates the requested patch (and for Pro/Enterprise renames, simulates bounded cross-file reference updates) and validates the resulting `Operation` against `.code-scalpel/budget.yaml`.
    - `SCALPEL_GOVERNANCE_ENFORCEMENT=off`: no budget checks.
    - `warn`: proceeds only with break-glass semantics and returns neutral warnings.
    - `block`: denies the tool call with `error_code=forbidden` before any write occurs.
  - **How to validate:** Run the budget enforcement tests (see "Validation" below).

- `policy.yaml` (policy evaluation)
  - **Status:** Enforced (tier-aware, feature-gated; write-tools only)
  - **Enforcement point:** MCP tool wrapper preflight in the server (before filesystem mutation).
  - **Tier:** Pro/Enterprise
  - **Enablement:** `SCALPEL_GOVERNANCE_FEATURES` includes `policy_evaluation`
  - **Schema:** `policies: [...]` (not the legacy `rules:` schema)
  - **Behavior:** For write-capable tools (`update_symbol`, `rename_symbol`), the server evaluates `.code-scalpel/policy.yaml` against the requested operation and blocks/warns according to `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block`.
    - Pro/Enterprise `warn` requires break-glass; without break-glass, `warn` behaves as `block`.
  - **How to validate:** Run the policy evaluation enforcement tests (see "Validation" below).

- `audit.jsonl`
  - **Status:** Enforced (MCP preflight audit)
  - **Enforcement point:** MCP tool wrapper preflight in the server.
  - **Tier:** Pro/Enterprise (when governance preflight runs)
  - **Behavior:** The server appends JSONL audit events for governance preflight decisions (policy integrity + change budget), unless explicitly disabled.
    - Control: `SCALPEL_GOVERNANCE_AUDIT=0|1` (default: on)
  - **How to validate:** Run the budget enforcement tests (see "Validation" below).

## Enforced by specific subsystems/tools (not global MCP preflight)

These are real and working, but they only apply when the specific subsystem/tool is used.

- `policy.yaml` (policy engine usage)
  - **Status:** Enforced (tool-dependent)
  - **Enforcement point:** `PolicyEngine` defaults to `.code-scalpel/policy.yaml` when instantiated without arguments.
  - **Tier:** Community/Pro/Enterprise (only applies when the policy subsystem/tool is invoked)
  - **Notes:** This is separate from MCP-boundary policy evaluation (which is feature-gated under `policy_evaluation`).

- `audit.log`
  - **Status:** Enforced (tool-dependent)
  - **Enforcement point:** Policy engine audit logging uses an audit log file (commonly `.code-scalpel/audit.log`).
  - **Tier:** Community/Pro/Enterprise (only when the emitting subsystem runs)

- `audit.jsonl`
  - **Status:** Enforced (MCP preflight + tool-dependent)
  - **Enforcement point:**
    - MCP boundary: governance preflight appends events for policy integrity/budget decisions.
    - Tool-dependent: code-policy checks can persist JSONL audit events.
  - **Tier:** Community/Pro/Enterprise (depends on which subsystem emits)

- `autonomy_audit/`
  - **Status:** Enforced (subsystem-dependent)
  - **Enforcement point:** Autonomy engine writes audit artifacts under `.code-scalpel/autonomy_audit/` when enabled.
  - **Tier:** Pro/Enterprise (recommended; Community should remain low-overhead)

## Defined-only (present in `.code-scalpel/` contract, but not enforced by default today)

These exist as configuration/templates, but are **not currently wired into the MCP tool wrapper preflight** (so they are not “invisible governance” yet).

- `config.json` and profile variants (e.g. `config.minimal.json`, `config.restrictive.json`)
  - **Status:** Defined, subsystem-dependent
  - **Tier (recommended target):** Community/Pro/Enterprise
  - **Notes:** Used by governance/autonomy configuration loaders, but not applied as global MCP preflight policy.

- `dev-governance.yaml`
  - **Status:** Defined-only
  - **Tier (recommended target):** Enterprise (optionally Pro if kept lightweight)
  - **Notes:** Template exists, but there is no runtime loader/enforcer wired in by default.

- `project-structure.yaml` and `policies/project/structure.rego`
  - **Status:** Defined-only
  - **Tier (recommended target):** Enterprise
  - **Notes:** Templates exist; enforcement is not currently applied automatically.

## Security hygiene notes

- `development-2025-01.private.pem`
  - **Status:** **Never commit** (secret material)
  - **Action:** Ensure it stays excluded via `.gitignore` and/or is removed from any distributed template packs.

## Validation

- Run targeted tests:
  - `pytest -q tests/test_governance_invisible_enforcement.py`
  - `pytest -q tests/test_governance_budget_enforcement.py`
  - `pytest -q tests/test_governance_policy_evaluation_enforcement.py`
  - `pytest -q tests/test_mcp_auto_init.py`
  - `pytest -q tests/mcp/test_response_config.py`

### Validation checklist for “production capability” wiring

> [20251231_DOCS] When you wire in new preflight features, validate both the positive path (allowed) and negative path (denied), and validate that disabling the feature restores baseline behavior.

**Common checks (apply to all new governance preflight features)**
- `off|warn|block` behavior is consistent and deterministic.
- No “upgrade/upsell” wording appears in warnings/errors.
- Audit events are emitted when enforcement runs (at least in `warn|block`).

**Suggested targeted test coverage**
- Budget preflight (`budget.yaml`)
  - Covered by `tests/test_governance_budget_enforcement.py`:
    - `block` denies and leaves the filesystem unchanged.
    - `warn` (with break-glass) allows and returns neutral warnings.
    - Cross-file renames are accounted for in budget evaluation (bounded by configured rename limits).
- Profile selection (`config*.json`)
  - Add tests that verify precedence and that profile selection alone does not alter behavior when enforcement is `off`.
- Dev governance (`dev-governance.yaml`)
  - Add a minimal rule fixture and assert allow/deny at MCP boundary.
- Project structure (`project-structure.yaml` / structure.rego)
  - Add tests that attempt to write inside vs outside allowed roots.

**Existing tests to use as anchors**
- `pytest -q tests/test_governance_invisible_enforcement.py`
- `pytest -q tests/mcp/test_response_config.py`
- `pytest -q tests/mcp/test_tier_boundary_limits.py`
- `pytest -q tests/tools/tiers/test_tier_gating_smoke.py`


## Recommended next wiring (if you want full “invisible governance”)

- Add optional, tier-gated preflight evaluation using `UnifiedGovernance` for **write-capable tools** (e.g., apply/patch/update operations), so `budget.yaml` and policy decisions apply before filesystem mutation.
- Decide whether `dev-governance.yaml` and `project-structure.yaml` are intended to be:
  - enforced (block/warn) at MCP boundary, or
  - informational resources only.

## Production capability checklist (feature-by-feature)

> [20251231_DOCS] The goal is to make each governance feature production-capable by wiring it into the MCP boundary (where appropriate), providing a stable enablement model (flags), and adding tests that validate both enabled and disabled behavior.

### Standard enablement model (flags)

**Principles**
- Default behavior should remain stable: features that are not enabled must not change MCP behavior.
- Tier-aware: Community should remain low-overhead; Pro/Enterprise can enable stronger checks.
- No marketing language: enforcement failures/warnings must not suggest upgrading.

**Recommended flags (environment variables)**
- `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block`
  - Global posture used by MCP preflight.
  - `off`: do not block; do not warn (except tool-specific local behavior).
  - `warn`: run checks, surface warnings in results.
  - `block`: fail tool calls when governance denies.
- `SCALPEL_GOVERNANCE_FEATURES=...`
  - Comma-separated feature gates for MCP preflight, e.g. `policy_integrity,response_config,limits,budget,dev_governance,project_structure,policy_evaluation`.
  - If unset: treat as “current behavior” (today: `policy_integrity,response_config,limits`).
- `SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY=true|false`
  - If `true`: run governance preflight checks only for write-capable tools.
  - Default: `false` (current behavior continues to preflight policy integrity on all tools in Pro/Enterprise).
- `SCALPEL_GOVERNANCE_BREAK_GLASS=...`
  - Existing break-glass constraints apply; document the required accompanying fields (e.g., reason + limited TTL) and ensure audit logging.

**Precedence (recommended)**
1) Tool invocation parameters (explicit) if supported
2) Environment variables
3) Project `.code-scalpel/` config defaults
4) Package defaults

### Tier separation (what exists where)

> [20251231_DOCS] This matrix describes “production intent”: which features are expected to be meaningful in each tier once fully wired.

| Governance capability | Community | Pro | Enterprise |
|---|---:|---:|---:|
| Response shaping (`response_config.json`) | Yes | Yes | Yes |
| Tier limits (`limits.toml`) | Yes | Yes | Yes |
| Policy integrity preflight (`policy.manifest.json`) | No | Yes | Yes |
| Change budgets (`budget.yaml`) | No (default) | Yes | Yes |
| Governance profiles (`config*.json`) | Yes | Yes | Yes |
| Dev governance rules (`dev-governance.yaml`) | No | Optional | Yes |
| Project structure controls (`project-structure.yaml` / Rego) | No | Optional | Yes |
| Global policy evaluation (`policy.yaml` at MCP boundary) | No (default) | Optional | Yes |

**Recommended default feature set by tier (when `SCALPEL_GOVERNANCE_FEATURES` is unset)**
- Community: `response_config,limits`
- Pro: `policy_integrity,response_config,limits,budget`
- Enterprise: `policy_integrity,response_config,limits,budget`

**Tier-aware evaluation rule (required)**
- The current tier is determined by Authentication/Licensing in the MCP server.
- If a feature is requested via `SCALPEL_GOVERNANCE_FEATURES` but is not available in the current tier:
  - `SCALPEL_GOVERNANCE_ENFORCEMENT=off`: no-op
  - `warn`: emit a non-upsell warning that the feature is unavailable in this tier
  - `block`: treat as no-op (recommended) unless the feature is safety-essential for that tier

### Tier-specific implementation (explicit)

> [20251231_DOCS] This section describes how governance is implemented by tier in production terms: what is enforced automatically at the MCP boundary, what is tool-dependent, and what can be enabled via flags.

#### Community

**MCP boundary (default / “invisible governance”)**
- Enforced: `response_config.json`, `limits.toml`.
- Not enforced: policy integrity preflight (`policy.manifest.json`) by default.

**Optional via flags (recommended stance)**
- Allow enabling only lightweight features (e.g., additional response shaping profiles).
- Treat heavier controls (`budget`, `dev_governance`, `project_structure`, global `policy.yaml`) as no-ops by default.

**Operational intent**
- Keep overhead minimal; avoid preflights that require policy integrity or repo-wide scanning.

#### Pro

**MCP boundary (default / “invisible governance”)**
- Enforced: `policy.manifest.json` (policy integrity preflight), `response_config.json`, `limits.toml`.

**Optional via flags**
- `budget`: enable change budgets for write-capable tools.
- `policy_evaluation`: enable global policy evaluation at MCP boundary for write tools.
- `dev_governance` / `project_structure`: optional only if kept lightweight and deterministic; otherwise reserve for Enterprise.

**Operational intent**
- Provide meaningful governance improvements without Enterprise-level complexity; default remains “safe + low-noise”.

#### Enterprise

**MCP boundary (default / “invisible governance”)**
- Enforced: `policy.manifest.json` (policy integrity preflight), `response_config.json`, `limits.toml`.

**Optional via flags**
- `budget`: enforce change budgets for write tools.
- `dev_governance`: enable additional rule sets for engineering governance.
- `project_structure`: enforce structural rules pre-mutation (allowed roots, forbidden paths, etc.).
- `policy_evaluation`: enable global policy evaluation at MCP boundary for write tools.

**Operational intent**
- Enterprise is the tier where “full invisible governance” is expected to be viable: strong preflight checks, auditability, and strict posture (`block`) when desired.

**Non-negotiables (all tiers)**
- No “upgrade/upsell” language in errors or warnings.
- Clear separation between “MCP boundary enforcement” vs “tool-dependent enforcement”.
- Deterministic behavior under `SCALPEL_GOVERNANCE_ENFORCEMENT=off|warn|block`.

### `budget.yaml` (change budgets)

**Target state**: Enforced at MCP boundary (tier-aware, write-tools-only).

**Tier**: Pro/Enterprise

**Checklist**
- Wiring
  - Done: MCP wrapper preflight invokes ChangeBudget evaluation for write-capable tools.
  - Done: Budget preflight includes bounded cross-file rename simulation for Pro/Enterprise renames.
  - Next: Add explicit `SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY` gating (currently implicit via tool allowlist).
- Config contract
  - Define schema and validation: reject malformed budgets with a clear error in `warn|block` modes.
  - Support project-local overrides (`.code-scalpel/budget.yaml`) without requiring user tool calls.
- Auditability
  - Next: Record budget decisions to `.code-scalpel/audit.jsonl` with: tool name, target path(s), decision, reason, budget summary.
- Failure modes
  - `off`: no behavior change.
  - `warn`: tool proceeds, warnings returned.
  - `block`: tool fails with non-upsell error; include a stable machine-readable code.
- Tests
  - Done: `tests/test_governance_budget_enforcement.py` covers deny in `warn` and `block`, and cross-file rename budgeting.
  - Next: Add a positive “within budget” case (enabled+pass) and a disabled/no-op case.

## Next steps (recommended)

> [20251231_DOCS] Follow-on work after `budget.yaml` MCP preflight.

1) **Auditability for MCP preflight**
  - Emit structured audit events for policy integrity + budget decisions to `.code-scalpel/audit.jsonl` (and optionally `audit.log`) when enforcement runs in `warn|block`.

2) **Make write-tool gating explicit**
  - Implement `SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY=true|false` to control whether heavy preflights run only on write tools (default recommended: `true`).

3) **Governance profiles (`config*.json`)**
  - Add a single profile loader path used by MCP preflight (env → project → defaults), with tests for precedence and no-op behavior when enforcement is `off`.

4) **`policy_evaluation` at MCP boundary (opt-in)**
  - For Pro/Enterprise when enabled, evaluate `.code-scalpel/policy.yaml` as part of write-tool preflight (keeping tool-dependent PolicyEngine behavior intact).

5) **Enterprise-only structure/dev governance (opt-in)**
  - `project_structure`: enforce allow/deny on filesystem mutation paths using deterministic checks.
  - `dev_governance`: add a minimal rule fixture + evaluation hook gated behind the feature flag.

### `config.json` + profiles (`config.minimal.json`, `config.restrictive.json`)

**Target state**: Profile selection affects MCP boundary governance behavior (without forcing users to understand internal policy files).

**Tier**: Community/Pro/Enterprise

**Checklist**
- Wiring
  - Add a single “governance profile loader” path used by MCP wrapper preflight.
  - Support `SCALPEL_GOVERNANCE_PROFILE=minimal|default|restrictive` (or equivalent) that selects the config variant.
- Compatibility
  - If a profile references a non-existent artifact, handle gracefully: warn in `warn`, deny only in `block` if the missing item is required.
- Observability
  - Emit a one-line debug log of the resolved profile + sources (env/project/default) when verbose logging is enabled.
- Tests
  - Add tests for profile precedence and that profile selection does not change tool semantics when enforcement is `off`.

### `dev-governance.yaml`

**Target state**: Optional, explicit enablement; runs as additional rules in MCP preflight.

**Tier**: Enterprise (optionally Pro if lightweight)

**Checklist**
- Wiring
  - Add loader + rule evaluation hook in MCP preflight when `dev_governance` is enabled.
  - Define whether this file is advisory-only (warn) or enforceable (block) under posture.
- Rule boundaries
  - Scope dev-governance rules to write-capable tools by default.
  - Ensure rules are deterministic and fast (avoid scanning entire repo unless the tool already does so).
- Tests
  - Add at least one minimal rule fixture and validate: deny and allow paths.

### `project-structure.yaml` + `policies/project/structure.rego`

**Target state**: Optional structural governance for file operations (e.g., prevent writing outside allowed directories), enforced pre-mutation.

**Tier**: Enterprise (optionally Pro if lightweight)

**Checklist**
- Wiring
  - Implement a structure validation step in MCP preflight for write-capable tools.
  - If using Rego: ensure policy integrity verification is performed before loading Rego policy artifacts.
- Rule clarity
  - Define the minimum viable constraints: allowed roots, forbidden paths, file extension allowlists/denylists.
  - Ensure failures return actionable, non-upsell messages (what was attempted + which rule denied).
- Tests
  - Add fixtures that attempt writes to allowed vs disallowed paths.

### `policy.yaml` (tool-dependent today)

**Target state**: Optional “invisible governance” expansion: allow enabling policy evaluation globally for write tools.

**Tier**: Pro/Enterprise

**Feature flag name (recommended)**: `policy_evaluation`

**Checklist**
- Wiring
  - When `policy.yaml` is enabled via `SCALPEL_GOVERNANCE_FEATURES`, run policy evaluation in MCP preflight for write-capable tools.
  - Keep existing tool-dependent use intact (do not break callers that instantiate `PolicyEngine` directly).
- Rollout safety
  - Provide a safe default policy (or require explicit opt-in with `warn` first).
- Tests
  - Validate policy evaluation happens only when enabled; validate `off|warn|block` semantics.
---

## Quick Start Examples

### Example 1: Community Tier (No Extra Setup)

Community tier enforces `response_config.json` and `limits.toml` automatically. No environment variables needed.

```bash
# Just run - governance is automatic
code-scalpel-server
```

### Example 2: Pro/Enterprise with Full Governance

```bash
export SCALPEL_GOVERNANCE_ENFORCEMENT=block
export SCALPEL_GOVERNANCE_FEATURES=policy_integrity,budget,response_config,limits
export SCALPEL_GOVERNANCE_AUDIT=1
export SCALPEL_MANIFEST_SECRET=your-256-bit-secret

code-scalpel-server
```

### Example 3: Enable Policy Evaluation (Opt-in)

```bash
export SCALPEL_GOVERNANCE_FEATURES=policy_integrity,budget,policy_evaluation,response_config,limits
export SCALPEL_GOVERNANCE_ENFORCEMENT=warn  # Test first
export SCALPEL_GOVERNANCE_BREAK_GLASS=1      # Required for Pro/Enterprise warn mode

code-scalpel-server
```

### Example 4: Break-Glass for Emergency Operations

```bash
# Pro/Enterprise: relax enforcement temporarily
export SCALPEL_GOVERNANCE_ENFORCEMENT=warn
export SCALPEL_GOVERNANCE_BREAK_GLASS=1
export SCALPEL_GOVERNANCE_AUDIT=1  # Keep audit logging!

code-scalpel-server
```

### Example 5: Write-Tools-Only Enforcement

```bash
# Only enforce on update_symbol/rename_symbol, skip read-only tools
export SCALPEL_GOVERNANCE_WRITE_TOOLS_ONLY=1
export SCALPEL_GOVERNANCE_ENFORCEMENT=block

code-scalpel-server
```

---

## Validation Commands

Run the governance test suite to confirm enforcement works correctly:

```bash
# All governance tests (21 tests total)
pytest tests/test_governance_invisible_enforcement.py \
       tests/test_governance_budget_enforcement.py \
       tests/test_governance_policy_evaluation_enforcement.py \
       tests/test_governance_tier_gating.py -v

# Individual test files
pytest tests/test_governance_invisible_enforcement.py -v    # 6 tests
pytest tests/test_governance_budget_enforcement.py -v       # 5 tests
pytest tests/test_governance_policy_evaluation_enforcement.py -v  # 5 tests
pytest tests/test_governance_tier_gating.py -v              # 5 tests
```

---

## See Also

- [.code-scalpel/README.md](../.code-scalpel/README.md) - Governance file reference
- [README.md](../README.md#governance--policy-system) - Main project governance section
- [TIER_CONFIGURATION.md](TIER_CONFIGURATION.md) - Tier feature matrix