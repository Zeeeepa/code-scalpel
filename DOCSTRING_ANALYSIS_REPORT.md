# Tool Docstring Analysis Report

## Executive Summary
Analyzed 9 Python files containing 23 async tool functions in `src/code_scalpel/mcp/tools/`.
Found significant inconsistencies in docstring formatting across tools.

---

## Detailed Findings

### 1. MISSING SECTIONS ANALYSIS

#### Tools with COMPLETE sections:
- `analyze_code`: Brief + Tier Features + self-correction note
- `crawl_project`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `get_file_context`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `get_symbol_references`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `extract_code`: Brief + Tier Requirements + (Args in code, not docstring)
- `update_symbol`: Brief + Tier Behavior + Tier Capabilities + Validation Levels + Args + Returns
- `get_call_graph`: Brief + Tier Behavior + Tier Capabilities + Advanced Features + Args + Returns
- `get_graph_neighborhood`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `get_project_map`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `get_cross_file_dependencies`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `cross_file_security_scan`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `write_perfect_code`: Brief description + Args + Returns (NO explicit tier sections)
- `unified_sink_detect`: Brief + Tier Features (NO Args/Returns sections)
- `type_evaporation_scan`: Brief + Tier Features (NO Args/Returns sections)
- `scan_dependencies`: Only one-line description (MINIMAL)
- `security_scan`: Brief + Tier Features (NO Args/Returns sections)
- `symbolic_execute`: Brief + Tier Behavior + Tier Capabilities + Args + Returns
- `generate_unit_tests`: Brief + Tier Behavior + Tier Capabilities + Input Methods + Args + Returns
- `simulate_refactor`: Brief + Tier Behavior + Tier Capabilities + Change Specification + Args + Returns
- `validate_paths`: Only one-line description (MINIMAL)
- `verify_policy_integrity`: Only one-line description (MINIMAL)
- `code_policy_check`: Only one-line description (MINIMAL)
- `get_capabilities`: Brief + Usage by Agents + Tier Behavior + Args + Returns + Example

---

## 2. FORMATTING INCONSISTENCIES DISCOVERED

### A. SECTION HEADER VARIATIONS

#### Variation 1: "Tier Behavior" + "Tier Capabilities" (Preferred Pattern)
```
**Tier Behavior:**
- All tiers: Tool is available.
- Limits and optional enhancements are applied based on tool capabilities.

**Tier Capabilities:**
- Community: [capabilities]
- Pro: [capabilities]
- Enterprise: [capabilities]
```
TOOLS USING THIS PATTERN:
- crawl_project (lines 36-43)
- get_file_context (lines 96-103)
- get_symbol_references (lines 147-154)
- update_symbol (lines 189-201)
- get_call_graph (lines 49-56)
- get_graph_neighborhood (lines 160-167)
- get_project_map (lines 215-222)
- get_cross_file_dependencies (lines 345-352)
- cross_file_security_scan (lines 432-439)
- symbolic_execute (lines 42-49)
- generate_unit_tests (lines 138-145)
- simulate_refactor (lines 309-316)

#### Variation 2: "Tier Features" + optional Ad-hoc features
```
Tier Features:
- Community: [features]
- Pro: + [additional features]
- Enterprise: + [additional features]
```
TOOLS USING THIS PATTERN:
- analyze_code (lines 41-44) - also includes note about v1_1
- extract_code (lines 58-61) - uses "Tier Requirements" instead
- rename_symbol (lines 131-134)
- unified_sink_detect (lines 37-40)
- type_evaporation_scan (lines 103-106)
- security_scan (lines 277-280)

#### Variation 3: "Tier Features" (Inconsistent naming)
```
Tier Features:
- Community: [features]
- Pro: + [features]
- Enterprise: + [features]
```
PROBLEMATIC CASES:
- extract_code uses "Tier Requirements" (line 58)
- security_scan uses "Tier Features" (line 277)
- unified_sink_detect uses "Tier Features" (line 37)

#### Variation 4: Minimal/Missing Tier Documentation
```
(Single line description only)
```
TOOLS WITH INSUFFICIENT DOCUMENTATION:
- validate_paths: "Validate that paths are accessible before running file-based operations."
- verify_policy_integrity: "Verify policy file integrity using cryptographic signatures."
- code_policy_check: "Check code against style guides, best practices, and compliance standards."
- scan_dependencies: "Scan project dependencies for known vulnerabilities."

---

### B. ARGUMENT SECTION VARIATIONS

