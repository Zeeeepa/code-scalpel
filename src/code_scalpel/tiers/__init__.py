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
"""

# TODO [COMMUNITY_P0_CRITICAL] Implement @requires_tier decorator with runtime tier checking
# TODO [COMMUNITY_P0_CRITICAL] Add graceful error messages for tier requirement failures
# TODO [COMMUNITY_P0_CRITICAL] Create decorator tests (20 tests)
# TODO [COMMUNITY_P1_HIGH] Build central feature→tier mapping registry
# TODO [COMMUNITY_P1_HIGH] Implement dynamic feature registration
# TODO [COMMUNITY_P1_HIGH] Add feature discovery functionality
# TODO [COMMUNITY_P1_HIGH] Create registry tests (25 tests)
# TODO [COMMUNITY_P2_MEDIUM] Map tools to tier requirements
# TODO [COMMUNITY_P2_MEDIUM] Implement tool availability filtering
# TODO [COMMUNITY_P2_MEDIUM] Add tool metadata enrichment
# TODO [COMMUNITY_P2_MEDIUM] Create MCP integration tests (20 tests)
# TODO [PRO_P1_HIGH] Implement feature bundles for grouping related features
# TODO [PRO_P1_HIGH] Add bundle-level gating logic
# TODO [PRO_P1_HIGH] Create bundle tests (20 tests)
# TODO [PRO_P2_MEDIUM] Implement beta feature flags system
# TODO [PRO_P2_MEDIUM] Add A/B testing support
# TODO [PRO_P2_MEDIUM] Create feature flag tests (15 tests)
# TODO [PRO_P3_LOW] Implement feature usage tracking
# TODO [PRO_P3_LOW] Add tier adoption metrics
# TODO [PRO_P3_LOW] Create analytics tests (10 tests)
# TODO [ENTERPRISE_P2_MEDIUM] Implement custom tier definitions
# TODO [ENTERPRISE_P2_MEDIUM] Add feature override rules
# TODO [ENTERPRISE_P2_MEDIUM] Create custom tier tests (20 tests)
# TODO [ENTERPRISE_P3_LOW] Implement policy-based gating
# TODO [ENTERPRISE_P3_LOW] Add audit logging for governance
# TODO [ENTERPRISE_P3_LOW] Create policy tests (15 tests)
# TODO [ENTERPRISE_P4_LOW] Implement remote feature enablement
# TODO [ENTERPRISE_P4_LOW] Add real-time tier updates
# TODO [ENTERPRISE_P4_LOW] Create dynamic control tests (10 tests)

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


# [20260102_REFACTOR] Imports below remain for backward-compatible API surface.
# ruff: noqa: E402
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
