# Feature Gating Architecture Analysis

**Date**: 2025-12-25  
**Context**: Evaluating current tool-level gating vs desired parameter-level gating  
**Status**: Analysis Phase - Implementation Pending

---

## Current State (v3.2.8)

### Architecture: Tool-Level + Parameter-Level Hybrid

The current implementation uses a **hybrid approach**:

1. **Some tools are hidden by tier** (tool-level gating)
2. **Some tools have behavioral differences** (parameter-level gating)

#### Tool-Level Gating (Tool Availability)

From `docs/reference/mcp_tools_by_tier.md`:

| Tool | Community | Pro | Enterprise |
|------|-----------|-----|------------|
| `analyze_code` | ✅ | ✅ | ✅ |
| `crawl_project` | ❌ | ✅ | ✅ |
| `cross_file_security_scan` | ❌ | ❌ | ✅ |
| `extract_code` | ✅ | ✅ | ✅ |
| `generate_unit_tests` | ❌ | ✅ | ✅ |
| `get_call_graph` | ❌ | ✅ | ✅ |
| `get_cross_file_dependencies` | ❌ | ❌ | ✅ |
| `symbolic_execute` | ❌ | ✅ | ✅ |
| `simulate_refactor` | ❌ | ✅ | ✅ |
| `type_evaporation_scan` | ❌ | ✅ | ✅ |
| `verify_policy_integrity` | ❌ | ❌ | ✅ |

**Problem**: Community users can't even access these tools. They're completely hidden.

#### Parameter-Level Gating (Behavioral Restrictions)

From `docs/release_notes/RELEASE_NOTES_v3.2.8.md`:

**`crawl_project`**:
- **Community**: Discovery mode only (file inventory, entrypoints, no complexity analysis)
- **Pro/Enterprise**: Deep crawl (full AST parsing, complexity, dependencies)

**`get_call_graph`**:
- **Community**: Depth limited to 3 hops
- **Pro/Enterprise**: Configurable depth (up to 50 hops)

**`get_graph_neighborhood`**:
- **Community**: Limited to k=1 (immediate neighbors only)
- **Pro/Enterprise**: Configurable k-hop traversal

**`get_symbol_references`**:
- **Community**: Returns first 10 files only
- **Pro/Enterprise**: Full project-wide search

**This is the right approach** - tools are available, but features are restricted.

---

## User's Vision: All Tools Available, Features Gated

### Proposed Architecture

**Core Principle**: Every MCP tool is available in COMMUNITY tier, but with restricted parameters/features.

### Examples of Parameter-Level Gating

#### `analyze_code`
- **Community**: 
  - Basic AST parsing
  - Function/class inventory
  - Simple line count metrics
- **Pro**:
  - Cyclomatic complexity metrics
  - Halstead complexity
  - Cognitive complexity
  - Import dependency analysis
- **Enterprise**:
  - Custom analysis rules
  - Organization-specific patterns
  - Compliance checks

#### `security_scan`
- **Community**:
  - Basic vulnerability detection (SQL injection, XSS, command injection)
  - Single-file taint analysis
  - Top 10 most critical findings only
- **Pro**:
  - Advanced taint flow analysis
  - Full vulnerability list (no limit)
  - Remediation suggestions
  - OWASP Top 10 categorization
- **Enterprise**:
  - Cross-file taint tracking
  - Custom security rules
  - Compliance reporting (SOC2, HIPAA, PCI-DSS)
  - Priority CVE alerting

#### `extract_code`
- **Community**:
  - Single-file extraction
  - No dependency resolution
  - Basic function/class extraction
- **Pro**:
  - Cross-file dependency resolution
  - Depth=1 (direct dependencies)
  - Context extraction (imports, constants)
- **Enterprise**:
  - Unlimited depth dependency resolution
  - Organization-wide symbol resolution
  - Custom extraction patterns

#### `symbolic_execute`
- **Community**:
  - Max 3 paths explored
  - Basic input generation
  - Simple constraints only
- **Pro**:
  - Max 10 paths explored
  - Complex constraint solving
  - String constraint support
