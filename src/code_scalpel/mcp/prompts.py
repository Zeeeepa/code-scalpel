"""
Code Scalpel Prompts Module.

Intent-Driven User Experience (refactored 2026-01-16)

Defines user-initiated "Slash Commands" that orchestrate multiple tools for
complex workflows. Users express INTENT (what they want), and the AI decides
which tools to invoke.

Design Philosophy:
- Users type `/audit_security_deep`, NOT `/security_scan`
- Users type `/map_architecture`, NOT `/get_call_graph`
- The AI is the expert on tool selection, not the user

These prompts are displayed in Claude Desktop (and other MCP clients) as
slash commands that users can invoke to trigger sophisticated workflows.
"""

from __future__ import annotations

from importlib import import_module

# Import mcp instance from protocol module
mcp = import_module("code_scalpel.mcp.protocol").mcp


# =============================================================================
# INTENT PROMPT 1: Deep Security Audit
# =============================================================================


@mcp.prompt(title="Deep Security Audit")
def audit_security_deep(path: str) -> str:
    """
    Orchestrates a comprehensive security review.

    Combines static analysis with cross-file taint tracking to find deep
    vulnerabilities that simple scanners miss.

    User Intent: "Don't just scan. Trace the taint flow across files."
    """
    return f"""I need a **deep security audit** of `{path}`.

Please execute the following workflow:

### Step 1: Initial Vulnerability Scan
Run `security_scan` on the file to find immediate vulnerabilities (SQL injection,
XSS, command injection, hardcoded secrets, etc.).

### Step 2: Cross-File Taint Tracking
If any findings are detected, use `cross_file_security_scan` to trace where
tainted data flows across module boundaries. This catches vulnerabilities where
user input in one file reaches a dangerous sink in another.

### Step 3: Framework-Specific Analysis
Use `unified_sink_detect` to verify if any web frameworks (Flask, Django,
FastAPI, Express) are being used insecurely.

### Step 4: Dependency Audit
Run `scan_dependencies` to check if any third-party packages have known CVEs.

### Step 5: Summary Report
Summarize the findings by severity (CRITICAL → HIGH → MEDIUM → LOW) and provide:
- Exact file locations and line numbers
- Risk assessment for each vulnerability
- Concrete remediation code examples

Be thorough. I want to know if this code is safe to deploy."""


# =============================================================================
# INTENT PROMPT 2: Safe Refactor Workflow
# =============================================================================


@mcp.prompt(title="Refactor Safely")
def refactor_safely(file_path: str, symbol_name: str, goal: str) -> str:
    """
    Guides the AI to refactor code safely using extraction and verification tools.

    Prevents "rewrite and break" scenarios by enforcing a disciplined workflow
    that includes impact analysis, testing, and verification.

    User Intent: "Don't just change code. Extract it, test it, verify it."
    """
    return f"""I want to **safely refactor** the symbol `{symbol_name}` in `{file_path}`.

**Goal:** {goal}

Please follow this strict protocol:

### Step 1: Impact Analysis
Use `get_symbol_references` to find ALL places that call or depend on `{symbol_name}`.
This tells us what breaks if we change the signature or behavior.

### Step 2: Understand Dependencies
Use `get_cross_file_dependencies` to see what `{symbol_name}` imports and uses.
We need to understand the full context before making changes.

### Step 3: Extract Current Implementation
Use `extract_code` to isolate the function/class with its dependencies.
This gives us a clean view of what we're working with.

### Step 4: Generate Baseline Tests
Use `generate_unit_tests` to create a test suite for the CURRENT behavior.
These tests become our safety net - they must pass after refactoring.

### Step 5: Simulate the Refactor
Use `simulate_refactor` to apply the changes virtually and check for:
- Behavior changes (function should do the same thing)
- Security regressions (no new vulnerabilities introduced)
- Structural changes (understand what's different)

### Step 6: Propose Final Code
Only after all checks pass, propose the final code update using `update_symbol`.

**DO NOT skip steps.** Each step is a safety gate."""


# =============================================================================
# INTENT PROMPT 3: Modernize Legacy Code
# =============================================================================


