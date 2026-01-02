# rename_symbol Tool Roadmap

**Tool Name:** `rename_symbol`  
**Tool Version:** v1.0  
**Code Scalpel Version:** v3.3.0  
**Current Status:** Stable  
**Primary Module:** `src/code_scalpel/ast_tools/transformer.py`  
**Tier Availability:** All tiers (Community, Pro, Enterprise)

---

## Configuration Files

| File | Purpose |
|------|---------|
| `src/code_scalpel/licensing/features.py` | Tier capability definitions |
| `.code-scalpel/limits.toml` | Numeric limits (file scope) |
| `.code-scalpel/response_config.json` | Output filtering |

---

## Overview

The `rename_symbol` tool safely renames functions, classes, or methods in a file while ensuring consistent changes throughout the codebase.

**Why AI Agents Need This:**
- **Safe refactoring:** Automated reference updates prevent broken code
- **Consistency:** All occurrences renamed atomically
- **Auditability:** Enterprise tier tracks all renames for compliance
- **Reduced errors:** Syntax validation prevents invalid renames
- **Batch operations:** Pro tier enables bulk refactoring workflows

---

## Research Queries for Future Development

### Foundational Research
| Topic | Query | Purpose |
|-------|-------|---------|
| AST Transformation | "AST-preserving code transformation techniques" | Maintain formatting |
| Rename Semantics | "identifier renaming semantic correctness verification" | Ensure correctness |
| Breaking Changes | "breaking change detection automated refactoring" | Prevent regressions |
| Undo/Redo | "transactional code modifications rollback strategies" | Better recovery |

### Language-Specific Research
| Topic | Query | Purpose |
|-------|-------|---------|
| Python Scoping | "python nonlocal global variable renaming challenges" | Better scope handling |
| JavaScript | "javascript variable hoisting rename complications" | Improve JS support |
| TypeScript | "typescript type alias renaming declaration files" | TS module support |
| Java | "java refactoring reflection-safe renaming" | Reflection handling |

### Advanced Techniques
| Topic | Query | Purpose |
|-------|-------|---------|
| AI-Suggested Names | "machine learning variable naming suggestions code" | Smart name hints |
| Test Impact | "test case selection after refactoring" | Validate renames |
| Documentation Sync | "automated documentation update code changes" | Doc consistency |
| Cross-Repository | "cross-repository refactoring coordination" | Multi-repo renames |

---

## Current Capabilities (v1.0)

### Community Tier
- ✅ Rename functions by name
- ✅ Rename classes by name
- ✅ Rename methods in classes
- ✅ Automatic reference updates in same file
- ✅ Syntax validation
- ✅ Supports Python, JavaScript, TypeScript
- ⚠️ **Limits:** Single file only

### Pro Tier
- ✅ All Community features
- ✅ Cross-file rename propagation
- ✅ Import statement updates
- ✅ Documentation string updates
- ✅ Test file synchronization
- ✅ Backup and rollback support

### Enterprise Tier
- ✅ All Pro features
- ✅ Repository-wide renames
- ✅ Multi-repository coordination
- ✅ Approval workflow integration
- ✅ Compliance-checked renames
- ✅ Audit trail for all renames

---

## Return Model: RenameResult

```python
class RenameResult(BaseModel):
    # Core fields (All Tiers)
    success: bool                           # Whether rename succeeded
    old_name: str                           # Original symbol name
    new_name: str                           # New symbol name
    file_path: str                          # File that was modified
    changes_made: int                       # Number of occurrences renamed
    backup_path: str | None                 # Path to backup file
    
    # Pro Tier
    files_updated: list[str]                # Cross-file renames
    imports_updated: int                    # Import statements changed
    docstrings_updated: int                 # Documentation strings changed
    tests_updated: list[str]                # Test files modified
    
    # Enterprise Tier
    approval_required: bool                 # Whether approval workflow triggered
    approval_status: str | None             # "pending" | "approved" | "rejected"
    compliance_check: ComplianceResult      # Compliance validation result
    audit_id: str | None                    # Audit trail identifier
    
    error: str | None                       # Error message if failed
```

---

## Usage Examples

