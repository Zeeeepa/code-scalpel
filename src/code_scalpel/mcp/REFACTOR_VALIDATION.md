UPDATED PLAN: v1.0.1 Refactoring Validation
Detailed TODOs for Refactor Validation (exhaustive)

Create validation scripts
- [ ] TDD: Add failing tests first (tests/tools/validation/)
    - [ ] tests/tools/validation/test_validate_tool_compliance.py (AST cases: @mcp.tool, envelop_tool_function, helper patterns, wrong signatures)
    - [ ] tests/tools/validation/test_analyze_deprecated_code.py (deprecation marker and import counts)
    - [ ] tests/tools/validation/test_validate_import_paths.py (deprecated import detection)
- [ ] Implement scripts/validate_tool_compliance.py
    - [ ] CLI flags: --root, --out-csv, --format (csv|md|json), --strict, --verbose
    - [ ] AST-based extractor: find decorated functions, record module, decorator type, signature, line numbers
    - [ ] Programmatic checks for all 13 criteria (use canonical detection logic)
    - [ ] Unit tests for each detection rule
    - [ ] Output: CSV matrix and optional Markdown table and JSON summary
    - [ ] Exit codes: 0 (pass), 1 (warnings), 2 (fail)
    - [ ] Include change tag comment above main (e.g., # [20260125_TEST] validate tool compliance)
- [ ] Implement scripts/analyze_deprecated_code.py
    - [ ] CLI flags: --root, --out-json, --min-import-threshold
    - [ ] Scan for deprecation markers (regex), DeprecationWarning on import, migration guidance strings
    - [ ] Count imports by scanning AST and repo-wide grep
    - [ ] Identify legacy functions and search for callers
    - [ ] Produce JSON inventory with file metadata and recommendations
    - [ ] Tests for each category (shims, modules, legacy functions, datetime patterns)
- [ ] Implement scripts/validate_import_paths.py
    - [ ] CLI flags: --root, --whitelist, --out-json
    - [ ] Search for deprecated import patterns and categorize by file type (source/test/doc/example)
    - [ ] Provide path-fix suggestions (canonical new import)
    - [ ] Tests verifying detection and suggested fixes
- [ ] Shared script hygiene tasks
    - [ ] Logging (structured JSON logs), verbose mode, dry-run mode
    - [ ] Robustness: skip binary files, follow .gitignore-like rules
    - [ ] Add inline docstring and usage examples
    - [ ] Add unit tests with pyproject compatible fixtures

Run automated tool compliance validation
- [ ] Add test fixture that prepares a minimal repo subtree with representative tool modules
- [ ] Run scripts/validate_tool_compliance.py against the real codebase
    - [ ] Collect CSV and JSON outputs in artifacts/
    - [ ] Verify "Tool count == 22" and "criteria pass counts"
- [ ] Verify edge cases:
    - [ ] envelop_tool_function wrappers (decorator factory, aliasing)
    - [ ] sync helper naming variants and placement
    - [ ] async wrapper vs synchronous helper invocation via asyncio.to_thread
- [ ] Record failures: capture failing tool names, errors and line numbers
- [ ] Update tests to reproduce any failures and ensure fix coverage

Run automated deprecated code inventory validation
- [ ] Execute scripts/analyze_deprecated_code.py
    - [ ] Verify all shim files are discovered and import counts measured
    - [ ] Verify polyglot deprecation and migration targets exist
    - [ ] Verify legacy functions caller counts and recommendations
    - [ ] Detect datetime.datetime.now() without timezone in licensing files
- [ ] Validate output JSON schema and example content
- [ ] Add tests that simulate import patterns and verify import counting logic

Run automated import path validation
- [ ] Execute scripts/validate_import_paths.py across src/ and tests/
    - [ ] Produce categorized report (tests/source/examples/docs)
    - [ ] Tag source findings as CRITICAL in the result JSON
- [ ] For each CRITICAL finding:
    - [ ] Create a suggested replacement import line
    - [ ] Create a short patch / PR template snippet to fix
- [ ] Verify no deprecated import occurrences in the main source tree after fixes

Review edge cases (manual + automated)
- [ ] Manual review plan week (pair of reviewers)
    - [ ] envelop_tool_function uses that wrap multiple functions
    - [ ] Tools with multiple decorators or wrappers
    - [ ] Tools where helper logic is inlined vs helper file
    - [ ] False positive patterns for helper detection (naming collisions)
- [ ] Add unit tests for each identified edge case
- [ ] Add TODO or comment locations for items requiring code author clarification

Verify tier enforcement logic
- [ ] Tests to ensure tool code calls get_tool_capabilities(tool_id, tier)
    - [ ] Detect missing calls or wrong parameter use
    - [ ] Verify limits are enforced by detecting reading of limits.toml keys
- [ ] Tier test fixtures: use existing tests/tools/tiers/conftest.py patterns
    - [ ] Add tests that assert result metadata fields populated (tier_applied, *_applied)
    - [ ] Validate behavior for community/pro/enterprise where applicable
- [ ] Add unit tests for limits violation detection and expected failure behavior

Check error handling coverage
- [ ] Verify each tool wraps exceptions in ToolError or returns ToolResponseEnvelope with error
    - [ ] Detect bare exceptions or print-only handlers
- [ ] Add tests that simulate helper exceptions and assert tool-level wrapping
- [ ] Ensure logs and stack traces are captured and sanitized in envelope
- [ ] Verify presence and use of make_envelope() where applicable

Compile compliance matrix
- [ ] Aggregate outputs from validate_tool_compliance.py into canonical CSV/JSON
- [ ] Implement script to generate final Markdown table for docs (scripts/generate_reports.py)
- [ ] Validate totals: tool counts, pass/fail counts, per-criteria summary
- [ ] Include per-tool fields: tool_id, module, criteria boolean columns, status, first-failure-line

Compile deprecated code inventory analysis
- [ ] Aggregate analyze_deprecated_code.py outputs into:
    - [ ] JSON inventory file (docs/evidence/v{VERSION}_deprecated_inventory.json)
    - [ ] Summary statistics (safe_to_remove, must_keep)
- [ ] Ensure legacy function recommendations are explicit and actionable
- [ ] Record datetime migration locations and suggested code change

Generate compliance matrix report
- [ ] Create Markdown report (docs/reports/refactor_validation_compliance.md)
    - [ ] Include: Matrix table, executive summary, counts, failing items
    - [ ] Add instructions for how to reproduce the run locally
- [ ] Produce CSV/JSON artifacts and attach example outputs
- [ ] Add an automated report generator script that accepts run metadata (timestamp, git sha)

Generate deprecated code inventory report
- [ ] Create JSON report (release_artifacts/v{VERSION}/v{VERSION}_deprecated_inventory.json)
- [ ] Create short Markdown summary and checklist (docs/reports/refactor_deprecated_inventory.md)
- [ ] Include recommendations (KEEP/REMOVE/KEEP_WITH_WARNING) as computed
- [ ] Provide guidance for removal timelines (only as plan items, not release decisions)

Create cleanup action items checklist
- [ ] For each CRITICAL item generate a GitHub issue template with:
    - [ ] Title, description, reproduction steps, suggested fix, tests to add
    - [ ] Priority/state (user to decide blocking vs enhancement)
- [ ] For SAFE TO REMOVE items:
    - [ ] Add issues that include a deprecation window and required migration notes
- [ ] For Document & Maintain items:
    - [ ] Add tasks to docs/ (place files under docs/where-appropriate per taxonomy)
    - [ ] Update docs/INDEX.md as needed (only if user approves)
- [ ] For Future items:
    - [ ] Create backlog issues with clear scope and acceptance criteria
- [ ] Triage meeting agenda item: present the checklist and get user decisions
- [ ] Add labels: refactor-validation, security, docs, follow-up

Cross-cutting engineering tasks
- [ ] CI Integration
    - [ ] Add CI job to run the validation scripts on push to main and on PRs (optional gating, ask user)
    - [ ] Upload artifacts to workflow run and store JSON/CSV
- [ ] Pre-commit / Code Quality
    - [ ] Ensure ruff and black pass on all new scripts and tests
    - [ ] Add type hints for public functions (Python 3.9+)
- [ ] Coverage and Tests
    - [ ] Ensure tests for validation scripts reach project coverage standard (add tests to keep coverage >=95%)
- [ ] Documentation & Runbook
    - [ ] Add a short runbook snippet describing "how to run validation locally" (docs/guides/validate_refactor.md) — add only if user explicitly asks to create docs
- [ ] Evidence and Artifacts
    - [ ] Store run artifacts in release_artifacts/v{VERSION}/ with timestamped filenames
    - [ ] Add small example outputs under examples/validation/
- [ ] Change Tagging & Commits
    - [ ] Add tag comments to new/changed files per policy (e.g., # [20260125_TEST])
    - [ ] Ask: "Have we run the verification script?" before any commit that claims validation passed
    - [ ] Do not commit/push without explicit permission
- [ ] Checklist Execution Policy
    - [ ] Execute all checklist items; capture results and evidence
    - [ ] If an item cannot be completed, document why and what was attempted

Acceptance criteria (for each task)
- Tests added and passing
- Scripts produce expected CSV/JSON/MD outputs
- All findings reproducible via tests
- Critical items have GitHub issues created and assigned
- Pre-commit hooks (ruff/black) pass on changed files
- Artifacts stored under release_artifacts/v{VERSION}/ or examples/ as appropriate

Minimal first sprint (Week 1)
- [ ] Add tests and skeletons for three scripts
- [ ] Implement validate_tool_compliance.py and its tests
- [ ] Implement analyze_deprecated_code.py and its tests
- [ ] Run both on repo and collect initial artifacts
- [ ] Open PR with changes and request review (do not merge until user approval)

Manual review sprint (Week 2)
- [ ] Manual triage of failures and edge cases
- [ ] Create issues for fixes
- [ ] Run follow-up validation after fixes

Notes / Constraints
- Follow TDD: write failing tests before implementation
- Use license fixtures for tier-related tests (do not monkeypatch to upgrade tiers)
- Do not create persistent docs unless user explicitly requests it
- Always ask for commit/push permission before creating commits or CI changes

Updated Todos (expanded)
- [ ] Create validation scripts (full spec above)
- [ ] Run automated tool compliance validation
- [ ] Run automated deprecated code inventory validation
- [ ] Run automated import path validation
- [ ] Review edge cases (manual & tests)
- [ ] Verify tier enforcement logic (fixtures & tests)
- [ ] Check error handling coverage
- [ ] Compile compliance matrix (CSV/MD/JSON)
- [ ] Compile deprecated code inventory analysis (JSON)
- [ ] Generate compliance matrix report (Markdown + artifacts)
- [ ] Generate deprecated code inventory report (JSON + Markdown)
- [ ] Create cleanup action items checklist (issues + triage)
- [ ] Integrate into CI (proposal only; require approval)
- [ ] Ask for permission to commit/push changes and to create or update documentation