@mcp.prompt(title="Modernize Legacy Code")
def modernize_legacy(path: str) -> str:
    """
    Targeted workflow for upgrading old Python/JS codebases.

    Focuses on Type Evaporation, code smells, and technical debt that
    accumulates in legacy systems.

    User Intent: "Fix my technical debt."
    """
    return f"""Help me **modernize the legacy code** at `{path}`.

### Step 1: Type System Analysis
Run `type_evaporation_scan` to find:
- Missing type hints (implicit `Any`)
- Type assertions that evaporate at runtime boundaries
- Places where TypeScript types don't survive JSON serialization

### Step 2: Complexity Analysis
Run `analyze_code` to identify:
- High-complexity functions (Cyclomatic Complexity > 10)
- Deeply nested code (> 4 levels of indentation)
- Large functions (> 50 lines)

### Step 3: Security Debt
Run `security_scan` to find security anti-patterns:
- Hardcoded credentials
- Weak cryptography (MD5, SHA1 for passwords)
- Dangerous patterns (eval, exec, shell=True)

### Step 4: Dependency Health
Run `scan_dependencies` to check for:
- Outdated packages with known CVEs
- Deprecated packages that need replacement
- License conflicts

### Step 5: Modernization Plan
Based on the analysis, propose a prioritized plan:

**P0 - Security (fix immediately):**
- List critical security issues

**P1 - Type Safety (this sprint):**
- Add Pydantic models for API boundaries
- Add type hints to public functions

**P2 - Complexity (next sprint):**
- Refactor high-complexity functions
- Extract helper methods

**P3 - Nice to Have:**
- Code formatting
- Documentation updates

Output concrete code changes for the P0 and P1 items."""


# =============================================================================
# INTENT PROMPT 4: Map Architecture
# =============================================================================


@mcp.prompt(title="Map Architecture")
def map_architecture(module_path: str) -> str:
    """
    Visualizes the dependency graph and identifies architectural patterns.

    Great for onboarding, understanding spaghetti code, or preparing for
    large refactoring efforts.

    User Intent: "Show me how this spaghetti connects."
    """
    return f"""I need to **understand the architecture** of `{module_path}`.

### Step 1: Project Overview
Use `crawl_project` to get a high-level view:
- Total lines of code
- Number of modules
- Complexity hotspots

### Step 2: Module Map
Use `get_project_map` to list the core modules and their responsibilities.
Identify the "big players" in the codebase.

### Step 3: Dependency Graph
Use `get_graph_neighborhood` centered on `{module_path}` to visualize:
- What `{module_path}` imports (dependencies)
- What imports `{module_path}` (dependents)
- Transitive dependencies (2-3 hops)

### Step 4: Call Flow
Use `get_call_graph` to understand the execution flow through key functions.
Identify entry points and critical paths.

### Step 5: Architectural Smells
Check for common problems:
- Circular dependencies (A → B → C → A)
- God modules (one module that knows everything)
- Orphan modules (unused code)
- Layer violations (UI calling database directly)

### Output
Generate a **Mermaid diagram** showing:
```mermaid
graph LR
    subgraph Core
        A[module_a]
        B[module_b]
    end
    subgraph Services
        C[service_c]
    end
    A --> B
    B --> C
```

Include a written summary of the architecture and any concerns."""


# =============================================================================
# INTENT PROMPT 5: Verify Supply Chain
# =============================================================================


