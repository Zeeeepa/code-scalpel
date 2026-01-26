# Releasing Code Scalpel

This guide documents the process for releasing new versions of Code Scalpel to PyPI, GitHub, and VS Code Marketplace.

---

## Overview

Code Scalpel releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes (rare, planned in advance)
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Example: `v1.0.2` = major 1, minor 0, patch 2

---

## Release Targets

Each release is published to multiple distribution channels:

1. **PyPI** (Python Package Index)
   - Official Python package repository
   - Command: `pip install codescalpel==X.Y.Z`

2. **GitHub Releases**
   - Release notes and source artifacts
   - URL: https://github.com/anthropics/code-scalpel/releases

3. **VS Code Marketplace**
   - VSCode extension
   - Separate versioning for `vscode-extension/`
   - Requires VS Code Marketplace token

4. **UVX (Recommended Entry Point)**
   - Auto-installation for Claude Desktop
   - Command: `uvx codescalpel mcp`

---

## Prerequisites

### Required Credentials

Before releasing, ensure you have:

1. **GitHub Token** (for pushing tags and creating releases)
   ```bash
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```
   - Requires: `repo`, `read:packages` scopes
   - Generate: https://github.com/settings/tokens/new

2. **PyPI Token** (for publishing to PyPI)
   ```bash
   export PYPI_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxx
   ```
   - Requires: Upload permissions to `codescalpel` project
   - Generate: https://pypi.org/manage/account/tokens/
   - Store in `~/.pypirc` or use environment variable

3. **VS Code Marketplace Token** (for VSCode extension)
   ```bash
   export VSCE_TOKEN=xxxxxxxxxxxxxxxxxxxx
   ```
   - Required for VSCode Marketplace publishing
   - Generate via VS Code Marketplace dashboard
   - Only needed if publishing to marketplace

### Tools Required

```bash
# Python build system
pip install build

# Distribution tools
pip install twine

# VS Code extension publisher (optional)
npm install -g vsce
```

### Access Requirements

- Push access to `anthropics/code-scalpel` repository
- Maintainer role on PyPI project
- VS Code Marketplace publisher account

---

## Pre-Release Checklist

Before releasing, verify:

- [ ] All tests pass locally: `pytest`
- [ ] Code passes linting: `black --check . && ruff check .`
- [ ] No uncommitted changes: `git status`
- [ ] On `main` branch: `git branch`
- [ ] Up-to-date with remote: `git pull origin main`
- [ ] Version in `pyproject.toml` is correct: `version = "X.Y.Z"`
- [ ] Version in `src/code_scalpel/__init__.py` matches
- [ ] Version in `vscode-extension/package.json` matches (for extension releases)
- [ ] `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md` exists
- [ ] `CHANGELOG.md` updated with release entry
- [ ] All contributors credited in release notes

### Version Synchronization Check

```bash
# Verify all versions match
grep 'version' pyproject.toml | head -1
grep '__version__' src/code_scalpel/__init__.py
grep 'version' vscode-extension/package.json | head -1

# All should show: X.Y.Z
```

---

## Release Process

### Option A: Automated Release (Recommended)

Using the provided `release.sh` script:

```bash
# Dry run first (shows what would happen)
./scripts/release.sh --version X.Y.Z --dry-run

# Execute release
./scripts/release.sh --version X.Y.Z

# With specific options
./scripts/release.sh --version X.Y.Z --skip-tests --all-platforms
```

**Script Features**:
- Validates version format
- Runs quality checks (black, ruff, pytest)
- Updates version in all files
- Creates git commit and tag
- Builds distributions
- Publishes to PyPI
- Creates GitHub release
- Publishes to VSCode Marketplace

**Script Options**:
```bash
--version X.Y.Z          # Version to release
--dry-run               # Show what would happen without executing
--skip-tests            # Skip pytest run (use with caution)
--skip-pypi             # Don't publish to PyPI
--skip-github           # Don't create GitHub release
--skip-vscode           # Don't publish to VSCode (extension only)
--all-platforms         # Publish to all targets
```

### Option B: Manual Release (Step-by-Step)

