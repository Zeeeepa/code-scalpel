# v3.2.8 Release Checklist

**Target Version:** 3.2.8  
**Target Tag:** v3.2.8  
**Release Type:** Patch (Production-fork preparation)  
**Owner:** (fill)  
**Date:** (fill)

---

## 0) Scope Lock (Do First)

- [ ] Confirm the exact scope for v3.2.8 (features/bugfixes/docs only).
- [ ] Confirm whether v3.2.8 is allowed to include workflow/process changes (CI, release pipelines).
- [ ] Confirm whether v3.2.8 starts any tier **behavior** splits (not just tool exposure).

---

## 1) Development Tasks (v3.2.8 Work Items)

### A) V1.0 Production Requirements (Must Land in v3.2.8)

> These items are required by `docs/guides/production_release_v1.0.md` and are not satisfied by “tool hiding” alone.

#### 1) Real feature-splitting (per-tier behavior), not usage caps

- [x] Implement Community vs Pro/Enterprise behavior splits for project-wide/expensive tools.
- [x] `crawl_project` split:
  - [x] Community = **Discovery Crawl** only (inventory + entrypoint/framework hints; no graphs, no cross-file dependency resolution; no file contents).
  - [x] Pro/Enterprise = **Deep Crawl** (project-wide indexing/summaries; may include dependency/call-graph indexing where applicable).
- [x] Apply the same principle to other project-wide tools (at minimum define the split and implement it for the highest-risk/most expensive ones):
  - [x] `get_call_graph` - Community: depth=3, Pro/Enterprise: depth=configurable
  - [x] `get_graph_neighborhood` - Community: k=1, Pro/Enterprise: k=configurable  
  - [x] `get_symbol_references` - Community: 10 files, Pro/Enterprise: project-wide
- [x] Acceptance: MCP contract tests assert the **different outputs/capabilities** by tier (not just availability).

#### 2) Universal response envelope + error codes contract

- [x] Implement a response envelope returned by **all** MCP tools (all tiers), including universal fields:
  - [x] `tier`
  - [x] `tool_version`
  - [x] `tool_id`
  - [x] `request_id`
  - [x] `capabilities`
  - [x] `duration_ms` (required for Pro/Enterprise; recommended for Community)
  - [x] `error` (structured; includes `error_code`)
  - [x] `upgrade_hints`
- [x] Implement a stable error code registry (minimum set: `invalid_argument`, `invalid_path`, `forbidden`, `not_found`, `timeout`, `too_large`, `resource_exhausted`, `not_implemented`, `upgrade_required`, `dependency_unavailable`, `internal_error`).
- [x] Update contract tests to validate envelope fields + structured errors for:
  - [x] success responses
  - [x] expected failures (invalid args/path)
  - [x] upgrade-required behavior and presence of `upgrade_hints`
- [x] Publish/refresh reference docs:
  - [x] `docs/reference/mcp_response_envelope.md`
  - [x] `docs/reference/error_codes.md`
  - [ ] (Enterprise) `docs/reference/audit_event_schema.md`

#### 3) Distribution separation (open-core correctness)

- [x] Implement distribution separation so Pro/Enterprise capabilities are **not shipped** inside the Community MIT wheel.
  - **Decision**: Runtime tier enforcement (single package) instead of separate packages
  - **Rationale**: Simplicity, transparency, maintainability; licensing enforces usage rights
- [x] Decide packaging layout (document in checklist notes before code moves):
  - [x] Single package (`code-scalpel`) with MIT license
  - [x] Runtime tier configuration via `CODE_SCALPEL_TIER` environment variable
  - [x] All code ships in one package; behavioral restrictions enforced at runtime
  - [x] No import boundaries needed (all code visible for auditing)
- [x] Implement packaging split:
  - [x] Tier checks in 4 major tools: `crawl_project`, `get_symbol_references`, `get_call_graph`, `get_graph_neighborhood`
  - [x] Community tier: discovery mode, depth/hop limits, file limits
  - [x] Pro/Enterprise tiers: full functionality
  - [x] All responses include `tier` field for audit trail
- [x] Verification:
  - [x] Created `scripts/verify_distribution_separation.py` (validates tier checks)
  - [x] Verified 5 tier check calls, 4 restricted features have checks
  - [x] Documented in `docs/architecture/distribution_separation.md`
- [ ] Container/image split (if you ship images):
  - [ ] Build Community image from Community distribution only.
  - [ ] Build Pro/Enterprise images from their respective distributions.
- [x] Acceptance:
  - [x] All code ships in single MIT-licensed package (transparency)
  - [x] Tier restrictions enforced at runtime via tier checks
  - [x] Verification script validates tier checks (`scripts/verify_distribution_separation.py`)
  - [x] Documentation explains runtime tier model and upgrade path
  - [ ] CI includes distribution verification check (script exists, needs integration)

### B) Release Notes / GitHub Release Attachment (Required)