@mcp.prompt(title="Verify Supply Chain")
def verify_supply_chain(manifest_path: str) -> str:
    """
    Audits third-party dependencies for security and licensing risks.

    Protects against supply chain attacks, typosquatting, and license
    contamination.

    User Intent: "Am I importing malware?"
    """
    return f"""**Audit the software supply chain** defined in `{manifest_path}`.

### Step 1: Vulnerability Scan
Run `scan_dependencies` to check for known CVEs in all packages.
Flag any with CRITICAL or HIGH severity.

### Step 2: Typosquatting Detection
Check for packages with names suspiciously similar to popular packages:
- `requests` vs `request` vs `reqeusts`
- `numpy` vs `numppy`
- `django` vs `djang0`

These are common attack vectors.

### Step 3: License Audit
Identify packages with restrictive licenses:
- **GPL/AGPL**: May require you to open-source your code
- **SSPL**: Server-side restrictions
- **No License**: Legally risky to use

### Step 4: Maintainer Analysis
For critical dependencies, check:
- Is the package actively maintained?
- Last update date
- Number of maintainers (bus factor)

### Step 5: Risk Score
Calculate a **Supply Chain Risk Score** (0-100):
- CVEs found: +20 per HIGH, +40 per CRITICAL
- Typosquatting risk: +30
- Restrictive licenses: +15 per package
- Unmaintained (>1 year): +10 per package

### Output
Provide:
1. Total Risk Score with breakdown
2. List of packages to remove/replace
3. Recommended alternatives for risky packages
4. SBOM (Software Bill of Materials) summary"""


# =============================================================================
# INTENT PROMPT 6: Explain & Document
# =============================================================================


@mcp.prompt(title="Explain & Document")
def explain_and_document(path: str) -> str:
    """
    Standard documentation workflow.

    Analyzes code and generates comprehensive documentation including
    docstrings, README content, and architecture notes.

    User Intent: "Help me understand and document this code."
    """
    return f"""Please **analyze and document** `{path}`.

### Step 1: Structure Analysis
Use `analyze_code` to extract:
- All functions, classes, and methods
- Import dependencies
- Complexity metrics

### Step 2: File Summary
Write a 2-3 sentence summary of the file's responsibility.
What problem does it solve? Where does it fit in the architecture?

### Step 3: Public API Documentation
For each public function/class, generate a docstring that includes:
- Brief description
- Args with types and descriptions
- Returns with type and description
- Raises (if applicable)
- Example usage

### Step 4: Complex Logic Explanation
For any function with complexity > 5:
- Add inline comments explaining the algorithm
- Create a "How it works" section in the docstring

### Step 5: Architecture Notes
If this file is a key module:
- Document its role in the system
- List its main collaborators (what it calls, what calls it)
- Note any important design decisions

### Output
Provide:
1. The generated documentation (docstrings, comments)
2. A README section if this is a package/module
3. Any questions about unclear logic that need human clarification"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "audit_security_deep",
    "refactor_safely",
    "modernize_legacy",
    "map_architecture",
    "verify_supply_chain",
    "explain_and_document",
]


# ==========================================================================
# WORKFLOW PROMPTS - Orchestrated Multi-Tool Workflows
# ==========================================================================


@mcp.prompt(title="Refactor Function")
def refactor_function_prompt(
    file_path: str, function_name: str, refactor_goal: str
) -> str:
    """
    Safe refactoring workflow with validation.

    Added in v2.0.0: Orchestrated refactor workflow.
    """
    return f"""# Safe Refactoring Workflow

## Target
- **File**: `{file_path}`
- **Function**: `{function_name}`
- **Goal**: {refactor_goal}

## Workflow Steps

