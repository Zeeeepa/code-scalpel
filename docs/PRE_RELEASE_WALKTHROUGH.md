# Code Scalpel Pre-Release Walkthrough Checklist

**Purpose**: Standardized, auditable checklist with commit evidence for each release stage  
**Format**: Each stage documents commits, verifications, and sign-offs  
**Audience**: Release manager, maintainers, stakeholders

---

## Release Information

| Field | Value |
|-------|-------|
| **Release Version** | vX.Y.Z (fill in) |
| **Release Date** | YYYY-MM-DD (fill in) |
| **Release Manager** | Name (fill in) |
| **Codename** | (optional) |

---

## Phase 1: Pre-Release Code Preparation (1-2 days)

### 1.1 Version Number Synchronization

**Objective**: All version numbers across the project are synchronized to the new version

**Tasks**:
- [ ] Update `src/code_scalpel/__init__.py` with new version
- [ ] Update `pyproject.toml` with new version
- [ ] Update `vscode-extension/package.json` with new version
- [ ] Update `vscode-extension/package-lock.json` (regenerate if needed)

**Commit Evidence**:
```bash
git log --oneline --grep="version" | head -5
# Should show: "Update version to vX.Y.Z" commits
```

**Sign-off**: 
- [ ] Confirmed: `grep -r "1.1.0" src/code_scalpel/__init__.py pyproject.toml vscode-extension/package.json`
- [ ] Committed: `git show HEAD --name-only`

---

### 1.2 Documentation Updates

**Objective**: All documentation reflects the new version and features

**Tasks**:
- [ ] Update `README.md` - Latest Release line
- [ ] Update `README.md` - Feature descriptions (if applicable)
- [ ] Update `CHANGELOG.md` - Add new version section
- [ ] Update `CHANGELOG.md` - List all features, fixes, security updates
- [ ] Update release notes: `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md`
- [ ] Update installation guides with correct package name
  - [ ] `docs/INSTALLING_FOR_CLAUDE.md`
  - [ ] `docs/SETUP_CHECKLIST.md`
  - [ ] `docs/getting_started/getting_started.md`
  - [ ] `docs/BEGINNER_GUIDE.md`
  - [ ] Any other installation documentation
- [ ] Update package name references (from `code-scalpel` to `codescalpel`)
  - [ ] Search: `grep -r "code-scalpel" docs/ README.md CHANGELOG.md`
  - [ ] Replace: `sed -i 's/code-scalpel/codescalpel/g'`

**Commit Evidence**:
```bash
git log --oneline -5  # Shows documentation commits
git diff HEAD~5 CHANGELOG.md README.md  # Shows what changed
```

**Sign-off**:
- [ ] Confirmed: `grep "vX.Y.Z" README.md` shows new version
- [ ] Confirmed: `grep "codescalpel" docs/INSTALLING_FOR_CLAUDE.md` (correct package name)
- [ ] Committed: Document update commits present

---

### 1.3 Code Quality Checks

**Objective**: All code quality gates pass

**Tasks**:
- [ ] Run linter: `ruff check src/`
- [ ] Run formatter: `black --check src/`
- [ ] Run type checker: `pyright -p pyrightconfig.json`
- [ ] Run security scan: `bandit -r src/ -ll -ii -x '**/test_*.py'`
- [ ] Run dependency audit: `pip-audit`

**Verification**:
```bash
# Run all checks
ruff check src/ && black --check src/ && pyright -p pyrightconfig.json && bandit -r src/ -ll -ii
echo "Exit code: $?"  # Should be 0
```

**Sign-off**:
- [ ] All checks passing (Exit code 0)
- [ ] No warnings in critical areas
- [ ] Security issues documented and approved

---

### 1.4 Test Suite Execution

**Objective**: All tests pass with new code

**Tasks**:
- [ ] Run unit tests: `pytest tests/ -v`
- [ ] Run integration tests (if applicable)
- [ ] Check coverage: `pytest --cov=src/code_scalpel tests/`
- [ ] Verify coverage threshold met (target: >80%)

**Verification**:
```bash
pytest tests/ -v --tb=short
# Should show: "X passed, 0 failed"
```

**Sign-off**:
- [ ] All tests passing
- [ ] Coverage >= 80%
- [ ] No flaky tests detected

---

## Phase 2: Git Preparation (30 minutes)

### 2.1 Commit History Review

**Objective**: Verify clean commit history for release

**Tasks**:
- [ ] Review commits since last release: `git log vX.Y-1.Z..HEAD --oneline`
- [ ] Verify commit messages follow convention (feat:, fix:, docs:, etc.)
- [ ] Ensure no accidental debug code or secrets in commits

**Verification**:
```bash
git log vX.Y-1.Z..HEAD --pretty=format:"%h %s"
# Review output for appropriateness
```

**Sign-off**:
- [ ] All commits follow convention
- [ ] No sensitive data in commit history

---

### 2.2 Release Branch/Tag Setup

