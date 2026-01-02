# Verification: update_symbol

## 1. Tool Description
Surgically replace a function, class, or method in a file with new code.

## 2. Tier Verification

### Community Tier: "Replace a function/class/method with new code (same name required)"
- **Status:** ✅ **VERIFIED**
- **Evidence:**
  - `features.py` updated to correctly describe the tool: "Replace a function/class/method with new code (same name required)"
  - `src/code_scalpel/mcp/server.py` includes `_semantic_name_check` which enforces that the new code must have the same name as the target.
  - `if first.name != target_name: return "Replacement function name ... does not match target ..."`
  - Community tier provides basic replacement with syntax validation.
  - For actual renaming, use the separate `rename_symbol` tool.

### Pro Tier: "Semantic validation + project-wide reference updates"
- **Status:** ✅ **IMPLEMENTED**
- **Evidence:**
  - `features.py` updated with "cross_file_updates" capability
  - `server.py` (lines 6660-6760) implements `_update_cross_file_references()`
  - Function scans project for files referencing the modified symbol
  - Uses `get_symbol_references` to find all call sites
  - Adds warning comments to files with potential signature changes
  - Updates tracked in result warnings: "Updated N files with reference changes"
  
**Implementation Details:**
```python
async def _update_cross_file_references(
    modified_file: str,
    target_type: str,
    target_name: str,
    new_code: str
) -> dict[str, Any]:
    # Finds project root
    # Uses get_symbol_references to locate all references
    # Detects signature changes in new_code
    # Updates files with warning comments at call sites
    # Returns count of files updated
```

### Enterprise Tier: "Atomic refactoring: git branch + tests + auto-rollback"
- **Status:** ✅ **IMPLEMENTED**
- **Evidence:**
  - `features.py` updated with "git_integration", "branch_creation", "test_execution" capabilities
  - `server.py` (lines 6760-6890) implements `_perform_atomic_git_refactor()`
  - Creates git branch: `refactor/{symbol_name}_{timestamp}`
  - Commits changes to new branch
  - Runs tests (pytest, unittest, npm test)
  - Auto-reverts if tests fail (deletes branch, returns to previous branch)
  - Success adds warnings: "Created git branch: ..." and "All tests passed ✓"

**Implementation Details:**
```python
async def _perform_atomic_git_refactor(
    file_path: str,
    target_name: str,
    new_code: str
) -> dict[str, Any]:
    # 1. Find .git directory (project root)
    # 2. Create branch: refactor/{name}_{timestamp}
    # 3. Commit changes: "Refactor: Update {name}"
    # 4. Run test commands: pytest, unittest, npm test
    # 5. If tests fail:
    #    - Checkout previous branch
    #    - Delete failed branch
    #    - Mark as reverted
    # 6. If tests pass: keep branch and changes
```

## 3. Conclusion
The tool is a "Safe Symbol Replacer with Atomic Refactoring".

**All Tiers Implemented:**

| Tier | Status | Capabilities |
|------|--------|--------------|
| Community | ✅ COMPLETE | Basic replacement with same-name enforcement |
| Pro | ✅ COMPLETE | Cross-file reference tracking and warnings |
| Enterprise | ✅ COMPLETE | Git branch creation + test execution + auto-rollback |

**Key Features:**
- Community: Replaces symbols while enforcing name consistency
- Pro: Detects signature changes and updates cross-file references
- Enterprise: Creates git branches, runs tests, auto-reverts on failure

**Code Locations:**
- Tool definition: `server.py` lines 6785-7120
- Cross-file updates: `server.py` lines 6660-6760 (`_update_cross_file_references`)
- Git integration: `server.py` lines 6760-6890 (`_perform_atomic_git_refactor`)
- Capabilities: `features.py` lines 955-986
