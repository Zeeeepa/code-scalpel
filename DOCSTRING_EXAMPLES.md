# Tool Docstring Variations - Examples

## Example 1: PREFERRED FORMAT (Standard)
File: `context.py` - `crawl_project` (Lines 34-56)

```python
@mcp.tool()
async def crawl_project(
    root_path: str | None = None,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = 10,
    include_report: bool = True,
    pattern: str | None = None,
    pattern_type: str = "regex",
    include_related: list[str] | None = None,
    ctx: Context | None = None,
) -> ToolResponseEnvelope:
    """Crawl a project directory and analyze Python files.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Up to 100 files, no parsing, no complexity analysis
    - Pro: Unlimited files, full parsing, complexity analysis
    - Enterprise: Unlimited files, full parsing, complexity analysis

    Args:
        root_path: Root directory to crawl (default: server's project root)
        exclude_dirs: List of directory names to exclude
        complexity_threshold: Threshold for complexity analysis (default: 10)
        include_report: Whether to include detailed report (default: True)
        pattern: Optional pattern to filter files
        pattern_type: Type of pattern matching ("regex" or "glob", default: "regex")
        include_related: Optional list of related file types to include

    Returns:
        ToolResponseEnvelope with crawl results and tier metadata
    """
```

**Status:** COMPLETE - All required sections present with consistent formatting

---

## Example 2: LEGACY FORMAT (Tier Features only)
File: `security.py` - `unified_sink_detect` (Lines 28-41)

```python
@mcp.tool()
async def unified_sink_detect(
    code: str, language: str = "auto", confidence_threshold: float = 0.7
) -> ToolResponseEnvelope:
    """Unified polyglot sink detection with confidence thresholds.

    If language is not specified or set to 'auto', it will be auto-detected from the code.
    Supported languages: python, javascript, typescript, java.

    Tier Features:
    - Community: Basic sink detection, CWE mapping, confidence scoring
    - Pro: + Context-aware detection, framework-specific sinks, custom patterns
    - Enterprise: + Compliance reporting, risk scoring, remediation suggestions
    """
```

**Status:** INCOMPLETE
- Missing: Structured Args section
- Missing: Returns section
- Issue: Uses "Tier Features" instead of "Tier Behavior + Tier Capabilities"
- Issue: Parameters documented inline instead of in Args section

---

## Example 3: MISSING TIER INFORMATION
File: `oracle.py` - `write_perfect_code` (Lines 127-150)

```python
@mcp.tool()
async def write_perfect_code(
    file_path: str,
    instruction: str,
) -> ToolResponseEnvelope:
    """
    Generate constraint specification for AI-assisted code generation.

    Provides a Markdown specification containing:
    - Strict symbol table (function/class signatures)
    - Graph constraints (dependencies, callers)
    - Architectural rules (layer boundaries)
    - Code context (relevant snippet)
    - Implementation notes (best practices)

    The LLM uses this spec to generate code that compiles and integrates correctly.

    Args:
        file_path: Path to target file (e.g., "src/auth.py")
        instruction: What needs to be implemented (e.g., "Add JWT validation")

    Returns:
        Markdown constraint specification in response envelope
    """
```

**Status:** INCOMPLETE
- Has: Args and Returns sections
- Missing: Tier Behavior and Tier Capabilities sections
- Note: Code has `TIER_LIMITS` defined at module level (lines 28-32) but not documented

```python
# Module level TIER_LIMITS (not documented in docstring):
TIER_LIMITS = {
    "community": {"max_files": 50, "max_depth": 2},
    "pro": {"max_files": 2000, "max_depth": 10},
    "enterprise": {"max_files": 100000, "max_depth": 50},
}
```

---

## Example 4: MINIMAL DOCUMENTATION (CRITICAL)
File: `policy.py` - `validate_paths` (Lines 24-28)

```python
@mcp.tool()
async def validate_paths(
    paths: list[str], project_root: str | None = None
) -> ToolResponseEnvelope:
    """Validate that paths are accessible before running file-based operations."""
```

**Status:** CRITICAL
- Has: One-sentence description only
- Missing: Tier information
- Missing: Args section
- Missing: Returns section
- Impact: Users cannot determine tier-specific limits or capabilities

---

## Example 5: INCONSISTENT TIER NAMING
File: `extraction.py` - `extract_code` (Lines 32-62)

```python
@mcp.tool()
async def extract_code(
    target_type: str,
    target_name: str,
    # ... 10 more parameters ...
) -> ToolResponseEnvelope:
    """Extract code elements with optional dependency context.

    Provide either 'file_path' (recommended) or 'code' for the source.
    Language is auto-detected if not specified.

    Tier Requirements:
    - Community: Basic extraction, max_depth=0, include_cross_file_deps=false
    - Pro: + cross-file deps, variable_promotion, closure_detection, dependency_injection_suggestions, max_depth=1
    - Enterprise: + as_microservice, organization_wide, unlimited depth
    """
```

