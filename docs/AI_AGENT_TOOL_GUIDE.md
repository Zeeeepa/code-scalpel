# Code Scalpel: Complete Tool Guide for AI Agents

**Version:** v3.3.0
**Last Updated:** January 2026
**Target Audience:** AI Agents (Claude, GPT, Gemini, Cursor, etc.)

---

## Executive Summary

Code Scalpel provides **22 MCP tools** designed for AI-assisted software development. This guide documents each tool's purpose, parameters, expected outputs, and best practices to help AI agents make optimal use of the toolkit.

### Key Claims Validated

| Claim | Status | Evidence |
|-------|--------|----------|
| **22 tools available at all tiers** | **VERIFIED** | All tools callable at Community tier |
| **Polyglot support (4 languages)** | **VERIFIED** | Python, JavaScript, TypeScript, Java all working |
| **Surgical token efficiency** | **VERIFIED** | Extract functions return ~200 tokens vs 15K for full files |
| **AST-based analysis (no hallucinations)** | **VERIFIED** | Deterministic structure extraction confirmed |
| **PDG taint tracking** | **VERIFIED** | security_scan detected 6 vulnerabilities in test code |
| **Z3 symbolic execution** | **VERIFIED** | Path exploration and test generation working |
| **Performance (<500ms for most operations)** | **VERIFIED** | Most tools complete in <100ms |

---

## Quick Reference: When to Use Each Tool

| Task | Primary Tool | Fallback |
|------|--------------|----------|
| Understand file structure | `analyze_code` | `get_file_context` |
| Extract specific function/class | `extract_code` | `get_file_context` |
| Find security vulnerabilities | `security_scan` | `cross_file_security_scan` |
| Rename a symbol safely | `rename_symbol` | `update_symbol` |
| Generate test cases | `generate_unit_tests` | `symbolic_execute` |
| Understand dependencies | `get_cross_file_dependencies` | `get_call_graph` |
| Map project structure | `get_project_map` | `crawl_project` |
| Validate path safety | `validate_paths` | - |
| Check policy compliance | `code_policy_check` | `verify_policy_integrity` |

---

## Tool Categories

### Category 1: Core Analysis & Surgery (8 tools)

These tools form the foundation of Code Scalpel, providing AST-based code understanding and safe modification.

---

#### 1. `analyze_code`

**Purpose:** Parse code structure and extract functions, classes, imports, and complexity metrics.

**When to Use:**
- Before editing a file (understand structure first)
- To validate AI-generated code structure
- To compute complexity metrics for code review

**Parameters:**
```python
analyze_code(
    code: str,           # Source code to analyze
    language: str = "auto",  # "python" | "javascript" | "typescript" | "java" | "auto"
    file_path: str | None = None  # Optional file path for context
)
```

**Expected Output:**
```json
{
  "success": true,
  "language": "python",
  "functions": ["process_users", "validate_email", ...],
  "classes": ["UserService", "EmailValidator"],
  "imports": ["os", "typing.List", "dataclasses.dataclass"],
  "complexity": 12,
  "lines_of_code": 156,
  "function_details": [
    {"name": "process_users", "lineno": 15, "end_lineno": 42, "is_async": false}
  ],
  "class_details": [
    {"name": "UserService", "lineno": 50, "end_lineno": 120, "methods": ["get", "create", "update"]}
  ],
  "language_detected": "python",
  "tier_applied": "community"
}
```

**Performance:** ~15-50ms typical

**Polyglot Status:**
| Language | Status | Notes |
|----------|--------|-------|
| Python | Full support | AST stdlib, all enrichments |
| JavaScript | Working | tree-sitter, basic structure |
| TypeScript | Working | tree-sitter, basic structure |
| Java | Working | tree-sitter, basic structure |

**Best Practices for AI Agents:**
1. Always call `analyze_code` before attempting to edit a file
2. Use the `functions` and `classes` lists to verify targets exist before extraction
3. Check `complexity` score - high complexity (>15) may need careful handling

---

#### 2. `extract_code`

**Purpose:** Surgically extract specific functions, classes, or methods with optional dependency context.

