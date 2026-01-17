# Code Scalpel Cleanup Execution Checklist

## Inventory Complete ✓

### Root-Level Directories Inventory

#### DELETE (Non-Essential/Artifact)

**Hidden Directories (Cache/Temp):**
- `.archive/` (4.0M) - old/deprecated code
- `.bench_tmp/` (816K) - temporary benchmark files
- `.claude/` (?)- Claude-specific cache
- `.code_scalpel_cache/` (329M) - local cache
- `.internal/` (1.3M) - internal checklists/status
- `.pytest_cache/` - pytest cache
- `.ruff_cache/` - ruff cache  
- `.scalpel_ast_cache/` - AST cache
- `.scalpel_cache/` (5.0M) - local cache
- `.test_simple/` - temporary test directory
- `.tmp_tier_comm/` - leftover temp directory
- `.venv/`, `.venv-mcp-smoke/` - virtual environments (if not needed)

**Build/Distribution Artifacts:**
- `dist/` (5.2M) - local build output
- `dist_protected/` (776K) - protected build output
- `build_protected/` (300K) - protected build directory
- `htmlcov/` (43M) - HTML coverage reports

**Documentation (Root-level .md files to DELETE):**
- `docs/ASSESSMENT_*.md` (3 files) - internal assessment
- `docs/BETA_OUTREACH_STRATEGY.md` - internal marketing
- `docs/CUSTOMER_COMMUNICATION_v4.md` - internal comms
- `docs/DOCUMENT_REORGANIZATION_20260108.md` - process docs
- `docs/GOVERNANCE_ENFORCEMENT_STATUS.md` - internal status
- `docs/PROJECT_INDEX.md` - redundant index
- `docs/PROJECT_REORG_REFACTOR.md` - process docs
- `docs/QUICK_REFERENCE_DOCS.md` - redundant
- `docs/ROADMAP_INDEX.md`, `docs/ROADMAP_SUMMARY.md` - redundant
- `docs/QUICK_SETUP_GUIDE.md` - consolidate into getting_started
- `docs/TEST_SUITE_BREAKDOWN.md` - internal detail
- `docs/TIER_CONFIGURATION.md` - internal config
- `docs/TODO_FORMAT_STANDARDIZATION.md` - process docs
- `docs/V1.0_ROADMAP*.md` (2 files) - old/deprecated roadmaps
- `docs/code_scalpel_assessment_checklist*.md` (2 files) - internal
- `docs/stress.md` - unclear purpose, low value
- `docs/technical_debt.md` - internal tracking
- `docs/AI_AGENT_TOOL_GUIDE.md` - check if redundant with guides

**Documentation Subdirectories to DELETE:**
- `docs/archive/` - old archived docs
- `docs/internal/` - internal documentation
- `docs/status/` - internal status tracking
- `docs/todo_reports/` - generated reports
- `docs/week_1_launch/` - internal launch planning
- `docs/go_to_market/` - internal marketing
- `docs/marketing-pack/` - internal marketing
- `docs/analysis/` - internal analysis (check content first)
- `docs/issues/` - issue tracking (check if needed)

**Release Artifacts:**
- `release_artifacts/local_build/` - local build outputs
- `release_artifacts/v1.4.0/` through `release_artifacts/v3.0.*/` - old versions (unless needed for reference)
- Keep: `release_artifacts/v3.3.0/` (current version)

**Other Directories (Evaluate):**
- `evidence/` - keep essential (v3.1.0+), delete demos/outdated
- `website/` - delete unless launching public site
- `certs/` - verify & delete test certificates
- `compliance_reports/` - delete old reports

---

## Phase 1: Delete Large Cache & Build Artifacts (~383M)

**Command:** (run with caution - verify paths first)
```bash
cd /mnt/k/backup/Develop/code-scalpel

# Cache directories (~339M)
rm -rf .code_scalpel_cache
rm -rf .scalpel_cache
rm -rf .scalpel_ast_cache
rm -rf .ruff_cache
rm -rf .pytest_cache

# Coverage & test artifacts (~43M)
rm -rf htmlcov
rm -rf .coverage

# Build artifacts (~6M)
rm -rf dist
rm -rf dist_protected
rm -rf build_protected

# Check before delete
du -sh .archive .bench_tmp .test_simple .tmp_tier_comm .internal .claude .venv .venv-mcp-smoke
```

