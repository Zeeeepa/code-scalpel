# CI/CD Pipeline Documentation

This document is the central reference for all validation and release pipelines in Code Scalpel.

## Overview

Code Scalpel uses a **three-tier validation strategy** to catch issues early and prevent surprises in CI:

| Tier | Trigger | Script | Runtime | Purpose |
|------|---------|--------|---------|---------|
| 1 | Auto (pre-commit) | `verify_local.sh` | ~30-60s | Fast feedback with auto-fix |
| 2 | Manual (pre-push) | `verify.sh` | ~5-10min | Full local validation matching CI |
| 3 | Auto (push) | GitHub Actions CI | ~10-15min | Matrix testing across Python versions |

## Pipeline Architecture

```
Developer Commit
       │
       ▼
┌─────────────────┐
│  Pre-Commit      │  (~30-60s)
│  - Black (fix)   │
│  - Ruff (fix)    │  ← verify_local.sh
│  - Pyright       │
│  - detect-secrets│
│  - commit-msg    │
└────────┬────────┘
         │  commit succeeds
         ▼
┌─────────────────┐
│  Pre-Push        │  (~5-10min)
│  (manual)        │
│  - All 11 checks │  ← verify.sh
│  - Version sync  │
│  - Build check   │
│  - Docs validation│
└────────┬────────┘
         │  git push
         ▼
┌─────────────────┐
│  GitHub Actions  │  (~10-15min)
│  CI Matrix       │
│  - Python 3.10   │
│  - Python 3.11   │  ← .github/workflows/ci.yml
│  - Python 3.12   │
│  - Python 3.13   │
│  - 12+ stages    │
└────────┬────────┘
         │  all checks pass
         ▼
┌─────────────────┐
│  Release         │  (on tag)
│  - PyPI publish  │  ← .github/workflows/publish.yml
│  - GitHub Release│
└─────────────────┘
```

## Tier 1: Pre-Commit Hooks

Configured in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml).

### local-pre-flight
- **Script**: `scripts/verify_local.sh`
- **Runtime**: 30-60 seconds
- **Auto-fix**: Yes (Black and Ruff)
- **Checks**:
  1. Black formatting on `src/ tests/`
  2. Ruff linting on `src/ tests/`
  3. Pyright type checking
  4. Bandit security scan (warning only, non-blocking)
  5. pip-audit dependency audit (warning only, non-blocking)
  6. Pytest basic tests (no coverage requirement)

### detect-secrets
- **Tool**: Yelp/detect-secrets v1.4.0
- **Runtime**: 5-10 seconds
- **Purpose**: Prevent credential and secret leaks
- **Baseline**: `.secrets.baseline` (must exist in repo root)
- **See**: [DEVELOPMENT.md - detect-secrets troubleshooting](DEVELOPMENT.md#detect-secrets-hook-failing)

### commit-message-version
- **Script**: `scripts/hooks/ensure_commit_version.py`
- **Purpose**: Enforce version tag in commit messages
- **Pattern**: Messages must contain `v\d+\.\d+\.\d+` or `[YYYYMMDD_TAG]`

## Tier 2: Pre-Push Validation

**Script**: `scripts/verify.sh`

Run manually before pushing to ensure all CI checks will pass locally.

### Usage
```bash
./scripts/verify.sh              # Run all 11 checks
./scripts/verify.sh --skip-build # Skip expensive build check
```

### Pre-check: Version Sync
Before numbered steps, verify.sh checks that `pyproject.toml` and `src/code_scalpel/__init__.py` have matching versions. See `scripts/verify_version_sync.sh` for standalone usage.

### 11 Checks

| Step | Check | Tool | Blocking |
|------|-------|------|----------|
| 1 | Formatter | Black (check mode) | Yes |
| 2 | Linter | Ruff (check mode) | Yes |
| 3 | Type Check | Pyright | Yes |
| 4 | Security Scan | Bandit | Yes |
| 5 | Dependency Audit | pip-audit | Yes |
| 6 | Tests + Coverage | Pytest (24% min) | Yes |
| 7 | MCP Contracts | Pytest (3 transports) | Yes |
| 8 | Package Build | build (wheel + sdist) | Yes (skippable) |
| 9 | MCP Tools Ref | generate_mcp_tools_reference.py | Conditional |
| 10 | MCP Tier Matrix | generate_mcp_tier_matrix.py | Conditional |
| 11 | Documentation Sync | validate_docs_sync.py | Conditional |

Steps 9-11 are conditional: they run when the required license env vars are available, otherwise they are skipped with a warning (validated fully in CI with injected secrets).

## Tier 3: GitHub Actions CI

**Workflow**: `.github/workflows/ci.yml`

### Matrix
Tests run across **Python 3.10, 3.11, 3.12, 3.13** to ensure compatibility.

### Stages (12 total)
1. **Smoke Test** - Fast import validation
2. **License Setup** - Inject test JWTs from GitHub Secrets
3. **Ruff** - Lint check
4. **Black** - Formatting check
5. **Pyright** - Type check
6. **Pytest + Coverage** - Full test suite with coverage reporting
7. **Bandit** - Security scan
8. **pip-audit** - Dependency vulnerability check
9. **MCP Tools Reference** - Validates auto-generated documentation
10. **MCP Tier Matrix** - Validates tier documentation
11. **Documentation Sync** - Checks README/code alignment
12. **Coverage Upload** - Reports to Codecov

### Secrets Required

See [GITHUB_SECRETS.md](GITHUB_SECRETS.md) for full setup guide.

| Secret | Purpose | Required |
|--------|---------|----------|
| `TEST_PRO_LICENSE_JWT` | Enable Pro-tier in CI tests | Yes |
| `TEST_ENTERPRISE_LICENSE_JWT` | Enable Enterprise-tier in CI tests | Yes |
| `TEST_PRO_LICENSE_BROKEN_JWT` | Test license validation errors | Yes |
| `TEST_ENTERPRISE_LICENSE_BROKEN_JWT` | Test license validation errors | Yes |
| `CODECOV_TOKEN` | Upload coverage reports | Optional |

## Release Pipeline

**Workflow**: `.github/workflows/publish.yml`

### Trigger
Git tags matching `v*.*.*` (e.g., `v1.3.3`)

### Stages
1. Validate version tag matches `pyproject.toml`
2. Build wheel and sdist
3. Run full verification suite
4. Publish to PyPI
5. Create GitHub Release with artifacts

### Secrets Required
| Secret | Purpose |
|--------|---------|
| `PYPI_API_TOKEN` | Authenticate PyPI publish |

## Adding New Checks

To add a new check to all tiers consistently:

1. **Add to `scripts/verify_local.sh`** - Fast/non-blocking variant (warnings only)
2. **Add to `scripts/verify.sh`** - Comprehensive/blocking variant
3. **Add to `.github/workflows/ci.yml`** - As a CI stage
4. **Document in this file** - Update the tables above

Example: Adding shellcheck for bash scripts

```bash
# 1. verify_local.sh (non-blocking)
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck scripts/*.sh || echo "Warning: ShellCheck issues found"
fi

# 2. verify.sh (blocking)
echo "Step N/11: ShellCheck..."
shellcheck scripts/*.sh || { echo "ERROR: ShellCheck failed"; exit 1; }

# 3. ci.yml
- name: ShellCheck
  run: |
    sudo apt-get install -y shellcheck
    shellcheck scripts/*.sh
```

## Troubleshooting

For common issues and solutions, see [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting).