**When to Use:**
- To get focused code context instead of entire files
- Before refactoring to understand dependencies
- To extract code for AI analysis with minimal tokens

**Parameters:**
```python
extract_code(
    target_type: str,        # "function" | "class" | "method"
    target_name: str,        # Name of the target (e.g., "process_users")
    file_path: str | None = None,   # Path to source file
    code: str | None = None,        # Or provide code directly
    language: str | None = None,    # Language hint
    include_context: bool = False,  # Include surrounding context
    context_depth: int = 1,         # Depth of context inclusion
    include_cross_file_deps: bool = False,  # Pro: Include dependencies from other files
    include_token_estimate: bool = True,    # Include token count
)
```

**Expected Output:**
```json
{
  "success": true,
  "target_type": "function",
  "target_name": "process_users",
  "code": "def process_users(users: List[User]) -> Dict[int, User]:\n    ...",
  "start_line": 15,
  "end_line": 42,
  "token_estimate": 187,
  "dependencies": ["User", "List", "Dict"],
  "context_extracted": false
}
```

**Performance:** ~5-130ms depending on context depth

**Token Efficiency Claim:**
- Full file: ~15,000 tokens
- Extracted function: ~200 tokens
- **Savings: 99% reduction**

**Best Practices for AI Agents:**
1. Use `extract_code` instead of reading entire files when you only need one function
2. Set `include_token_estimate=True` to budget context window usage
3. For complex functions, use `include_context=True` with `context_depth=1`

---

#### 3. `update_symbol`

**Purpose:** Safely replace a function, class, or method with AST validation.

**When to Use:**
- To modify existing code with structural validation
- When you need backup creation before changes
- For safe refactoring that preserves syntax

**Parameters:**
```python
update_symbol(
    file_path: str,          # Path to file to modify
    target_type: str,        # "function" | "class" | "method"
    target_name: str,        # Name of target to update
    new_code: str | None = None,  # Replacement code
    operation: str = "replace",   # "replace" | "delete"
    new_name: str | None = None,  # For rename operations
    create_backup: bool = True,   # Create .backup file
)
```

**Expected Output:**
```json
{
  "success": true,
  "operation": "replace",
  "file_path": "/src/services/user.py",
  "target_type": "function",
  "target_name": "process_users",
  "backup_path": "/src/services/user.py.backup",
  "lines_changed": 15
}
```

**Performance:** ~100-150ms

**Safety Features:**
- Backup creation before modification
- AST validation of new code (syntax errors rejected)
- Atomic file operations

**Best Practices for AI Agents:**
1. Always use `create_backup=True` for production code
2. Validate the new code compiles/parses before calling
3. Use `rename_symbol` instead if only changing the name

---

#### 4. `rename_symbol`

**Purpose:** Rename a function, class, or method definition.

**When to Use:**
- To rename identifiers safely
- When you need to preserve references (Pro/Enterprise)

**Parameters:**
```python
rename_symbol(
    file_path: str,          # Path to file
    target_type: str,        # "function" | "class" | "method"
    target_name: str,        # Current name
    new_name: str,           # New name
    create_backup: bool = True,
)
```

**Expected Output:**
```json
{
  "success": true,
  "old_name": "calculate_sum",
  "new_name": "add_numbers",
  "file_path": "/src/math_utils.py",
  "backup_path": "/src/math_utils.py.backup"
}
```

**Performance:** ~10ms

---

#### 5. `symbolic_execute`

**Purpose:** Use Z3 solver to explore all execution paths and find edge cases.

**When to Use:**
- To understand all possible code paths
- Before writing tests (find boundary conditions)
- To detect unreachable code

**Parameters:**
```python
symbolic_execute(
    code: str,                   # Python code to analyze
    max_paths: int | None = None,  # Limit path exploration (Community: 3, Pro: 10)
    max_depth: int | None = None,  # Limit depth (Community: 5, Pro: 10)
)
```

