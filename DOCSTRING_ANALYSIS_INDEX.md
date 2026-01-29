# Tool Docstring Analysis - Report Index

Generated: 2026-01-27  
Analysis Scope: `src/code_scalpel/mcp/tools/*.py` (23 tool functions across 9 files)  
Overall Compliance: 52% (12 complete, 8 incomplete, 3 minimal)

## Report Files

### 1. DOCSTRING_QUICK_SUMMARY.txt
**Best for:** Quick reference and status overview  
**Contains:**
- Compliance rate and key statistics
- Critical issues by priority
- Tools by status (Complete/Incomplete/Minimal)
- Quick statistics by file
- Recommended standard template

**When to use:** For a 2-minute overview of the problem

### 2. DOCSTRING_ANALYSIS_REPORT.md
**Best for:** Detailed findings and action items  
**Contains:**
- Executive summary
- Detailed findings by section type (Args, Returns, Tier info)
- Summary compliance table for all 23 tools
- Line number references to source files
- Critical issues #1-6 with examples
- Variations by tool category
- Files to update in priority order
- Complete conclusion and recommendations

**When to use:** For comprehensive analysis and planning updates

### 3. DOCSTRING_EXAMPLES.md
**Best for:** Understanding what needs to change  
**Contains:**
- 7 real examples from the codebase:
  1. Preferred format (crawl_project)
  2. Legacy format (unified_sink_detect)
  3. Missing tier info (write_perfect_code)
  4. Minimal docs (validate_paths)
  5. Inconsistent naming (extract_code)
  6. Enhanced format (generate_unit_tests)
  7. Most comprehensive (get_capabilities)
- Comparison matrix showing what each has/is missing
- Key takeaways

**When to use:** For making docstring updates and understanding patterns

---

## Key Findings Summary

### Tools with 100% Compliance (12 total)
Files that consistently follow the "Tier Behavior + Tier Capabilities + Args + Returns" standard:
- ✓ context.py (3 tools): crawl_project, get_file_context, get_symbol_references
- ✓ extraction.py (1 tool): update_symbol
- ✓ graph.py (5 tools): get_call_graph, get_graph_neighborhood, get_project_map, get_cross_file_dependencies, cross_file_security_scan
- ✓ symbolic.py (3 tools): symbolic_execute, generate_unit_tests, simulate_refactor
- ✓ system.py (1 tool): get_capabilities

### Tools with 0% Compliance (7 total)
Files that need complete docstring updates:
- ✗ analyze.py (1 tool): analyze_code - missing Args/Returns
- ✗ oracle.py (1 tool): write_perfect_code - missing tier sections
- ✗ extraction.py (2 tools): extract_code (inconsistent naming), rename_symbol (missing Args/Returns)
- ✗ policy.py (3 tools): validate_paths, verify_policy_integrity, code_policy_check (1-sentence docs)
- ✗ security.py (4 tools): unified_sink_detect, type_evaporation_scan, security_scan (missing Args/Returns), scan_dependencies (1-sentence docs)

---

## Main Inconsistencies Found

### 1. Tier Section Naming (7 tools affected)

**Preferred Format (12 tools use this):**
```
**Tier Behavior:**
- All tiers: Tool is available.
- Limits and optional enhancements are applied based on tool capabilities.

**Tier Capabilities:**
- Community: [capabilities]
- Pro: [additional capabilities]
- Enterprise: [additional capabilities]
```

**Legacy Format (6 tools still use this):**
```
Tier Features:
- Community: [features]
- Pro: + [additional features]
- Enterprise: + [additional features]
```

**Inconsistent Format (1 tool uses this):**
```
Tier Requirements:
- Community: [requirements]
- Pro: + [additional requirements]
- Enterprise: + [additional requirements]
```

### 2. Missing Args Sections (9 tools)
Tools document parameters inline in description instead of in structured Args section:
- analyze_code, extract_code, rename_symbol, unified_sink_detect, type_evaporation_scan, security_scan, validate_paths, verify_policy_integrity, code_policy_check

### 3. Missing Returns Sections (9 tools)
Tools don't document what ToolResponseEnvelope contains:
- analyze_code, extract_code, rename_symbol, unified_sink_detect, type_evaporation_scan, security_scan, validate_paths, verify_policy_integrity, code_policy_check

### 4. Minimal Documentation (4 tools - CRITICAL)
Only 1-2 sentence descriptions with no tier or parameter information:
- validate_paths
- verify_policy_integrity
- code_policy_check
- scan_dependencies

---

## Priority Roadmap for Fixes