- **Enterprise**:
  - Unlimited path exploration
  - Custom constraint solvers
  - Advanced symbolic types (lists, dicts)

#### `crawl_project`
- **Community**:
  - File inventory only (no parsing)
  - Entrypoint detection
  - Basic statistics (file count, line count)
  - Max 100 files
- **Pro**:
  - Full AST parsing
  - Complexity analysis
  - Dependency graph
  - Max 1000 files
- **Enterprise**:
  - Unlimited files
  - Organization-wide indexing
  - Cross-repository analysis
  - Custom metrics

---

## Implementation Approaches

### Approach 1: Hierarchical Feature Dictionary (Recommended)

```python
# src/code_scalpel/licensing/features.py

FEATURE_CAPABILITIES = {
    "analyze_code": {
        "community": {
            "enabled": True,
            "capabilities": ["basic_ast", "function_inventory", "class_inventory"],
            "limits": {"max_file_size_mb": 1},
        },
        "pro": {
            "enabled": True,
            "capabilities": [
                "basic_ast", "function_inventory", "class_inventory",
                "complexity_metrics", "halstead_metrics", "dependency_analysis"
            ],
            "limits": {"max_file_size_mb": 10},
        },
        "enterprise": {
            "enabled": True,
            "capabilities": [
                "basic_ast", "function_inventory", "class_inventory",
                "complexity_metrics", "halstead_metrics", "dependency_analysis",
                "custom_rules", "compliance_checks", "org_patterns"
            ],
            "limits": {"max_file_size_mb": 100},
        },
    },
    
    "security_scan": {
        "community": {
            "enabled": True,
            "capabilities": ["basic_vulnerabilities", "single_file_taint"],
            "limits": {
                "max_findings": 10,
                "vulnerability_types": ["sql_injection", "xss", "command_injection"],
            },
        },
        "pro": {
            "enabled": True,
            "capabilities": [
                "basic_vulnerabilities", "single_file_taint",
                "advanced_taint", "remediation", "owasp_categorization"
            ],
            "limits": {
                "max_findings": None,  # Unlimited
                "vulnerability_types": "all",
            },
        },
        "enterprise": {
            "enabled": True,
            "capabilities": [
                "basic_vulnerabilities", "single_file_taint",
                "advanced_taint", "remediation", "owasp_categorization",
                "cross_file_taint", "custom_rules", "compliance_reporting"
            ],
            "limits": {
                "max_findings": None,
                "vulnerability_types": "all",
            },
        },
    },
    
    "extract_code": {
        "community": {
            "enabled": True,
            "capabilities": ["single_file_extraction"],
            "limits": {"include_cross_file_deps": False, "max_depth": 0},
        },
        "pro": {
            "enabled": True,
            "capabilities": ["single_file_extraction", "cross_file_deps"],
            "limits": {"include_cross_file_deps": True, "max_depth": 1},
        },
        "enterprise": {
            "enabled": True,
            "capabilities": [
                "single_file_extraction", "cross_file_deps",
                "org_wide_resolution", "custom_patterns"
            ],
            "limits": {"include_cross_file_deps": True, "max_depth": None},
        },
    },
    
    # ... all other tools follow same pattern
}
```

#### Usage in Tool Implementation

```python
# src/code_scalpel/mcp/tools/analyze_code.py

from code_scalpel.licensing import LicenseManager, get_feature_capabilities

async def analyze_code(code: str, language: str = "python") -> Dict:
    """Analyze code structure with tier-based features."""
    
    manager = LicenseManager()
    tier = manager.get_current_tier()
    caps = get_feature_capabilities("analyze_code", tier)
    
    # Basic analysis (all tiers)
    result = {
        "functions": extract_functions(code),
        "classes": extract_classes(code),
        "imports": extract_imports(code),
    }
    
    # Pro/Enterprise: Add complexity metrics
    if "complexity_metrics" in caps["capabilities"]:
        result["complexity"] = calculate_complexity(code)
        result["halstead_metrics"] = calculate_halstead(code)
    
    # Enterprise: Add custom rules
    if "custom_rules" in caps["capabilities"]:
        result["custom_analysis"] = apply_custom_rules(code, manager.get_organization())
    
    # Add upgrade hints if features missing
    if tier == "community":
        result["upgrade_hints"] = [
            "Upgrade to PRO for complexity metrics and dependency analysis",
            "Upgrade to ENTERPRISE for custom rules and compliance checks"
        ]
    
    return result
```