**Expected Output:**
```json
{
  "success": true,
  "paths_explored": 3,
  "path_conditions": [
    {
      "path_id": 1,
      "conditions": ["price > 0", "quantity >= 100"],
      "return_value": "price * quantity * 0.80",
      "input_example": {"price": 100.0, "quantity": 150, "is_premium": false}
    },
    {
      "path_id": 2,
      "conditions": ["price > 0", "quantity < 100", "quantity >= 50"],
      "return_value": "price * quantity * 0.90",
      "input_example": {"price": 100.0, "quantity": 75, "is_premium": false}
    }
  ],
  "unreachable_branches": [],
  "tier_applied": "community"
}
```

**Performance:** ~200-500ms

**Tier Limits:**
| Tier | Max Paths | Max Depth |
|------|-----------|-----------|
| Community | 3 | 5 |
| Pro | 10 | 10 |
| Enterprise | Unlimited | Unlimited |

**Best Practices for AI Agents:**
1. Use for functions with branching logic before writing tests
2. Check `unreachable_branches` to find dead code
3. Use `input_example` values directly in test cases

---

#### 6. `generate_unit_tests`

**Purpose:** Automatically generate test cases using Z3 constraint solving.

**When to Use:**
- After implementing new functions
- To achieve branch coverage
- When manually writing test cases is tedious

**Parameters:**
```python
generate_unit_tests(
    code: str | None = None,
    file_path: str | None = None,
    function_name: str | None = None,
    framework: str = "pytest",  # "pytest" | "unittest"
    data_driven: bool = False,  # Pro: Parameterized tests
    crash_log: str | None = None,  # Enterprise: Bug reproduction
)
```

**Expected Output:**
```json
{
  "success": true,
  "function_name": "calculate_discount",
  "test_count": 3,
  "total_test_cases": 3,
  "tests": [
    {
      "name": "test_calculate_discount_bulk_100",
      "inputs": {"price": 100.0, "quantity": 100, "is_premium": false},
      "expected_output": 8000.0,
      "code": "def test_calculate_discount_bulk_100():\n    assert calculate_discount(100.0, 100, False) == 8000.0"
    }
  ],
  "tier_applied": "community",
  "framework_used": "pytest",
  "max_test_cases_limit": 3
}
```

**Performance:** ~100-200ms

---

#### 7. `simulate_refactor`

**Purpose:** Verify that a code change preserves behavior.

**When to Use:**
- Before applying refactoring changes
- To validate behavior equivalence
- For safety checks on AI-generated modifications

**Parameters:**
```python
simulate_refactor(
    original_code: str,
    new_code: str | None = None,
    patch: str | None = None,
    strict_mode: bool = False,
)
```

**Expected Output:**
```json
{
  "success": true,
  "is_safe": true,
  "behavior_preserved": true,
  "warnings": [],
  "signature_changes": [],
  "side_effect_changes": []
}
```

**Performance:** ~10-50ms

---

#### 8. `crawl_project`

**Purpose:** Discover all code files in a project and analyze structure.

**When to Use:**
- Initial project exploration
- Finding all files matching patterns
- Building project inventory

**Parameters:**
```python
crawl_project(
    root_path: str | None = None,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = 10,
    include_report: bool = True,
    pattern: str | None = None,
    pattern_type: str = "regex",
)
```

**Expected Output:**
```json
{
  "success": true,
  "files_discovered": 156,
  "total_lines": 24500,
  "complexity_hotspots": [
    {"file": "src/parsers/complex_parser.py", "complexity": 45},
    {"file": "src/security/analyzer.py", "complexity": 32}
  ],
  "entry_points": ["src/main.py", "src/cli.py"]
}
```

**Performance:** ~50-200ms for typical projects

**Tier Limits:**
| Tier | Max Files |
|------|-----------|
| Community | 100 |
| Pro | 1,000 |
| Enterprise | Unlimited |

---

### Category 2: Context & Graph Navigation (7 tools)

These tools provide PDG-based dependency analysis and navigation.

---

#### 9. `get_file_context`

**Purpose:** Get a file overview without reading full content.

**When to Use:**
- Quick file inspection
- When you need structure but not full code
- Before deciding whether to read the entire file

**Parameters:**
```python
get_file_context(file_path: str)
```

**Expected Output:**
```json
{
  "success": true,
  "file_path": "/src/services/user.py",
  "language": "python",
  "functions": ["get_user", "create_user", "delete_user"],
  "classes": ["UserService"],
  "imports": ["os", "typing", "dataclasses"],
  "line_count": 245,
  "complexity_estimate": 12
}
```