**Status:** INCONSISTENT
- Uses: "Tier Requirements" instead of "Tier Behavior + Tier Capabilities"
- Missing: Structured Args section
- Missing: Returns section
- Issue: No documentation for the 10+ parameters

---

## Example 6: ENHANCED FORMAT (Extra Sections)
File: `symbolic.py` - `generate_unit_tests` (Lines 127-162)

```python
@mcp.tool()
async def generate_unit_tests(
    code: str | None = None,
    file_path: str | None = None,
    function_name: str | None = None,
    framework: str = "pytest",
    data_driven: bool = False,
    crash_log: str | None = None,
) -> ToolResponseEnvelope:
    """Generate unit tests from code using symbolic execution.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max 5 test cases, pytest framework only
    - Pro: Max 20 test cases, pytest/unittest frameworks, data-driven tests
    - Enterprise: Unlimited test cases, all frameworks, data-driven tests, bug reproduction

    **Input Methods (choose one):**
    - `code`: Direct Python code string to analyze
    - `file_path`: Path to Python file containing the code
    - `function_name`: Name of function to generate tests for (requires file_path)

    Args:
        code: Python code string to generate tests for
        file_path: Path to Python file to analyze
        function_name: Specific function name to target (optional)
        framework: Test framework ("pytest", "unittest", etc.)
        data_driven: Generate parameterized data-driven tests (Pro+)
        crash_log: Crash log for bug reproduction tests (Enterprise only)

    Returns:
        ToolResponseEnvelope with generated test cases and tier metadata
    """
```

**Status:** COMPLETE with ENHANCEMENTS
- Has: All standard sections
- Extra: "Input Methods" subsection explaining mutually exclusive parameters
- Benefit: Clear guidance on which parameters to use together

---

## Example 7: MOST COMPREHENSIVE (With Usage Examples)
File: `system.py` - `get_capabilities` (Lines 21-75)

```python
@mcp.tool()
async def get_capabilities(
    tier: str | None = None,
    ctx: Context | None = None,
) -> ToolResponseEnvelope:
    """Get the capabilities available for the current license tier.

    This tool returns a complete list of all 22 Code Scalpel tools and their
    availability/limits at the specified tier or current tier.

    **Usage by Agents:**
    Agents can call this tool to discover:
    - Which tools are available at the current tier
    - The limits applied to each tool (max_files, max_depth, etc.)
    - Whether specific features are enabled

    **Tier Behavior:**
    - Community: All tools available with basic limits
    - Pro: 19 tools available with expanded limits
    - Enterprise: 10 tools available with no limits

    Args:
        tier: Optional tier to query (defaults to current tier from license)
              Must be one of: "community", "pro", "enterprise"
              If not specified, uses the tier from the current license.

    Returns:
        ToolResponseEnvelope containing:
        {
            "tier": "pro",
            "tool_count": 22,
            "available_count": 19,
            "capabilities": {
                "analyze_code": {
                    "tool_id": "analyze_code",
                    "tier": "pro",
                    "available": true,
                    "limits": {
                        "max_file_size_mb": 10,
                        "languages": ["python", "javascript", "typescript", "java"]
                    }
                },
                ...
            }
        }

    Example:
        ```
        # Get capabilities for current tier (from license)
        result = await get_capabilities()

        # Get capabilities for a specific tier (testing/downgrade only)
        result = await get_capabilities(tier="community")
        ```
    """
```

**Status:** COMPLETE with EXCELLENCE
- Has: All standard sections
- Extra: "Usage by Agents" subsection
- Extra: Example JSON response structure
- Extra: Code usage examples
- Benefit: Developers understand both what the tool does and how to use it

---

## Comparison Matrix

| Feature | Example 1 (Preferred) | Example 2 (Legacy) | Example 3 (Missing) | Example 4 (Minimal) |
|---------|:---:|:---:|:---:|:---:|
| Brief Description | ✓ | ✓ | ✓ | ✓ |
| Tier Behavior | ✓ | ✗ | ✗ | ✗ |
| Tier Capabilities | ✓ | ~ | ✗ | ✗ |
| Args Section | ✓ | ✗ | ✓ | ✗ |
| Returns Section | ✓ | ✗ | ✓ | ✗ |
| Documentation Lines | 23 | 10 | 18 | 1 |
| Completeness | 100% | 40% | 60% | 5% |

---

## Key Takeaways

1. **Preferred Format**: Use "Tier Behavior" + "Tier Capabilities" (12 tools currently use this)
2. **Legacy Format**: "Tier Features" is still present in 6 tools and should be updated
3. **Missing Sections**: 9 tools are missing either Args or Returns sections
4. **Critical Gap**: 4 tools have minimal documentation (1 sentence only)
5. **Best Practice**: Use structured Args/Returns sections for clarity and IDE support
6. **Enhancement**: Add subsections for complex parameter combinations (like "Input Methods")
7. **Excellence**: Include usage examples for introspection tools (like get_capabilities)
