# v3.2.8 Release Checklist

**Target Version:** 3.2.8  
**Target Tag:** v3.2.8  
**Release Type:** Patch (Production-fork preparation)  
**Owner:** (fill)  
**Date:** (fill)

---

## 0) Scope Lock (Do First)

- [x] Confirm the exact scope for v3.2.8 (features/bugfixes/docs only).
  - **Confirmed**: V1.0 production requirements (response envelope, tier behavior, distribution separation)
- [x] Confirm whether v3.2.8 is allowed to include workflow/process changes (CI, release pipelines).
  - **Confirmed**: GitHub Release workflow improved to use release notes from tag
- [x] Confirm whether v3.2.8 starts any tier **behavior** splits (not just tool exposure).
  - **Confirmed**: Yes, 4 major tools have tier-based behavioral differences

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
  - [x] `docs/reference/audit_event_schema.md`

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
- [x] Container/image split (if you ship images): **N/A** — Not shipping container images in this release
- [x] Acceptance:
  - [x] All code ships in single MIT-licensed package (transparency)
  - [x] Tier restrictions enforced at runtime via tier checks
  - [x] Verification script validates tier checks (`scripts/verify_distribution_separation.py`)
  - [x] Documentation explains runtime tier model and upgrade path
  - [x] CI includes distribution verification check (integrated into CI pipeline)

### B) Release Notes / GitHub Release Attachment (Required)

- [x] Add release notes file: `docs/release_notes/RELEASE_NOTES_v3.2.8.md`.
- [x] Backfill (repo-only): ensure `docs/release_notes/RELEASE_NOTES_v3.2.7.md` exists on the default branch for historical completeness (cannot retrofit old tags).
- [x] Ensure GitHub Release workflow uses `docs/release_notes/RELEASE_NOTES_v{VERSION}.md` as the release body.
- [x] Ensure release notes are present **in the tag** (GitHub Release body must match tagged source).
  - **Implemented**: Workflow prefers notes from tag with `git show refs/tags/$TAG:$NOTES_PATH`
- [x] Verify behavior for legacy tags (warn+fallback vs fail hard) and keep it consistent.
  - **Implemented**: Fallback to current branch with warning for legacy tags

### C) Tier Work (Current State vs Next)

- [x] Confirm tier tool lists are still correct (Community / Pro / Enterprise).
  - **Confirmed**: All basic tools available to Community; 4 project-wide tools have restrictions
- [x] Confirm tier behavior split implementation matches V1.0 requirements (see section 1A).
  - **Confirmed**: Discovery vs deep crawl, file/depth/hop limits implemented and tested

### D) Docs-as-Contract (Required if tool surface changes)

- [x] If any MCP tool signature/metadata changes, regenerate tool reference docs:
  - [x] `docs/reference/mcp_tools_current.md`
  - [x] `docs/reference/mcp_tools_by_tier.md` (generated automatically)

---

## 2) Versioning (Required)

- [x] Bump `pyproject.toml` project version to `3.2.8`.
- [x] Update `__version__` in:
  - [x] `src/code_scalpel/__init__.py`
  - [x] `src/code_scalpel/autonomy/__init__.py`
- [x] If any workflow defaults reference a tag, update defaults to `v3.2.8`:
  - [x] `.github/workflows/release-confidence.yml`
  - [x] `.github/workflows/publish-pypi.yml`

---

## 3) Local Pre-Release Confidence Checks (Must Pass Before Commit)

> Run these locally and fix failures before creating the release commit.

### A) Formatting & Lint

- [x] `black --check --diff src/ tests/`
- [x] `ruff check src/ tests/`

### B) Type Checking

- [x] `pyright -p pyrightconfig.json`

### C) Security

- [x] `bandit -r src/ -ll -ii -x '**/test_*.py' --format json --output bandit-report.json || true`
- [x] `bandit -r src/ -ll -ii -x '**/test_*.py'`
- [x] `pip-audit -r requirements-secure.txt --format json --output pip-audit-report.json`
- [x] `pip-audit -r requirements-secure.txt`

### D) Tests

- [x] `pytest tests/ -q`

### E) MCP Contract Tests (All Transports)

- [x] `MCP_CONTRACT_TRANSPORT=stdio pytest -q tests/test_mcp_all_tools_contract.py`
- [x] `MCP_CONTRACT_TRANSPORT=sse pytest -q tests/test_mcp_all_tools_contract.py`
- [x] `MCP_CONTRACT_TRANSPORT=streamable-http pytest -q tests/test_mcp_all_tools_contract.py`

### F) Packaging

- [x] `python -m build`
- [x] `python -m twine check dist/*`

### G) Release Baseline Validation

- [x] `python scripts/validate_all_releases.py`
- [x] `python scripts/regression_test.py`

---

## 4) Repo Hygiene (Must Pass Before Commit)

- [x] `git status` is clean aside from intended changes.
- [x] No accidental file mode flips (e.g., executable bit on docs/yaml) in `git diff --summary`.
- [x] Generated docs are committed (if required by CI).
- [x] No secrets or tokens committed (spot-check diff for credentials).

---

## 5) Release Commit (One Commit)

> Create exactly one release commit after local gates pass.

- [x] Commit includes:
  - [x] Version bump (3.2.8)
  - [x] Release notes file (3.2.8)
  - [x] Any required workflow changes
  - [x] Any regenerated docs/contracts
  - **Commit**: 0e67bef

---

## 6) Tag + CI Release Confidence

- [x] Create annotated tag: `v3.2.8`.
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

- **Decision**: GitHub Release workflow behavior when notes are missing in-tag: Fallback to current branch file with warning (supports legacy tags)
- **Decision**: First tier behavior split in v3.2.8? YES - Runtime tier enforcement with 4 major tools having Community limits
- **Decision**: Distribution separation approach: Runtime tier enforcement (single package) over separate packages
  - Rationale: Simplicity, transparency, maintainability, trust
- **Decision**: Default tier: Community (was incorrectly defaulting to Enterprise; fixed in commit 9ebc393)
- **Commits**:
  - aa9c911: Universal response envelope, tier behavior, distribution separation
  - 9322652: Distribution verification script
  - 8f2bda7: Implementation review document
  - 9ebc393: Tier configuration fix and comprehensive documentation
  - 07b713e: Final release summary
  - 76de71f: Regenerated MCP tool reference docs with tier behavior
  - 6e27cfe: Audit event schema documentation
  - 8315a9c: CI distribution separation verification
