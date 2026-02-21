import os
from tests.utils.tier_setup import tier_context
from code_scalpel.licensing.features import has_capability, get_tool_capabilities
from code_scalpel.mcp.server import _get_current_tier

with tier_context("pro", skip_if_missing=True):
    tier = _get_current_tier()
    print(f"Tier: {tier}")
    caps = get_tool_capabilities("analyze_code", tier)
    print(f"Capabilities: {caps.get('capabilities', set())}")
    has_halstead = has_capability("analyze_code", "halstead_metrics", tier)
    print(f"Has halstead: {has_halstead}")