### Step 1: Extract Current Implementation
First, use `extract_code` to get the current function:
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    include_context=True,
    include_cross_file_deps=True
)
```

### Step 2: Analyze Dependencies
Check what depends on this function using `get_symbol_references`:
```
get_symbol_references(
    symbol_name="{function_name}",
    project_root="<project_root>"
)
```

### Step 3: Create Refactored Version
Based on the goal "{refactor_goal}", create the new implementation.
Ensure it maintains the same function signature if there are external callers.

### Step 4: Validate Safety
Before applying, use `simulate_refactor` to verify the change is safe:
```
simulate_refactor(
    original_code=<extracted_code>,
    new_code=<your_refactored_code>,
    strict_mode=True
)
```

### Step 5: Apply the Change
If simulation passes, use `update_symbol` to apply:
```
update_symbol(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    new_code=<your_refactored_code>,
    create_backup=True
)
```

## Safety Notes
- Always check the simulation result before applying
- A backup file (.bak) will be created
- If anything goes wrong, restore from backup

Please proceed with Step 1 to begin the refactoring process."""


@mcp.prompt(title="Debug Vulnerability")
def debug_vulnerability_prompt(file_path: str, vulnerability_type: str = "any") -> str:
    """
    Security vulnerability investigation and remediation workflow.

    Added in v2.0.0: Security debugging workflow.
    """
    vuln_filter = (
        f"Focus specifically on **{vulnerability_type}** vulnerabilities."
        if vulnerability_type != "any"
        else "Check for all vulnerability types."
    )

    return f"""# Security Vulnerability Investigation

## Target
- **File**: `{file_path}`
- **Focus**: {vuln_filter}

## Investigation Workflow

### Step 1: Initial Security Scan
Run a security scan on the target file:
```
security_scan(file_path="{file_path}")
```

### Step 2: Cross-File Taint Analysis
If vulnerabilities are found, trace the taint flow across files:
```
cross_file_security_scan(
    project_root="<project_root>",
    entry_points=["{file_path}:<function_name>"],
    include_diagram=True
)
```

### Step 3: Understand the Data Flow
For each vulnerability found:
1. Identify the **taint source** (user input, request data, etc.)
2. Trace the flow through function calls
3. Find the **sink** where the vulnerability occurs

### Step 4: Extract Vulnerable Code
Use `extract_code` to get the vulnerable function(s):
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="<vulnerable_function>",
    include_cross_file_deps=True
)
```

### Step 5: Generate Fix
Create a fixed version that:
- Adds proper input validation/sanitization
- Uses parameterized queries for SQL
- Escapes output for XSS
- Validates file paths for traversal

### Step 6: Validate Fix
Use `simulate_refactor` to ensure the fix:
- Doesn't introduce new vulnerabilities
- Preserves the function's behavior
```
simulate_refactor(
    original_code=<vulnerable_code>,
    new_code=<fixed_code>,
    strict_mode=True
)
```

### Step 7: Apply Fix
If validation passes, apply with `update_symbol`.

## Common Fixes by Vulnerability Type
- **SQL Injection**: Use parameterized queries, ORM methods
- **XSS**: HTML escape output, use template auto-escaping
- **Command Injection**: Use subprocess with list args, avoid shell=True
- **Path Traversal**: Use pathlib, validate against allowed directories

Please proceed with Step 1 to begin the investigation."""


@mcp.prompt(title="Analyze Codebase")
def analyze_codebase_prompt(project_description: str = "Python project") -> str:
    """
    Comprehensive codebase analysis workflow.

    Added in v2.0.0: Full project analysis workflow.
    """
    return f"""# Comprehensive Codebase Analysis

## Project
{project_description}

## Analysis Workflow

### Step 1: Project Structure Overview
Start by understanding the project layout:
```
# Read the project structure resource
# URI: scalpel://project/structure
```

Then crawl for detailed metrics:
```
crawl_project(
    complexity_threshold=10,
    include_report=True
)
```

### Step 2: Dependency Analysis
Check project dependencies for vulnerabilities:
```
scan_dependencies(scan_vulnerabilities=True)
```

Also check internal dependencies:
```
# Read the dependencies resource
# URI: scalpel://project/dependencies
```

### Step 3: Call Graph Analysis
Understand how code flows through the project:
```
# Read the call graph resource
# URI: scalpel://project/call-graph
```

Or use the tool for specific functions:
```
get_call_graph(
    target_function="<main_entry_point>",
    include_diagram=True
)
```

### Step 4: Identify Hotspots
From the crawl results, identify:
1. **High Complexity Functions** (complexity > 10)
2. **Large Files** (> 500 lines)
3. **Deeply Nested Code**

For each hotspot, get detailed analysis:
```
# URI: scalpel://analysis/<file_path>
```

### Step 5: Security Assessment
Run cross-file security scan:
```
cross_file_security_scan(
    include_diagram=True,
    max_depth=5
)
```

### Step 6: Generate Report
Compile findings into:

1. **Architecture Overview**
   - Key modules and their responsibilities
   - Data flow patterns
   - External dependencies

2. **Quality Metrics**
   - Total lines of code
   - Average complexity
   - Test coverage (if detectable)

