# Unicode Encoding Validation

**[20260210_FEATURE]** Pre-release validation to prevent Windows encoding issues.

---

## Purpose

This validation check ensures all `write_text()` and `read_text()` calls in the codebase explicitly specify `encoding='utf-8'`. This prevents `UnicodeEncodeError` on Windows systems that default to cp1252 encoding.

---

## The Problem

### What Happens Without Explicit Encoding

On **Linux/Mac**, Python defaults to UTF-8 encoding, so this works fine:
```python
path.write_text("Hello ✅ World")  # Works on Linux/Mac
```

On **Windows**, Python defaults to cp1252 encoding, which can't handle Unicode characters:
```python
path.write_text("Hello ✅ World")  # ❌ UnicodeEncodeError on Windows!
```

**Error message:**
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 194-196:
character maps to <undefined>
```

### Why This Matters

Code Scalpel uses Unicode characters in templates:
- Box drawing: `─`, `│`, `├`, `└`
- Status indicators: `✅`, `❌`, `⚠️`
- Documentation formatting

Without explicit encoding, the `codescalpel init` command fails on Windows systems.

---

## The Solution

**Always specify `encoding='utf-8'`** for all Path read/write operations:

```python
# ✅ CORRECT - Works on all platforms
path.write_text(content, encoding="utf-8")
data = path.read_text(encoding="utf-8")

# ❌ WRONG - Fails on Windows with Unicode content
path.write_text(content)
data = path.read_text()
```

---

## Running the Validation

### Locally

```bash
# Check all Python files for encoding violations
python scripts/validate_encoding.py
```

**Success output:**
```
✅ ENCODING VALIDATION PASSED
   Checked 247 Python files
   All write_text() and read_text() calls specify encoding='utf-8'
```

**Failure output:**
```
❌ ENCODING VALIDATION FAILED

Found write_text() or read_text() calls without explicit encoding='utf-8':

  src/code_scalpel/config/init_config.py:
    Line 167: write_text() missing encoding parameter
    Line 172: write_text() missing encoding parameter
    Line 177: write_text() missing encoding parameter

Fix: Add encoding='utf-8' parameter to all calls:
  - path.write_text(content, encoding='utf-8')
  - path.read_text(encoding='utf-8')

Total violations: 27
```

### In CI Pipeline

The validation runs automatically as part of the CI pipeline:

```yaml
encoding-validation:
  name: Unicode Encoding Validation (Windows compatibility)
  runs-on: ubuntu-latest
  needs: [smoke]
  timeout-minutes: 5
```

View results: https://github.com/3D-Tech-Solutions/code-scalpel/actions

---

## How It Works

The validation script (`scripts/validate_encoding.py`):

1. **Parses Python AST** - Uses `ast.parse()` to analyze code structure
2. **Finds Path operations** - Identifies all `.write_text()` and `.read_text()` calls
3. **Checks for encoding** - Verifies `encoding='utf-8'` keyword argument is present
4. **Reports violations** - Lists file paths and line numbers for missing encoding

**Example AST check:**
```python
class EncodingValidator(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            if method_name in ("write_text", "read_text"):
                has_encoding = any(
                    kw.arg == "encoding" for kw in node.keywords
                )
                if not has_encoding:
                    self.violations.append((node.lineno, method_name))
```

---

## Common Patterns to Fix

### Pattern 1: Configuration Files

```python
# ❌ BEFORE
config_file.write_text(CONFIG_JSON_TEMPLATE)

# ✅ AFTER
config_file.write_text(CONFIG_JSON_TEMPLATE, encoding="utf-8")
```

### Pattern 2: Reading Source Code

```python
# ❌ BEFORE
source = Path("script.py").read_text()

# ✅ AFTER
source = Path("script.py").read_text(encoding="utf-8")
```

### Pattern 3: Template Generation

```python
# ❌ BEFORE
readme_file.write_text(README_TEMPLATE)
gitignore_file.write_text(GITIGNORE_TEMPLATE)

# ✅ AFTER
readme_file.write_text(README_TEMPLATE, encoding="utf-8")
gitignore_file.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
```

### Pattern 4: Multi-line String Literals

```python
# ❌ BEFORE
license_readme.write_text("""# Code Scalpel License Directory
This directory stores license keys.
""")

# ✅ AFTER
license_readme.write_text("""# Code Scalpel License Directory
This directory stores license keys.
""", encoding="utf-8")
```

---

## Pre-Release Integration

The encoding validation is now part of the **pre-release checklist**:

From `docs/RELEASING.md`:
```markdown
## Pre-Release Checklist

Before releasing, verify:

- [ ] All tests pass locally: `pytest`
- [ ] Code passes linting: `black --check . && ruff check .`
- [ ] Unicode encoding validation passes: `python scripts/validate_encoding.py` ✨
- [ ] No uncommitted changes: `git status`
- [ ] On `main` branch: `git branch`
- [ ] Up-to-date with remote: `git pull origin main`
```

---

## Why Not Use a Linter?

You might wonder: "Why not use `ruff` or `pylint` for this?"

**Answer:** Most linters don't check for missing encoding parameters because:
1. It's platform-specific (only affects Windows)
2. It's a runtime issue, not a syntax issue
3. Default encoding behavior varies by environment

By creating a **custom validation script**, we:
- Catch this specific issue early
- Provide clear, actionable error messages
- Integrate seamlessly with CI/CD
- Run fast (<5 seconds for entire codebase)

---

## Related Issues

- **Issue #1**: Windows users getting `UnicodeEncodeError` on `codescalpel init`
- **Root Cause**: Missing `encoding='utf-8'` in `init_config.py`
- **Fix**: Added encoding validation to CI pipeline
- **Prevention**: This check prevents the issue from happening again

---

## References

- Python PEP 597: https://peps.python.org/pep-0597/
- pathlib.Path documentation: https://docs.python.org/3/library/pathlib.html
- Windows default encoding: https://docs.python.org/3/library/codecs.html#standard-encodings

---

## Summary

✅ **Always use `encoding='utf-8'`** for file I/O
✅ **Run validation locally** before committing
✅ **CI automatically checks** all pull requests
✅ **Prevents Windows encoding errors** in production

This simple check saves hours of debugging Windows-specific issues!
