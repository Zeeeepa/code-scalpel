<!-- [20251215_DOCS] Project Management: Release Management -->

# Release Management

This document defines the release management process for Code Scalpel.

---

## Release Philosophy

- **Ship early, ship often**: Prefer frequent small releases over rare large ones
- **Quality over speed**: Never release with known critical bugs
- **Semantic versioning**: Strict adherence to SemVer
- **Evidence-based**: All releases require documented evidence

---

## Versioning Strategy

### Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Breaking API changes
MINOR: New features, backward compatible
PATCH: Bug fixes, backward compatible
```

### Examples

| Change | Version Bump | Example |
|--------|--------------|---------|
| New MCP tool | MINOR | 1.5.0 → 1.6.0 |
| Bug fix | PATCH | 1.5.0 → 1.5.1 |
| Tool parameter change | MAJOR | 1.5.0 → 2.0.0 |
| Performance improvement | PATCH | 1.5.0 → 1.5.1 |
| Dependency update | PATCH | 1.5.0 → 1.5.1 |

---

## Release Types

### Regular Release

- Scheduled cadence (bi-weekly target)
- Full test suite execution
- Complete documentation update
- Full evidence generation

### Hotfix Release

- Unscheduled, triggered by critical bug
- Minimal changes (fix only)
- Expedited testing (critical paths)
- Abbreviated documentation

### Pre-Release

- Alpha/Beta/RC releases
- Opt-in installation
- Limited documentation
- Community testing

---

## Release Process

### Phase 1: Preparation

```
1. [ ] Create release branch from main
2. [ ] Update version in pyproject.toml
3. [ ] Update CHANGELOG/release notes
4. [ ] Review open issues/PRs
```

### Phase 2: Validation

```
1. [ ] Run full test suite (pytest)
2. [ ] Verify coverage ≥95%
3. [ ] Run linting (ruff, black)
4. [ ] Run security scan
5. [ ] Run benchmarks
```

### Phase 3: Evidence

```
1. [ ] Generate test evidence JSON
2. [ ] Generate coverage report
3. [ ] Create release artifacts
4. [ ] Update release gate checklist
```

### Phase 4: Release

```
1. [ ] Tag release (git tag vX.Y.Z)
2. [ ] Build package (python -m build)
3. [ ] Upload to PyPI
4. [ ] Publish GitHub release
5. [ ] Update documentation
```

### Phase 5: Verification

```
1. [ ] Install from PyPI
2. [ ] Run smoke tests
3. [ ] Verify MCP integration
4. [ ] Monitor for issues
```

---

## Release Gate Criteria

### Mandatory Gates

| Gate | Criteria | Blocking |
|------|----------|----------|
| Tests | 100% pass | Yes |
| Coverage | ≥95% | Yes |
| Lint | 0 errors | Yes |
| Security | No critical vulns | Yes |

### Advisory Gates

| Gate | Criteria | Blocking |
|------|----------|----------|
| Benchmarks | No regression >10% | No |
| Documentation | Updated | No |
| Examples | Working | No |

---

## Release Artifacts

### Required Artifacts

```
release_artifacts/vX.Y.Z/
├── vX.Y.Z_test_evidence.json
├── coverage.xml
├── pytest_full.log
├── ruff_black.log
└── RELEASE_NOTES.md (linked)
```

### Evidence JSON Format

```json
{
  "version": "2.0.1",
  "timestamp": "2025-12-15T00:00:00Z",
  "test_results": {
    "total": 2698,
    "passed": 2698,
    "failed": 0,
    "skipped": 0,
    "xfailed": 1
  },
  "coverage": {
    "line": 95.0,
    "branch": 92.0
  },
  "lint_results": {
    "ruff_errors": 0,
    "black_reformatted": 0
  }
}
```

---

## Release Cadence

### Target Schedule

| Week | Activity |
|------|----------|
| Week 1-2 | Feature development |
| Week 3 | Stabilization, bug fixes |
| Week 4 | Release preparation, testing |
| End of Week 4 | Release |

### Actual Cadence

Releases happen when ready, not on fixed schedule. Quality gates must pass.

---

## Release Communication

### Pre-Release

- Draft release notes
- Notify early adopters (if breaking changes)
- Update documentation

### Release Announcement

- GitHub Release with notes
- PyPI package update
- Documentation site update

### Post-Release

- Monitor issue tracker
- Respond to bug reports
- Plan hotfix if needed

---

## Hotfix Process

### Triggers

- Security vulnerability
- Critical functionality broken
- Data loss/corruption risk

### Expedited Process

```
1. Create hotfix branch from release tag
2. Implement minimal fix
3. Run critical path tests
4. Generate abbreviated evidence
5. Release immediately
6. Cherry-pick to main
```

### Hotfix Naming

```
vX.Y.Z → vX.Y.(Z+1)

Example: v2.0.0 → v2.0.1 (hotfix)
```

---

## Rollback Procedure

### When to Rollback

- Critical bug discovered post-release
- Incompatibility with major clients
- Security vulnerability introduced

### Rollback Steps

```
1. Yank PyPI release (if needed)
2. Publish previous version as current
3. Document rollback reason
4. Communicate to users
5. Plan fixed release
```

---

## Tools and Automation

### Build Tools

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### Evidence Generation

```bash
# Run tests with coverage
pytest --cov=src --cov-report=xml -v > pytest_full.log 2>&1

# Run linting
ruff check src/ > ruff_black.log 2>&1
black --check src/ >> ruff_black.log 2>&1
```

### Release Tagging

```bash
# Create annotated tag
git tag -a v2.0.1 -m "Release v2.0.1: Bug fixes"
git push origin v2.0.1
```

---

## Metrics

### Release Metrics to Track

| Metric | Target |
|--------|--------|
| Time to release | <1 day from code freeze |
| Post-release bugs | <2 per release |
| Hotfix frequency | <1 per 5 releases |
| User-reported issues | <5 per release |

---

## References

- [Release Gate Checklist](../release_gate_checklist.md)
- [Metrics Dashboard](METRICS_DASHBOARD.md)
- [Risk Register](RISK_REGISTER.md)
