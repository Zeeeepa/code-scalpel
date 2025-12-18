# Release Protocol

**Version:** 1.0  
**Last Updated:** 2025-12-04  
**Status:** [CELEBRATION] Gate 3 [COMPLETE] PASSED - v0.1.0 LIVE ON PyPI

---

## Philosophy

> A Roadmap says "We will do X in Q4."  
> A Release Protocol says "We will not ship X until it passes Gate Y."

We do not ship hope. We ship verified artifacts.

---

## Gate Status Overview

| Gate | Name | Status | Blocking |
|------|------|--------|----------|
| 0 | Security Gate | [COMPLETE] PASSED | - |
| 1 | Artifact Gate | [COMPLETE] PASSED | - |
| 2 | Dress Rehearsal | [COMPLETE] PASSED | - |
| 3 | Public Debut | [COMPLETE] PASSED | - |
| 4 | Redemption | [TESTING] EXPERIMENTAL | - |

---

## [SECURITY]️ Gate 0: Security Gate

**Status: [COMPLETE] PASSED (2025-12-04)**

### Checklist

- [x] **Network Binding Audit**
  - Default bind address changed from `0.0.0.0` to `127.0.0.1`
  - Users must explicitly use `--host 0.0.0.0` for network access
  - Files modified: `mcp_server.py`, `cli.py`

- [x] **Path Traversal Test**
  - MCP server does not read files from disk
  - Only accepts `code` as a string in JSON body
  - Tested with: `../../../../etc/passwd`, `file:///etc/passwd`
  - Result: No file contents leaked

- [x] **Code Execution Test**
  - Dangerous code is ANALYZED, not EXECUTED
  - Tested with: `os.system()`, `eval()`, `exec()`
  - Result: No side effects, security issues detected

- [x] **Dependency Audit**
  - Ran `pip-audit`
  - Created `requirements-secure.txt` with pinned, patched versions
  - Critical fixes: `werkzeug>=3.1.4`, `jinja2>=3.1.6`, `urllib3>=2.5.0`

### Evidence

```
$ python scripts/simulate_mcp_client.py --port 8098
[COMPLETE] SECURITY: No path traversal (21ms)
   No path traversal detected
[COMPLETE] SECURITY: No code execution (3ms)
   Code analyzed (not executed), security issues detected
[CELEBRATION] ALL TESTS PASSED (11/11)
```

---

## [PACKAGE] Gate 1: Artifact Gate

**Status: [COMPLETE] PASSED (2025-12-04)**

### Checklist

- [x] **Configure pyproject.toml sdist**
  ```toml
  [tool.hatch.build]
  ignore-vcs = true
  
  [tool.hatch.build.targets.sdist]
  only-include = [
      "src/code_scalpel",
      "README.md",
      "LICENSE",
      "pyproject.toml",
  ]
  ```

- [x] **Build Verification**
  ```bash
  hatch build
  # [COMPLETE] dist/code_scalpel-0.1.0.tar.gz (86 files)
  # [COMPLETE] dist/code_scalpel-0.1.0-py3-none-any.whl
  ```

