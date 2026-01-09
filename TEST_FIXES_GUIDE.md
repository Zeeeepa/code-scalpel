# v3.3.0 Test Fixes - Quick Guide

## Issue 1: Missing `get_cached_limits` Function

**File:** `tests/test_missing_limits_toml.py`
**Error:** `AttributeError: <module 'code_scalpel.licensing.features'> does not have the attribute 'get_cached_limits'`

### Investigation Needed
```bash
cd /mnt/k/backup/Develop/code-scalpel

# Check what's actually in features.py
grep -n "def.*cached.*limit" src/code_scalpel/licensing/features.py

# Check what the test expects
head -60 tests/test_missing_limits_toml.py
```

### Possible Fixes
1. **Option A:** Add the missing function to `features.py`
2. **Option B:** Update test to use correct function name
3. **Option C:** Delete test if it's obsolete

---

## Issue 2: Working Directory Error

**File:** `tests/test_no_limits_file.py`
**Error:** `FileNotFoundError: [Errno 2] No such file or directory` from `Path.cwd()`

### Investigation
```bash
# Check the test file
head -20 tests/test_no_limits_file.py

# The issue is likely on line 12:
# original_cwd = Path.cwd()
```

### Fix
The test is likely running from a directory that no longer exists. Wrap in try/except:

```python
try:
    original_cwd = Path.cwd()
except FileNotFoundError:
    original_cwd = Path(__file__).parent
```

---

## Issue 3: pytest_plugins Configuration

**File:** `tests/tools/rename_symbol/conftest.py`
**Error:** `Defining 'pytest_plugins' in a non-top-level conftest is no longer supported`

### Fix Steps

1. **Check what plugins are defined:**
```bash
cat tests/tools/rename_symbol/conftest.py | grep pytest_plugins
```

2. **Move to root conftest.py:**
```bash
# Edit the root conftest.py
vim conftest.py  # or create if doesn't exist

# Add the plugins from tests/tools/rename_symbol/conftest.py
# Then remove pytest_plugins from the subdirectory conftest
```

### Example Root conftest.py
```python
# /mnt/k/backup/Develop/code-scalpel/conftest.py
import pytest

# Plugins that were in tests/tools/rename_symbol/conftest.py
pytest_plugins = [
    # Add whatever was defined there
]
```

---

## Testing After Fixes

```bash
cd /mnt/k/backup/Develop/code-scalpel

# Test collection only (fast check)
pytest tests/ --collect-only

# Run specific fixed tests
pytest tests/test_missing_limits_toml.py -v
pytest tests/test_no_limits_file.py -v
pytest tests/tools/rename_symbol/ -v

# Full test suite with coverage
pytest tests/ -v --cov --cov-report=html
```

---

## Deprecation Warnings to Fix (Lower Priority)

### Update Test Imports

Find and replace deprecated imports:

```bash
# Find files using deprecated imports
grep -r "from code_scalpel.polyglot import" tests/
grep -r "from code_scalpel.project_crawler import" tests/
grep -r "from code_scalpel.surgical_extractor import" tests/
grep -r "from code_scalpel.code_analyzer import" tests/

# Update them:
# code_scalpel.polyglot → code_scalpel.code_parsers
# code_scalpel.project_crawler → code_scalpel.analysis
# code_scalpel.surgical_extractor → code_scalpel.surgery
# code_scalpel.surgical_patcher → code_scalpel.surgery
# code_scalpel.code_analyzer → code_scalpel.analysis
```

### Add Slow Marker to pytest.ini

```bash
# Edit pytest.ini
vim pytest.ini

# Add to [pytest] section:
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
```

---

## Commands Summary

```bash
# Investigation
cd /mnt/k/backup/Develop/code-scalpel
grep -n "get_cached_limits" src/code_scalpel/licensing/features.py
head -20 tests/test_no_limits_file.py
cat tests/tools/rename_symbol/conftest.py

# After fixes - verify
pytest tests/ --collect-only  # Should collect 6426 tests with no errors

# Run full suite
pytest tests/ -v --cov --cov-report=html --cov-report=term-missing

# Generate coverage report
open htmlcov/index.html
```

---

**Next:** Fix these 3 issues, then run full test suite for v3.3.0 release validation
