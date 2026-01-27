"""Code Scalpel testing framework for tier-aware tests."""

from code_scalpel.testing.adapters.tier_adapter import TierAdapter, TierAdapterFactory
from code_scalpel.testing.assertions import (
    assert_all_capabilities,
    assert_capability_present,
    assert_limit_value,
    assert_limits_present,
    assert_tier_detected,
    assert_tool_available,
    assert_tool_count,
    assert_tool_unavailable,
)
from code_scalpel.testing.markers import (
    performance,
    regression,
    requires_capability,
    requires_tier,
    requires_tool,
    security,
    tier_aware,
)

__all__ = [
    "TierAdapter",
    "TierAdapterFactory",
    "assert_tool_available",
    "assert_tool_unavailable",
    "assert_capability_present",
    "assert_limit_value",
    "assert_limits_present",
    "assert_all_capabilities",
    "assert_tier_detected",
    "assert_tool_count",
    "requires_tier",
    "requires_tool",
    "requires_capability",
    "tier_aware",
    "performance",
    "security",
    "regression",
]