- [x] **Verify package contents**
  - [COMPLETE] No tests/ in wheel or sdist
  - [COMPLETE] No docs/ in wheel or sdist
  - [COMPLETE] No examples/ in wheel or sdist
  - [COMPLETE] No scripts/ in wheel or sdist
  - [COMPLETE] README.md and LICENSE present
  - [WARNING] .gitignore present (hatchling intentional, see #1203)

- [x] **twine check**
  ```bash
  $ twine check dist/*
  Checking dist/code_scalpel-0.1.0-py3-none-any.whl: PASSED
  Checking dist/code_scalpel-0.1.0.tar.gz: PASSED
  ```

### Note

The `.gitignore` file is intentionally included by hatchling for reproducibility.
This is a known design decision (pypa/hatch#1203). It's a 1KB file and does not
affect package functionality.

---

## [RELEASE] Gate 2: Dress Rehearsal (TestPyPI)

**Status: ⚪ NOT STARTED**
**Blocked by:** Gate 1

### Checklist

- [ ] **Configure TestPyPI credentials**
  ```bash
  # In ~/.pypirc or via environment
  TWINE_USERNAME=__token__
  TWINE_PASSWORD=pypi-...
  ```

- [x] **Upload to TestPyPI**
  ```bash
  twine upload --repository testpypi dist/*
  ```
  [COMPLETE] Uploaded: https://test.pypi.org/project/code-scalpel/0.1.0/

- [x] **The "Stranger" Test**
  ```bash
  pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ code-scalpel
  code-scalpel version  # [COMPLETE] Code Scalpel v0.1.0
  python -c "from code_scalpel import CodeAnalyzer; print('OK')"  # [COMPLETE] OK
  ```

---

## [LAUNCH] Gate 3: Public Debut (v0.1.0)

**Status: [COMPLETE] PASSED (2025-12-04)**

**Live:** https://pypi.org/project/code-scalpel/0.1.0/

### Scope

**Included:**
- AST Analysis (94% coverage)
- PDG Analysis (86% coverage)
- MCP Server (65% coverage, integration tested)
- CLI (76% coverage)
- Integrations: Autogen, CrewAI (67-70% coverage)

**Excluded (Quarantined):**
- Symbolic Execution (experimental, crashes on use)

### Checklist

- [x] **Final test run**
  - 180 tests passing
  - 37% coverage

- [x] **Git tag created**
  ```bash
  git tag -a v0.1.0 -m "Release v0.1.0: First public release"
  git push origin v0.1.0
  ```

- [x] **Upload to PyPI**
  ```bash
  twine upload dist/*
  # [COMPLETE] View at: https://pypi.org/project/code-scalpel/0.1.0/
  ```

- [x] **Verify installation**
  ```bash
  pip install code-scalpel
  code-scalpel version  # [COMPLETE] Code Scalpel v0.1.0
  python -c "from code_scalpel import CodeAnalyzer; print('OK')"  # [COMPLETE] OK
  ```

- [ ] **Create GitHub Release** (manual step required)

---

## [PREVIEW] Gate 4: Redemption (v0.2.0)

**Status: [TESTING] EXPERIMENTAL**
**Blocked by:** Gate 3

### Goal

Re-enable Symbolic Execution as a production feature.

### Requirements

- [ ] Implement `SymbolicExecutionEngine._infer_type()`
- [ ] Implement `ConstraintSolver.solve()`
- [ ] Integrate Z3 solver properly
- [ ] Achieve 80% coverage on `symbolic_execution_tools/`
- [ ] Remove `UserWarning` from `__init__.py`
- [ ] Update README to move from "Experimental" to "Features"

### Evidence Required

```bash
python -c "
from code_scalpel.symbolic_execution_tools import SymbolicExecutionEngine
from code_scalpel.symbolic_execution_tools import ConstraintSolver

solver = ConstraintSolver()
engine = SymbolicExecutionEngine(solver)
result = engine.execute('x = 1 + 2')
print('Paths explored:', len(result.paths))
"
# Must complete without error
```

---

## Audit Trail

| Date | Gate | Action | Result |
|------|------|--------|--------|
| 2025-12-04 | 0 | Security audit | [COMPLETE] PASSED |
| 2025-12-04 | 0 | Fixed 0.0.0.0 → 127.0.0.1 | [COMPLETE] Fixed |
| 2025-12-04 | 0 | Path traversal test | [COMPLETE] No vulnerability |
| 2025-12-04 | 0 | Code execution test | [COMPLETE] No vulnerability |
| 2025-12-04 | 0 | pip-audit | [WARNING] 47 CVEs in system, mitigated with requirements-secure.txt |
| 2025-12-04 | 1 | Configure sdist exclusions | [COMPLETE] Fixed |
| 2025-12-04 | 1 | Removed tests/docs/examples from sdist | [COMPLETE] Done |
| 2025-12-04 | 1 | twine check | [COMPLETE] PASSED |
| 2025-12-04 | 2 | Upload to TestPyPI | [COMPLETE] https://test.pypi.org/project/code-scalpel/0.1.0/ |
| 2025-12-04 | 2 | Stranger Test (TestPyPI) | [COMPLETE] Install + CLI + Import all work |
| 2025-12-04 | 3 | Git tag v0.1.0 | [COMPLETE] Pushed to origin |
| 2025-12-04 | 3 | Upload to PyPI | [COMPLETE] https://pypi.org/project/code-scalpel/0.1.0/ |
| 2025-12-04 | 3 | Stranger Test (PyPI) | [COMPLETE] Install + CLI + Import all work |
| 2025-12-04 | 3 | **v0.1.0 LIVE** | [CELEBRATION] First public release |
