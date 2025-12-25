# vX.Y.Z Release Checklist

**Target Version:** X.Y.Z  
**Target Tag:** vX.Y.Z  
**Release Type:** [Major | Minor | Patch | Hotfix]  
**Owner:** (fill)  
**Date:** (fill)

---

## 0) Scope Lock (Do First)

- [ ] Confirm the exact scope for vX.Y.Z (features/bugfixes/docs only).
  - **Proposed Scope**: (describe scope here)
- [ ] Confirm whether vX.Y.Z is allowed to include workflow/process changes (CI, release pipelines).
  - **Decision**: (yes/no and rationale)
- [ ] Confirm whether vX.Y.Z starts any tier **behavior** splits (not just tool exposure).
  - **Decision**: (yes/no and details)
- [ ] Lock scope: No new work items after this point without explicit approval.

---

## 1) Development Tasks (vX.Y.Z Work Items)

### A) Features / Enhancements

> List all new features or enhancements for this release.

- [ ] Feature 1: (description)
  - [ ] Implementation complete
  - [ ] Tests added
  - [ ] Documentation updated
- [ ] Feature 2: (description)
  - [ ] Implementation complete
  - [ ] Tests added
  - [ ] Documentation updated

### B) Bug Fixes

> List all bug fixes for this release.

- [ ] Bug 1: (description)
  - [ ] Root cause identified
  - [ ] Fix implemented
  - [ ] Regression test added
  - [ ] Verified fix resolves issue
- [ ] Bug 2: (description)
  - [ ] Root cause identified
  - [ ] Fix implemented
  - [ ] Regression test added
  - [ ] Verified fix resolves issue

### C) Documentation Updates

- [ ] Add release notes file: `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md`
- [ ] Update any affected user guides
- [ ] Update API documentation if signatures changed
- [ ] Update README if user-facing changes

### D) Tier Work (if applicable)

- [ ] Review tier tool lists (Community / Pro / Enterprise)
- [ ] Implement any tier behavior changes
- [ ] Update tier documentation
- [ ] Test tier enforcement

### E) Docs-as-Contract (if tool surface changes)

- [ ] If any MCP tool signature/metadata changes, regenerate tool reference docs:
  - [ ] `docs/reference/mcp_tools_current.md`
  - [ ] `docs/reference/mcp_tools_by_tier.md`
- [ ] If response envelope changes, update:
  - [ ] `docs/reference/mcp_response_envelope.md`
  - [ ] `docs/reference/error_codes.md`
- [ ] If audit events change, update:
  - [ ] `docs/reference/audit_event_schema.md`

---

## 2) Versioning (Required)

- [ ] Bump `pyproject.toml` project version to `X.Y.Z`.
- [ ] Update `__version__` in:
  - [ ] `src/code_scalpel/__init__.py`
  - [ ] `src/code_scalpel/autonomy/__init__.py`
- [ ] If any workflow defaults reference a tag, update defaults to `vX.Y.Z`:
  - [ ] `.github/workflows/release-confidence.yml`
  - [ ] `.github/workflows/publish-pypi.yml`
- [ ] Update any version references in documentation

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
- [ ] Review security reports for new vulnerabilities

### D) Tests

- [ ] `pytest tests/ -q`
- [ ] Verify all new tests pass
- [ ] Verify no test regressions

### E) MCP Contract Tests (All Transports)

- [ ] `MCP_CONTRACT_TRANSPORT=stdio pytest -q tests/test_mcp_all_tools_contract.py`
- [ ] `MCP_CONTRACT_TRANSPORT=sse pytest -q tests/test_mcp_all_tools_contract.py`
- [ ] `MCP_CONTRACT_TRANSPORT=streamable-http pytest -q tests/test_mcp_all_tools_contract.py`

### F) Packaging

- [ ] `python -m build`
- [ ] `python -m twine check dist/*`
- [ ] Verify package contents are correct

### G) Release Baseline Validation

- [ ] `python scripts/validate_all_releases.py`
- [ ] `python scripts/regression_test.py`

### H) Distribution Separation Verification (if applicable)

- [ ] `python scripts/verify_distribution_separation.py`

### I) Additional Verification (as needed)

- [ ] Run any release-specific verification scripts
- [ ] Verify backward compatibility if required
- [ ] Test upgrade path from previous version

---

## 4) Repo Hygiene (Must Pass Before Commit)

- [ ] `git status` is clean aside from intended changes.
- [ ] No accidental file mode flips (e.g., executable bit on docs/yaml) in `git diff --summary`.
- [ ] Generated docs are committed (if required by CI).
- [ ] No secrets or tokens committed (spot-check diff for credentials).
- [ ] No debug code, console.log, or temporary files committed.
- [ ] All TODO/FIXME comments addressed or documented.

---

## 5) Release Commit (One Commit)

> Create exactly one release commit after local gates pass.

- [ ] Stage all release changes: `git add -A`
- [ ] Commit with descriptive message: `git commit -m "Release vX.Y.Z: [brief summary]"`
- [ ] Commit includes:
  - [ ] Version bump (X.Y.Z)
  - [ ] All feature/bugfix code
  - [ ] Release notes file (vX.Y.Z)
  - [ ] Any updated tests
  - [ ] Any regenerated docs
  - [ ] Any workflow/config updates
  - **Commit SHA**: (will be filled after commit)
