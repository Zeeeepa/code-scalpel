<!-- [20251221_DOCS] Public-Fork Checklist - v1.0 ("go public" readiness) -->

# Public-Fork Checklist (v1.0)

This checklist is for forking the current Code Scalpel codebase into a **public-facing v1.0** repository and shipping it with high confidence (docs, demos, listings, evidence).

It is intentionally **exhaustive** and assumes we want a public fork that is:
- legally clean,
- security-audited,
- reproducible to build,
- easy to install and run,
- documented and demoable,
- acceptable to MCP registries/directories,
- ready for initial community adoption and a clear premium/pro upgrade path.

---

## 0) Decisions (must be explicit before doing anything)

- [ ] **Versioning strategy** decided and recorded.
  - Option A: Public fork starts at `1.0.0` (marketing version) even if upstream was `3.x`.
  - Option B: Public fork keeps upstream semver (`3.1.0`) to preserve chronological meaning.
  - Evidence: A short note in `README.md` or `docs/` explaining the choice and compatibility expectations.

- [ ] **Public scope** decided: what is included in v1.0.
  - Tools included/excluded (if any)
  - Supported languages and limitations
  - What “production-ready” means (local use vs enterprise governance)

- [ ] **Premium/Pro plan boundaries** decided (even if Pro is not implemented yet).
  - What’s free forever
  - What’s paid (if any)
  - What’s roadmap only
  - Ensure the public repo does not imply features that don’t exist

- [ ] **Community vs Pro packaging model** decided.
  - Option A: Community is the only public package; Pro/Enterprise ships as a separate add-on package/plugin.
  - Option B: Single package with feature gating (discouraged: creates licensing as a Community blocker).
  - Evidence: short statement in `README.md` or `docs/` describing how Pro is added.

- [ ] **Licensing mode** decided (for Pro/Enterprise).
  - Recommended: offline signed license file (plus optional short grace window via cached “last known good”).
  - Explicitly decide: fail-closed vs fail-open behavior for Pro features.
  - Evidence: one paragraph in public docs; do not surprise users.

---

## 1) Repo Hygiene (public fork safety)

### 1.1 Remove sensitive / internal content

- [ ] Search for secrets and purge them.
  - Evidence: `release_artifacts/v1.0.0/security/secret_scan.txt`
  - Suggested commands:
    - `git grep -n "pypi-"`
    - `git grep -n "BEGIN PRIVATE KEY"`
    - `git grep -n "AWS_SECRET"`
    - `git grep -n "OPENAI_API_KEY"`

- [ ] Verify `.env` is not committed.
  - Evidence: `release_artifacts/v1.0.0/security/dotenv_audit.txt`

- [ ] Verify certs/sample keys are non-sensitive.
  - If `certs/` contains real material, remove or replace with dev/test-only examples.
  - Evidence: `release_artifacts/v1.0.0/security/certs_review.txt`

- [ ] Remove or sanitize internal/proprietary references.
  - Company internal names, internal URLs, private Slack links, private issue trackers
  - Evidence: `release_artifacts/v1.0.0/repo/public_sanitization_notes.md`

### 1.2 Repository metadata

- [ ] Ensure top-level docs exist and are consistent:
  - `README.md`
  - `LICENSE`
  - `SECURITY.md`
  - `DOCKER_QUICK_START.md`
  - `DEVELOPMENT_ROADMAP.md`

- [ ] Ensure `CONTRIBUTING.md` exists and is appropriate for public.

- [ ] Ensure `.gitignore` covers `.env`, `.venv`, `.pytest_cache`, build artifacts.

- [ ] Ensure issues/PR templates are present (optional but recommended).
  - `.github/ISSUE_TEMPLATE/*`
  - `.github/pull_request_template.md`

---

## 2) Legal, Licensing, and Attribution

- [ ] Confirm license choice (MIT currently) and ensure it is consistent across:
  - `LICENSE`
  - `pyproject.toml` classifiers
  - `README.md` badges/headers

- [ ] Third-party licenses reviewed.
  - Evidence: `release_artifacts/v1.0.0/legal/third_party_licenses_report.md`
  - Verify that tree-sitter bindings, parsers, and tokenizers are compliant with distribution.

- [ ] Trademark text reviewed.
  - If “Code Scalpel” is a trademark, ensure wording is appropriate for a public OSS repo.

---

## 3) Supply Chain, Packaging, and Distribution

### 3.1 Packaging correctness

- [ ] `pyproject.toml` is correct for public publishing.
  - Name, version, description, authors/maintainers, URLs, classifiers

- [ ] `MANIFEST.in` includes what we actually want to ship.
  - Exclude tests/benchmarks if not intended
  - Include required runtime data files

