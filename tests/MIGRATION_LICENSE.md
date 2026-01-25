License Handling Migration Plan
===============================

Purpose
-------
- Centralize license env setup used by tests so tests uniformly and safely choose a license
  state (community/pro/enterprise/expired/revoked/missing). This reduces flakiness and
  makes future license-related test changes easy.

Location
--------
- This document: `tests/MIGRATION_LICENSE.md`
- Helper to add for subprocess tests: `tests/utils/license_helpers.py`
- Codemod script (implementation): `tools/codemods/migrate_license_env.py`
- Fixtures already added/used: `tests/conftest.py` (contains `use_license`) and
  `tests/utils/tier_setup.py` (import-time `activate_tier` / `tier_context`).

High-level strategy
-------------------
1. Discover all test locations that set license-related environment variables (explicit
   `CODE_SCALPEL_LICENSE_PATH`, `CODE_SCALPEL_ALLOW_HS256`, `CODE_SCALPEL_SECRET_KEY`,
   `CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY`, `CODE_SCALPEL_TIER`).
2. Transform tests in safe, small batches using an AST-aware codemod (libcst) that:
   - Replaces function-scoped monkeypatch/setenv calls with `use_license(...)`.
   - Replaces module-level import-time env hacks with `activate_tier(...)` or `tier_context(...)`.
   - Replaces subprocess env dict population with `tests.utils.license_helpers.populate_subprocess_env(...)`.
   - Detects and skips tests that intentionally manipulate CRLs, generate JWTs, or stub the
     JWT validator (these remain manual-review candidates).
3. Validate each batch by running a targeted pytest subset; revert any batch that breaks tests
   in unexpected ways and flag affected files for manual review.
4. Iterate until all safe changes are applied; run full test suite in CI with extended timeouts.

Codemod / tooling
-----------------
- Use an AST-aware tool (libcst) so changes are syntactically safe and imports/signatures are
  preserved. Implement `tools/codemods/migrate_license_env.py` to perform transformations and
  generate a migration report.
- The codemod should:
  - Add import statements when needed (e.g., `from tests.utils.tier_setup import activate_tier`)
  - Add `use_license` as a fixture argument where appropriate, or, when simpler, insert an
    in-function call to `use_license("state")` (prefer fixture injection when the test already
    uses fixtures).
  - Replace subprocess env key writes with a single helper call and preserve unrelated ENV sets.

Helper API (subprocess)
-----------------------
- `tests/utils/license_helpers.py` (recommended shared helper)

  populate_subprocess_env(env: dict[str, str], tmp_path: pathlib.Path, *, state: str = "valid") -> None

  - `state` values: `valid` (alias -> pro/enterprise as appropriate), `expired`, `revoked`, `missing`,
    `pro`, `enterprise`, `community`.
  - Sets minimal keys required for subprocesses: `CODE_SCALPEL_ALLOW_HS256`, `CODE_SCALPEL_SECRET_KEY`,
    `CODE_SCALPEL_LICENSE_PATH` and `CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY` as appropriate.

Batch rollout
-------------
- Batch 1: `tests/licensing/` and small unit tests that only affect license parsing/validation.
  - Purpose: validate codemod correctness on the most license-centric tests.
  - Validation: `pytest -q tests/licensing`

- Batch 2: MCP tests (function-scoped, excluding heavy live/transport tests).
  - Validation: `pytest -q tests/mcp -k "not transport and not live"`

- Batch 3: Tools tests under `tests/tools/` in tool-sized chunks (e.g., security_scan group).
  - Validation: `pytest -q tests/tools/<tool>` per chunk.

- Batch 4: CLI and subprocess-heavy tests. Use `populate_subprocess_env()` and run with
  extended timeouts locally or in CI.

- Final: full-suite CI run with extended timeout (20–60 minutes) to ensure no regressions.

Validation & rollback
---------------------
- After each batch:
  - Run the targeted pytest subset.
  - Run linters (ruff/flake8) if available.
  - If regressions appear: revert the batch commit/branch, inspect flagged files manually, and
    apply surgical fixes.

- Keep each batch as a standalone branch/PR to allow easy rollback and review.

Files to skip / manual review
----------------------------
- Tests that explicitly generate or mutate JWTs/CRLs (use fixtures `write_hs256_license_jwt`
  or `write_hs256_crl_jwt`) — these intentionally control low-level license artifacts.
- Tests that patch `JWTLicenseValidator` or otherwise stub license validation.
- Tests that dynamically change license env mid-test for very specific negative scenarios.

Examples (transform patterns)
-----------------------------
- Replace inline monkeypatch:

  Before:

  ```py
  def test_some(monkeypatch, tmp_path):
      monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(PRO_LICENSE))
      monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)
      ...
  ```

  After:

  ```py
  def test_some(use_license, tmp_path):
      use_license("valid")
      ...
  ```

- Replace module-level import-time license setup:

  Before (top of module):

  ```py
  os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(ENTERPRISE_LICENSE)
  ```

  After:

  ```py
  from tests.utils.tier_setup import activate_tier
  activate_tier("enterprise", skip_if_missing=True)
  ```

- Replace subprocess env dict population:

  Before:

  ```py
  env = _pythonpath_env(...)
  env["CODE_SCALPEL_ALLOW_HS256"] = "1"
  env["CODE_SCALPEL_SECRET_KEY"] = secret
  env["CODE_SCALPEL_LICENSE_PATH"] = str(license_path)
  ```

  After:

  ```py
  from tests.utils.license_helpers import populate_subprocess_env
  env = _pythonpath_env(...)
  populate_subprocess_env(env, tmp_path, state="enterprise")
  ```

Operational notes
-----------------
- Branching: use `tests/license-centralize/<batch-number>` for each batch commit.
- Reporting: the codemod will produce `tools/codemods/migration_report.md` listing changed files
  and skipped files needing manual review.
- Rollback: `git checkout -b <branch>` for changes; revert or drop branch if batch fails.

Recommended default choices
--------------------------
- Use a shared subprocess helper `tests/utils/license_helpers.py` (recommended) to keep subprocess
  env population consistent across tests.
- Use `use_license(...)` fixture for function-scoped tests and `activate_tier(...)` for import-time
  activation.

Timeline
--------
- Implement codemod + helper: 2–4 hours
- Batch 1 (licensing tests): 1–2 hours
- Batch 2 (MCP): 2–4 hours
- Batch 3 (tools): 3–8 hours depending on regressions
- Batch 4 (CLI/subprocess): 1–3 hours
- CI full-run and follow-up fixes: 1–3 hours

Next action (automated)
-----------------------
- I will implement the codemod scaffold and the shared subprocess helper, then run Batch 1 (licensing tests).
- Results, failing files, and migration report will be committed to a feature branch and reported back.

Contact
-------
- File location: `tests/MIGRATION_LICENSE.md`