**Objective**: Create release tag pointing to correct commit

**Tasks**:
- [ ] Ensure on main branch: `git status`
- [ ] Ensure branch is clean: `git status --short` (should be empty)
- [ ] Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Verify tag: `git tag -ln vX.Y.Z`

**Verification**:
```bash
git tag -ln vX.Y.Z  # Should show your message
git show vX.Y.Z  # Should show release commit
```

**Sign-off**:
- [ ] Tag created: `git tag | grep vX.Y.Z`
- [ ] Tag points to correct commit: `git rev-parse vX.Y.Z`

---

## Phase 3: Artifact Building (10 minutes)

### 3.1 PyPI Artifacts

**Objective**: Build and verify PyPI distribution files

**Tasks**:
- [ ] Clean build directory: `rm -rf dist/ build/ *.egg-info`
- [ ] Build artifacts: `python -m build`
- [ ] Verify artifacts exist: `ls -lah dist/`
- [ ] Check wheel contents: `unzip -l dist/code_scalpel-X.Y.Z-py3-none-any.whl | head`
- [ ] Check source dist contents: `tar -tzf dist/code_scalpel-X.Y.Z.tar.gz | head`

**Verification**:
```bash
ls dist/  # Should show:
# - codescalpel-X.Y.Z-py3-none-any.whl
# - codescalpel-X.Y.Z.tar.gz
```

**Sign-off**:
- [ ] Both wheel and source distribution present
- [ ] Version correct in artifact names
- [ ] Files pass metadata check: `twine check dist/*`

---

### 3.2 VS Code Extension Build

**Objective**: Build and verify VS Code extension package

**Tasks**:
- [ ] Navigate to extension: `cd vscode-extension`
- [ ] Install dependencies: `npm install`
- [ ] Build extension: `npm run vscode:prepublish` or package as needed
- [ ] Verify package: `ls -lah out/` or extension package file

**Verification**:
```bash
cd vscode-extension && npm list  # Check dependencies
# Verify version in package.json matches release version
grep "\"version\"" package.json
```

**Sign-off**:
- [ ] Extension version matches release version
- [ ] Build completes without errors
- [ ] Package files present

---

## Phase 4: Release Publishing (5-10 minutes)

### 4.1 Push Tag to GitHub

**Objective**: Trigger automated release workflows

**Tasks**:
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Verify workflows triggered: Visit Actions page
- [ ] Monitor workflows:
  - [ ] `publish-pypi.yml` - Publish to PyPI
  - [ ] `publish-github-release.yml` - Create GitHub Release
  - [ ] `publish-vscode.yml` - Publish VS Code Extension

**Verification**:
```bash
# Check GitHub Actions status
gh run list -w publish-pypi.yml --limit 1
gh run list -w publish-github-release.yml --limit 1
gh run list -w publish-vscode.yml --limit 1
# All should show "in_progress" or "completed success"
```

**Sign-off**:
- [ ] Tag pushed: `git ls-remote origin | grep vX.Y.Z`
- [ ] All workflows triggered (check Actions page)

---

### 4.2 Monitor Workflow Execution

**Objective**: Ensure all publishing workflows complete successfully

**Expected Times**:
- PyPI: 2-3 minutes
- GitHub Release: 1 minute  
- VS Code Extension: 3-5 minutes

**Tasks** (repeat for each workflow):
- [ ] Watch workflow: `gh run watch <run_id>`
- [ ] Verify all steps pass
- [ ] Capture run ID and output for documentation

**Verification**:
```bash
# After ~10 minutes total
gh run list -w publish-pypi.yml --limit 1
gh run list -w publish-github-release.yml --limit 1
gh run list -w publish-vscode.yml --limit 1
# All should show "completed success"
```

**Sign-off**:
- [ ] All workflows completed successfully
- [ ] No errors in logs
- [ ] Workflow run IDs documented:
  - PyPI: ___________
  - GitHub Release: ___________
  - VS Code: ___________

---

## Phase 5: Post-Release Verification (15-20 minutes)

### 5.1 PyPI Verification

**Objective**: Confirm package published correctly on PyPI

**Tasks**:
- [ ] Visit PyPI page: `https://pypi.org/project/codescalpel/X.Y.Z/`
- [ ] Verify version listed
- [ ] Verify all files present:
  - [ ] `.whl` wheel file
  - [ ] `.tar.gz` source distribution
  - [ ] `.dist-info` metadata
- [ ] Verify package metadata:
  - [ ] Description matches `pyproject.toml`
  - [ ] Keywords correct
  - [ ] Homepage link correct
  - [ ] License: MIT

**Verification Commands**:
```bash
# Test installation
pip index versions codescalpel
# Should show vX.Y.Z

# Test actual install
pip install codescalpel==X.Y.Z --upgrade
python -c "import code_scalpel; print(code_scalpel.__version__)"
# Should output: X.Y.Z
```