- [ ] Wheels and sdists build cleanly.
  - Evidence:
    - `release_artifacts/v1.0.0/build/build_log.txt`
    - `release_artifacts/v1.0.0/build/dist_tree.txt`
  - Suggested commands:
    - `python -m build`
    - `twine check dist/*`

- [ ] Install test from built artifacts in a clean venv.
  - Evidence: `release_artifacts/v1.0.0/build/install_smoke_test.txt`

### 3.2 Dependency and vulnerability scanning

- [ ] Dependency vulnerability scan executed.
  - Evidence: `release_artifacts/v1.0.0/security/dependency_scan.json`
  - Suggested approaches:
    - OSV scan
    - `pip-audit`

- [ ] Dependency pinning strategy confirmed.
  - If pins exist, justify them.
  - If no pins, ensure minimum versions are safe.

### 3.3 Reproducibility

- [ ] Document supported Python versions (3.9+ currently).
- [ ] Confirm CI matrix matches support statement.
- [ ] Confirm deterministic outputs where claimed.

---

## 4) Security Posture (public release expectations)

### 4.1 Security claims must map to evidence

- [ ] For each security claim in `README.md` (sink coverage, taint tracking, etc.), ensure:
  - There is a test
  - There is evidence output
  - The claim is phrased accurately (no overclaims)

- [ ] Run Code Scalpel security tooling against its own codebase (dogfooding).
  - Evidence: `release_artifacts/v1.0.0/security/self_scan_report.json`

### 4.2 OWASP / CWE mapping

- [ ] Validate sink-to-CWE mapping list is up to date.
  - Evidence: `release_artifacts/v1.0.0/security/sink_registry_report.md`

### 4.3 Hardening review

- [ ] Confirm there is no dangerous default behavior:
  - No arbitrary code execution from untrusted input
  - No network calls unless explicitly enabled
  - File access obeys configured roots/policy

- [ ] Confirm policy engine fails closed (deny-by-default).
  - Note: only applicable if Policy Engine is shipped in the public fork (recommended as Pro/Enterprise add-on).
  - Evidence: `release_artifacts/v1.0.0/security/fail_closed_evidence.txt`

---

## 5) Quality Gates (tests, lint, type checking)

- [ ] Full test suite passes in clean environment.
  - Evidence: `release_artifacts/v1.0.0/test/pytest_full.log`

- [ ] Coverage gate meets declared minimum.
  - Evidence: `release_artifacts/v1.0.0/test/coverage.xml`

- [ ] Lint + format checks pass.
  - Evidence: `release_artifacts/v1.0.0/quality/ruff.log`
  - Evidence: `release_artifacts/v1.0.0/quality/black.log`

- [ ] Type checking passes.
  - Evidence: `release_artifacts/v1.0.0/quality/pyright.log` or `mypy.log`

- [ ] Smoke test the CLI.
  - Evidence: `release_artifacts/v1.0.0/test/cli_smoke.txt`

---

## 6) Product Readiness (docs, UX, correctness)

### 6.1 README accuracy

- [ ] README matches actual current behavior:
  - Correct version strings
  - Correct tool counts
  - Correct Docker image tags
  - Correct CLI commands
  - Correct MCP JSON examples

- [ ] Ensure no stale references to earlier versions.
  - Evidence: `release_artifacts/v1.0.0/docs/readme_audit.txt`

### 6.2 Documentation structure

- [ ] `docs/INDEX.md` is current and points to the canonical guides.

- [ ] Quickstart docs cover:
  - installation
  - starting MCP server (stdio + HTTP)
  - configuring roots
  - common troubleshooting

- [ ] Examples are runnable.
  - Evidence: `release_artifacts/v1.0.0/examples/examples_smoke.txt`

---

## 7) MCP Registry / Directory Readiness

> Goal: get listed on “all MCP sites” (registries/directories) without churn.

- [ ] Confirm MCP server identity metadata is consistent.
  - MCP name, description, tags, repo URL
  - `server.json` (if used)
  - README footer metadata (e.g., `mcp-name` comment)

- [ ] Verify tool schema outputs are stable and documented.
  - Evidence: `release_artifacts/v1.0.0/mcp/tools_inventory.json`

- [ ] Confirm transport modes documented:
  - stdio
  - HTTP
  - Docker

- [ ] Confirm health endpoint behavior and output.
  - Evidence: `release_artifacts/v1.0.0/mcp/health_endpoint.txt`

---

## 8) Demos and Media Kit (launch-grade)

### 8.1 Demo scenarios (must be scripted)

- [ ] Security demo: find a non-trivial injection flow.
  - Evidence: `release_artifacts/v1.0.0/demos/security_demo.md`

- [ ] Surgical extraction demo: show token reduction and precision.
  - Evidence: `release_artifacts/v1.0.0/demos/token_efficiency_demo.md`

