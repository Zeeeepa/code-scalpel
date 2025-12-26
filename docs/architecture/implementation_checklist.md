# Implementation Checklist: All Tools Available

[20251225_DOCS] Task list for completing the all-tools-available feature gating implementation

## Status: Architecture Complete, Tool Updates Pending

### ✅ COMPLETED (Phase 1: Architecture)

- [x] Created `licensing/features.py` with TOOL_CAPABILITIES matrix (900+ lines)
- [x] Updated `tiers/tool_registry.py` - all 20 tools set to `tier="community"`
- [x] Updated `tiers/feature_registry.py` - all features set to `tier="community"`
- [x] Updated `licensing/__init__.py` - added feature capability exports
- [x] Created `examples/feature_gating_example.py` - working demonstrations
- [x] Created `docs/guides/implementing_feature_gating.md` - implementation guide
- [x] Created `docs/reference/tier_capabilities_matrix.md` - complete reference
- [x] Created `docs/architecture/feature_gating_analysis.md` - analysis document
- [x] Created `docs/architecture/all_tools_available_summary.md` - summary
- [x] Created `docs/architecture/all_tools_available_diagram.md` - visual diagrams
- [x] Updated `docs/TIER_CONFIGURATION.md` - new feature comparison section
- [x] Updated `README.md` - tier section emphasizes all tools available

**Total work**: ~4,000 lines of code/documentation created

---

## 🔄 IN PROGRESS (Phase 2: Tool Implementation)

### HIGH PRIORITY: Update Tool Handlers

Update each tool to use the capability system. Pattern:

```python
async def tool_handler(params: dict) -> dict:
    # 1. Get tier and capabilities
    tier = get_current_tier()
    caps = get_tool_capabilities("tool_id", tier)
    
    # 2. Perform basic operation (all tiers)
    results = perform_basic_operation(params)
    
    # 3. Apply tier-based limits
    max_items = caps["limits"]["max_items"]
    if max_items and len(results) > max_items:
        results = results[:max_items]
        truncated = True
    
    # 4. Check capabilities for advanced features
    if has_capability("tool_id", "advanced_feature", tier):
        results["advanced"] = perform_advanced(results)
    
    # 5. Add upgrade hints
    if truncated or missing_capabilities:
        results["upgrade_hints"] = [get_upgrade_hint(...)]
    
    return results
```

#### Tools Requiring Updates

**Priority 1 (Most Impactful)**:

- [ ] `security_scan` - Apply max_findings limit (10 → ∞)
  - File: `src/code_scalpel/mcp/handlers/security_analysis.py`
  - Limit: `max_findings` (10 community, unlimited pro/enterprise)
  - Advanced features: `advanced_taint_flow`, `remediation_suggestions`, `compliance_reporting`
  - Estimated: 2-3 hours

- [ ] `symbolic_execute` - Apply max_paths limit (3 → 10 → ∞)
  - File: `src/code_scalpel/mcp/handlers/symbolic_execution.py`
  - Limit: `max_paths` (3 community, 10 pro, unlimited enterprise)
  - Advanced features: `path_prioritization`, `branch_coverage`
  - Estimated: 2 hours

- [ ] `crawl_project` - Apply max_files limit and mode switch (discovery vs deep)
  - File: `src/code_scalpel/mcp/handlers/project_analysis.py`
  - Limit: `max_files` (100 community, 1000 pro, unlimited enterprise)
  - Mode: discovery (community) vs deep (pro/enterprise)
  - Advanced features: `full_ast_parsing`, `complexity_analysis`, `org_indexing`
  - Estimated: 3-4 hours

- [ ] `extract_code` - Check cross-file deps permission and apply depth limit
  - File: `src/code_scalpel/mcp/handlers/code_extraction.py`
  - Limit: `include_cross_file_deps` (false community, true pro/enterprise)
  - Limit: `max_depth` (0 community, 1 pro, unlimited enterprise)
  - Advanced features: `org_wide_resolution`
  - Estimated: 2 hours

**Priority 2 (Important)**:

- [ ] `generate_unit_tests` - Apply max_test_cases limit
  - Limit: `max_test_cases` (5 → 20 → ∞)
  - Advanced features: `coverage_targeting`, `custom_frameworks`
  - Estimated: 1-2 hours

- [ ] `get_call_graph` - Apply max_depth limit
  - Limit: `max_depth` (3 → 10 → ∞)
  - Estimated: 1 hour

- [ ] `get_graph_neighborhood` - Apply k-hops and max_nodes limits
  - Limit: `max_k` (1 → 2 → ∞)
  - Limit: `max_nodes` (50 → 100 → ∞)
  - Estimated: 1 hour

- [ ] `scan_dependencies` - Apply max_dependencies limit
  - Limit: `max_dependencies` (50 → ∞)
  - Advanced features: `auto_update_pr`
  - Estimated: 1-2 hours

- [ ] `get_cross_file_dependencies` - Apply max_depth limit
  - Limit: `max_depth` (1 → 3 → ∞)
  - Estimated: 1 hour