#### Variation 1: Structured Args section with descriptions
```
Args:
    param_name: Description (default: value)
    param_name: Description (optional)
```
TOOLS USING THIS:
- crawl_project (lines 45-52)
- get_file_context (lines 105-106)
- get_symbol_references (lines 156-160)
- update_symbol (lines 203-210)
- get_call_graph (lines 65-73)
- get_graph_neighborhood (lines 169-176)
- get_project_map (lines 224-228)
- get_cross_file_dependencies (lines 354-362)
- cross_file_security_scan (lines 441-450)
- write_perfect_code (lines 144-146)
- generate_unit_tests (lines 152-158)
- simulate_refactor (lines 322-326)
- get_capabilities (lines 42-45)

#### Variation 2: Missing Args section
TOOLS WITHOUT ARGS:
- analyze_code
- extract_code (uses "Provide either..." in description instead)
- rename_symbol
- unified_sink_detect
- type_evaporation_scan (brief mention in description)
- security_scan (mentions code vs file_path inline)
- validate_paths
- verify_policy_integrity
- code_policy_check

#### Variation 3: Minimal/Inline Args
- unified_sink_detect: "If language is not specified..." (inline in description)
- type_evaporation_scan: "Provide either..." (inline in description)
- security_scan: "Provide either 'code' or 'file_path'." (inline in description)

---

### C. RETURNS SECTION VARIATIONS

#### Variation 1: Structured Returns with type and description
```
Returns:
    ToolResponseEnvelope with [description of data]
```
TOOLS USING THIS:
- crawl_project (line 54-55)
- get_file_context (line 108-109)
- get_symbol_references (line 162-163)
- update_symbol (line 212-213)
- get_call_graph (line 75-76)
- get_graph_neighborhood (line 178-179)
- get_project_map (line 230-231)
- get_cross_file_dependencies (line 364-366)
- cross_file_security_scan (line 453-454)
- symbolic_execute (line 56-57)
- generate_unit_tests (line 160-161)
- simulate_refactor (line 328-329)
- write_perfect_code (line 149-149)
- get_capabilities (line 47-64) - EXTRA DETAILED with example JSON

#### Variation 2: Missing Returns section
TOOLS WITHOUT RETURNS:
- analyze_code (returns ToolResponseEnvelope, not documented)
- extract_code (returns ToolResponseEnvelope, not documented)
- rename_symbol (returns ToolResponseEnvelope, not documented)
- unified_sink_detect (returns ToolResponseEnvelope, not documented)
- type_evaporation_scan (returns ToolResponseEnvelope, not documented)
- security_scan (returns ToolResponseEnvelope, not documented)
- validate_paths (returns ToolResponseEnvelope, not documented)
- verify_policy_integrity (returns ToolResponseEnvelope, not documented)
- code_policy_check (returns ToolResponseEnvelope, not documented)

---

### D. ADDITIONAL SECTIONS (Special cases)

#### Tools with Extra Sections:
1. **extract_code**: "Provide either 'file_path'..." (inline explanation)
2. **update_symbol**: "Validation Levels:" subsection (lines 198-201)
3. **get_call_graph**: "Advanced Features:" subsection (lines 58-63)
4. **generate_unit_tests**: "Input Methods (choose one):" subsection (lines 147-150)
5. **simulate_refactor**: "Change Specification (choose one):" subsection (lines 318-320)
6. **get_capabilities**: "Usage by Agents:", "Example:" sections with full code blocks
7. **write_perfect_code**: Multi-line description with Markdown output format info

---

## 3. SUMMARY TABLE: DOCSTRING COMPLETENESS

| File | Tool Name | Brief | Tier Info | Args | Returns | Status |
|------|-----------|:-----:|:---------:|:----:|:-------:|--------|
| analyze.py | analyze_code | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| context.py | crawl_project | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| context.py | get_file_context | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| context.py | get_symbol_references | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| extraction.py | extract_code | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| extraction.py | rename_symbol | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| extraction.py | update_symbol | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| graph.py | get_call_graph | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| graph.py | get_graph_neighborhood | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| graph.py | get_project_map | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| graph.py | get_cross_file_dependencies | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| graph.py | cross_file_security_scan | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| oracle.py | write_perfect_code | ✓ | ✗ | ✓ | ✓ | INCOMPLETE |
| policy.py | validate_paths | ~ | ✗ | ✗ | ✗ | MINIMAL |
| policy.py | verify_policy_integrity | ~ | ✗ | ✗ | ✗ | MINIMAL |
| policy.py | code_policy_check | ~ | ✗ | ✗ | ✗ | MINIMAL |
| security.py | unified_sink_detect | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| security.py | type_evaporation_scan | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| security.py | scan_dependencies | ~ | ✗ | ✗ | ✗ | MINIMAL |
| security.py | security_scan | ✓ | Partial | ✗ | ✗ | INCOMPLETE |
| symbolic.py | symbolic_execute | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| symbolic.py | generate_unit_tests | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| symbolic.py | simulate_refactor | ✓ | ✓ | ✓ | ✓ | COMPLETE |
| system.py | get_capabilities | ✓ | ✓ | ✓ | ✓ | COMPLETE |