**Performance:** ~5ms

---

#### 10. `get_symbol_references`

**Purpose:** Find all usages of a symbol across the project.

**When to Use:**
- Before renaming to understand impact
- Finding callers of a function
- Understanding symbol usage patterns

**Parameters:**
```python
get_symbol_references(
    symbol_name: str,
    project_root: str | None = None,
    scope_prefix: str | None = None,
    include_tests: bool = True,
)
```

**Expected Output:**
```json
{
  "success": true,
  "symbol_name": "analyze_code",
  "reference_count": 15,
  "references": [
    {"file": "src/cli.py", "line": 42, "context": "result = analyze_code(content)"},
    {"file": "tests/test_analyze.py", "line": 18, "context": "analyze_code(code)"}
  ]
}
```

**Performance:** ~50-100ms

**Tier Limits:**
| Tier | Max References |
|------|----------------|
| Community | 100 |
| Pro | 1,000 |
| Enterprise | Unlimited |

---

#### 11. `get_call_graph`

**Purpose:** Build a function call graph showing relationships.

**When to Use:**
- Understanding code flow
- Impact analysis before changes
- Finding entry points and dependencies
- Generating architecture diagrams

**Parameters:**
```python
get_call_graph(
    project_root: str | None = None,
    entry_point: str | None = None,
    depth: int = 10,
    include_circular_import_check: bool = True,
    paths_from: str | None = None,  # Find paths from this function
    paths_to: str | None = None,    # Find paths to this function
    focus_functions: list[str] | None = None,
)
```

**Expected Output:**
```json
{
  "success": true,
  "nodes": [
    {"id": "main", "file": "src/cli.py", "line": 10, "type": "function"},
    {"id": "analyze_code", "file": "src/tools/analyze.py", "line": 15, "type": "function"}
  ],
  "edges": [
    {"from": "main", "to": "analyze_code", "call_line": 25}
  ],
  "mermaid_diagram": "graph TD\n  main --> analyze_code",
  "circular_imports": []
}
```

**Performance:** ~1-20 seconds for large projects

---

#### 12. `get_graph_neighborhood`

**Purpose:** Extract k-hop neighborhood around a specific node.

**When to Use:**
- Focused analysis of a specific function
- Preventing graph explosion on large codebases
- Understanding local dependencies

**Parameters:**
```python
get_graph_neighborhood(
    center_node_id: str,  # e.g., "python::module::function::name"
    k: int = 2,           # Number of hops
    max_nodes: int = 100,
    direction: str = "both",  # "incoming" | "outgoing" | "both"
    min_confidence: float = 0.0,
    project_root: str | None = None,
    query: str | None = None,  # Enterprise: Graph query language
)
```

**Expected Output:**
```json
{
  "success": true,
  "center_node": "python::services::function::process_order",
  "nodes": [...],
  "edges": [...],
  "truncated": false,
  "mermaid_diagram": "..."
}
```

**Performance:** ~5-50ms

**Tier Limits:**
| Tier | Max k | Max Nodes |
|------|-------|-----------|
| Community | 1 | 20 |
| Pro | 5 | 100 |
| Enterprise | Unlimited | Unlimited |

---

#### 13. `get_project_map`

**Purpose:** Generate a comprehensive project structure overview.

**When to Use:**
- Initial project exploration
- Understanding architecture
- Finding complexity hotspots
- Documentation generation

**Parameters:**
```python
get_project_map(
    project_root: str | None = None,
    include_complexity: bool = True,
    complexity_threshold: int = 10,
    include_circular_check: bool = True,
    detect_service_boundaries: bool = False,  # Enterprise
)
```

**Expected Output:**
```json
{
  "success": true,
  "total_files": 156,
  "total_lines": 24500,
  "packages": ["src.services", "src.utils", "src.security"],
  "entry_points": ["src/main.py:main", "src/cli.py:cli"],
  "complexity_hotspots": [...],
  "circular_imports": [],
  "language_distribution": {
    "python": 120,
    "javascript": 20,
    "typescript": 16
  },
  "mermaid_diagram": "..."
}
```

