"""
Tiers Module - Feature gating and tier management for Code Scalpel.

[20251225_FEATURE] Created as part of Project Reorganization Issue #5.
Implements the three-tier feature gating system (COMMUNITY/PRO/ENTERPRISE).

This module provides:
- TierConfig: Tier configuration and feature definitions
- @requires_tier: Decorator for tier-gated functions
- FeatureRegistry: Central registry of features and their tiers
- ToolRegistry: MCP tool tier mapping

Architecture:
    Features are mapped to minimum required tiers.
    @requires_tier decorator enforces tier requirements at runtime.
    Graceful degradation provides helpful upgrade messages.

Usage:
    from code_scalpel.tiers import requires_tier, Tier, is_feature_enabled

    @requires_tier(Tier.PRO)
    def advanced_security_scan():
        # Only runs if user has PRO or ENTERPRISE tier
        pass

    if is_feature_enabled("security_scan"):
        # Feature is available
        pass

TODO ITEMS: tiers/__init__.py
============================================================================
COMMUNITY TIER - Core Feature Gating (P0-P2)
============================================================================

# [P0_CRITICAL] Decorator implementation:
#     - @requires_tier decorator
#     - Runtime tier checking
#     - Graceful error messages
#     - Test count: 20 tests (decorator)

# [P1_HIGH] Feature registry:
#     - Central feature→tier mapping
#     - Dynamic feature registration
#     - Feature discovery
#     - Test count: 25 tests (registry)

# [P2_MEDIUM] MCP tool integration:
#     - Tool→tier mapping
#     - Tool availability filtering
#     - Tool metadata enrichment
#     - Test count: 20 tests (MCP integration)

============================================================================
PRO TIER - Advanced Feature Gating (P1-P3)
============================================================================

# [P1_HIGH] Feature bundles:
#     - Group related features
#     - Bundle-level gating
#     - Bundle metadata
#     - Test count: 20 tests (bundles)

# [P2_MEDIUM] Feature flags:
#     - Beta feature flags
#     - A/B testing support
#     - Feature rollout control
#     - Test count: 15 tests (flags)

# [P3_LOW] Usage analytics:
#     - Feature usage tracking
#     - Tier adoption metrics
#     - Test count: 10 tests (analytics)

============================================================================
ENTERPRISE TIER - Advanced Gating Features (P2-P4)
============================================================================

# [P2_MEDIUM] Custom tiers:
#     - Define custom tier levels
#     - Feature override rules
#     - Organization-specific features
#     - Test count: 20 tests (custom)

# [P3_LOW] Policy-based gating:
#     - Governance policy integration
#     - Audit logging
#     - Compliance enforcement
#     - Test count: 15 tests (policy)

# [P4_LOW] Dynamic feature control:
#     - Remote feature enablement
#     - Real-time tier updates
#     - Feature kill switches
#     - Test count: 10 tests (dynamic)

============================================================================
TOTAL ESTIMATED TESTS: 155 tests
============================================================================
"""

from enum import Enum


# [20251225_FEATURE] Re-export Tier from licensing for convenience
class Tier(Enum):
    """License tier levels for Code Scalpel."""

    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    @classmethod
    def from_string(cls, value: str) -> "Tier":
        """Convert string to Tier enum."""
        value_lower = value.lower().strip()
        for tier in cls:
            if tier.value == value_lower:
                return tier
        return cls.COMMUNITY

    def __ge__(self, other: "Tier") -> bool:
        """Compare tiers (ENTERPRISE >= PRO >= COMMUNITY)."""
        order = {Tier.COMMUNITY: 0, Tier.PRO: 1, Tier.ENTERPRISE: 2}
        return order[self] >= order[other]

    def __gt__(self, other: "Tier") -> bool:
        order = {Tier.COMMUNITY: 0, Tier.PRO: 1, Tier.ENTERPRISE: 2}
        return order[self] > order[other]

    def __le__(self, other: "Tier") -> bool:
        return other >= self

    def __lt__(self, other: "Tier") -> bool:
        return other > self


# [20251225_FEATURE] Import from submodules
from .decorators import TierRequirementError, requires_feature, requires_tier
from .feature_registry import (
    Feature,
    FeatureRegistry,
    get_feature_tier,
    get_registry,
    is_feature_enabled,
)
from .tool_registry import (
    MCPTool,
    ToolRegistry,
    get_available_tools,
    get_tool_registry,
    is_tool_available,
)

__all__ = [
    # Tier enum
    "Tier",
    # Decorators
    "requires_tier",
    "requires_feature",
    "TierRequirementError",
    # Feature registry
    "FeatureRegistry",
    "Feature",
    "is_feature_enabled",
    "get_feature_tier",
    "get_registry",
    # Tool registry
    "ToolRegistry",
    "MCPTool",
    "get_available_tools",
    "is_tool_available",
    "get_tool_registry",
]

__version__ = "1.0.0"
