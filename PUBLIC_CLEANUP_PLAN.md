# Code Scalpel Public Release Cleanup Plan

## Inventory Summary

### To DELETE (Dead/Old/Archived/Build Artifacts)

#### Cache & Build Artifacts (383M total)
- `.code_scalpel_cache/` (329M) - internal cache, not needed for public
- `htmlcov/` (43M) - coverage reports, regenerate if needed
- `.scalpel_cache/` (5M) - internal cache
- `.ruff_cache/` (564K) - local linter cache
- `.scalpel_ast_cache/` - empty but should clean
- `build_protected/` (300K) - internal build
- `dist_protected/` (776K) - internal distribution
- `dist/` (5.2M) - local build, regenerate on publish

#### Archived & Temporary Directories
- `.archive/` (4M) - old/deprecated code and tests
- `.bench_tmp/` (816K) - temporary benchmark files
- `.test_simple/` - temporary test directory
- `.tmp_tier_comm/` - leftover test temp directory
- `.internal/` (1.3M) - internal checklists/status/summaries
- `.venv/`, `.venv-mcp-smoke/` - virtual envs (symlink if needed)
- `.claude/` - Claude-specific cache

#### Release Artifacts to Evaluate
- `release_artifacts/local_build/**` - delete (local build outputs)
- `release_artifacts/v1.4.0` through `v3.0.2` - consider archiving or deleting if not needed for public
- Keep: `release_artifacts/v3.3.0/` (current version evidence)

#### Documentation to Consolidate
**DELETE (Bloat/Internal/Redundant):**
- `docs/ASSESSMENT_*.md` - internal assessment docs
- `docs/BETA_OUTREACH_STRATEGY.md` - internal marketing
- `docs/CUSTOMER_COMMUNICATION_v4.md` - internal comms
- `docs/DOCUMENT_REORGANIZATION_*.md` - process docs
- `docs/GOVERNANCE_ENFORCEMENT_STATUS.md` - internal status
- `docs/PROJECT_REORG_REFACTOR.md` - process docs
- `docs/TODO_FORMAT_STANDARDIZATION.md` - process docs
- `docs/V1.0_ROADMAP*.md` - old roadmaps
- `docs/TIER_CONFIGURATION.md` - internal config doc
- `docs/code_scalpel_assessment_checklist*.md` - internal only
- `docs/technical_debt.md` - internal tracking
- `docs/stress.md` - unclear purpose
- `docs/todo_reports/**` - generated reports (regenerate if needed)

**DELETE (Redundant with better versions):**
- `docs/COMPREHENSIVE_GUIDE.md` - check if same as guides
- `docs/QUICK_REFERENCE_DOCS.md` - check if duplicate of docs/reference
- `docs/INDEX.md` - consolidate with docs/README.md
- `docs/PROJECT_INDEX.md` - consolidate
- `docs/ROADMAP_INDEX.md` - consolidate
- `docs/QUICK_SETUP_GUIDE.md` - consolidate with getting_started

**KEEP (Essential for Public):**
- `docs/README.md` - entry point
- `docs/DEVELOPMENT_ROADMAP.md` - public roadmap
- `docs/MIGRATION_v3.2_to_v3.3.md` - migration guide (keep recent ones)

#### Subdirectories to Evaluate
- `docs/archive/` - delete old archived docs
- `docs/internal/` - delete entirely
- `docs/go_to_market/`, `docs/marketing-pack/` - decide if public-facing or delete
- `docs/week_1_launch/` - internal planning, delete
- `docs/status/` - internal status, delete

#### Other Artifacts
- `evidence/` - keep structured versions (v3.1.0+), delete old demos/comparisons
- `website/` - keep if launching public site, else delete
- `certs/` - check if real or test certs; delete test certs
- `compliance_reports/` - delete old reports, keep latest if needed

### Files to Keep/Preserve (Public-Ready)

#### Root Level
- `README.md` - project overview (UPDATE)
- `LICENSE` - license terms (VERIFY)
- `SECURITY.md` - security policy (UPDATE)
- `DEVELOPMENT_ROADMAP.md` - public roadmap (UPDATE)
- `pyproject.toml` - package metadata (VERIFY/UPDATE)
- `.gitignore` - git ignore rules (EXPAND to include cleanups)
- `docker-compose.yml`, `Dockerfile` - if using (VERIFY)

#### Source Code
- `src/code_scalpel/` - keep all production code
- Remove: old agent placeholder files if any
- Remove: marked deprecated code with warnings