- [ ] Add release notes file: `docs/release_notes/RELEASE_NOTES_v3.2.8.md`.
- [ ] Backfill (repo-only): ensure `docs/release_notes/RELEASE_NOTES_v3.2.7.md` exists on the default branch for historical completeness (cannot retrofit old tags).
- [ ] Ensure GitHub Release workflow uses `docs/release_notes/RELEASE_NOTES_v{VERSION}.md` as the release body.
- [ ] Ensure release notes are present **in the tag** (GitHub Release body must match tagged source).
- [ ] Verify behavior for legacy tags (warn+fallback vs fail hard) and keep it consistent.

### C) Tier Work (Current State vs Next)

- [ ] Confirm tier tool lists are still correct (Community / Pro / Enterprise).
- [ ] Confirm tier behavior split implementation matches V1.0 requirements (see section 1A).

### D) Docs-as-Contract (Required if tool surface changes)

- [ ] If any MCP tool signature/metadata changes, regenerate tool reference docs:
  - [ ] `docs/reference/mcp_tools_current.md`
  - [ ] `docs/reference/mcp_tools_by_tier.md`

---

## 2) Versioning (Required)

- [ ] Bump `pyproject.toml` project version to `3.2.8`.
- [ ] Update `__version__` in:
  - [ ] `src/code_scalpel/__init__.py`
  - [ ] `src/code_scalpel/autonomy/__init__.py`
- [ ] If any workflow defaults reference a tag, update defaults to `v3.2.8`:
  - [ ] `.github/workflows/release-confidence.yml`
  - [ ] `.github/workflows/publish-pypi.yml`

---

## 3) Local Pre-Release Confidence Checks (Must Pass Before Commit)

> Run these locally and fix failures before creating the release commit.

### A) Formatting & Lint

- [ ] `black --check --diff src/ tests/`
- [ ] `ruff check src/ tests/`

### B) Type Checking

- [ ] `pyright -p pyrightconfig.json`

### C) Security

- [ ] `bandit -r src/ -ll -ii -x '**/test_*.py' --format json --output bandit-report.json || true`
- [ ] `bandit -r src/ -ll -ii -x '**/test_*.py'`
- [ ] `pip-audit -r requirements-secure.txt --format json --output pip-audit-report.json`
- [ ] `pip-audit -r requirements-secure.txt`

### D) Tests

- [ ] `pytest tests/ -q`

### E) MCP Contract Tests (All Transports)

- [ ] `MCP_CONTRACT_TRANSPORT=stdio pytest -q tests/test_mcp_all_tools_contract.py`
- [ ] `MCP_CONTRACT_TRANSPORT=sse pytest -q tests/test_mcp_all_tools_contract.py`
- [ ] `MCP_CONTRACT_TRANSPORT=streamable-http pytest -q tests/test_mcp_all_tools_contract.py`

### F) Packaging

- [ ] `python -m build`
- [ ] `python -m twine check dist/*`

### G) Release Baseline Validation

- [ ] `python scripts/validate_all_releases.py`
- [ ] `python scripts/regression_test.py`

---

## 4) Repo Hygiene (Must Pass Before Commit)

- [ ] `git status` is clean aside from intended changes.
- [ ] No accidental file mode flips (e.g., executable bit on docs/yaml) in `git diff --summary`.
- [ ] Generated docs are committed (if required by CI).
- [ ] No secrets or tokens committed (spot-check diff for credentials).

---

## 5) Release Commit (One Commit)

> Create exactly one release commit after local gates pass.

- [ ] Commit includes:
  - [ ] Version bump (3.2.8)
  - [ ] Release notes file (3.2.8)
  - [ ] Any required workflow changes
  - [ ] Any regenerated docs/contracts

---

## 6) Tag + CI Release Confidence

- [ ] Create annotated tag: `v3.2.8`.
- [ ] Push branch + tag.
- [ ] Confirm GitHub Actions “Release Confidence” passes for `v3.2.8`.

---

## 7) Publish Steps

### A) GitHub Release

- [ ] Ensure GitHub Release is created for `v3.2.8`.
- [ ] Confirm release body is pulled from `docs/release_notes/RELEASE_NOTES_v3.2.8.md`.

### B) PyPI

- [ ] Confirm the PyPI publish workflow ran (tag-triggered) or run manual publish workflow for `v3.2.8`.
- [ ] Verify PyPI shows `code-scalpel==3.2.8` and installs cleanly.

---

## 8) Post-Release Verification

- [ ] Install test in a fresh venv:
  - [ ] `pip install code-scalpel==3.2.8`
  - [ ] `python -c "import code_scalpel; print(code_scalpel.__version__)"` → `3.2.8`
- [ ] Quick smoke: run one MCP contract test transport locally against installed package.

---

## Notes / Decisions Log

- Decision: GitHub Release workflow behavior when notes are missing in-tag: (fill)
- Decision: First tier behavior split in v3.2.8? (fill)
