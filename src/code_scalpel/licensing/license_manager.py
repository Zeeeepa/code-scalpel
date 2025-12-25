"""
License Manager - Central license management for Code Scalpel.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.

This module provides the central LicenseManager class that coordinates
tier detection, license validation, and feature availability checks.

TODO ITEMS: license_manager.py
============================================================================
COMMUNITY TIER (P0-P2)
============================================================================
# [P0_CRITICAL] Tier-based feature availability
# [P1_HIGH] Feature registry integration
# [P1_HIGH] Graceful degradation messaging
# [P2_MEDIUM] License state persistence

============================================================================
PRO TIER (P1-P3)
============================================================================
# [P1_HIGH] License key validation
# [P2_MEDIUM] License expiration handling
# [P2_MEDIUM] Grace period support
# [P3_LOW] License renewal reminders

============================================================================
ENTERPRISE TIER (P2-P4)
============================================================================
# [P2_MEDIUM] Seat counting
# [P3_LOW] Concurrent usage limits
# [P3_LOW] Organization management
# [P4_LOW] Custom license terms
============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set

from .tier_detector import TierDetector

logger = logging.getLogger(__name__)


@dataclass
class LicenseInfo:
    """Information about the current license."""

    tier: str
    is_valid: bool
    expiration_date: Optional[datetime] = None
    organization: Optional[str] = None
    seats: Optional[int] = None
    features: Set[str] = field(default_factory=set)
    metadata: Dict[str, str] = field(default_factory=dict)


# [20251225_FEATURE] Feature to tier mapping
# Features are available at the specified tier and all higher tiers
FEATURE_TIERS: Dict[str, str] = {
    # COMMUNITY features (always available)
    "analyze_code": "community",
    "extract_code": "community",
    "update_symbol": "community",
    "crawl_project": "community",
    "get_file_context": "community",
    "get_symbol_references": "community",
    "get_call_graph": "community",
    "get_project_map": "community",
    "validate_paths": "community",
    # PRO features
    "security_scan": "pro",
    "unified_sink_detect": "pro",
    "symbolic_execute": "pro",
    "generate_unit_tests": "pro",
    "simulate_refactor": "pro",
    "scan_dependencies": "pro",
    "get_cross_file_dependencies": "pro",
    "get_graph_neighborhood": "pro",
    # ENTERPRISE features
    "cross_file_security_scan": "enterprise",
    "verify_policy_integrity": "enterprise",
    "type_evaporation_scan": "enterprise",
    "autonomous_repair": "enterprise",
    "compliance_report": "enterprise",
}

# Tier hierarchy for comparison
TIER_HIERARCHY = {
    "community": 0,
    "pro": 1,
    "enterprise": 2,
}


class LicenseManager:
    """
    Central license management for Code Scalpel.

    Coordinates tier detection, license validation, and feature
    availability checks.

    Usage:
        manager = LicenseManager()

        # Get current tier
        tier = manager.get_current_tier()

        # Check feature availability
        if manager.is_feature_available("security_scan"):
            # Run security scan
            pass
        else:
            # Show upgrade message
            pass
    """

    def __init__(self, tier_detector: Optional[TierDetector] = None):
        """
        Initialize the license manager.

        Args:
            tier_detector: Optional custom tier detector
        """
        self._tier_detector = tier_detector or TierDetector()
        self._license_info: Optional[LicenseInfo] = None

    def get_current_tier(self) -> str:
        """
        Get the current license tier.

        Returns:
            Tier string: "community", "pro", or "enterprise"
        """
        return self._tier_detector.get_tier_string()

    def get_license_info(self) -> LicenseInfo:
        """
        Get detailed license information.

        Returns:
            LicenseInfo with tier, validity, and features
        """
        if self._license_info is None:
            tier = self.get_current_tier()
            available_features = self._get_available_features(tier)

            self._license_info = LicenseInfo(
                tier=tier,
                is_valid=True,  # COMMUNITY is always valid
                features=available_features,
            )

        return self._license_info

    def is_feature_available(self, feature_name: str) -> bool:
        """
        Check if a feature is available at the current tier.

        Args:
            feature_name: Name of the feature to check

        Returns:
            True if feature is available, False otherwise
        """
        current_tier = self.get_current_tier()
        required_tier = FEATURE_TIERS.get(feature_name, "community")

        current_level = TIER_HIERARCHY.get(current_tier, 0)
        required_level = TIER_HIERARCHY.get(required_tier, 0)

        return current_level >= required_level

    def get_upgrade_message(self, feature_name: str) -> Optional[str]:
        """
        Get an upgrade message for a feature not available at current tier.

        Args:
            feature_name: Name of the feature

        Returns:
            Upgrade message if feature unavailable, None if available
        """
        if self.is_feature_available(feature_name):
            return None

        required_tier = FEATURE_TIERS.get(feature_name, "community")
        current_tier = self.get_current_tier()

        return (
            f"Feature '{feature_name}' requires {required_tier.upper()} tier. "
            f"Current tier: {current_tier.upper()}. "
            f"Upgrade at https://code-scalpel.dev/pricing"
        )

    def get_available_features(self) -> List[str]:
        """
        Get list of all features available at current tier.

        Returns:
            List of feature names
        """
        tier = self.get_current_tier()
        return list(self._get_available_features(tier))

    def get_unavailable_features(self) -> List[str]:
        """
        Get list of features NOT available at current tier.

        Returns:
            List of feature names requiring upgrade
        """
        available = set(self.get_available_features())
        all_features = set(FEATURE_TIERS.keys())
        return list(all_features - available)

    def _get_available_features(self, tier: str) -> Set[str]:
        """Get all features available at the specified tier."""
        tier_level = TIER_HIERARCHY.get(tier, 0)
        available = set()

        for feature, required_tier in FEATURE_TIERS.items():
            required_level = TIER_HIERARCHY.get(required_tier, 0)
            if tier_level >= required_level:
                available.add(feature)

        return available

    def refresh(self) -> None:
        """Refresh license information (re-detect tier)."""
        self._tier_detector.detect(force_refresh=True)
        self._license_info = None