- [ ] `cross_file_security_scan` - Apply depth/modules/timeout limits
  - Limit: `max_depth` (2 → 5 → ∞)
  - Limit: `max_modules` (50 → 500 → ∞)
  - Limit: `timeout` (30s → 120s → configurable)
  - Estimated: 2 hours

**Priority 3 (Already Unrestricted - Verify)**:

These tools should already work at all tiers, but verify they don't have hidden tier checks:

- [ ] `analyze_code` - Verify no tier restrictions
- [ ] `update_symbol` - Verify no tier restrictions
- [ ] `unified_sink_detect` - Verify no tier restrictions
- [ ] `simulate_refactor` - Verify no tier restrictions
- [ ] `get_file_context` - Verify no tier restrictions
- [ ] `get_symbol_references` - Verify no tier restrictions
- [ ] `get_project_map` - Verify no tier restrictions
- [ ] `validate_paths` - Verify no tier restrictions
- [ ] `verify_policy_integrity` - Verify no tier restrictions
- [ ] `type_evaporation_scan` - Verify no tier restrictions

**Total Priority 3**: 1 hour to verify all

---

### MEDIUM PRIORITY: Testing

#### Unit Tests

- [ ] Test `get_tool_capabilities()` for all 20 tools × 3 tiers (60 test cases)
  - File: `tests/licensing/test_features.py`
  - Verify all capabilities returned correctly
  - Verify all limits set correctly
  - Estimated: 2 hours

- [ ] Test `has_capability()` for various capability checks
  - Test positive cases (capability exists)
  - Test negative cases (capability missing)
  - Test tier hierarchy (pro inherits community)
  - Estimated: 1 hour

- [ ] Test `get_upgrade_hint()` for various scenarios
  - Test COMMUNITY → PRO hints
  - Test PRO → ENTERPRISE hints
  - Test unknown capabilities
  - Estimated: 1 hour

- [ ] Test `get_all_tools_for_tier()` returns 20 tools for each tier
  - Estimated: 30 minutes

#### Integration Tests

- [ ] Test `security_scan` with COMMUNITY tier
  - Verify max_findings=10 enforced
  - Verify truncated flag set
  - Verify upgrade hints present
  - Verify no advanced features in result
  - File: `tests/integration/test_security_scan_tiers.py`
  - Estimated: 1 hour

- [ ] Test `security_scan` with PRO tier
  - Verify unlimited findings
  - Verify advanced features present (taint_flows, remediation)
  - Estimated: 1 hour

- [ ] Test `symbolic_execute` with COMMUNITY tier (max_paths=3)
  - File: `tests/integration/test_symbolic_execution_tiers.py`
  - Estimated: 1 hour

- [ ] Test `crawl_project` with COMMUNITY tier (discovery mode, max_files=100)
  - File: `tests/integration/test_crawl_project_tiers.py`
  - Estimated: 1 hour

- [ ] Test `extract_code` with COMMUNITY tier (no cross-file deps)
  - File: `tests/integration/test_extract_code_tiers.py`
  - Estimated: 1 hour

**Total Testing**: ~10 hours

---

### MEDIUM PRIORITY: Documentation Updates

- [ ] Update `docs/mcp_tools_by_tier.md`
  - Change from availability matrix (❌/✅) to capability matrix
  - Show all 20 tools with ✅ at all tiers
  - Add "Capabilities" column showing what differs by tier
  - Estimated: 1 hour

- [ ] Update main documentation to emphasize "all tools available"
  - Update any references to "X tools at community tier"
  - Emphasize "All 20 tools, different capabilities"
  - Estimated: 1 hour

- [ ] Create migration guide for v3.3.0
  - Document breaking change: "All tools now available to COMMUNITY"
  - Show before/after for each tier
  - Explain new upgrade hint messaging
  - File: `docs/guides/migration_v3.3.0.md`
  - Estimated: 2 hours

- [ ] Update marketing/landing page copy
  - Change messaging from "Get more tools" to "Get more from each tool"
  - Emphasize capability progression
  - Estimated: 1 hour

**Total Documentation**: ~5 hours

---

### LOW PRIORITY: Polish

- [ ] Add examples for each gated tool
  - Show COMMUNITY vs PRO vs ENTERPRISE results side-by-side
  - File: `examples/tier_comparison_examples.py`
  - Estimated: 2 hours

- [ ] Create video/GIF showing upgrade hints in action
  - Demo COMMUNITY hitting limit
  - Demo upgrade hint appearing
  - Demo PRO getting unlimited results
  - Estimated: 2 hours

- [ ] Add telemetry for upgrade hints
  - Track how often users hit limits
  - Track which features drive upgrades
  - Estimated: 2 hours

- [ ] Update pricing page
  - Show capability comparison table
  - Link to tier_capabilities_matrix.md
  - Estimated: 1 hour

**Total Polish**: ~7 hours

---

## Estimated Total Work Remaining

