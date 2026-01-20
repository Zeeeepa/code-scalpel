# Quick Reference: All 22 Tools at Every Tier

## The Model

**All 22 Code Scalpel tools are available at Community, Pro, and Enterprise tiers.**
Tier determines feature access and capability limits.

## All 22 Tools

```
analyze_code                 • code_policy_check            • crawl_project
cross_file_security_scan     • extract_code                 • generate_unit_tests
get_call_graph               • get_cross_file_dependencies  • get_file_context
get_graph_neighborhood       • get_project_map              • get_symbol_references
rename_symbol                • scan_dependencies            • security_scan
simulate_refactor            • symbolic_execute             • type_evaporation_scan
unified_sink_detect          • update_symbol                • validate_paths
verify_policy_integrity
```

## Tier-Based Limitations (Examples)

### Example 1: get_call_graph
```
Community  → max_depth=3, max_nodes=50
Pro        → max_depth=50, max_nodes=500
Enterprise → unlimited depth, unlimited nodes
```

### Example 2: code_policy_check
```
Community  → 50 rules, no custom rules, no compliance mode
Pro        → 200 rules, custom rules enabled, no compliance
Enterprise → unlimited rules, custom rules, compliance + audit trail + PDF reports
```

### Example 3: extract_code
```
Community  → 1MB files, no cross-file deps, depth=0
Pro        → 10MB files, cross-file deps (direct only), depth=1
Enterprise → 100MB files, deep cross-file deps, unlimited depth
```

## Configuration

**Source of Truth**: [.code-scalpel/limits.toml](.code-scalpel/limits.toml)

Each tool has sections like:

```toml
[community.TOOL_NAME]
limit_key = value

[pro.TOOL_NAME]
limit_key = value

[enterprise.TOOL_NAME]
# omit = unlimited
```

## How It Works

1. ✅ **Tool Registration**: All 22 tools register at startup (no tier-gating)
2. ✅ **Tier Detection**: User's tier determined from JWT license
3. ✅ **Limit Loading**: Tool loads limits from [TIER.TOOL] section
4. ✅ **Enforcement**: Tool applies limits during execution
5. ✅ **Graceful Degradation**: Partial results if limits exceeded

## Key Principles

- ✅ All tools available at all tiers
- ✅ NO `@requires_tier` decorators on tools
- ✅ Limits defined in externalized config (limits.toml)
- ✅ Tier controls feature depth, not tool access
- ✅ Easy to customize per deployment

## User Experience

| Scenario | Old Model | New Model |
|----------|-----------|-----------|
| Community user wants to use symbolic_execute | ❌ Error: "Not available in Community" | ✅ Works with conservative limits (max_paths=50) |
| Pro user wants larger analysis depth | ❌ Need Enterprise | ✅ Pro tier provides depth=50, can upgrade for unlimited |
| Deployer wants to adjust limits | ❌ Need to recompile | ✅ Edit limits.toml, restart server |

## Related Documentation

- [TIER_MODEL_UPDATED.md](TIER_MODEL_UPDATED.md) - Complete guide with examples
- [TIER_MODEL_IMPLEMENTATION.md](TIER_MODEL_IMPLEMENTATION.md) - Technical implementation
- [.code-scalpel/limits.toml](.code-scalpel/limits.toml) - Configuration details

## Verify It Works

```bash
# All 22 tools should be registered at startup
python -m code_scalpel.mcp.server
# Output: Tool registration complete - 22 tools registered

# Check Community limits
CODE_SCALPEL_TIER=community python -c \
  "from code_scalpel.licensing import get_limits; \
   print(get_limits()['community']['get_call_graph'])"
# Output: {'max_depth': 3, 'max_nodes': 50}

# Check Enterprise unlimited
CODE_SCALPEL_TIER=enterprise python -c \
  "from code_scalpel.licensing import get_limits; \
   print(get_limits()['enterprise']['get_call_graph'])"
# Output: {} (empty dict = unlimited)
```

## Summary

**All 22 tools. Every tier. Tier controls features.**

This is the correct, modern SaaS model where users have access to all features from day one, but deeper capability comes with higher tiers.

---

**Version**: 1.0.0  
**Date**: January 20, 2026  
**Status**: ✅ Ready for Production