3. **Security Posture**
   - Vulnerabilities found
   - Risk level assessment
   - Remediation priorities

4. **Recommendations**
   - Refactoring candidates
   - Security fixes needed
   - Code quality improvements

Please proceed with Step 1 to begin the analysis."""


@mcp.prompt(title="Extract and Test")
def extract_and_test_prompt(file_path: str, function_name: str) -> str:
    """
    Extract a function and generate comprehensive tests.

    Added in v2.0.0: Test generation workflow.
    """
    return f"""# Extract and Generate Tests Workflow

## Target
- **File**: `{file_path}`
- **Function**: `{function_name}`

## Workflow Steps

### Step 1: Extract the Function
Get the function with all dependencies:
```
extract_code(
    file_path="{file_path}",
    target_type="function",
    target_name="{function_name}",
    include_context=True,
    include_cross_file_deps=True
)
```

### Step 2: Analyze Execution Paths
Run symbolic execution to discover all paths:
```
symbolic_execute(
    code=<extracted_code>,
    max_paths=20
)
```

### Step 3: Generate Test Cases
Create tests covering each path:
```
generate_unit_tests(
    code=<extracted_code>,
    function_name="{function_name}",
    framework="pytest"
)
```

### Step 4: Review Generated Tests
The generated tests will include:
- **Happy path tests**: Normal expected inputs
- **Edge case tests**: Boundary conditions
- **Error path tests**: Invalid inputs, exceptions

For each test case, verify:
1. The input values make sense for the path
2. The expected behavior is correct
3. Assertions are meaningful

### Step 5: Enhance Tests
Consider adding:
- **Property-based tests** for functions with numeric inputs
- **Mock tests** for external dependencies
- **Integration tests** if the function calls other modules

### Step 6: Create Test File
Save the tests to `tests/test_{function_name}.py`:
```python
# tests/test_{function_name}.py
import pytest
from {file_path.replace("/", ".").replace(".py", "")} import {function_name}

<generated_test_code>
```

### Step 7: Verify Tests Pass
Run the tests to ensure they work:
```bash
pytest tests/test_{function_name}.py -v
```

## Coverage Goals
- Aim for 100% branch coverage
- Each path from symbolic execution should have a test
- Edge cases should be explicitly tested

Please proceed with Step 1 to begin extracting the function."""


# ==========================================================================
# v2.2.0 WORKFLOW PROMPTS - Guided Multi-Step Workflows
# ==========================================================================


@mcp.prompt(title="Security Audit Workflow")
def security_audit_workflow_prompt(project_path: str) -> str:
    """
    Guide an AI agent through a comprehensive security audit.

    Added in v2.2.0.
    """
    return f"""## Security Audit Workflow for {project_path}

Follow these steps to perform a comprehensive security audit:

### Step 1: Project Analysis
Use `crawl_project` to understand the codebase structure:
```
crawl_project(
    project_root="{project_path}"
)
```

This will identify:
- All Python/JavaScript/TypeScript files
- Entry points and main modules
- Overall project structure

### Step 2: Vulnerability Scan
Use `security_scan` on each Python/JavaScript/TypeScript file discovered.
For each file with potential security issues:
```
security_scan(
    code=<file_contents>,
    filename=<file_path>
)
```

For multi-file taint analysis, use:
```
cross_file_security_scan(
    project_root="{project_path}",
    entry_point=<main_file>
)
```

### Step 3: Dependency Check
Use `scan_dependencies` to check for known CVEs:
```
scan_dependencies(
    project_path="{project_path}"
)
```

This checks:
- Python: requirements.txt, Pipfile, poetry.lock
- JavaScript/TypeScript: package.json, package-lock.json
- Known vulnerabilities from OSV database

### Step 4: Report Generation
Compile findings into a prioritized report with:

**CRITICAL** (Immediate action required):
- SQL Injection vulnerabilities
- Command Injection vulnerabilities
- Hardcoded secrets/credentials
- Known CVEs with exploit availability

**HIGH** (Address within 1 week):
- XSS vulnerabilities
- Path Traversal issues
- Insecure deserialization
- Authentication bypasses

