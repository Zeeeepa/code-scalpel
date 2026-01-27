# Code Scalpel Release Process Guide

Complete guide to building, testing, and publishing Code Scalpel releases using the automated release pipeline.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Release Workflow](#release-workflow)
- [Conventional Commits](#conventional-commits)
- [Semantic Versioning](#semantic-versioning)
- [Manual Release Commands](#manual-release-commands)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The Code Scalpel release pipeline automates the entire process of:

1. **Version Determination** - Automatically calculates version bumps from commit history
2. **Release Notes Generation** - Creates formatted markdown from conventional commits
3. **Changelog Updates** - Maintains a Keep a Changelog compliant CHANGELOG.md
4. **GitHub Releases** - Creates releases on GitHub with release notes
5. **PyPI Publishing** - Builds and uploads packages to PyPI

### Key Components

```
code_scalpel/release/
├── versioning.py       - Semantic versioning and commit parsing
├── notes.py           - Release notes and changelog management
├── git_history.py     - Git repository interaction
├── orchestrator.py    - Release orchestration and coordination
├── github_releases.py - GitHub API integration
└── pypi_publisher.py  - PyPI package building and publishing
```

## Prerequisites

### Required Dependencies

```bash
# Core releases tools (bundled with [dev] extra)
pip install build twine PyGithub

# Environment variables required
export GITHUB_TOKEN="ghp_xxxx..."  # GitHub personal access token
export PYPI_TOKEN="pypi-xxxx..."   # PyPI API token
```

### Token Setup

**GitHub Token:**
- Visit https://github.com/settings/tokens
- Create Personal Access Token (classic)
- Select `repo` and `public_repo` scopes
- Copy token to environment variable

**PyPI Token:**
- Visit https://pypi.org/account/
- Create API token (project or account level)
- Copy token to environment variable

## Release Workflow

### Step 1: Commit Work with Conventional Commits

All commits must follow the [Conventional Commits](#conventional-commits) specification:

```bash
# Feature
git commit -m "feat: Add new diagnostic tool"

# Bug fix
git commit -m "fix: Handle edge case in parser"

# Breaking change
git commit -m "feat!: Redesign API structure"
git commit -m "feat: New API

BREAKING CHANGE: Old API endpoints removed"
```

### Step 2: Preview Release Plan

Before creating a release, preview what will be released:

```bash
from code_scalpel.release.orchestrator import ReleaseOrchestrator

orchestrator = ReleaseOrchestrator()
orchestrator.print_release_plan()
```

Output example:
```
📋 Release Plan
Current version: 1.2.0
New version: 1.3.0
Bump type: MINOR
Commits: 5

📝 Release Notes Preview:

## [1.3.0] - 2024-01-15

### ✨ Features
- Add new diagnostic tool (#123)
- Improve performance of code analysis

### 🐛 Bug Fixes
- Handle edge case in parser (#124)

### 📝 Other Changes
- Update documentation
```

### Step 3: Execute Release (Dry Run)

Test the release process without making changes:

```bash
from code_scalpel.release.orchestrator import ReleaseOrchestrator

orchestrator = ReleaseOrchestrator()
result = orchestrator.execute_release(dry_run=True)
```

### Step 4: Execute Release (Production)

Perform the actual release:

```bash
from code_scalpel.release.orchestrator import ReleaseOrchestrator

orchestrator = ReleaseOrchestrator()
result = orchestrator.execute_release(dry_run=False)
```

This will:
1. Check that working directory is clean
2. Analyze commits since last tag
3. Determine new version
4. Generate release notes
5. Update `pyproject.toml` with new version
6. Update `CHANGELOG.md` with release notes
7. Create git tag with release notes

### Step 5: Build and Upload Distributions

```bash
from code_scalpel.release.pypi_publisher import PyPIPublisher

publisher = PyPIPublisher()

# Build wheel and source distribution
builds = publisher.build_distributions()
print(f"Built: {builds['wheel']}")
print(f"Built: {builds['sdist']}")

# Verify package metadata
verify = publisher.verify_package()
print(f"Verification: {verify['status']}")

# Upload to PyPI
result = publisher.upload_to_pypi()
print(f"Upload status: {result['status']}")
```

### Step 6: Create GitHub Release

```bash
from code_scalpel.release.github_releases import GitHubReleaseManager

github = GitHubReleaseManager()

# Create the release
release = github.create_release(
    tag="v1.3.0",
    title="Release 1.3.0",
    body="""## New Features
- Feature 1
- Feature 2

## Bug Fixes
- Bug fix 1""",
    prerelease=False
)

print(f"Released: {release['url']}")

# Upload assets (wheels, source distributions)
assets = github.upload_assets("v1.3.0", [
    "dist/codescalpel-1.3.0-py3-none-any.whl",
    "dist/codescalpel-1.3.0.tar.gz"
])
```

## Conventional Commits

The release pipeline uses Conventional Commits to determine version bumps and categorize changes.

### Format

```
<type>(<scope>)!: <description>

<body>

<footer>
```

### Types

| Type | Bump | Example |
|------|------|---------|
| `feat:` | MINOR | `feat: Add support for Go analysis` |
| `fix:` | PATCH | `fix: Resolve memory leak in parser` |
| `docs:` | NONE | `docs: Update README` |
| `style:` | NONE | `style: Format code` |
| `refactor:` | NONE | `refactor: Improve code structure` |
| `perf:` | NONE | `perf: Optimize algorithm` |
| `test:` | NONE | `test: Add unit tests` |
| `chore:` | NONE | `chore: Update dependencies` |
| `ci:` | NONE | `ci: Setup GitHub Actions` |

### Breaking Changes

Breaking changes trigger a MAJOR version bump:

```bash
# Option 1: Add ! suffix to type
git commit -m "feat!: Redesign the API"

# Option 2: Use BREAKING CHANGE footer
git commit -m "feat: New API structure

BREAKING CHANGE: Old endpoints removed"

# Option 3: Combine
git commit -m "feat!: Redesign API

BREAKING CHANGE: - DELETE /api/v1/analyze
- MOVE /api/v2/* to /api/*"
```

### Scope

Optional scope in parentheses:

```bash
git commit -m "fix(parser): Handle Java generics correctly"
git commit -m "feat(api): Add batch analysis endpoint"
```

## Semantic Versioning

Version format: `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`

### Bump Rules

```python
from code_scalpel.release.versioning import ConventionalCommit, SemanticVersioner

# Parse a commit
commit = ConventionalCommit.parse("feat(api): Add new endpoint")
commit.is_feature()  # True
commit.is_breaking()  # False

# Determine version bump
versioner = SemanticVersioner("1.2.3")
commits = [
    "feat: New feature",
    "fix: Bug fix",
    "BREAKING CHANGE: API redesign"
]
bump = versioner.analyze_commits(commits)
print(bump.new_version)  # "2.0.0" (MAJOR)
```

### Version Bumping Examples

```
1.0.0 + fix → 1.0.1
1.0.0 + feat → 1.1.0
1.0.0 + breaking → 2.0.0

1.2.3 + [feat, fix, breaking] → 2.0.0 (breaking takes precedence)
1.2.3 + [feat, fix] → 1.3.0 (feat takes precedence)
1.2.3 + [fix, docs] → 1.2.4 (fix takes precedence)
```

## Manual Release Commands

### Python API

```python
# Complete workflow
from code_scalpel.release.orchestrator import ReleaseOrchestrator
from code_scalpel.release.pypi_publisher import PyPIPublisher
from code_scalpel.release.github_releases import GitHubReleaseManager

# 1. Prepare and execute release
orchestrator = ReleaseOrchestrator()
release_info = orchestrator.execute_release(dry_run=False)

# 2. Build and publish to PyPI
publisher = PyPIPublisher()
publisher.upload_to_pypi()

# 3. Create GitHub release
github = GitHubReleaseManager()
github.create_release(
    tag=f"v{release_info['new_version']}",
    title=f"Release {release_info['new_version']}",
    body=release_info['release_notes'],
    prerelease=False
)
```

### Git Commands

```bash
# View tags
git tag -l

# View commits since last release
git log <last-tag>..HEAD --oneline

# Manually create tag
git tag -a v1.3.0 -m "Release 1.3.0"

# Push tag to remote
git push origin v1.3.0
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run release'
        required: false
        type: boolean
        default: false

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Execute release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          python -c "
          from code_scalpel.release.orchestrator import ReleaseOrchestrator
          from code_scalpel.release.pypi_publisher import PyPIPublisher
          from code_scalpel.release.github_releases import GitHubReleaseManager
          
          # Release
          orchestrator = ReleaseOrchestrator()
          info = orchestrator.execute_release()
          
          # Publish
          publisher = PyPIPublisher()
          publisher.upload_to_pypi()
          
          # GitHub
          github = GitHubReleaseManager()
          github.create_release(
              tag=f'v{info[\"new_version\"]}',
              title=f'Release {info[\"new_version\"]}',
              body=info['release_notes']
          )
          "

      - name: Push changes
        run: |
          git push origin main
          git push origin --tags
```

## Troubleshooting

### Release Won't Execute

**Problem:** "Release preconditions not met"

**Solution:**
```bash
# Check for uncommitted changes
git status

# Commit all changes
git add .
git commit -m "your message"

# Check for tags
git tag -l

# Or skip the check:
from code_scalpel.release.orchestrator import ReleaseOrchestrator
orch = ReleaseOrchestrator()
# Manually verify preconditions
```

### Version Not Found

**Problem:** "Version not found in pyproject.toml"

**Solution:**
```toml
# Ensure pyproject.toml has version field
[project]
name = "codescalpel"
version = "1.2.3"  # Required!
```

### PyPI Upload Failed

**Problem:** "Upload failed: Invalid token"

**Solution:**
```bash
# Verify token is set
echo $PYPI_TOKEN

# Test with dry run
from code_scalpel.release.pypi_publisher import PyPIPublisher
pub = PyPIPublisher()
pub.upload_to_pypi(dry_run=True)

# Check PyPI token validity
# - Visit https://pypi.org/account/
# - Ensure token hasn't expired
```

### GitHub Release Not Created

**Problem:** "GitHub authentication failed"

**Solution:**
```bash
# Verify token
echo $GITHUB_TOKEN

# Test authentication
from code_scalpel.release.github_releases import GitHubReleaseManager
gh = GitHubReleaseManager()
auth = gh.verify_auth()
print(f"Authenticated as: {auth['login']}")

# Check token permissions at:
# https://github.com/settings/tokens
```

## Release Checklist

Before releasing:

- [ ] All commits follow Conventional Commits format
- [ ] All tests pass: `pytest tests/`
- [ ] Code formatted: `black src/ tests/`
- [ ] No linting errors: `ruff check src/`
- [ ] Type check passes: `pyright`
- [ ] GITHUB_TOKEN environment variable set
- [ ] PYPI_TOKEN environment variable set
- [ ] Latest code committed and pushed

After releasing:

- [ ] Verify GitHub release was created
- [ ] Verify PyPI package exists at https://pypi.org/project/codescalpel/
- [ ] Test installation: `pip install codescalpel==<new-version>`
- [ ] Announce release in project channels

## Release History

All releases are documented in [CHANGELOG.md](CHANGELOG.md) and available at:
- GitHub: https://github.com/3D-Tech-Solutions/code-scalpel/releases
- PyPI: https://pypi.org/project/codescalpel/

## See Also

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PyPI Documentation](https://pypi.org/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)