| Phase | Priority | Hours | Status |
|-------|----------|-------|--------|
| Tool Implementation | HIGH | 20-25 | Not started |
| Testing | MEDIUM | 10 | Not started |
| Documentation | MEDIUM | 5 | Not started |
| Polish | LOW | 7 | Not started |
| **TOTAL** | | **42-47 hours** | **~12% complete** |

---

## Success Criteria

### Phase 2 Complete When:

- [ ] All 10 gated tools enforce limits at COMMUNITY tier
- [ ] All 10 gated tools add upgrade hints when limits hit
- [ ] All 10 gated tools provide advanced features at PRO/ENTERPRISE tier
- [ ] All 10 unrestricted tools verified to work at all tiers
- [ ] Integration tests pass for all tiers
- [ ] Documentation updated to reflect "all tools available"
- [ ] Migration guide published for v3.3.0

### Phase 3 (Optional Enhancements):

- [ ] Telemetry showing upgrade conversion rates
- [ ] Video demos of tier differences
- [ ] Pricing page updated
- [ ] Marketing materials updated

---

## Quick Start: Implementing Your First Tool

Want to get started? Here's how to update `security_scan` (highest priority):

### Step 1: Find the Handler

```bash
cd src/code_scalpel/mcp/handlers
# Edit security_analysis.py
```

### Step 2: Add Capability Check

```python
from code_scalpel.licensing import (
    get_current_tier,
    get_tool_capabilities,
    has_capability,
    get_upgrade_hint,
)

async def security_scan(code: str, file_path: str = None) -> dict:
    # Get tier and capabilities
    tier = get_current_tier()
    caps = get_tool_capabilities("security_scan", tier)
    
    # Run scan (all tiers)
    all_vulnerabilities = _run_security_scan(code, file_path)
    
    # Apply limit
    max_findings = caps["limits"]["max_findings"]
    if max_findings and len(all_vulnerabilities) > max_findings:
        vulnerabilities = all_vulnerabilities[:max_findings]
        truncated = True
    else:
        vulnerabilities = all_vulnerabilities
        truncated = False
    
    result = {
        "tier": tier,
        "vulnerabilities": vulnerabilities,
    }
    
    # Add upgrade hint if truncated
    if truncated:
        result["truncated"] = True
        result["total_vulnerabilities"] = len(all_vulnerabilities)
        result["upgrade_hints"] = [
            f"Showing {max_findings}/{len(all_vulnerabilities)} vulnerabilities.",
            get_upgrade_hint("security_scan", "full_vulnerability_list", tier)
        ]
    
    # Add advanced features if available
    if has_capability("security_scan", "advanced_taint_flow", tier):
        result["taint_flows"] = _analyze_taint_flows(code, vulnerabilities)
    
    if has_capability("security_scan", "remediation_suggestions", tier):
        result["remediation"] = _generate_remediation(vulnerabilities)
    
    if has_capability("security_scan", "compliance_reporting", tier):
        result["compliance"] = _generate_compliance_report(vulnerabilities)
    
    return result
```

### Step 3: Test It

```python
# tests/integration/test_security_scan_tiers.py
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_security_scan_community_limits():
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        result = await security_scan(vulnerable_code)
        
        assert len(result["vulnerabilities"]) == 10
        assert result["truncated"] is True
        assert "upgrade_hints" in result
        assert "taint_flows" not in result  # Not available at community

@pytest.mark.asyncio
async def test_security_scan_pro_unlimited():
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        result = await security_scan(vulnerable_code)
        
        assert len(result["vulnerabilities"]) > 10
        assert result.get("truncated") is False
        assert "taint_flows" in result  # Available at pro
```

### Step 4: Document It

Update the tool's docstring to mention tier-based features:

```python
async def security_scan(code: str, file_path: str = None) -> dict:
    """
    Security vulnerability scanning with tier-based features.
    
    Available at ALL tiers:
    - COMMUNITY: Basic vulnerabilities, max 10 findings
    - PRO: Advanced taint analysis, unlimited findings, remediation
    - ENTERPRISE: Cross-file taint, compliance reporting, custom rules
    
    Args:
        code: Source code to scan
        file_path: Optional file path for context
    
    Returns:
        Security scan results with tier-appropriate features
    """
```

**That's it!** Repeat this pattern for the other 9 gated tools.

---

## Getting Help

Questions about implementation:
- Read: [implementing_feature_gating.md](../guides/implementing_feature_gating.md)
- Read: [feature_gating_example.py](../../examples/feature_gating_example.py)
- Read: [tier_capabilities_matrix.md](../reference/tier_capabilities_matrix.md)

Questions about architecture:
- Read: [all_tools_available_summary.md](all_tools_available_summary.md)
- Read: [all_tools_available_diagram.md](all_tools_available_diagram.md)
- Read: [feature_gating_analysis.md](feature_gating_analysis.md)

---

## See Also

- [DEVELOPMENT_ROADMAP.md](../../DEVELOPMENT_ROADMAP.md) - Overall project roadmap
- [TIER_CONFIGURATION.md](../TIER_CONFIGURATION.md) - Tier setup guide
- [features.py](../../src/code_scalpel/licensing/features.py) - Capability definitions