**Score: 12 COMPLETE, 8 INCOMPLETE, 3 MINIMAL out of 23 tools (52% compliance)**

---

## 4. CRITICAL ISSUES

### Issue 1: Three Policy Tools Have Minimal Documentation
**Files:** policy.py (lines 24-145)
**Affected Tools:**
- validate_paths (line 25): Single sentence only
- verify_policy_integrity (line 59): Single sentence only
- code_policy_check (line 98): Single sentence only

**Example:**
```python
@mcp.tool()
async def validate_paths(
    paths: list[str], project_root: str | None = None
) -> ToolResponseEnvelope:
    """Validate that paths are accessible before running file-based operations."""
```

**Missing:** Tier information, detailed args, returns documentation

---

### Issue 2: Inconsistent Tier Section Naming
**Patterns Found:**
1. "Tier Behavior" + "Tier Capabilities" (12 tools) - PREFERRED
2. "Tier Features" (6 tools) - LEGACY
3. "Tier Requirements" (1 tool: extract_code) - INCONSISTENT

**Example of Mismatch:**
```python
# PREFERRED (context.py, crawl_project):
    Tier Behavior:
    - All tiers: Tool is available.
    Tier Capabilities:
    - Community: Up to 100 files...

# LEGACY (security.py, unified_sink_detect):
    Tier Features:
    - Community: Basic sink detection...

# INCONSISTENT (extraction.py, extract_code):
    Tier Requirements:
    - Community: Basic extraction...
```

---

### Issue 3: Missing Args/Returns Sections in Security Tools
**Files:** security.py
**Affected Tools:**
- unified_sink_detect (line 29): No Args/Returns sections
- type_evaporation_scan (line 91): No Args/Returns sections (but has inline parameter docs)
- security_scan (line 268): No Args/Returns sections
- scan_dependencies (line 206): No Args/Returns sections

**Example:**
```python
async def unified_sink_detect(
    code: str, language: str = "auto", confidence_threshold: float = 0.7
) -> ToolResponseEnvelope:
    """Unified polyglot sink detection with confidence thresholds.

    If language is not specified or set to 'auto', it will be auto-detected from the code.
    Supported languages: python, javascript, typescript, java.

    Tier Features:
    - Community: Basic sink detection...
    """
    # No Args or Returns section!
```

---

### Issue 4: Inline Parameter Documentation vs Structured Args Sections
**Pattern 1: Tools using structured Args (GOOD)**
```python
    Args:
        symbol_name: Name of the symbol to find references for
        project_root: Project root directory (default: server's project root)
```

**Pattern 2: Tools using inline description (INCONSISTENT)**
```python
    """Rename a function, class, or method in a file.

    Tier Features:
    - Community: Definition-only rename...
    """
    # Parameters documented in code signature, not docstring!
```

---

### Issue 5: Write Perfect Code (oracle.py) Missing Tier Information
**File:** oracle.py, write_perfect_code (line 127)
**Problem:** Despite having Args and Returns, no Tier Behavior/Capabilities sections

```python
@mcp.tool()
async def write_perfect_code(
    file_path: str,
    instruction: str,
) -> ToolResponseEnvelope:
    """
    Generate constraint specification for AI-assisted code generation.
    
    [Detailed description...]
    
    Args:
        file_path: Path to target file...
        instruction: What needs to be implemented...
    
    Returns:
        Markdown constraint specification in response envelope
    """
    # NO TIER SECTIONS, but code has TIER_LIMITS at module level (lines 28-32)
```

---

### Issue 6: Inconsistent Returns Documentation Format
**Format 1:** Simple one-line
```python
    Returns:
        ToolResponseEnvelope with crawl results and tier metadata
```