**MEDIUM** (Address within 1 month):
- Information disclosure
- Weak cryptography
- Missing input validation

**LOW** (Nice to fix):
- Code quality issues
- Minor security improvements
- Best practice recommendations

For each finding, include:
- **Location**: File path and line number
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **Description**: What the vulnerability is
- **Impact**: What could go wrong
- **Remediation**: How to fix it
- **Code Example**: Show the vulnerable code and fixed version

Begin by running `crawl_project("{project_path}")` to start the audit.
"""


@mcp.prompt(title="Safe Refactor Workflow")
def safe_refactor_workflow_prompt(file_path: str, symbol_name: str) -> str:
    """
    Guide an AI agent through a safe refactoring operation.

    Added in v2.2.0.
    """
    return f"""## Safe Refactor Workflow for {symbol_name} in {file_path}

### Step 1: Extract Current Implementation
Use `extract_code` to get the current implementation:
```
extract_code(
    file_path="{file_path}",
    target_name="{symbol_name}",
    include_context=True
)
```

Review the extracted code to understand:
- Current function signature
- Dependencies (imports, other functions)
- Complexity and structure
- Existing patterns

### Step 2: Find All Usages
Use `get_symbol_references` to find all call sites:
```
get_symbol_references(
    symbol_name="{symbol_name}",
    project_root="<project_root>"
)
```

Document all locations where {symbol_name} is:
- Called/invoked
- Imported
- Referenced in type annotations
- Used in tests

### Step 3: Plan Changes
List all changes needed across files:

**Primary Changes** (in {file_path}):
- [ ] Function signature modifications
- [ ] Logic improvements
- [ ] Error handling updates
- [ ] Documentation updates

**Secondary Changes** (in dependent files):
- [ ] Update imports if renaming
- [ ] Update call sites if signature changes
- [ ] Update type annotations if types change
- [ ] Update tests to match new behavior

**Risk Assessment**:
- Breaking changes: YES/NO
- Number of dependent files: <count>
- Test coverage: <percentage>

### Step 4: Simulate Refactor
Use `simulate_refactor` to verify changes are safe:
```
simulate_refactor(
    original_code=<current_implementation>,
    new_code=<your_refactored_code>,
    strict_mode=True
)
```

The simulation will check:
- Function signature compatibility
- Return type consistency
- Exception handling preservation
- Side effect changes

**DO NOT PROCEED** if simulation fails or shows warnings.

### Step 5: Apply Changes
Only if simulation passes with no warnings:

For the primary file:
```
update_symbol(
    file_path="{file_path}",
    target_type="function",  # or "class"
    target_name="{symbol_name}",
    new_code=<your_refactored_code>,
    create_backup=True
)
```

For dependent files (if needed):
- Update each file manually or with update_symbol
- Update imports using extract_code + update_symbol
- Verify each change with simulation

### Step 6: Verify
After applying changes:

1. **Run Tests**:
   - Unit tests for {symbol_name}
   - Integration tests for dependent code
   - Full test suite if breaking changes

2. **Check Linters**:
   - Run static analysis tools
   - Check type checking (mypy, TypeScript)
   - Verify code formatting

3. **Review Changes**:
   - Use git diff to review all changes
   - Verify backup files were created
   - Check that all usages were updated

### Rollback Plan
If anything goes wrong:
1. Restore from .bak backup files
2. Run tests to verify rollback
3. Investigate what went wrong before retrying

### Safety Checklist
- [ ] Step 1: Current code extracted
- [ ] Step 2: All usages found
- [ ] Step 3: Changes planned and reviewed
- [ ] Step 4: Simulation passed
- [ ] Step 5: Changes applied with backups
- [ ] Step 6: Tests passing

Begin by running `extract_code(file_path="{file_path}", target_name="{symbol_name}")` to extract the current implementation.
"""


__all__ = [
    "code_review_prompt",
    "security_audit_prompt",
    "refactor_function_prompt",
    "debug_vulnerability_prompt",
    "analyze_codebase_prompt",
    "extract_and_test_prompt",
    "security_audit_workflow_prompt",
    "safe_refactor_workflow_prompt",
]
