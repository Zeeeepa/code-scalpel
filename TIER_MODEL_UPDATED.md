# Code Scalpel - Updated Tier Model

**Status**: COMPLETE ✅  
**Date**: January 20, 2026  
**Change**: All 22 tools now available at every tier with tier-based limitations

---

## New Tier Model

### Architecture Change

**OLD MODEL**: Tools assigned to specific tiers
- Community: 6 tools
- Pro: 8 tools (includes Community tools)
- Enterprise: 8 tools (includes Pro + Community tools)

**NEW MODEL**: All tools available at all tiers with capability limitations
- Community: All 22 tools with basic features
- Pro: All 22 tools with enhanced features
- Enterprise: All 22 tools with full features

---

## What This Means

### All 22 Tools Available Everywhere

Every user, regardless of tier, has access to all 22 Code Scalpel tools:

```
analyze_code
code_policy_check
crawl_project
cross_file_security_scan
extract_code
generate_unit_tests
get_call_graph
get_cross_file_dependencies
get_file_context
get_graph_neighborhood
get_project_map
get_symbol_references
rename_symbol
scan_dependencies
security_scan
simulate_refactor
symbolic_execute
type_evaporation_scan
unified_sink_detect
update_symbol
validate_paths
verify_policy_integrity
```

### Tier Determines Capability Limits

Each tool has three sets of configuration in [limits.toml](.code-scalpel/limits.toml):

**Community Tier Limits:**
- Conservative resource limits (smaller files, shallower analysis)
- Basic features only (no custom rules, no compliance audit trails)
- Example: analyze_code max_file_size=1MB vs 100MB (Enterprise)

**Pro Tier Limits:**
- Moderate resource limits (larger files, deeper analysis)
- Enhanced features enabled (custom rules, semantic validation)
- Example: extract_code with cross-file dependencies enabled

**Enterprise Tier Limits:**
- No limits (or very generous limits)
- All features enabled (compliance audit trails, PDF reports, deep analysis)
- Example: symbolic_execute with unlimited paths and all constraint types

---

## Examples of Tier-Based Limitations

### Tool: analyze_code

| Tier | Max File Size | Languages | Detail Level |
|------|---------------|-----------|--------------|
| Community | 1 MB | Python, JS, TS, Java | Basic |
| Pro | 10 MB | Python, JS, TS, Java | Detailed |
| Enterprise | 100 MB | All (roadmap) | Comprehensive |

**Result**: All tiers can use analyze_code, but with different limits.

### Tool: get_call_graph

| Tier | Max Depth | Max Nodes |
|------|-----------|-----------|
| Community | 3 | 50 |
| Pro | 50 | 500 |
| Enterprise | Unlimited | Unlimited |

**Result**: All tiers can use get_call_graph, but Community gets shallower graphs.

### Tool: extract_code

| Tier | Cross-File Deps | Max Depth | Max Size |
|------|-----------------|-----------|----------|
| Community | No | 0 | 1 MB |
| Pro | Yes (direct) | 1 | 10 MB |
| Enterprise | Yes (deep) | Unlimited | 100 MB |

**Result**: All tiers can use extract_code, but with different capabilities.

### Tool: code_policy_check

| Tier | Rules | Custom Rules | Compliance | Audit Trail | PDF Reports |
|------|-------|--------------|-----------|-------------|-------------|
| Community | 50 | No | No | No | No |
| Pro | 200 | Yes | No | No | No |
| Enterprise | Unlimited | Yes | Yes | Yes | Yes |

**Result**: All tiers can check code policies, but with different feature sets.

---

## Configuration in limits.toml

The [.code-scalpel/limits.toml](.code-scalpel/limits.toml) file defines limits for all tools at all tiers:

```toml
[community.analyze_code]
max_file_size_mb = 1
languages = ["python", "javascript", "typescript", "java"]

[pro.analyze_code]
max_file_size_mb = 10
languages = ["python", "javascript", "typescript", "java"]

[enterprise.analyze_code]
max_file_size_mb = 100
# languages unlimited
```

