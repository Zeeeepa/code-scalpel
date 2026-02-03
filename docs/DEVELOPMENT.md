# Development Workflow

This document describes the local validation workflow for Code Scalpel development and how it aligns with GitHub Actions CI.

## Validation Tiers

Code Scalpel uses a **three-tier validation strategy** to balance speed and coverage:

### Tier 1: Pre-Commit Checks (Fast ~30-60 seconds)
**Script**: `./scripts/verify_local.sh`
**Trigger**: Automatically on every commit via pre-commit hook
**Purpose**: Fast feedback - catch formatting and obvious issues

**Checks**:
1. Black formatting (auto-fix on `src/` and `tests/`)
2. Ruff linting (auto-fix on `src/` and `tests/`)
3. Pyright type checking
4. Bandit security scan (warning-only, doesn't block)
5. pip-audit dependency audit (warning-only, doesn't block)
6. Pytest basic tests (no coverage requirement)

**Key**: Pre-commit is intentionally fast so developers don't get blocked. Security checks are warnings only.

### Tier 2: Pre-Push Validation (Comprehensive ~5-10 minutes)
**Script**: `./scripts/verify.sh`
**Trigger**: Manually before pushing (or via optional git hook)
**Purpose**: Comprehensive validation - match CI exactly

**Checks** (11 total):
1. Black formatting (check mode on `src/`, `tests/`, `examples/`)
2. Ruff linting (check mode)
3. Pyright type checking
4. Bandit security scan (blocking)
5. pip-audit dependency audit (blocking)
6. Pytest with coverage (24% minimum required)
7. MCP contract tests (validates all 3 transports: stdio, streamable-http, sse)
8. Package build verification (validates wheel and sdist)
9. MCP tools reference documentation (auto-generates if missing)
10. MCP tools tier matrix documentation (auto-generates if missing)
11. Documentation sync validation (ensures README and code match)

**Key**: This matches all GitHub Actions CI checks except multi-Python matrix (3.10-3.13 tested only in CI).

### Tier 3: Full CI Simulation (Optional ~15-20 minutes)
**Script**: `./scripts/verify_ci_local.sh` (if created)
**Trigger**: Manually before releases or when debugging CI
**Purpose**: Complete CI simulation

**Use when**:
- Preparing a release
- Debugging why CI failed
- Validating multi-Python compatibility (requires Python 3.10, 3.11, 3.12, 3.13 installed)

## Quick Reference

| When | Command | Time | What It Does |
|------|---------|------|--------------|
| During development | `./scripts/verify_local.sh` | ~30-60s | Fast checks, auto-fix, warnings OK |
| Before commit | *(automatic)* | ~30-60s | Pre-commit hook runs verify_local.sh |
| Before push | `./scripts/verify.sh` | ~5-10min | Full validation, matches CI |
| Before release | Review CI output | - | All tests across Python 3.10-3.13 |

## Installation

### First Time Setup

1. **Clone and install dependencies**:
   ```bash
   git clone https://github.com/3D-Tech-Solutions/code-scalpel.git
   cd code-scalpel
   pip install -e '.[dev]'
   ```

2. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

3. **Install optional security tools** (recommended):
   ```bash
   pip install bandit pip-audit
   ```

### Verify Installation

```bash
# Quick test
./scripts/verify_local.sh

# Comprehensive test (takes longer)
./scripts/verify.sh
```

## Common Workflows

### Regular Development

```bash
# Edit some files
vim src/code_scalpel/some_file.py

# Make a commit (pre-commit hook runs automatically)
git add .
git commit -m "v1.3.0: Add new feature"

# Before pushing, run comprehensive checks
./scripts/verify.sh

# If all checks pass, push
git push origin feature-branch
```

### Fixing Common Issues

#### Black Formatting Errors
Formatting is automatically fixed during pre-commit. If verify.sh fails on formatting:

```bash
black src/ tests/
git add -u
git commit -m "v1.3.0: Apply Black formatting"
```

#### Coverage Below 24%
The `verify.sh` script requires 24% minimum coverage. If tests fail:

```bash
# Generate coverage report
pytest --cov=code_scalpel --cov-report=html

# Open the report
open htmlcov/index.html  # macOS
# or xdg-open htmlcov/index.html  # Linux
```

Then add tests for uncovered lines.

#### Documentation Out of Sync
If verify.sh fails on documentation checks:

```bash
# Regenerate documentation
python scripts/generate_mcp_tools_reference.py
python scripts/generate_mcp_tier_matrix.py
python scripts/validate_docs_sync.py

# Verify it passes
python scripts/validate_docs_sync.py

# Commit the changes
git add docs/reference/
git commit -m "v1.3.0: Update auto-generated documentation"
```

#### Bandit Security Issues
If Bandit reports issues in pre-push validation:

```bash
# Review the issue
bandit -r src/ -ll -ii

# Fix the security issue in your code, then re-run
./scripts/verify.sh
```

#### Dependency Vulnerabilities
If pip-audit reports vulnerabilities:

```bash
# Review vulnerabilities
pip-audit -r requirements-secure.txt

# Update the dependency (requires pinning in requirements-secure.txt)
pip install --upgrade <vulnerable-package>

# Re-run validation
./scripts/verify.sh
```

### Before Releasing

1. **Run comprehensive validation**:
   ```bash
   ./scripts/verify.sh
   ```

2. **Check git status**:
   ```bash
   git status
   ```

3. **Push to main and wait for CI**:
   ```bash
   git push origin main
   ```

4. **Wait for all GitHub Actions to pass**:
   - Check [GitHub Actions page](https://github.com/3D-Tech-Solutions/code-scalpel/actions)
   - All 12+ CI jobs must pass

## Advanced Topics

### Skipping Validation (Emergency Only)

If you absolutely must skip validation:

```bash
# Skip pre-commit hook only
git commit --no-verify

# Skip pre-push check and push
git push --no-verify
```

**Note**: CI will still run, and failures will block merging to main.

### Testing Against Specific Python Versions

By default, verify_local.sh tests with your current Python version. To test multiple versions:

1. **Install Python 3.10-3.13**
2. **Use tox or pyenv** to test:
   ```bash
   pyenv install 3.10 3.11 3.12 3.13
   tox
   ```

### Debugging Test Failures

Run individual test files:

```bash
# Run one test file
pytest tests/tools/get_file_context/test_enterprise_tier.py -v

# Run tests matching a pattern
pytest tests/tools/ -k "tier" -v

# Run with print statements visible
pytest tests/tools/get_file_context/ -v -s

# Run with detailed error info
pytest tests/tools/ -v --tb=long
```

### Understanding CI Stages

The GitHub Actions CI runs 12+ stages in sequence:

1. **Smoke Test** (5 min) - Fast gate for formatting/lint issues
2. **Lint** - Black & Ruff detailed checks
3. **Type Check** - Pyright validation
4. **Test Matrix** - Python 3.10, 3.11, 3.12, 3.13
5. **Security** - Bandit scan
6. **Dependency Audit** - pip-audit scan
7. **Build Check** - Package build validation
8. **Distribution Verify** - Tier separation validation
9. **MCP Contract** - All 3 transports
10. **MCP Tools Ref** - Documentation validation
11. **MCP Tools Tier** - Tier matrix docs
12. **Docs Sync** - README/code sync

All stages are required to pass before merging to main.

## FAQs

**Q: Why does pre-commit run verify_local.sh but not verify.sh?**
A: verify_local.sh is fast (~30s) so it doesn't block your commit workflow. Run verify.sh manually before pushing to catch all issues.

**Q: Can I configure pre-commit to run verify.sh instead?**
A: Yes, edit `.pre-commit-config.yaml` and change `entry: ./scripts/verify_local.sh` to `entry: ./scripts/verify.sh`, but it will make commits slower.

**Q: What if I don't have Bandit or pip-audit installed?**
A: verify_local.sh will print a warning but continue. Pre-push validation with verify.sh requires them for blocking checks.

**Q: How do I test if my changes will pass CI?**
A: Run `./scripts/verify.sh` - it matches all CI checks except multi-Python matrix testing.

**Q: Why do some tests skip with "optional dependency" errors?**
A: Some tests require optional dependencies (e.g., `[web]`, `[agents]`). Install them with:
```bash
pip install -e '.[dev,web,agents]'
```

**Q: Can I commit without running pre-commit?**
A: Yes, use `git commit --no-verify`, but CI will still run and may fail.

## Troubleshooting

### Pre-commit hook not running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### "Bandit not installed" warnings
```bash
pip install -e '.[dev]'
```

### Tests timeout
- Some tests are slow (especially MCP contract tests)
- Default timeout is 600 seconds per test
- Run faster tests first: `pytest tests/core/ -v`

### Can't install tree-sitter packages
```bash
# Requires system C compiler
# macOS:
brew install gcc

# Ubuntu:
sudo apt-get install build-essential

# Windows:
# Use Visual Studio Build Tools or MinGW
```

### detect-secrets Hook Failing

**Symptom**: Pre-commit fails with "Potential secrets detected"

**Solution**:
```bash
# Review flagged secrets (marks false positives as allowed)
detect-secrets audit .secrets.baseline

# Update baseline with false positives marked
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
git commit -m "v1.3.2: Update secrets baseline"
```

### Missing .secrets.baseline

**Symptom**: Pre-commit fails with `FileNotFoundError: .secrets.baseline`

**Solution**:
```bash
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
git commit -m "v1.3.2: Add secrets baseline"
```

### Version Mismatch Between Files

**Symptom**: `verify.sh` fails with "Version mismatch detected"

Version is defined in **two places** and must be kept in sync:
- `pyproject.toml` (source of truth for builds)
- `src/code_scalpel/__init__.py` (runtime version)

**Solution**:
```bash
# Run the version sync checker for details
./scripts/verify_version_sync.sh

# Update both files to match
VERSION="1.3.2"
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/code_scalpel/__init__.py

# Verify sync
./scripts/verify_version_sync.sh
```

### Skipping Build Check in verify.sh

If the package build check is slow during iteration:

```bash
# Skip the build step
./scripts/verify.sh --skip-build
```

Note: The full build check will still run in CI.

## Related Documentation

- [README.md](../README.md) - Project overview
- [.github/workflows/ci.yml](../.github/workflows/ci.yml) - GitHub Actions configuration
- [pyproject.toml](../pyproject.toml) - Project configuration
- [pytest.ini](../pytest.ini) - Test configuration

## Contributing

When contributing to Code Scalpel:

1. **Follow the validation workflow**: Pre-commit → Pre-push → Push
2. **Run `./scripts/verify.sh` before pushing**
3. **All CI checks must pass** before PR can merge
4. **Add tests for new features** (coverage requirement: 24% minimum)
5. **Update documentation** if changing behavior

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.