**Sign-off**:
- [ ] Package visible on PyPI
- [ ] All files present
- [ ] Installation works: `pip install codescalpel==X.Y.Z`
- [ ] Version correct after install

---

### 5.2 GitHub Release Verification

**Objective**: Confirm GitHub Release created with correct info

**Tasks**:
- [ ] Visit release page: `https://github.com/3D-Tech-Solutions/code-scalpel/releases/tag/vX.Y.Z`
- [ ] Verify release tag present
- [ ] Verify release notes populated
- [ ] Verify download artifacts available
- [ ] Verify commit reference correct

**Verification**:
```bash
# Get release info
gh release view vX.Y.Z
# Should show tag, title, body, and assets
```

**Sign-off**:
- [ ] Release page displays
- [ ] Release notes present and accurate
- [ ] Artifacts downloadable
- [ ] Commit hash matches tagged commit

---

### 5.3 VS Code Marketplace Verification

**Objective**: Confirm extension published to VS Code Marketplace

**Tasks**:
- [ ] Search extension: Ctrl+Shift+X → Search "Code Scalpel"
- [ ] Verify version displayed: Should show vX.Y.Z
- [ ] Verify publisher: 3DTechus
- [ ] Verify install button available
- [ ] Optionally install and verify functionality

**Verification (Web)**:
- [ ] Visit: `https://marketplace.visualstudio.com/items?itemName=3DTechus.code-scalpel`
- [ ] Check version number displayed
- [ ] Verify description and icon present

**Sign-off**:
- [ ] Extension visible in marketplace
- [ ] Version number correct
- [ ] Install option functional

---

## Phase 6: Documentation & Announcement (30 minutes)

### 6.1 Release Notes Finalization

**Objective**: Create final release announcement

**Tasks**:
- [ ] Review `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md`
- [ ] Add installation instructions (copy from README)
- [ ] Add upgrade path for existing users
- [ ] Add known limitations (if any)
- [ ] Add links to PyPI, GitHub, VS Code Marketplace
- [ ] Create summary for announcements (GitHub Discussions, email, etc.)

**Sign-off**:
- [ ] Release notes complete and reviewed
- [ ] Upgrade instructions clear
- [ ] All links verified working

---

### 6.2 Stakeholder Communication

**Objective**: Notify users and stakeholders of new release

**Tasks**:
- [ ] Post to GitHub Discussions: `https://github.com/3D-Tech-Solutions/code-scalpel/discussions`
- [ ] Update project status (if applicable)
- [ ] Notify maintainers/team members
- [ ] Monitor for early issue reports

**Sign-off**:
- [ ] Announcement posted
- [ ] Team notified
- [ ] Monitoring plan in place

---

## Phase 7: Post-Release Monitoring (Ongoing)

### 7.1 Issue Tracking

**Objective**: Monitor for release-related issues

**Tasks**:
- [ ] Watch GitHub Issues for vX.Y.Z-related reports
- [ ] Track PyPI statistics
- [ ] Monitor VS Code Extension reviews/ratings
- [ ] Plan for patch releases if critical issues found

**Sign-off**:
- [ ] No critical issues reported (after 24 hours)
- [ ] User feedback positive
- [ ] Patch release decision made (if needed)

---

## Phase 8: Release Sign-Off

### Final Verification Checklist

- [ ] Version numbers synchronized across all files
- [ ] Documentation updated (README, CHANGELOG, guides, package names)
- [ ] All code quality checks pass (linter, formatter, type checker, security)
- [ ] All tests pass (unit + integration, coverage > 80%)
- [ ] Commits reviewed and documented
- [ ] Release tag created and pushed
- [ ] Artifacts built (PyPI wheel + source, VS Code extension)
- [ ] All workflows completed successfully
- [ ] PyPI package verified (installation works)
- [ ] GitHub Release verified
- [ ] VS Code Extension verified
- [ ] Release notes finalized
- [ ] Stakeholders notified
- [ ] Post-release monitoring active

---

## Rollback Procedures

### If Critical Issue Found During Phase 4-5

**Quick Rollback**:
```bash
# Delete tag locally
git tag -d vX.Y.Z

# Delete tag from GitHub
git push origin --delete vX.Y.Z

# Cancel any in-progress workflows in GitHub Actions UI
```

**After Rollback**:
1. Fix the issue in code
2. Update version number
3. Create new release tag
4. Restart release process

### If Published with Issues

**PyPI**: Cannot delete, must use yank or patch
```bash
# Yank the version (users see warning)
# Done via PyPI web interface
```

**GitHub**: Delete release in web UI

**VS Code**: Unpublish via marketplace (takes 24h)

---

## Template for Next Release

Copy this checklist and:
1. Replace `X.Y.Z` with new version
2. Replace `vX.Y-1.Z` with previous version
3. Add today's date
4. Assign release manager
5. Walk through each phase, checking items
6. Document commit hashes for each phase
7. Get final sign-off

---

**Release Manager Signature**: _______________________  
**Date**: _______________________  
**Approval**: _______________________