- [ ] “Safe refactor” demo: `simulate_refactor` proves safety.
  - Evidence: `release_artifacts/v1.0.0/demos/refactor_demo.md`

- [ ] “Impact analysis” demo: callers/deps identified and scoped.
  - Evidence: `release_artifacts/v1.0.0/demos/impact_demo.md`

### 8.2 Reproducible demo environment

- [ ] Provide a small demo repo (or `examples/`) that works out-of-the-box.
  - Includes:
    - vulnerable sample
    - multi-language sample
    - expected outputs

- [ ] Docker demo works end-to-end.
  - Evidence: `release_artifacts/v1.0.0/demos/docker_demo.txt`

---

## 9) Premium/Pro Readiness (even if not launched yet)

<!-- [20251221_DOCS] Clarified Community vs Pro packaging + licensing behavior -->

- [ ] **v1.0 scope note: Pro add-on hooks deferred to v3.1.1.**
  - For the v1.0 public fork, treat Pro/Enterprise as documentation + roadmap boundaries only.
  - Do not block Community release on Pro infrastructure (license issuance/validation, paid tool registration).

- [ ] **Community remains fully functional without Pro.**
  - No license check is required for Community tools.
  - No hidden telemetry or mandatory network “phone home” behavior.

- [ ] **Pro/Enterprise ships as an add-on** (recommended).
  - Pro installs cleanly on top of Community.
  - Pro features are discoverable (documented capability list/tool list).
  - Pro is optional: absence yields clear “requires Pro” errors.

- [ ] **Licensing behavior is explicit and safe.**
  - Community tier: always usable offline.
  - Pro features: fail closed when no valid license is present.
  - If Pro supports offline usage: implement a short grace window based on cached “last known good” validation.
  - Pro gating errors include:
    - stable error code
    - actionable message
    - docs URL / upgrade URL

- [ ] Public messaging does not promise paid features that do not exist.

- [ ] If “Pro” is planned:
  - [ ] A clear roadmap statement exists (what/when, not over-promising).
  - [ ] A contact path exists (email or website link).

- [ ] If rate limiting/licensing will exist later:
  - [ ] Ensure the OSS repo does not contain hidden telemetry or “phone home.”
  - [ ] Document any future licensing plans honestly.

---

## 10) Evidence Bundle (required for confidence)

Create a release folder:
- `release_artifacts/v1.0.0/`

<!-- [20251221_DOCS] Split evidence expectations: Community required, Pro optional -->

Evidence scope:
- Community launch requires the full evidence bundle below.
- Pro/Enterprise evidence is only required if shipping a Pro add-on at the same time.

Minimum expected structure:
- `release_artifacts/v1.0.0/build/`
- `release_artifacts/v1.0.0/test/`
- `release_artifacts/v1.0.0/quality/`
- `release_artifacts/v1.0.0/security/`
- `release_artifacts/v1.0.0/mcp/`
- `release_artifacts/v1.0.0/demos/`
- `release_artifacts/v1.0.0/legal/`
- `release_artifacts/v1.0.0/repo/`

Required evidence files (minimum):
- [ ] `release_artifacts/v1.0.0/test/pytest_full.log`
- [ ] `release_artifacts/v1.0.0/test/coverage.xml`
- [ ] `release_artifacts/v1.0.0/quality/ruff.log`
- [ ] `release_artifacts/v1.0.0/quality/black.log`
- [ ] `release_artifacts/v1.0.0/security/dependency_scan.json`
- [ ] `release_artifacts/v1.0.0/security/secret_scan.txt`
- [ ] `release_artifacts/v1.0.0/mcp/tools_inventory.json`
- [ ] `release_artifacts/v1.0.0/mcp/health_endpoint.txt`
- [ ] `release_artifacts/v1.0.0/demos/security_demo.md`
- [ ] `release_artifacts/v1.0.0/demos/token_efficiency_demo.md`

Optional Pro/Enterprise evidence (only if shipping Pro now):
- [ ] `release_artifacts/v1.0.0/pro/licensing/license_behavior.md` (fail-closed + grace policy)
- [ ] `release_artifacts/v1.0.0/pro/licensing/trial_flow.md` (how trials are issued + validated)
- [ ] `release_artifacts/v1.0.0/pro/mcp/pro_tools_inventory.json` (additional tools/capabilities)
- [ ] `release_artifacts/v1.0.0/pro/security/policy_fail_closed_evidence.txt` (deny-by-default verified)

---

## 11) Final Go/No-Go Signoff

- [ ] All checklist sections 0–10 completed.
- [ ] Evidence bundle present and reviewed by at least one other human.
- [ ] README claims match evidence outputs.
- [ ] All MCP tool schemas validated.
- [ ] Clean install smoke test from wheel succeeded.

**Decision:**
- [ ] GO: fork public and announce
- [ ] NO-GO: list blockers and owners