### Community Tier
```python
result = await rename_symbol(
    file_path="/src/utils.py",
    old_name="process_data",
    new_name="transform_data"
)
# Returns: success, old_name, new_name, changes_made, backup_path
# Single file only
```

### Pro Tier
```python
result = await rename_symbol(
    file_path="/src/utils.py",
    old_name="process_data",
    new_name="transform_data",
    include_imports=True,
    include_tests=True
)
# Additional: files_updated, imports_updated, docstrings_updated, tests_updated
# Cross-file rename propagation
```

### Enterprise Tier
```python
result = await rename_symbol(
    file_path="/src/utils.py",
    old_name="process_data",
    new_name="transform_data",
    require_approval=True,
    compliance_check=True
)
# Additional: approval_required, approval_status, compliance_check, audit_id
# Repository-wide with governance
```

---

## MCP Request/Response Examples

### MCP Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp_code-scalpel_rename_symbol",
    "arguments": {
      "file_path": "/home/user/project/src/utils.py",
      "old_name": "process_data",
      "new_name": "transform_data"
    }
  },
  "id": 1
}
```

### Community Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "old_name": "process_data",
    "new_name": "transform_data",
    "file_path": "/home/user/project/src/utils.py",
    "changes_made": 4,
    "backup_path": "/home/user/project/src/utils.py.bak",
    "files_updated": null,
    "imports_updated": null,
    "docstrings_updated": null,
    "tests_updated": null,
    "approval_required": null,
    "approval_status": null,
    "compliance_check": null,
    "audit_id": null,
    "error": null
  },
  "id": 1
}
```

### Pro Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "old_name": "process_data",
    "new_name": "transform_data",
    "file_path": "/home/user/project/src/utils.py",
    "changes_made": 12,
    "backup_path": "/home/user/project/.code-scalpel/backups/rename_20251229_143022/",
    "files_updated": [
      "/home/user/project/src/utils.py",
      "/home/user/project/src/handlers.py",
      "/home/user/project/src/api/routes.py",
      "/home/user/project/tests/test_utils.py"
    ],
    "imports_updated": 3,
    "docstrings_updated": 2,
    "tests_updated": [
      "/home/user/project/tests/test_utils.py",
      "/home/user/project/tests/test_handlers.py"
    ],
    "approval_required": null,
    "approval_status": null,
    "compliance_check": null,
    "audit_id": null,
    "error": null
  },
  "id": 1
}
```

### Enterprise Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "old_name": "process_data",
    "new_name": "transform_data",
    "file_path": "/home/user/project/src/utils.py",
    "changes_made": 28,
    "backup_path": "/home/user/project/.code-scalpel/backups/rename_20251229_143022/",
    "files_updated": [
      "/home/user/project/src/utils.py",
      "/home/user/project/src/handlers.py",
      "/home/user/project/src/api/routes.py",
      "/home/user/project/tests/test_utils.py",
      "/home/user/shared-lib/src/compat.py"
    ],
    "imports_updated": 8,
    "docstrings_updated": 5,
    "tests_updated": [
      "/home/user/project/tests/test_utils.py",
      "/home/user/project/tests/test_handlers.py",
      "/home/user/project/tests/integration/test_api.py"
    ],
    "approval_required": true,
    "approval_status": "approved",
    "compliance_check": {
      "passed": true,
      "rules_checked": ["naming-convention", "breaking-change-review"],
      "warnings": [],
      "violations": []
    },
    "audit_id": "audit-rename-20251229-143022-abc123",
    "error": null
  },
  "id": 1
}
```