#### Tests (Modernized)
- `tests/core/`, `tests/tools/`, `tests/security/`, `tests/autonomy/` - keep essential tests
- Remove: `tests/manual/`, `tests/tool_exercise/`, `tests/scripts/` if internal-only
- Remove: old test data/fixtures not used

#### Documentation (Consolidated)
- `docs/README.md` - entry point
- `docs/getting_started/` - setup guide
- `docs/guides/` - how-to guides
- `docs/architecture/` - design docs
- `docs/release_notes/` - release history
- `docs/deployment/` - deployment info
- Cleanup: other subdirs as per above

#### Examples & Scripts
- `examples/` - keep working examples (VERIFY/UPDATE)
- `scripts/` - keep CI/deploy scripts needed for public
- `local_pipeline/` - decide if keep for internal CI or remove

#### Configuration
- `.code-scalpel/` - keep policy/governance files
- `.vscode/` - keep IDE settings if useful for contributors
- `configs/` - keep if needed, else remove

---

## Cleanup Execution Steps

### Phase 1: Delete Large Dead Code (Save ~380M)
```bash
rm -rf .code_scalpel_cache .scalpel_cache .ruff_cache .scalpel_ast_cache
rm -rf htmlcov dist dist_protected build_protected
rm -rf .archive .bench_tmp .test_simple .tmp_tier_comm
rm -rf .internal .claude .venv-mcp-smoke
```

### Phase 2: Clean Docs (Save ~10M)
```bash
# Delete internal assessment/marketing docs
rm docs/ASSESSMENT_*.md docs/CUSTOMER_COMMUNICATION*.md docs/BETA_*.md
rm docs/GOVERNANCE_ENFORCEMENT_STATUS.md docs/DOCUMENT_REORGANIZATION*.md
rm docs/PROJECT_REORG_REFACTOR.md docs/TODO_FORMAT*.md docs/TIER_CONFIGURATION.md
rm docs/code_scalpel_assessment*.md docs/technical_debt.md docs/stress.md
rm docs/V1.0_ROADMAP*.md

# Delete redundant indices
rm docs/INDEX.md docs/PROJECT_INDEX.md docs/ROADMAP_INDEX.md docs/QUICK_REFERENCE*.md

# Clean internal directories
rm -rf docs/internal docs/todo_reports docs/week_1_launch docs/status

# Optional: cleanup old subdirs if not public-facing
rm -rf docs/go_to_market docs/marketing-pack docs/archive
```

### Phase 3: Release Artifacts (Save ~20M)
```bash
# Keep only current version evidence
rm -rf release_artifacts/v1.* release_artifacts/v2.* release_artifacts/v3.0.* release_artifacts/v3.0.0-preview
rm -rf release_artifacts/local_build
# Keep: release_artifacts/v3.3.0/
```

### Phase 4: Evidence & Website (Save ~??M)
```bash
# Evaluate and keep only essential
rm -rf evidence/demos evidence/comparisons evidence/claims  # Keep: mcp-contract, v3.1.0, perf
rm -rf website/  # Decide: keep if launching, else delete
```

### Phase 5: Update .gitignore
Add:
```
*.bak
*.log
*.pyc
*.pyo
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.code_scalpel_cache/
.scalpel_cache/
htmlcov/
dist/
build/
*.egg-info/
.coverage
.venv*/
.env
.env.local
```

### Phase 6: Update Root Documents
- `README.md` - trim to public intro, install, quick example
- `SECURITY.md` - ensure complete for public
- `DEVELOPMENT_ROADMAP.md` - public-facing version
- `LICENSE` - confirm MIT or compatible
- Add: `CONTRIBUTING.md` with dev setup, lint/test commands
- Add: `CODE_OF_CONDUCT.md`

---

## File Count & Size Before/After

**Before:**
- Approx 750+ directories, ~1.5GB+ total with caches

**After (Estimate):**
- Approx 250-300 directories, ~200-300MB (mostly src + docs + tests)

---

## Notes

- Virtual environments (`.venv`, `.venv-mcp-smoke`) should stay if committing lock files; otherwise remove and document setup in `CONTRIBUTING.md`.
- Test certs in `certs/` should be verified as test-only before cleanup.
- `website/` needs decision: if launching public docs site, keep and modernize; else delete.
- CI scripts in `scripts/` and `local_pipeline/` need review for what's needed in public.
- Compliance reports should be regenerated/refreshed if keeping any.

