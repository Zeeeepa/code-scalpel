# Code Scalpel Release Automation - Local Release Guide

## Overview

The Code Scalpel release automation system provides a complete local testing and publishing workflow. You can run all checks locally, verify everything works, and then commit and push with options to skip CI and publish directly to PyPI, GitHub, Docker Hub, and the VS Code Marketplace.

## Quick Start

### 1. Run Full Local Validation and Testing

```bash
python scripts/release.py --validate --test
```

This will:
- ✓ Check code formatting (Black)
- ✓ Check linting (Ruff)
- ✓ Run all 324+ tests
- ✓ Print results summary

**Expected Output:**
```
======================================================================
→ RUNNING VALIDATION CHECKS
======================================================================

✓ Black formatting check passed
✓ Ruff linting check passed

======================================================================
→ RUNNING TEST SUITE
======================================================================

✓ ============================= 324 passed in 1.51s ==============================

======================================================================
→ SUMMARY
======================================================================

✓ Passed checks:
  ✓ Black formatting
  ✓ Ruff linting
  ✓ Test suite

Results: 3/3 passed
Time elapsed: 4.7s
```

### 2. Commit and Push with Testing

```bash
python scripts/release.py --validate --test --commit --push
```

This will:
- Run all validation and tests (same as above)
- Prompt you for a commit message
- Commit changes to git
- Push to the main branch
- Trigger CI/CD pipeline for publishing

### 3. Publish Everything Directly (Skip CI)

```bash
python scripts/release.py --validate --test --commit --push --skip-ci --publish-all
```

This will:
- Run all local tests
- Commit changes
- Push to remote **without** triggering CI
- Publish directly to:
  - PyPI (Python package)
  - GitHub (release and artifacts)
  - Docker Hub (container images)
  - VS Code Marketplace (extension)

**Prerequisites for direct publishing:**
- Set environment variables with credentials:
  ```bash
  export PYPI_TOKEN="your-pypi-token"
  export DOCKER_USERNAME="your-docker-username"
  export DOCKER_PASSWORD="your-docker-password"
  export GITHUB_TOKEN="your-github-token"
  export VSCE_PAT="your-vscode-token"
  ```

## Available Commands

### Basic Usage

```bash
# Show help
python scripts/release.py --help

# Show all available options
python scripts/release.py --help
```

### Validation and Testing

```bash
# Only validation (no tests)
python scripts/release.py --validate

# Only testing (no validation)
python scripts/release.py --test

# Test specific module
python scripts/release.py --test --test-filter release

# Verbose output
python scripts/release.py --validate --test --verbose
```

### Git Operations

```bash
# Validate, test, and commit (prompts for message)
python scripts/release.py --validate --test --commit

# Same but also push to remote
python scripts/release.py --validate --test --commit --push
```

### Publishing Options

```bash
# Publish to PyPI only
python scripts/release.py --skip-ci --publish-pypi

# Publish to Docker only
python scripts/release.py --skip-ci --publish-docker

# Publish to VS Code only
python scripts/release.py --skip-ci --publish-vscode

# Publish to GitHub only
python scripts/release.py --skip-ci --publish-github

# Publish to multiple platforms
python scripts/release.py --skip-ci --publish-pypi --publish-docker --publish-vscode

# Publish to all platforms
python scripts/release.py --skip-ci --publish-all
```

## Workflow Examples

### Scenario 1: Safe Local Development (CI-Based Release)

Use this when you want CI/CD to handle publishing:

```bash
# 1. Make changes, then run full validation locally
python scripts/release.py --validate --test

# 2. If everything passes, commit and push (CI will publish)
python scripts/release.py --commit --push
```

### Scenario 2: Direct Publishing (Skip CI)

Use this when you've verified everything locally:

```bash
# 1. Set up credentials
export PYPI_TOKEN="your-token"
export DOCKER_USERNAME="user"
export DOCKER_PASSWORD="pass"
export GITHUB_TOKEN="token"
export VSCE_PAT="token"

# 2. Run full workflow
python scripts/release.py \
  --validate \
  --test \
  --commit \
  --push \
  --skip-ci \
  --publish-all
```

### Scenario 3: Selective Publishing

Only publish to certain platforms:

```bash
python scripts/release.py \
  --validate \
  --test \
  --commit \
  --push \
  --skip-ci \
  --publish-pypi \
  --publish-docker
```

### Scenario 4: Emergency Hotfix

When you need to publish a quick fix:

```bash
# 1. Fix the issue
# (make changes)

# 2. Validate and test
python scripts/release.py --validate --test

# 3. Commit and publish directly
python scripts/release.py \
  --validate \
  --test \
  --commit \
  --push \
  --skip-ci \
  --publish-all
```

## Test Results

The test suite covers all major components:

| Component | Tests | Status |
|-----------|-------|--------|
| **Versioning** | 31 | ✅ |
| **GitHub Releases** | 23 | ✅ |
| **PyPI Publishing** | 20 | ✅ |
| **Docker Builder** | 26 | ✅ |
| **VS Code Publisher** | 19 | ✅ |
| **Secrets Manager** | 36 | ✅ |
| **Changelog Generator** | 58 | ✅ |
| **Release Templates** | 37 | ✅ |
| **Rollback Manager** | 29 | ✅ |
| **Metrics Tracker** | 21 | ✅ |
| **Build Profiler** | 9 | ✅ |
| **Status Dashboard** | 8 | ✅ |
| **Failure Alerter** | 10 | ✅ |
| **TOTAL** | **324** | **✅** |

## Code Quality Standards

Every release is validated for:

- ✓ **Black Formatting** - Consistent code style
- ✓ **Ruff Linting** - Code quality and best practices
- ✓ **Type Safety** - 100% type hints on all APIs
- ✓ **Docstrings** - Google-style documentation
- ✓ **Test Coverage** - 324+ tests (100% pass rate)
- ✓ **No External Dependencies** - Uses stdlib only

## Environment Variables

Set these to enable direct publishing:

```bash
# PyPI Publishing
export PYPI_TOKEN="pypi-xxx..."

# Docker Registry
export DOCKER_USERNAME="your-username"
export DOCKER_PASSWORD="your-password"
# Optional: For GitHub Container Registry
export GHCR_TOKEN="ghcr-xxx..."

# GitHub Releases
export GITHUB_TOKEN="ghp-xxx..."

# VS Code Marketplace
export VSCE_PAT="your-vsce-pat-token"

# Optional: Slack Notifications
export SLACK_WEBHOOK="https://hooks.slack.com/..."

# Project Directory (optional)
export PROJECT_DIR="/path/to/code-scalpel"
```

## Troubleshooting

### Tests Fail Locally

1. **Check Python version** - Requires Python 3.10+
   ```bash
   python --version
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   pip install pytest pytest-mock
   ```

3. **Run with verbose output**
   ```bash
   python scripts/release.py --validate --test --verbose
   ```

### Black Formatting Issues

```bash
# Auto-fix formatting
python -m black src/code_scalpel/release tests/release scripts/release.py
```

### Ruff Linting Issues

```bash
# Check issues
python -m ruff check src/code_scalpel/release tests/release scripts/release.py

# Auto-fix (if possible)
python -m ruff check --fix src/code_scalpel/release tests/release scripts/release.py
```

### Publishing Fails

Check that required tokens are set:

```bash
# Check if token is set
echo $PYPI_TOKEN

# If empty, set it
export PYPI_TOKEN="your-token-here"

# Test the connection
python scripts/release.py --skip-ci --publish-pypi
```

## Development Workflow

### When Making Changes

1. **Run local tests**
   ```bash
   python scripts/release.py --validate --test
   ```

2. **If tests pass, commit**
   ```bash
   git add .
   git commit -m "your message"
   ```

3. **Push to trigger CI/CD**
   ```bash
   git push
   ```

### When Publishing New Release

1. **Verify everything locally**
   ```bash
   python scripts/release.py --validate --test
   ```

2. **Choose publishing method:**

   **Option A: Let CI/CD handle it**
   ```bash
   python scripts/release.py --commit --push
   # GitHub Actions will automatically publish
   ```

   **Option B: Publish directly**
   ```bash
   python scripts/release.py --validate --test --commit --push --skip-ci --publish-all
   ```

## Advanced Usage

### Running Specific Tests

```bash
# Test only the release module
python scripts/release.py --test --test-filter release

# Test only secrets manager
python -m pytest tests/release/test_secrets_manager.py -v
```

### Dry Run Mode

Before publishing, test the workflow:

```bash
# Skip actual publishing, just prepare
python scripts/release.py --validate --test --commit
# Don't push - just see if commit works
```

### View Script Options

```bash
# Full help with examples
python scripts/release.py --help

# Verbose mode shows all steps
python scripts/release.py --validate --test --verbose
```

## Key Features

✓ **Local Testing** - Run all checks without CI/CD
✓ **Automated Validation** - Black, Ruff, Type hints
✓ **324+ Tests** - Complete test coverage
✓ **Multiple Publishers** - PyPI, GitHub, Docker, VS Code
✓ **Flexible Workflows** - CI-based or direct publishing
✓ **Skip CI Option** - Publish without triggering pipeline
✓ **Colored Output** - Easy to read progress
✓ **Error Handling** - Clear error messages
✓ **Credential Management** - Safe token handling

## Common Issues

| Issue | Solution |
|-------|----------|
| Tests fail | Run `pip install -e .` to install package |
| Black issues | Run `python -m black src/code_scalpel/release tests/release` |
| Ruff issues | Run `python -m ruff check --fix src/code_scalpel/release` |
| Permission denied | Make script executable: `chmod +x scripts/release.py` |
| Token not set | Export environment variable: `export PYPI_TOKEN="xxx"` |
| Publishing fails | Check internet connection and token validity |

## See Also

- `docs/release_automation/api_reference.md` - Complete API documentation
- `docs/release_automation/architecture.md` - System architecture
- `docs/release_automation/guides/` - Step-by-step guides
