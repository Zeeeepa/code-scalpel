#!/usr/bin/env python3
"""
Test to verify enterprise tier has unlimited k and max_nodes in practice.
"""

from code_scalpel.licensing.features import get_tool_capabilities

def test_tier_limits(tier: str):
    caps = get_tool_capabilities("get_graph_neighborhood", tier)
    limits = caps.get("limits", {})
    max_k = limits.get("max_k")
    max_nodes = limits.get("max_nodes")
    
    print(f"{tier.upper():12} - max_k: {max_k!r:6}, max_nodes: {max_nodes!r:6}", end="")
    
    # Simulate the MCP server logic
    requested_k = 100
    requested_max_nodes = 5000
    
    if max_k is not None and requested_k > max_k:
        actual_k = int(max_k)
        k_limited = True
    else:
        actual_k = requested_k
        k_limited = False
    
    if max_nodes is not None and requested_max_nodes > max_nodes:
        actual_max_nodes = int(max_nodes)
        nodes_limited = True
    else:
        actual_max_nodes = requested_max_nodes
        nodes_limited = False
    
    if k_limited or nodes_limited:
        print(f" → k={actual_k}, nodes={actual_max_nodes} (LIMITED)")
    else:
        print(f" → k={actual_k}, nodes={actual_max_nodes} (UNLIMITED)")

print("=" * 80)
print("TIER LIMIT APPLICATION TEST")
print("Request: k=100, max_nodes=5000")
print("=" * 80)
test_tier_limits("community")
test_tier_limits("pro")
test_tier_limits("enterprise")
print()
print("Expected:")
print("  Community: Limited to k=1, max_nodes=20")
print("  Pro: Limited to k=5, max_nodes=100")
print("  Enterprise: Unlimited (None) - should allow k=100, max_nodes=5000")
