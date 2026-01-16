"""MCP prompt handlers."""

from __future__ import annotations

from importlib import import_module

mcp = import_module("code_scalpel.mcp.protocol").mcp


# ==========================================================================
# PROMPTS
# ==========================================================================


@mcp.prompt(title="Code Review")
def code_review_prompt(code: str) -> str:
    """Generate a comprehensive code review prompt."""
    return f"""Please analyze the following Python code and provide:

1. **Structure Analysis**: Identify functions, classes, and imports
2. **Security Review**: Check for potential vulnerabilities
3. **Quality Assessment**: Evaluate code quality and suggest improvements
4. **Edge Cases**: Identify potential edge cases and error conditions

Use the available Code Scalpel tools to gather detailed analysis:
- analyze_code: For structure and complexity
- security_scan: For vulnerability detection
- symbolic_execute: For path analysis

Code to review:
```python
{code}
```

Provide actionable recommendations for improvement."""


@mcp.prompt(title="Security Audit")
def security_audit_prompt(code: str) -> str:
    """Generate a security-focused audit prompt."""
    return f"""Perform a security audit of the following Python code.

Focus on:
1. **Input Validation**: Are all inputs properly validated?
2. **Injection Risks**: SQL, command, code injection vulnerabilities
3. **Authentication/Authorization**: Proper access controls
4. **Data Exposure**: Sensitive data handling
5. **Dependencies**: Known vulnerable patterns

Use security_scan tool to detect vulnerabilities automatically.

Code to audit:
```python
{code}
```

Provide a risk assessment and remediation steps for each finding."""


# ==========================================================================
# WORKFLOW PROMPTS - Orchestrated Multi-Tool Workflows
# ==========================================================================


@mcp.prompt(title="Refactor Function")
def refactor_function_prompt(
    file_path: str, function_name: str, refactor_goal: str
) -> str:
    """
    Safe refactoring workflow with validation.

    [20251215_FEATURE] v2.0.0 - Orchestrated refactor workflow.
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

    [20251215_FEATURE] v2.0.0 - Security debugging workflow.
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

    [20251215_FEATURE] v2.0.0 - Full project analysis workflow.
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

    [20251215_FEATURE] v2.0.0 - Test generation workflow.
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
    [20251216_FEATURE] Guide an AI agent through a comprehensive security audit.
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
    [20251216_FEATURE] Guide an AI agent through a safe refactoring operation.
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