### Approach 2: Capability Decorators

```python
# src/code_scalpel/licensing/decorators.py

from functools import wraps

def requires_capability(capability: str, upgrade_tier: str):
    """Decorator to gate functionality behind capability check."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = LicenseManager()
            tier = manager.get_current_tier()
            caps = get_feature_capabilities(func.__module__, tier)
            
            if capability not in caps["capabilities"]:
                return {
                    "error": f"Feature '{capability}' requires {upgrade_tier} tier",
                    "upgrade_hint": f"Upgrade to {upgrade_tier} to unlock {capability}",
                }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage in tools
@requires_capability("complexity_metrics", "pro")
def calculate_complexity(code: str) -> Dict:
    """Calculate cyclomatic complexity (PRO+)."""
    return {"cyclomatic": ..., "cognitive": ...}


@requires_capability("custom_rules", "enterprise")
def apply_custom_rules(code: str, org: str) -> Dict:
    """Apply organization-specific analysis rules (ENTERPRISE)."""
    return {"violations": ..., "compliance": ...}
```

### Approach 3: Runtime Parameter Validation

```python
# src/code_scalpel/mcp/tools/extract_code.py

async def extract_code(
    file_path: str,
    target_type: str,
    target_name: str,
    include_cross_file_deps: bool = False,
    max_depth: int = 0,
) -> Dict:
    """Extract code with tier-based depth limits."""
    
    manager = LicenseManager()
    tier = manager.get_current_tier()
    caps = get_feature_capabilities("extract_code", tier)
    
    # Enforce tier limits
    limits = caps["limits"]
    
    if include_cross_file_deps and not limits["include_cross_file_deps"]:
        return {
            "error": "Cross-file dependencies require PRO tier",
            "upgrade_hint": "Upgrade to PRO for cross-file dependency resolution",
        }
    
    if max_depth and limits["max_depth"] is not None:
        max_depth = min(max_depth, limits["max_depth"])
        upgrade_hint = (
            f"Depth limited to {limits['max_depth']} in {tier.upper()} tier. "
            f"Upgrade to ENTERPRISE for unlimited depth."
        )
    
    # Proceed with extraction...
    result = perform_extraction(file_path, target_type, target_name, max_depth)
    
    if upgrade_hint:
        result["upgrade_hints"] = [upgrade_hint]
    
    return result
```

---

## Comparison Matrix

| Aspect | Current (v3.2.8) | Approach 1 (Hierarchical) | Approach 2 (Decorators) | Approach 3 (Runtime) |
|--------|------------------|---------------------------|-------------------------|----------------------|
| **Tool Availability** | Tool-level hiding | All tools available | All tools available | All tools available |
| **Feature Gating** | Partial (4 tools) | Comprehensive | Comprehensive | Comprehensive |
| **Complexity** | Low | Medium | Medium | High |
| **Maintainability** | Poor (scattered checks) | Excellent (centralized) | Good (explicit) | Poor (scattered) |
| **Testability** | Difficult | Easy (mock capabilities) | Easy (mock decorators) | Difficult |
| **Documentation** | External | Self-documenting | Self-documenting | Requires external docs |
| **Performance** | Fast | Fast (cached lookup) | Medium (decorator overhead) | Fast |
| **Upgrade Hints** | Manual | Automatic | Automatic | Manual |
| **Type Safety** | None | Full (TypedDict) | Partial | None |

---

## Recommended Approach

**Approach 1 (Hierarchical Feature Dictionary)** is recommended because:

1. **Centralized Configuration**: All tier capabilities in one place
2. **Self-Documenting**: Feature matrix is explicit and visible
3. **Testable**: Easy to mock and test different tier configurations
4. **Maintainable**: Adding new tools/features is straightforward
5. **Automatic Upgrade Hints**: Can compare current vs required capabilities
6. **Type-Safe**: Can use TypedDict for capability schemas