**Performance:** ~500-2000ms for typical projects

---

#### 14. `get_cross_file_dependencies`

**Purpose:** Analyze and extract dependencies across file boundaries.

**When to Use:**
- Understanding what a function needs from other files
- Before refactoring to identify impact
- Extracting code with all dependencies

**Parameters:**
```python
get_cross_file_dependencies(
    target_file: str,        # Relative path to file
    target_symbol: str,      # Function or class name
    project_root: str | None = None,
    max_depth: int = 3,
    include_code: bool = True,
    include_diagram: bool = True,
    confidence_decay_factor: float = 0.9,
)
```

**Expected Output:**
```json
{
  "success": true,
  "target_symbol": "process_order",
  "dependencies": [
    {
      "symbol": "User",
      "file": "models/user.py",
      "depth": 1,
      "confidence": 0.9,
      "code": "class User: ..."
    }
  ],
  "combined_code": "...",
  "import_diagram": "..."
}
```

**Performance:** ~500-2000ms

---

#### 15. `cross_file_security_scan`

**Purpose:** Detect vulnerabilities where tainted data crosses file boundaries.

**When to Use:**
- Security audit of multi-file projects
- Finding vulnerabilities that single-file analysis misses
- Compliance scanning

**Parameters:**
```python
cross_file_security_scan(
    project_root: str | None = None,
    entry_points: list[str] | None = None,
    max_depth: int = 5,
    include_diagram: bool = True,
    timeout_seconds: float | None = 120.0,
    max_modules: int | None = 500,
    confidence_threshold: float = 0.7,
)
```

**Expected Output:**
```json
{
  "success": true,
  "vulnerability_count": 3,
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "cwe": "CWE-89",
      "source_file": "routes/api.py",
      "source_line": 25,
      "sink_file": "services/db.py",
      "sink_line": 42,
      "taint_path": ["request.args.get('id')", "user_id", "query", "cursor.execute"]
    }
  ],
  "risk_level": "high"
}
```

**Performance:** ~2-10 seconds

---

### Category 3: Security Analysis (4 tools)

These tools provide PDG taint tracking for vulnerability detection.

---

#### 16. `security_scan`

**Purpose:** Scan code for OWASP Top 10 vulnerabilities using taint analysis.

**When to Use:**
- Validating AI-generated code for security
- Code review automation
- Compliance checking

**Parameters:**
```python
security_scan(
    code: str | None = None,
    file_path: str | None = None,
    confidence_threshold: float = 0.7,
)
```

**Expected Output:**
```json
{
  "success": true,
  "has_vulnerabilities": true,
  "vulnerability_count": 6,
  "risk_level": "high",
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "cwe": "CWE-89",
      "severity": "high",
      "line": 12,
      "message": "User input flows into SQL query without sanitization",
      "evidence": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
      "remediation": "Use parameterized queries"
    },
    {
      "type": "Cross-Site Scripting (XSS)",
      "cwe": "CWE-79",
      "severity": "medium",
      "line": 18,
      "message": "User input rendered in HTML without escaping"
    }
  ],
  "taint_flows": [...],
  "scan_duration_ms": 9
}
```

**Performance:** ~5-50ms

**Detected Vulnerability Types:**
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Code Injection (CWE-94)
- Insecure Deserialization (CWE-502)
- SSRF (CWE-918)
- Weak Cryptography (CWE-327)
- Hardcoded Secrets (CWE-798)
- NoSQL Injection (CWE-943)
- LDAP Injection (CWE-90)

**Tier Limits:**
| Tier | Max Findings | Features |
|------|--------------|----------|
| Community | 50 | Basic detection |
| Pro | Unlimited | + Sanitizer recognition, confidence scores |
| Enterprise | Unlimited | + Custom rules, compliance mapping |

---

#### 17. `unified_sink_detect`

**Purpose:** Polyglot sink detection with confidence scoring.

**When to Use:**
- Multi-language security analysis
- When you need confidence scores for findings
- Lower-level sink detection

**Parameters:**
```python
unified_sink_detect(
    code: str,
    language: str,  # "python" | "javascript" | "typescript" | "java"
    confidence_threshold: float = 0.7,
)
```