For maximum control, follow these steps:

#### Step 1: Quality Checks

```bash
# Run tests
pytest tests/

# Format code
black .

# Lint code
ruff check . --fix

# Type check (if configured)
mypy src/
```

#### Step 2: Update Version

Update version in all locations:

```bash
# 1. pyproject.toml
# Find: version = "X.Y.Z-1"
# Replace: version = "X.Y.Z"

# 2. src/code_scalpel/__init__.py
# Find: __version__ = "X.Y.Z-1"
# Replace: __version__ = "X.Y.Z"

# 3. vscode-extension/package.json (if releasing extension)
# Find: "version": "X.Y.Z-1"
# Replace: "version": "X.Y.Z"
```

#### Step 3: Update Documentation

```bash
# 1. Update CHANGELOG.md
# Add entry for this version at the top with:
# - Release date
# - Major features/fixes
# - Link to RELEASE_NOTES_vX.Y.Z.md

# 2. Verify RELEASE_NOTES_vX.Y.Z.md exists
# This is required for GitHub release creation
```

#### Step 4: Commit and Tag

```bash
# Stage changes
git add pyproject.toml src/code_scalpel/__init__.py CHANGELOG.md vscode-extension/

# Commit
git commit -m "chore: release v$(grep version pyproject.toml | head -1 | cut -d'"' -f2)"

# Create annotated tag
git tag -a vX.Y.Z -m "Release X.Y.Z

## Highlights
- Feature 1
- Feature 2
- Bug fix 1

See RELEASE_NOTES_vX.Y.Z.md for full details."

# Push changes and tag
git push origin main
git push origin vX.Y.Z
```

#### Step 5: Build Distributions

```bash
# Clean previous builds
rm -rf dist/ build/

# Build wheel and source distribution
python -m build

# Verify artifacts
ls -lh dist/
# Should see:
# - code_scalpel-X.Y.Z-py3-none-any.whl
# - code_scalpel-X.Y.Z.tar.gz
```

#### Step 6: Publish to PyPI

```bash
# Using twine (recommended)
twine upload dist/code_scalpel-X.Y.Z*

# Or using build's built-in publishing
python -m build --sdist
python -m twine upload dist/*
```

#### Step 7: Create GitHub Release

```bash
# Using gh CLI (recommended)
gh release create vX.Y.Z \
  --title "v X.Y.Z" \
  --notes-file docs/release_notes/RELEASE_NOTES_vX.Y.Z.md \
  --draft

# Verify draft, then publish:
gh release edit vX.Y.Z --draft=false
```

Or manually via GitHub web interface:
1. Go to Releases: https://github.com/anthropics/code-scalpel/releases
2. Click "Draft a new release"
3. Tag: `vX.Y.Z`
4. Title: `v X.Y.Z`
5. Description: Paste contents of `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md`
6. Publish release

#### Step 8: Publish to VS Code Marketplace (Optional)

Only for VSCode extension releases:

```bash
# Navigate to extension directory
cd vscode-extension/

# Publish using vsce
vsce publish

# Or publish with specific version
vsce publish X.Y.Z
```

---

## Post-Release Verification

After release, verify everything succeeded:

### PyPI Verification

```bash
# Wait 1-2 minutes for PyPI to process
sleep 90

# Verify package appears on PyPI
pip index versions code-scalpel | head -5

# Test installation
pip install --upgrade code-scalpel==X.Y.Z

# Verify version
python -c "import code_scalpel; print(f'Version: {code_scalpel.__version__}')"
```

### GitHub Verification

```bash
# Verify tag exists
git tag -l | grep vX.Y.Z

# Verify release created
gh release view vX.Y.Z

# Check release notes display correctly
```

### UVX Verification

```bash
# Test UVX installation
uvx codescalpel --version
# Should output: X.Y.Z
```

### Checklist

After release, verify:

- [ ] PyPI: Package appears on https://pypi.org/project/code-scalpel/
- [ ] GitHub: Release created at /releases with correct notes
- [ ] Git: Tag `vX.Y.Z` exists and points to correct commit
- [ ] UVX: `uvx codescalpel --version` shows `X.Y.Z`
- [ ] Changelog: CHANGELOG.md updated with release
- [ ] VSCode: Extension updated (if applicable)