**Format 2:** Detailed with nested structure
```python
    Returns:
        ToolResponseEnvelope containing:
        {
            "tier": "pro",
            "tool_count": 22,
            ...
        }
```

**Format 3:** Missing entirely
```python
    # No Returns section at all
```

---

## 5. VARIATIONS BY TOOL CATEGORY

### Analysis Tools (analyze.py)
- `analyze_code`: INCOMPLETE - has Tier Features, no Args/Returns sections

### Context Tools (context.py)
- All 3 tools: COMPLETE - consistent format across all

### Extraction Tools (extraction.py)
- `extract_code`: INCOMPLETE - uses "Tier Requirements" instead of "Tier Behavior"
- `rename_symbol`: INCOMPLETE - only Tier Features, no Args/Returns
- `update_symbol`: COMPLETE - full documentation with validation levels subsection

### Graph Tools (graph.py)
- All 5 tools: COMPLETE - consistent format with advanced features subsection

### Oracle Tools (oracle.py)
- `write_perfect_code`: INCOMPLETE - no tier documentation despite tier limits in code

### Policy Tools (policy.py)
- All 3 tools: MINIMAL - single sentence descriptions only

### Security Tools (security.py)
- All 4 tools: INCOMPLETE - mix of Tier Features with missing Args/Returns

### Symbolic Tools (symbolic.py)
- All 3 tools: COMPLETE - consistent format with extended input/change specifications

### System Tools (system.py)
- `get_capabilities`: COMPLETE - extensive documentation with usage examples

---

## 6. RECOMMENDED STANDARD TEMPLATE

```python
@mcp.tool()
async def tool_name(
    param1: str,
    param2: int = 10,
) -> ToolResponseEnvelope:
    """One-sentence brief description.
    
    Longer optional description explaining what the tool does and how to use it.
    
    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.
    
    **Tier Capabilities:**
    - Community: [capabilities with limits]
    - Pro: [additional capabilities]
    - Enterprise: [additional capabilities]
    
    Args:
        param1: Description (required)
        param2: Description (default: 10)
    
    Returns:
        ToolResponseEnvelope with [description of data] and tier metadata
    """
```

---

## 7. NON-COMPLIANCE SUMMARY

### By Type:
- **Missing Tier Documentation:** 9 tools (39%)
- **Missing Args Sections:** 9 tools (39%)
- **Missing Returns Sections:** 9 tools (39%)
- **Inconsistent Tier Naming:** 7 tools (30%)
- **Minimal/Single-Line Docs:** 4 tools (17%)

### By Severity:
- **Critical (MINIMAL docs):** 4 tools
  - validate_paths
  - verify_policy_integrity
  - code_policy_check
  - scan_dependencies

- **High (Missing major sections):** 5 tools
  - analyze_code
  - extract_code
  - rename_symbol
  - write_perfect_code
  - oracle tools

- **Medium (Inconsistent naming):** 7 tools
  - Various tier naming inconsistencies

---

## 8. FILES TO UPDATE (Priority Order)

1. **security.py** (4 tools affected)
   - unified_sink_detect: Add Args, Returns, and Tier Behavior sections
   - type_evaporation_scan: Add Args, Returns, and Tier Behavior sections
   - scan_dependencies: Expand from 1 line to full documentation
   - security_scan: Add Args, Returns, and Tier Behavior sections

2. **policy.py** (3 tools affected - CRITICAL)
   - validate_paths: Add complete documentation
   - verify_policy_integrity: Add complete documentation
   - code_policy_check: Add complete documentation

3. **extraction.py** (2 tools affected)
   - extract_code: Add formal Args/Returns; change "Tier Requirements" to "Tier Behavior"
   - rename_symbol: Add Args, Returns, and Tier Behavior sections

4. **oracle.py** (1 tool affected)
   - write_perfect_code: Add Tier Behavior and Tier Capabilities sections

5. **analyze.py** (1 tool affected)
   - analyze_code: Add Args and Returns sections

---

## Conclusion

The codebase shows a 52% compliance rate with a standard docstring format. The most recent tools (context.py, graph.py, symbolic.py, system.py) follow the preferred "Tier Behavior + Tier Capabilities" pattern consistently. Older and simpler tools (policy.py, parts of security.py) have minimal documentation.

The primary inconsistencies are:
1. Tier section naming ("Tier Features" vs "Tier Behavior + Tier Capabilities")
2. Presence/absence of Args and Returns sections
3. Some tools having tier limits defined in code but not documented in docstrings

A unified formatting pass would improve developer experience and maintainability significantly.