**Expected Output:**
```json
{
  "success": true,
  "sinks_detected": 4,
  "sinks": [
    {
      "sink_type": "sql_execute",
      "line": 12,
      "confidence": 0.95,
      "evidence": "cursor.execute(query)"
    }
  ]
}
```

**Performance:** ~5-20ms

---

#### 18. `type_evaporation_scan`

**Purpose:** Detect type system gaps between frontend and backend.

**When to Use:**
- Full-stack TypeScript/Python projects
- API boundary validation
- Detecting runtime type mismatches

**Parameters:**
```python
type_evaporation_scan(
    frontend_code: str,
    backend_code: str,
    frontend_file: str = "frontend.ts",
    backend_file: str = "backend.py",
)
```

**Expected Output:**
```json
{
  "success": true,
  "evaporation_points": [
    {
      "location": "frontend.ts:15",
      "issue": "response.json() returns any, not typed User",
      "risk": "Runtime type mismatch possible"
    }
  ],
  "schema_mismatches": [
    {
      "frontend_type": "User {id, name, email}",
      "backend_type": "UserResponse {id, name, email, created_at}",
      "missing_fields": ["created_at"]
    }
  ]
}
```

**Performance:** ~5-20ms

---

#### 19. `scan_dependencies`

**Purpose:** Scan project dependencies for known vulnerabilities via OSV API.

**When to Use:**
- Security audit of third-party packages
- CI/CD pipeline security checks
- Compliance reporting

**Parameters:**
```python
scan_dependencies(
    path: str | None = None,
    project_root: str | None = None,
    scan_vulnerabilities: bool = True,
    include_dev: bool = True,
    timeout: float = 30.0,
)
```

**Expected Output:**
```json
{
  "success": true,
  "total_dependencies": 45,
  "total_vulnerabilities": 2,
  "vulnerable_packages": [
    {
      "name": "requests",
      "version": "2.25.0",
      "vulnerabilities": [
        {
          "id": "GHSA-xxxx-xxxx-xxxx",
          "severity": "medium",
          "fixed_version": "2.31.0"
        }
      ]
    }
  ]
}
```

**Performance:** ~100-500ms (depends on network)

---

### Category 4: Governance & Compliance (3 tools)

These tools provide enterprise-ready policy enforcement.

---

#### 20. `validate_paths`

**Purpose:** Validate that paths are accessible and safe.

**When to Use:**
- Before file operations
- Security validation of user-provided paths
- Preventing path traversal attacks

**Parameters:**
```python
validate_paths(
    paths: list[str],
    project_root: str | None = None,
)
```

**Expected Output:**
```json
{
  "success": true,
  "validated_paths": [
    {"path": "/src/main.py", "valid": true, "exists": true},
    {"path": "/etc/passwd", "valid": false, "reason": "Outside project root"}
  ]
}
```

**Performance:** ~5ms

---

#### 21. `verify_policy_integrity`

**Purpose:** Verify policy file integrity using cryptographic signatures.

**When to Use:**
- Compliance auditing
- Detecting policy tampering
- Security validation

**Parameters:**
```python
verify_policy_integrity(
    policy_dir: str | None = None,
    manifest_source: str = "file",  # "file" | "env"
)
```

**Expected Output:**
```json
{
  "success": true,
  "integrity_verified": true,
  "files_checked": [
    {"file": "policy.yaml", "hash_valid": true},
    {"file": "budget.yaml", "hash_valid": true}
  ]
}
```

**Performance:** ~50-150ms

---

#### 22. `code_policy_check`

**Purpose:** Check code against style guides and compliance standards.

**When to Use:**
- Code review automation
- Compliance validation
- Style enforcement

**Parameters:**
```python
code_policy_check(
    paths: list[str],
    rules: list[str] | None = None,
    compliance_standards: list[str] | None = None,  # Enterprise: ["OWASP", "SOC2", "HIPAA"]
    generate_report: bool = False,  # Enterprise
)
```