### Key Principles

1. **All Tools Available**: Every tool has a section for [community.TOOL], [pro.TOOL], [enterprise.TOOL]
2. **Omit Means Unlimited**: If a limit is not specified, it's unlimited (or default value)
3. **Gradual Enhancement**: Community < Pro < Enterprise in terms of capabilities
4. **Externalized Configuration**: Limits can be changed without recompiling Python code

---

## Implementation Details

### How Tier Limits Are Applied

1. **Tool Registration**: All 22 tools register with MCP server at startup
   - No `@requires_tier` decorators at function level
   - Tools don't check tier - they receive limits as parameters

2. **Limit Enforcement**: When a tool is called, it loads its tier-specific limits from limits.toml
   - Community tier gets community limits
   - Pro tier gets pro limits
   - Enterprise tier gets enterprise limits

3. **Graceful Degradation**: If limits exceeded:
   - Tool returns partial results with warning
   - No errors thrown (graceful fallback)
   - User can adjust parameters for re-run

### Example: get_call_graph

```python
# Tool doesn't check tier - it just uses passed-in limits
async def get_call_graph(
    project_root: str,
    depth: int = None,  # None = use tier's max_depth
    max_nodes: int = None,
) -> CallGraphResult:
    # Limits loaded from limits.toml [TIER.get_call_graph]
    # depth defaults to min(depth, tier_max_depth)
    # max_nodes defaults to min(max_nodes, tier_max_nodes)
    
    # Rest of implementation...
```

---

## Deployment Impact

### What Stays the Same
- MCP server implementation (no changes needed)
- Tool function signatures (no changes needed)
- JSON-RPC protocol (no changes needed)

### What Changes
- Documentation (all 22 tools listed as "All Tiers")
- User expectations (feature access, not tool access)
- License messaging (upgrade for features, not tools)

### For Deployers
- limits.toml can be edited without recompiling
- Custom deployments can set different limits
- Tier detection via JWT license (unchanged)

---

## Benefits of This Model

✅ **More Transparent**: Users see all tools, understand tier differences  
✅ **More Flexible**: Developers can use all tools, upgrade for better limits  
✅ **More Fair**: No artificial tool gating, only capability limitation  
✅ **More Scalable**: Easy to add new limits without recompiling  
✅ **Better UX**: Users don't get "tool not found" errors

---

## Migration Path

If you had code expecting only certain tools at certain tiers:

**Before:**
```python
if tier == "enterprise":
    result = client.call("generate_unit_tests", code)  # Only in Enterprise
else:
    raise TierRequirementError("generate_unit_tests requires Enterprise")
```

**After:**
```python
# All tiers have the tool - limitations come from parameters
result = client.call("generate_unit_tests", code)
# Community tier gets max_test_cases=5
# Pro tier gets max_test_cases=20
# Enterprise tier gets unlimited
```

---

## Testing This Model

### Verify Tool Availability
```bash
# All tiers should list all 22 tools
CODE_SCALPEL_TIER=community python -m code_scalpel.mcp.server
CODE_SCALPEL_TIER=pro python -m code_scalpel.mcp.server
CODE_SCALPEL_TIER=enterprise python -m code_scalpel.mcp.server
```

### Verify Limit Enforcement
```bash
# Community: limited depth
CODE_SCALPEL_TIER=community code-scalpel-mcp < request-get-call-graph.json
# Result: max_depth=3

# Enterprise: unlimited depth
CODE_SCALPEL_TIER=enterprise code-scalpel-mcp < request-get-call-graph.json
# Result: max_depth=unlimited
```

---

## Summary

**The tier model has been updated to provide all 22 tools at every tier with tier-based feature limitations.**

This is more user-friendly, more transparent, and better aligns with modern SaaS practices where feature access determines tier (not tool access).

All configuration is in [limits.toml](.code-scalpel/limits.toml) and can be customized per deployment.

---

**Updated**: 2026-01-20 17:30 UTC  
**Status**: Ready for implementation