- [ ] Verify commit with `git show HEAD` (review diff)

---

## 6) Tag + CI Release Confidence

- [ ] Create annotated tag with release notes:
  ```bash
  git tag -a vX.Y.Z -m "Release vX.Y.Z: [brief summary]"
  ```
- [ ] Verify tag created: `git tag -l vX.Y.Z`
- [ ] Push branch: `git push origin <branch-name>`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Monitor GitHub Actions "Release Confidence" workflow
- [ ] Confirm all CI checks pass for vX.Y.Z tag

---

## 7) Publish Steps

### A) GitHub Release

- [ ] Navigate to GitHub Releases page
- [ ] Verify GitHub Release auto-created for vX.Y.Z (if workflow configured)
- [ ] If manual creation needed:
  - [ ] Create new release from vX.Y.Z tag
  - [ ] Copy content from `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md`
  - [ ] Add release category (Major/Minor/Patch/Hotfix)
  - [ ] Attach any release artifacts if applicable
- [ ] Confirm release is published and visible

### B) PyPI (if applicable)

- [ ] Verify PyPI publish workflow triggered (tag-based trigger)
- [ ] If manual publish needed:
  - [ ] Run manual publish workflow for vX.Y.Z
  - [ ] Or use: `python -m twine upload dist/*`
- [ ] Wait for PyPI processing (usually <5 minutes)
- [ ] Verify package appears on PyPI: https://pypi.org/project/code-scalpel/X.Y.Z/
- [ ] Verify package metadata is correct (version, description, classifiers)

### C) Container Images (if applicable)

- [ ] Verify container image build workflow triggered
- [ ] Verify images pushed to registry with vX.Y.Z tag
- [ ] Test pulling and running container image

---

## 8) Post-Release Verification

### A) Installation Test

- [ ] Create fresh virtual environment:
  ```bash
  python -m venv /tmp/test-vX.Y.Z
  source /tmp/test-vX.Y.Z/bin/activate  # or activate.bat on Windows
  ```
- [ ] Install from PyPI:
  ```bash
  pip install code-scalpel==X.Y.Z
  ```
- [ ] Verify installation:
  ```bash
  python -c "import code_scalpel; print(code_scalpel.__version__)"
  # Should output: X.Y.Z
  ```
- [ ] Verify dependencies installed correctly

### B) Smoke Tests

- [ ] Run one MCP contract test against installed package:
  ```bash
  MCP_CONTRACT_TRANSPORT=stdio pytest -q tests/test_mcp_all_tools_contract.py -k "test_extract_code"
  ```
- [ ] Test key features/fixes from this release:
  - [ ] Feature 1 verification
  - [ ] Feature 2 verification
  - [ ] Bug fix 1 verification
  - [ ] Bug fix 2 verification

### C) Integration Tests (as applicable)

- [ ] Test MCP server startup
- [ ] Test tool invocations
- [ ] Test tier enforcement (if changes)
- [ ] Test backward compatibility (if required)

---

## 9) Communication & Documentation

### A) Internal Communication

- [ ] Notify team of release completion
- [ ] Share release notes with stakeholders
- [ ] Update project roadmap/status

### B) External Communication (if applicable)

- [ ] Announce release on project blog/website
- [ ] Post to relevant social media channels
- [ ] Notify users on Discord/Slack/mailing list
- [ ] Update documentation website

### C) Monitoring

- [ ] Monitor GitHub issues for release-related reports
- [ ] Monitor PyPI download stats
- [ ] Watch for installation/compatibility issues

---

## 10) Exhaustive Testing (Optional but Recommended)

- [ ] Run Ninja Warrior exhaustive test suite against vX.Y.Z
- [ ] Analyze results and compare to previous version
- [ ] Update exhaustive test analysis document
- [ ] Document any new xfailed tests or xpassed tests
- [ ] Plan follow-up work based on findings

---

## 11) Post-Release Cleanup

- [ ] Remove or update any release-specific branches
- [ ] Archive release artifacts
- [ ] Update milestones/project boards
- [ ] Plan next release (if applicable)
- [ ] Document lessons learned from release process

---

## Notes / Decisions Log

> Use this section to document important decisions made during the release process.

- **Decision 1**: (date) - (decision and rationale)
- **Decision 2**: (date) - (decision and rationale)

---

## Troubleshooting

> Common issues and solutions during release process.

### Issue: CI tests fail after tag push
**Solution**: Review CI logs, fix issues, delete tag, re-tag after fixes

### Issue: PyPI publish fails
**Solution**: Check twine credentials, verify package metadata, check PyPI status page

### Issue: Version conflicts
**Solution**: Ensure all version references updated (pyproject.toml, __init__.py, workflows)

### Issue: Documentation not updating
**Solution**: Verify docs are committed in release commit, regenerate if needed

---

## Release Checklist Metadata

- **Template Version**: 1.0.0
- **Last Updated**: 2024-12-24
- **Based On**: v3.2.8 release process
- **Applicable To**: Code Scalpel v3.2.9+