**Expected Space Freed:** ~383M

---

## Phase 2: Clean Temp & Deprecated Directories (~12M)

**Command:**
```bash
cd /mnt/k/backup/Develop/code-scalpel

# Archived/temporary directories
rm -rf .archive
rm -rf .bench_tmp
rm -rf .test_simple
rm -rf .tmp_tier_comm
rm -rf .internal
rm -rf .claude
# Optional: rm -rf .venv .venv-mcp-smoke (if not using)
```

**Expected Space Freed:** ~12M

---

## Phase 3: Consolidate Documentation (~20M)

### Step 3a: Delete Internal/Redundant Markdown Files
```bash
cd /mnt/k/backup/Develop/code-scalpel

# Internal assessment/status docs
rm -f docs/ASSESSMENT_*.md
rm -f docs/code_scalpel_assessment_checklist*.md
rm -f docs/GOVERNANCE_ENFORCEMENT_STATUS.md
rm -f docs/technical_debt.md
rm -f docs/stress.md

# Redundant/old roadmaps
rm -f docs/V1.0_ROADMAP*.md
rm -f docs/ROADMAP_INDEX.md
rm -f docs/ROADMAP_SUMMARY.md
rm -f docs/QUICK_REFERENCE_DOCS.md
rm -f docs/PROJECT_INDEX.md
rm -f docs/INDEX.md  # Will consolidate into docs/README.md

# Process/internal documentation
rm -f docs/DOCUMENT_REORGANIZATION_*.md
rm -f docs/TODO_FORMAT_STANDARDIZATION.md
rm -f docs/TIER_CONFIGURATION.md
rm -f docs/CUSTOMER_COMMUNICATION*.md
rm -f docs/BETA_*.md
rm -f docs/PROJECT_REORG_REFACTOR.md
rm -f docs/QUICK_SETUP_GUIDE.md  # consolidate into getting_started
rm -f docs/TEST_SUITE_BREAKDOWN.md  # internal detail
rm -f docs/AI_AGENT_TOOL_GUIDE.md  # check if needed, likely redundant
```

### Step 3b: Delete Internal Documentation Subdirectories
```bash
cd /mnt/k/backup/Develop/code-scalpel

# Internal/temporary directories
rm -rf docs/internal
rm -rf docs/status
rm -rf docs/todo_reports
rm -rf docs/week_1_launch
rm -rf docs/go_to_market
rm -rf docs/marketing-pack
rm -rf docs/archive

# Evaluate:
# rm -rf docs/analysis  # check if internal or useful
# rm -rf docs/issues  # check if issue tracker needed
```

**Expected Space Freed:** ~950KB (not huge, but cleaner)

---

## Phase 4: Release Artifacts (~22M)

```bash
cd /mnt/k/backup/Develop/code-scalpel

# Delete old versions and local builds
rm -rf release_artifacts/local_build
rm -rf release_artifacts/v1.4.0
rm -rf release_artifacts/v1.5.0
rm -rf release_artifacts/v1.5.1
rm -rf release_artifacts/v2.0.0
rm -rf release_artifacts/v2.1.0
rm -rf release_artifacts/v3.0.0
rm -rf release_artifacts/v3.0.0-preview
rm -rf release_artifacts/v3.0.1
rm -rf release_artifacts/v3.0.2
rm -rf release_artifacts/v3.0.3
rm -rf release_artifacts/v3.0.4
rm -rf release_artifacts/v3.0.5
rm -rf release_artifacts/v3.1.0
rm -rf release_artifacts/v3.2.0
rm -rf release_artifacts/v3.2.1
rm -rf release_artifacts/v3.3.0-preview

# Keep only: release_artifacts/v3.3.0/
```

