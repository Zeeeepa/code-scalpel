"""
Code Scalpel Prompts Module.

[20260116_REFACTOR] Intent-Driven User Experience

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