### Enterprise Tier Response (Approval Pending)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": false,
    "old_name": "process_data",
    "new_name": "transform_data",
    "file_path": "/home/user/project/src/utils.py",
    "changes_made": 0,
    "backup_path": null,
    "files_updated": [],
    "imports_updated": 0,
    "docstrings_updated": 0,
    "tests_updated": [],
    "approval_required": true,
    "approval_status": "pending",
    "compliance_check": {
      "passed": false,
      "rules_checked": ["naming-convention", "breaking-change-review"],
      "warnings": ["Symbol is part of public API"],
      "violations": ["Breaking change requires team lead approval"]
    },
    "audit_id": "audit-rename-20251229-143025-def456",
    "error": "Approval required: Breaking change to public API symbol"
  },
  "id": 1
}
```

---

## Integration Points

### Related Tools
| Tool | Relationship |
|------|--------------|
| `get_symbol_references` | Find all references before rename |
| `update_symbol` | Code body changes (rename is name-only) |
| `simulate_refactor` | Preview rename impact |
| `get_call_graph` | Understand callers before rename |

### Export Formats
| Format | Status | Use Case |
|--------|--------|----------|
| **Diff** | ✅ v1.0 | Preview changes |
| **JSON** | ✅ v1.0 | Programmatic results |
| **Patch** | 🔄 v1.1 | Git-compatible patches |

---

## Competitive Analysis

| Tool | Strengths | Weaknesses | Our Differentiation |
|------|-----------|------------|---------------------|
| **IDE Rename** | Fast, integrated | Single IDE | Cross-tool, MCP-native |
| **rope (Python)** | Mature, accurate | Python-only | Multi-language support |
| **jscodeshift** | JS ecosystem | JS/TS only | Unified API |
| **Sourcery** | AI-powered | Limited scope | Broader refactoring |
| **LSP Rename** | Standard | Implementation varies | Consistent behavior |

---

## Roadmap

### v1.1 (Q1 2026): Enhanced Safety & Same-File References

#### Community Tier
- [ ] Same-file reference updates (local variable/call site renames)
- [ ] Preview mode (show changes before applying)
- [ ] Dry-run option (return diff without modifying)
- [ ] Conflict detection (shadowing, name collisions)

#### Pro Tier
- [ ] Documentation string updates (references in docstrings)
- [ ] Type hint updates (forward references)
- [ ] Automated test execution after rename
- [ ] Breaking change detection

#### Enterprise Tier
- [ ] Multi-stage approval workflow
- [ ] Automated rollback on test failure
- [ ] Risk scoring for renames
- [ ] Audit trail logging

### v1.2 (Q2 2026): Language Expansion

#### All Tiers
- [ ] JavaScript rename support
- [ ] TypeScript rename support

#### Pro Tier
- [ ] Java rename support
- [ ] Go rename support

#### Enterprise Tier
- [ ] Multi-language coordinated renames
- [ ] Organization-wide rename scope
- [ ] Multi-repository coordination

### v1.3 (Q3 2026): Advanced Features

#### Pro Tier
- [ ] Smart rename suggestions
- [ ] Pattern-based bulk renames
- [ ] Configuration file updates

#### Enterprise Tier
- [ ] Database schema renames
- [ ] Infrastructure-as-code updates
- [ ] Documentation portal sync

### v1.4 (Q4 2026): Integration & Automation

#### Community Tier
- [ ] IDE integration
- [ ] Git commit automation
- [ ] Pre-commit hook support

#### Pro Tier
- [ ] Continuous rename monitoring
- [ ] Automated PR creation
- [ ] Slack/Teams notifications

#### Enterprise Tier
- [ ] ServiceNow change management
- [ ] CMDB synchronization
- [ ] Compliance gate enforcement

---

## Known Issues & Limitations

### Current Limitations
- **Dynamic references:** Cannot update string-based references
- **External usage:** Cannot update external package references
- **Complex generics:** Some complex type parameters may need manual update

### Planned Fixes
- v1.1: String literal analysis (opt-in)
- v1.2: External package scanning (Enterprise)
- v1.3: Better generic handling

---

## Success Metrics

### Performance Targets
- **Rename time:** <1s for single file
- **Accuracy:** >99% correct reference updates
- **Success rate:** >98% successful renames

### Adoption Metrics
- **Usage:** 50K+ renames per month by Q4 2026
- **Time saved:** Average 30 minutes per rename vs manual

---

## Dependencies

### Internal Dependencies
- `ast_tools/transformer.py` - AST transformation
- `ast_tools/validator.py` - Validation
- `ast_tools/call_graph.py` - Reference finding

### External Dependencies
- None

---

## Breaking Changes

None planned for v1.x series.

**API Stability Promise:**
- Tool signature stable
- Backup behavior guaranteed
- Validation always performed

---

**Last Updated:** December 30, 2025  
**Next Review:** March 31, 2026
