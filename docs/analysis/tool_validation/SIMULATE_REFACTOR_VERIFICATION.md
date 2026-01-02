# Verification: simulate_refactor

## 1. Tool Description
Simulate applying a code change and check for safety issues.

## 2. Tier Verification

### Community Tier: "Returns a diff of what *would* happen if the AI applies a change"
- **Status:** ✅ **VERIFIED**
- **Evidence:**
  - `src/code_scalpel/generators/refactor_simulator.py` implements `simulate` which applies the patch and returns `patched_code`.
  - `src/code_scalpel/mcp/server.py` calculates `structural_changes` (added/removed/modified functions) by comparing ASTs of original and new code.
  - This effectively provides a semantic diff of the changes.

### Pro Tier: "Build Check – Verifies if the refactored code is syntactically valid and compiles"
- **Status:** ⚠️ **PARTIAL**
- **Evidence:**
  - `src/code_scalpel/mcp/server.py` calls `_validate_code` which performs a syntax check (`ast.parse`).
  - However, it does **not** perform a full "Build Check" (e.g., type checking, dependency resolution, or compilation for compiled languages).
  - `refactor_simulator.py` lists "type safety verification" as a TODO (#29).

### Enterprise Tier: "Regression Prediction – Uses AI+Graph to predict which existing features might break"
- **Status:** ❌ **MISSING**
- **Evidence:**
  - No AI or Graph-based regression prediction logic exists.
  - `refactor_simulator.py` lists "performance impact prediction (ML)" (#37) and "refactor risk scoring (ML)" (#65) as TODOs.
  - The "Regression Prediction" feature described is currently vaporware.

## 3. Conclusion
The tool is a "Safety Simulator" with basic diffing capabilities.
- Community features are implemented.
- Pro features are limited to syntax checking (no full build).
- Enterprise features (AI Regression Prediction) are completely missing.
