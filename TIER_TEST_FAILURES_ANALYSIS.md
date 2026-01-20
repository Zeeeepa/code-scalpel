# Security Scan Tier Test Failures - Root Cause Analysis

**Date**: January 20, 2026
**Test File**: `tests/tools/tiers/test_security_scan_tiers.py`

## Summary

Three test failures in security_scan tier tests indicate issues with:
1. Vulnerability detection with symbolic execution verification
2. Community tier cap enforcement after license expiry
3. Monkeypatch path for SecurityAnalyzer stub

## Test Failures

### 1. test_security_scan_enterprise_enables_enterprise_fields
- **Expected**: ≥5 vulnerabilities (1 weak crypto + 5 eval calls)
- **Actual**: 2 vulnerabilities (only weak crypto detected)
- **Status**: FAILED

```python
code = """\
import hashlib

def insecure_hash(user_input: str):
    return hashlib.sha1(user_input.encode()).hexdigest()

""" + _make_repetitive_vuln_code(5)  # Generates 5 lines of eval('1')
```

**Root Cause**: The `SecurityAnalyzer.analyze()` method (lines 370-430 in security_analyzer.py) uses symbolic execution verification via `_verify_vulnerability()` to prune false positives. The generated code `eval('1')` does not involve tainted input, so the symbolic executor determines these are not real vulnerabilities and prunes them.

**Code Path**:
```python
# security_analyzer.py:403-416
taint_vulns = self._taint_tracker.get_vulnerabilities()

# Part 2: Prune False Positives via Symbolic Execution
verified_vulns = []
for vuln in taint_vulns:
    if self._verify_vulnerability(vuln, code):
        verified_vulns.append(vuln)
    else:
        logger.info(f"Pruned vulnerability at line {vuln.sink_location[0]}")
```

**Why This Happens**:
- `eval('1')` has no tainted input, so there's no data flow from user input to the sink
- The symbolic executor correctly identifies this as dead code/non-exploitable
- The test assumption was that simple pattern matching would detect `eval()` regardless of context

### 2. test_security_scan_expired_license_after_grace_downgrades
- **Expected**: 50 vulnerabilities (Community cap)
- **Actual**: 70 vulnerabilities (no cap applied)
- **Status**: FAILED

```python
code = _make_repetitive_vuln_code(70)  # Generates 70 lines of eval('1')
```

**Root Cause**: The Community tier finding cap (max_findings = 50) is not being enforced after license expiry because:
1. The tier detection is not properly downgrading from "pro" to "community" after grace period
2. The `_security_scan_sync()` function at line 2077 applies the cap:
   ```python
   max_findings = limits.get("max_findings")
   if max_findings is not None and max_findings >= 0:
       vulnerabilities = vulnerabilities[:max_findings]
   ```
3. However, the tier is still being detected as "pro" instead of "community", so it gets pro limits

**Why This Happens**:
- The monkeypatch sets `server._LAST_VALID_LICENSE_AT` to a time beyond grace period
- However, the tier detection in `_get_current_tier()` is not checking the grace period correctly
- The server module's global state may not be properly reset between tests

### 3. test_security_scan_pro_detects_nosql_ldap_and_secrets
- **Expected**: 3 vulnerabilities (NoSQL, LDAP, Secret)
- **Actual**: 0 vulnerabilities
- **Status**: FAILED

```python
monkeypatch.setattr(
    "code_scalpel.security.analyzers.SecurityAnalyzer", _StubAnalyzer
)
```

**Root Cause**: The monkeypatch is using the wrong import path. The `_security_scan_sync()` function imports SecurityAnalyzer locally:
```python
# security_helpers.py:2048
analyzer = SecurityAnalyzer()
result = analyzer.analyze(code).to_dict()
```

The import happens in the function scope, so the monkeypatch path `"code_scalpel.security.analyzers.SecurityAnalyzer"` doesn't affect the local import from `code_scalpel.security.analyzers` (imported at the top of the file).

**Why This Happens**:
- Monkeypatch must match the import path used in the code being tested
- The helper file imports: `from code_scalpel.security.analyzers import SecurityAnalyzer`
- The correct monkeypatch path should be: `"code_scalpel.mcp.helpers.security_helpers.SecurityAnalyzer"`
- OR the monkeypatch should occur before the import

## Recommended Fixes

### Fix 1: Update Enterprise Test to Use Tainted Input

**Option A**: Generate code with actual tainted input that reaches eval():
```python
code = """\
import hashlib

def insecure_hash(user_input: str):
    return hashlib.sha1(user_input.encode()).hexdigest()

def process_input(user_input: str):
    eval(user_input)  # Tainted input reaches eval
    eval(user_input)
    eval(user_input)
    eval(user_input)
    eval(user_input)
"""
```

**Option B**: Disable symbolic verification for this test using monkeypatch:
```python
def _always_verify(self, vuln, code):
    return True

monkeypatch.setattr(
    "code_scalpel.security.analyzers.security_analyzer.SecurityAnalyzer._verify_vulnerability",
    _always_verify
)
```

**Option C**: Use the pattern matching fallback explicitly by mocking the analyzer import failure.

### Fix 2: Fix Community Cap Enforcement After Expiry

The issue is in how the test sets up the expired license. The test needs to ensure:
1. License validation returns `is_valid=False` and `is_expired=True`
2. The grace period check in the server properly downgrades to "community"
3. The tier passed to `_security_scan_sync()` is actually "community"

**Recommended approach**: Check the tier detection logic in `server.py` and ensure it properly handles grace period expiry.

### Fix 3: Fix Monkeypatch Path for SecurityAnalyzer Stub

**Option A**: Use correct import path for monkeypatch:
```python
monkeypatch.setattr(
    "code_scalpel.mcp.helpers.security_helpers.SecurityAnalyzer",
    _StubAnalyzer
)
```

**Option B**: Monkeypatch the analyze method directly on the instance (requires refactoring to make SecurityAnalyzer a singleton or class-level).

**Option C**: Use dependency injection to pass analyzer to `_security_scan_sync()`.

## Impact Assessment

**Severity**: MEDIUM
- Tests are correctly identifying gaps in tier enforcement and detection logic
- The failures represent real issues with how Pro/Enterprise features are gated
- Advanced fields (policy_violations, reachability_analysis, etc.) ARE being populated correctly when vulnerabilities exist
- The core issue is vulnerability detection, not tier gating

**User Impact**: LOW
- Real-world code with tainted input flows will still be detected correctly
- The symbolic execution verification is actually a feature, not a bug (reduces false positives)
- However, users expecting simple pattern matching may be surprised

## Next Steps

1. **Immediate**: Update test cases to use realistic tainted input patterns
2. **Short-term**: Fix Community cap enforcement after license expiry
3. **Medium-term**: Fix monkeypatch path for SecurityAnalyzer mocking
4. **Long-term**: Consider adding a "strict mode" flag to disable symbolic verification for testing

## Related Files

- `tests/tools/tiers/test_security_scan_tiers.py` - Test file with failures
- `src/code_scalpel/mcp/helpers/security_helpers.py` - `_security_scan_sync()` implementation
- `src/code_scalpel/security/analyzers/security_analyzer.py` - SecurityAnalyzer with symbolic verification
- `src/code_scalpel/mcp/server.py` - License tier detection and grace period logic