**Expected Space Freed:** ~20-22M

---

## Phase 5: Evidence & Miscellaneous (~??M)

```bash
cd /mnt/k/backup/Develop/code-scalpel

# Evidence directory - keep essential, delete old
# du -sh evidence/*  # inspect first
# rm -rf evidence/demos  # if not needed
# rm -rf evidence/comparisons  # if not needed

# Website - decide
# rm -rf website  # if not launching public site

# Test certificates - verify safe to delete
# du -sh certs/
# rm -rf certs  # if test only

# Compliance reports - delete old
# du -sh compliance_reports/
# rm -rf compliance_reports  # or keep only latest

# Benchmarks - keep or delete?
# du -sh benchmarks/
# rm -rf benchmarks  # if demo/internal only
```

**Expected Space Freed:** ~5-15M (varies by choices)

---

## Phase 6: Update Critical Root-Level Documents

### Tasks:

1. **README.md** - Trim to essential:
   - Project overview (what it is)
   - Quick install (pip install code-scalpel)
   - Quick example (5-10 lines)
   - Links to docs for more

2. **SECURITY.md** - Ensure complete:
   - Security policy
   - Responsible disclosure
   - Known vulnerabilities section
   - Update schedule

3. **DEVELOPMENT_ROADMAP.md** - Keep but verify it's public-facing
   - Remove internal dates/status
   - Focus on user-visible features

4. **LICENSE** - Verify MIT or compatible license

5. **CREATE: CONTRIBUTING.md**
   - How to contribute
   - Dev setup (poetry/pip, virtualenv, pre-commit)
   - Run tests: `pytest tests/`
   - Lint: `ruff check src/ tests/`
   - Format: `black src/ tests/`
   - Type check: `pyright src/`
   - Submit PR to main

6. **CREATE: CODE_OF_CONDUCT.md**
   - Standard community guidelines
   - Link to security/support contact

7. **UPDATE: .gitignore**
   - Add cache patterns
   - Add build patterns
   - Add venv patterns

---

## Phase 7: Test After Cleanup

```bash
cd /mnt/k/backup/Develop/code-scalpel

# 1. Verify structure is clean
du -sh .
ls -la | grep "^\."  # check for unwanted hidden dirs

# 2. Run full test suite
pytest tests/ -v --tb=short

# 3. Run linters
ruff check src/ tests/
black --check src/ tests/
pyright src/

# 4. Verify package can be built
python -m build

# 5. Verify imports work
python -c "import code_scalpel; print(code_scalpel.__version__)"
```

---

## Phase 8: Commit & Push

```bash
cd /mnt/k/backup/Develop/code-scalpel

git add -A
git commit -m "[20250116_CLEANUP] Public release cleanup: remove caches, builds, internal docs

- Removed cache directories: .code_scalpel_cache, .scalpel_cache, .ruff_cache
- Removed build artifacts: dist, dist_protected, build_protected, htmlcov
- Removed archived/temp dirs: .archive, .bench_tmp, .test_simple, .internal
- Consolidated docs: deleted internal assessment/roadmap/status docs
- Pruned release_artifacts: kept only v3.3.0
- Space freed: ~450M
- Repo now ready for public release"

git push origin main
```

---

## Summary

| Phase | Action | Space Freed | Status |
|-------|--------|-------------|--------|
| 1 | Delete caches & builds | ~383M | ⬜ Pending |
| 2 | Delete temp/archived dirs | ~12M | ⬜ Pending |
| 3 | Consolidate docs | ~1M | ⬜ Pending |
| 4 | Prune release_artifacts | ~20M | ⬜ Pending |
| 5 | Clean evidence/misc | ~5-15M | ⬜ Pending |
| 6 | Update root docs | N/A | ⬜ Pending |
| 7 | Test after cleanup | N/A | ⬜ Pending |
| 8 | Commit & push | N/A | ⬜ Pending |

**Total Space Saved:** ~420-450M
**Final Repo Size:** ~200-300MB (mostly src + tests + essential docs)