### Implementation Plan

#### Phase 1: Infrastructure (Week 1)
1. Create `src/code_scalpel/licensing/features.py` with FEATURE_CAPABILITIES
2. Add `get_feature_capabilities(tool_id, tier)` helper function
3. Add `check_capability(tool_id, capability, tier)` validation
4. Add `get_upgrade_hint(tool_id, missing_capability, current_tier)` generator
5. Update LicenseManager to use feature capabilities instead of tool-level checks

#### Phase 2: Tool Migration (Week 2-3)
1. **High Priority**: Migrate 4 existing parameter-gated tools
   - `crawl_project`
   - `get_call_graph`
   - `get_graph_neighborhood`
   - `get_symbol_references`
2. **Medium Priority**: Make currently-hidden tools available with restrictions
   - `symbolic_execute` (path limit: 3 → 10 → unlimited)
   - `generate_unit_tests` (test count limit: 5 → 20 → unlimited)
   - `simulate_refactor` (complexity limit: basic → advanced → custom)
3. **Low Priority**: Add parameter gating to currently-unrestricted tools
   - `analyze_code` (metrics: basic → pro → enterprise)
   - `security_scan` (findings limit: 10 → unlimited, compliance reporting)
   - `extract_code` (depth limit: 0 → 1 → unlimited)

#### Phase 3: Documentation (Week 4)
1. Update `docs/reference/mcp_tools_by_tier.md` to show capabilities not availability
2. Create `docs/reference/tier_capabilities_matrix.md` with detailed feature breakdown
3. Update README to emphasize "all tools available, features gated"
4. Add upgrade hint examples to docs

#### Phase 4: Testing (Week 4)
1. Add tier capability tests for all 20 tools
2. Test upgrade hints appear correctly
3. Test parameter enforcement
4. Test graceful degradation

---

## Migration Strategy

### Backward Compatibility

**Challenge**: Existing users expect certain tools to be completely hidden in Community.

**Solution**: Two-phase rollout:

**Phase A (v3.3.0)**: Hybrid Mode
- Keep tool-level hiding for now
- Add parameter-level gating to exposed tools
- Announce change in release notes: "Future release will expose all tools with restrictions"

**Phase B (v3.4.0)**: Full Parameter-Level Gating
- Expose all tools to Community with restricted parameters
- Remove tool-level hiding
- Update all documentation
- Breaking change: Community users now see tools they couldn't before (but with limits)

### Communication Plan

1. **Blog Post**: "All Tools, All Tiers: Code Scalpel's New Licensing Model"
2. **Migration Guide**: Show before/after for each tier
3. **FAQ**: Address common questions about the change
4. **Pricing Page Update**: Emphasize "feature access" not "tool access"

---

## Open Questions

1. **Should some tools remain ENTERPRISE-only?**
   - Example: `verify_policy_integrity` (requires signing infrastructure)
   - Recommendation: Make available but return "policy verification not available in Community" message

2. **What's the right limit for Community tier?**
   - Too restrictive: Users can't evaluate usefulness
   - Too permissive: No incentive to upgrade
   - Recommendation: "Useful for small projects, limited for large codebases"

3. **Should we version the capability schema?**
   - Future-proofing for capability changes
   - Recommendation: Yes, add `schema_version: "1.0"` to FEATURE_CAPABILITIES

4. **How do we handle new tools added in future?**
   - Default to Community-available with restrictions?
   - Or case-by-case basis?
   - Recommendation: Default to Community-available unless truly ENTERPRISE-only (governance, compliance)

---

## Next Steps

1. **Get User Approval**: Confirm this approach aligns with business goals
2. **Prototype Phase 1**: Implement infrastructure in feature branch
3. **Migrate One Tool**: Test with `analyze_code` as proof-of-concept
4. **Review and Iterate**: Get feedback before full migration
5. **Document Exhaustively**: Create tier capability matrix
6. **Execute Phase 2-4**: Full tool migration over 4 weeks

---

**Decision Required**: Should we proceed with Approach 1 (Hierarchical Feature Dictionary)?
