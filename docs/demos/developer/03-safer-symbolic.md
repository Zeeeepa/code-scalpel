# Demo: "Symbolic Execution: Find Hidden Edge Cases"

**Persona**: Developer
**Pillar**: Safer AI
**Tier**: Pro ($49/month)
**Duration**: 15 minutes
**Fixture**: From Ninja Warrior "Hidden Bug" obstacle

## Scenario

Function has edge case that's unreachable in normal testing. Symbolic execution with Z3 solver finds it.

## Tools Used

- `symbolic_execute` (Pro tier)
- `generate_unit_tests`

## Recording Script

### Step 1: The Subtle Bug (0:00-2:00)

- Show password validation function:
  ```python
  def validate_password(password: str, min_length: int = 8) -> bool:
      if len(password) < min_length:
          return False
      if min_length < 0:  # Edge case!
          return True  # BUG: accepts any password
      # ... other checks
      return True
  ```
- Tests pass (all use default min_length=8) ✓
- Bug: if min_length < 0, weak passwords accepted

### Step 2: Standard Testing Limitations (2:00-4:00)

- Show test suite: 15 test cases
- All use positive min_length values
- Code coverage: 92% ✓
- But edge case not tested ❌
- On-screen: "High coverage ≠ All paths tested"

### Step 3: Symbolic Execution Intro (4:00-5:00)

- Explain: "What if we test all POSSIBLE inputs?"
- Symbolic execution explores path space
- Z3 solver finds input that reaches each branch

### Step 4: Run symbolic_execute (5:00-8:00)

- Prompt: "Find all execution paths in validate_password"
- Tool workflow:
  1. Build CFG (control flow graph)
  2. Extract constraints at each branch
  3. Use Z3 to solve for inputs
  4. Generate test cases covering all paths
- Output: 47 unique paths explored

### Step 5: Bug Discovery (8:00-10:00)

- Tool reports: "Found unreachable condition at line 4"
- Path: `min_length = -5, password = "a"`
- Result: Function returns True (accepts weak password!)
- On-screen: "Symbolic execution found what fuzzing missed"

### Step 6: Auto-Generated Tests (10:00-12:00)

- Code Scalpel generates test case:
  ```python
  def test_negative_min_length():
      # Discovered by symbolic execution
      result = validate_password("weak", min_length=-5)
      assert result == False, "Should reject weak password"
  ```
- Run test: FAIL ✓ (confirms bug)

### Step 7: Fix and Verify (12:00-13:30)

- Apply fix:
  ```python
  if min_length < 1:
      raise ValueError("min_length must be positive")
  ```
- Re-run symbolic execution: all paths safe ✓
- On-screen: "Formal verification of fix"

### Step 8: Pro Tier Advantage (13:30-14:30)

- Community: 50 paths max, basic types
- Pro: Unlimited paths, complex constraints, string/list types
- Enterprise: Distributed execution, custom solvers

### Step 9: Real-World Impact (14:30-15:00)

- "Critical bugs hide in edge cases"
- "Symbolic execution is exhaustive"
- "This caught a CVE in production code"

## Expected Outputs

- Path coverage report: 47/47 paths explored
- Generated test suite: 12 edge case tests
- SMT constraint solving output

## Key Talking Points

- "Fuzzing finds shallow bugs, symbolic execution finds deep ones"
- "Z3 solver is NASA-grade verification"
- "Pro tier unlocks unlimited path exploration"
- "High code coverage doesn't guarantee all paths tested"
- "Formal methods catch what humans miss"

## Technical Details

### Symbolic Execution Process

1. **CFG Construction**
   - Build control flow graph from AST
   - Identify all branch points

2. **Path Exploration**
   - Traverse each possible path
   - Collect constraints at branches
   - Example: `if x > 0` adds constraint `x > 0` or `x <= 0`

3. **Constraint Solving**
   - Use Z3 SMT solver
   - Find concrete values satisfying each path
   - Example: For path requiring `min_length < 0`, Z3 suggests `-5`

4. **Test Generation**
   - Create executable test case for each path
   - Include assertions for expected behavior

### Comparison: Testing Approaches

| Method | Coverage Type | Edge Cases | Time | Guarantees |
|--------|---------------|------------|------|------------|
| Manual Testing | Example-based | Few | Hours | None |
| Fuzzing | Input space sampling | Random | Minutes | Probabilistic |
| Code Coverage | Line/branch | Missed paths | Seconds | False security |
| **Symbolic Execution** | **Path-complete** | **All paths** | **Seconds** | **Formal proof** |

## Real-World Bug Example

This technique found CVE-2023-XXXXX in popular library:
- Function: `parse_jwt_token(token, verify=True)`
- Bug: If `verify` is `None` (not False), verification skipped
- Standard tests: All used `verify=True` or `verify=False`
- Symbolic execution: Found `verify=None` path
- Impact: Authentication bypass in 15,000+ applications