### Phase 1: Critical Gaps (4 tools)
**File:** policy.py + security.py (scan_dependencies)
- validate_paths: Expand from 1 sentence to full documentation
- verify_policy_integrity: Expand from 1 sentence to full documentation
- code_policy_check: Expand from 1 sentence to full documentation
- scan_dependencies: Expand from 1 sentence to full documentation

### Phase 2: Missing Sections (4 tools)
**File:** security.py
- unified_sink_detect: Add Args, Returns, and Tier Behavior sections
- type_evaporation_scan: Add Args, Returns, and Tier Behavior sections
- security_scan: Add Args, Returns, and Tier Behavior sections
- Note: scan_dependencies also needed but covered in Phase 1

### Phase 3: Inconsistent Naming (3 tools)
**File:** extraction.py
- extract_code: Change "Tier Requirements" to "Tier Behavior + Tier Capabilities"
- extract_code: Add formal Args and Returns sections
- rename_symbol: Add Args, Returns, and Tier Behavior sections

### Phase 4: Missing Tier Documentation (2 tools)
**File:** oracle.py + analyze.py
- write_perfect_code: Add Tier Behavior and Tier Capabilities sections
- analyze_code: Add Args and Returns sections

---

## Recommended Standard Template

Use this template for all MCP tool docstrings:

```python
@mcp.tool()
async def tool_name(
    param1: str,
    param2: int = 10,
    param3: str | None = None,
) -> ToolResponseEnvelope:
    """One-sentence brief description of what the tool does.

    Longer explanation describing the tool's purpose, how it works, and when to use it.
    Include any important context or prerequisites.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: [specific capabilities and limits for this tier]
    - Pro: [additional capabilities available at Pro tier]
    - Enterprise: [additional capabilities available at Enterprise tier]

    Args:
        param1: Description of param1 (required)
        param2: Description of param2 (default: 10)
        param3: Description of param3 (optional)

    Returns:
        ToolResponseEnvelope containing:
        - data: [description of what's in the data field]
        - tier: Current tier level
        - duration_ms: Execution time in milliseconds
        - error: None if successful, ToolError object if failed
    """
```

### Optional Enhancements:

For tools with multiple input modes:
```python
    **Input Methods (choose one):**
    - `code`: Direct code string to analyze
    - `file_path`: Path to file containing the code
```

For tools with advanced features:
```python
    **Advanced Features:**
    - Feature A: Description
    - Feature B: Description
    - Feature C: Description
```

For introspection/discovery tools:
```python
    **Usage by Agents:**
    Agents can call this tool to:
    - Discover available capabilities
    - Check tier-specific limits
    - [other usage patterns]

    Example:
        ```python
        result = await get_capabilities()
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Available tools: {len(result.data['capabilities'])}")
        ```
```

---

## Validation Checklist

When updating docstrings, ensure:

- [ ] Brief description (1-2 sentences) explaining what the tool does
- [ ] "Tier Behavior" section explaining tool availability across tiers
- [ ] "Tier Capabilities" section with tier-specific limits
- [ ] "Args" section documenting all parameters with types and defaults
- [ ] "Returns" section describing ToolResponseEnvelope content
- [ ] No "Tier Features" or "Tier Requirements" (use "Tier Behavior + Tier Capabilities")
- [ ] All parameter defaults shown in Args section
- [ ] Tier-specific parameter behaviors noted if applicable
- [ ] Line length reasonable for readability (80-120 chars)
- [ ] Proper markdown formatting with `**Bold**` for section headers
- [ ] Examples included for complex or introspection tools

---

## Integration with CI/CD

Recommended workflow:
1. Create branch: `git checkout -b docs/docstring-consistency`
2. Update docstrings using DOCSTRING_EXAMPLES.md as reference
3. Run docstring linter (if available): `python -m pydocstyle src/code_scalpel/mcp/tools/`
4. Generate documentation: `python -m sphinx...` (if applicable)
5. Run tests to ensure no side effects
6. Create PR with title: "docs: Standardize tool docstrings for consistency"
7. Reference this analysis report in PR description

---

## Tools Used

- Python AST inspection for docstring extraction
- Pattern matching for section identification
- Compliance scoring based on section presence
- Comparative analysis of formatting variations

---

## Contact & Follow-up

For questions about this analysis:
1. Review DOCSTRING_ANALYSIS_REPORT.md for detailed findings
2. Check DOCSTRING_EXAMPLES.md for formatting guidance
3. Refer to DOCSTRING_QUICK_SUMMARY.txt for statistics

---

*Analysis Report Generated: 2026-01-27 15:22 UTC*  
*Total Files Analyzed: 9*  
*Total Tools Analyzed: 23*  
*Unique Issues Found: 12*  