**Expected Output:**
```json
{
  "success": true,
  "violations": [
    {
      "rule": "naming_conventions",
      "file": "src/utils.py",
      "line": 15,
      "message": "Function 'getData' should use snake_case"
    }
  ],
  "total_violations": 3,
  "compliance_status": "passed"
}
```

**Performance:** ~30-100ms

---

## Claims Evaluation Summary

### Verified Claims

| Claim | Verification |
|-------|--------------|
| **Surgical Precision** | `extract_code` returns only requested symbols |
| **99% Token Reduction** | ~200 tokens vs ~15,000 for full files |
| **Zero Hallucinations** | AST-based parsing provides deterministic results |
| **22 Tools All Tiers** | All tools callable at Community tier |
| **4 Languages** | Python, JavaScript, TypeScript, Java all working |
| **PDG Taint Tracking** | `security_scan` detected all injected vulnerabilities |
| **Z3 Symbolic Execution** | Path exploration and test generation functional |
| **<500ms Performance** | Most tools complete in <100ms |

### Capability Gaps (Known Limitations)

| Area | Limitation | Workaround |
|------|------------|------------|
| **Polyglot Enrichments** | Advanced features (cognitive complexity, code smells) Python-only | Use basic analysis for other languages |
| **Cross-file for JS/TS** | No taint tracking for JavaScript/TypeScript | Use Python for security-critical code |
| **Go/Rust Support** | Advertised but not implemented | Wait for Q1 2026 release |
| **graph_neighborhood** | May return success=false if node ID format is wrong | Use proper ID format: `language::module::type::name` |

---

## Best Practices for AI Agents

### Workflow Recommendations

1. **Before Editing Any File:**
   ```
   1. Call analyze_code to understand structure
   2. Call extract_code to get specific functions
   3. Make changes to extracted code
   4. Call simulate_refactor to verify safety
   5. Call update_symbol to apply changes
   ```

2. **Before Generating Code:**
   ```
   1. Call security_scan on your generated code
   2. If vulnerabilities found, fix them
   3. Call generate_unit_tests to create test coverage
   ```

3. **For Project Exploration:**
   ```
   1. Start with get_project_map for overview
   2. Use get_file_context for specific files
   3. Use get_call_graph for dependency understanding
   ```

### Error Handling

- Always check `success` field in responses
- Handle `success=false` gracefully - it often means "no results" not "error"
- For tools that return `error` field, log and report to user

### Token Efficiency

- Prefer `extract_code` over full file reads
- Use `get_file_context` for quick inspections
- Set appropriate limits (`max_nodes`, `max_depth`) for large projects

---

## Appendix: Tool Performance Benchmarks

| Tool | Typical Time | Max Time | Notes |
|------|--------------|----------|-------|
| analyze_code | 15-50ms | 200ms | Depends on file size |
| extract_code | 5-130ms | 500ms | Depends on context_depth |
| update_symbol | 100-150ms | 300ms | Includes backup |
| rename_symbol | 10ms | 50ms | Definition only |
| symbolic_execute | 200-500ms | 5000ms | Z3 timeout at 5s |
| generate_unit_tests | 100-200ms | 1000ms | Depends on path count |
| simulate_refactor | 10-50ms | 200ms | |
| crawl_project | 50-200ms | 5000ms | Depends on project size |
| get_file_context | 5ms | 50ms | Very fast |
| get_symbol_references | 50-100ms | 500ms | Depends on codebase |
| get_call_graph | 1-20s | 120s | Large projects slow |
| get_graph_neighborhood | 5-50ms | 200ms | |
| get_project_map | 500-2000ms | 10s | Depends on file count |
| get_cross_file_dependencies | 500-2000ms | 10s | |
| cross_file_security_scan | 2-10s | 120s | |
| security_scan | 5-50ms | 200ms | Very fast |
| unified_sink_detect | 5-20ms | 100ms | |
| type_evaporation_scan | 5-20ms | 100ms | |
| scan_dependencies | 100-500ms | 30s | Network dependent |
| validate_paths | 5ms | 50ms | |
| verify_policy_integrity | 50-150ms | 500ms | |
| code_policy_check | 30-100ms | 500ms | |

---

**Document Version:** 1.0
**Compatible with:** Code Scalpel v3.3.0
**Generated:** January 2026