---

## Rollback Procedures

If issues are discovered after release:

### Rollback Option 1: Patch Release

Create a quick patch for the issue:

```bash
# Revert problematic commit
git revert <commit-hash>

# Create patch release
./scripts/release.sh --version X.Y.(Z+1)
```

### Rollback Option 2: Yanking from PyPI

For critical security issues, yank the release from PyPI:

```bash
# Yank version from PyPI
twine upload --skip-existing --repository pypi dist/* --yank-version X.Y.Z

# Or via PyPI web interface:
# https://pypi.org/manage/project/code-scalpel/release/X.Y.Z/
```

### Rollback Option 3: GitHub Release Deletion

```bash
# Delete GitHub release (last resort)
gh release delete vX.Y.Z
```

---

## Common Issues

### Issue: PyPI Upload Fails with "File already exists"

**Cause**: Version already published
**Solution**:
- Check PyPI for existing version
- Increment patch version: `X.Y.(Z+1)`
- Release new version

### Issue: GitHub Release Shows No Release Notes

**Cause**: `RELEASE_NOTES_vX.Y.Z.md` file missing
**Solution**:
1. Create the release notes file
2. Commit and push
3. Delete GitHub release and recreate with notes

### Issue: Version Mismatch After Release

**Cause**: Not all version files updated
**Solution**:
1. Verify all locations updated
2. Create patch commit fixing versions
3. Re-release with patch number

### Issue: Tag Already Exists

**Cause**: Attempting to create tag that exists
**Solution**:
```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push origin --delete vX.Y.Z

# Recreate tag and push
```

---

## Release Cadence

- **Security Fixes**: Released ASAP (patch version)
- **Bug Fixes**: Released weekly or as needed (patch version)
- **Features**: Released monthly (minor version)
- **Major Changes**: Released quarterly or as needed (major version)

---

## Communication

After successful release:

1. **Announce on GitHub Discussions**: Link to release notes
2. **Update README**: Mention latest version
3. **Notify Users**: If major features or critical fixes
4. **Update Discord/Community**: If applicable

---

## Long-Term Version Strategy

### Current Version: v1.0.1

**Planned Releases**:
- v1.0.2: Release documentation improvements
- v1.1.0: Additional tool enhancements
- v2.0.0: (Future) Major API/architecture changes

### Deprecation Timeline

- v1.0.1: polyglot module marked for v3.3.0 removal
- v2.0.0: Remove deprecated contract fields
- v3.0.0: Consider major version changes
- v3.3.0: Remove polyglot module

---

## Release Checklist Template

```markdown
# Release v[VERSION] Checklist

## Pre-Release
- [ ] All tests pass: `pytest`
- [ ] Code formatted: `black .`
- [ ] Linting passes: `ruff check . --fix`
- [ ] No uncommitted changes: `git status`
- [ ] On `main` branch
- [ ] Latest from remote: `git pull origin main`

## Preparation
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/code_scalpel/__init__.py`
- [ ] Version updated in `vscode-extension/package.json`
- [ ] RELEASE_NOTES_v[VERSION].md created
- [ ] CHANGELOG.md updated

## Release
- [ ] Dry run successful: `./scripts/release.sh --version [VERSION] --dry-run`
- [ ] Release executed: `./scripts/release.sh --version [VERSION]`

## Verification
- [ ] PyPI: Package visible on https://pypi.org/project/code-scalpel/
- [ ] GitHub: Release created with correct notes
- [ ] Git: Tag `v[VERSION]` exists
- [ ] UVX: `uvx codescalpel --version` shows `[VERSION]`

## Communication
- [ ] Announce on GitHub Discussions
- [ ] Update README with latest version
- [ ] Notify users if major release
```

---

## Support

For questions about the release process:
- GitHub Issues: https://github.com/anthropics/code-scalpel/issues
- Discussions: https://github.com/anthropics/code-scalpel/discussions

---

**Last Updated**: 2025-01-25
**Maintained by**: Code Scalpel Team
