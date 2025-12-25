"""
Licensing Module - License management and validation for Code Scalpel.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.
Implements the open-core licensing model for COMMUNITY/PRO/ENTERPRISE tiers.

This module provides:
- LicenseManager: Central license validation and management
- LicenseValidator: License key verification
- LicenseCache: Cached license state for performance
- TierDetector: Environment-based tier detection

Architecture:
    COMMUNITY tier is free and requires no license.
    PRO/ENTERPRISE tiers require valid license keys.
    All code ships in a single MIT-licensed package.
    Features are restricted at runtime based on tier.

Configuration:
    - Environment variable: CODE_SCALPEL_TIER=community|pro|enterprise
    - Command line: --tier community|pro|enterprise
    - Config file: .code-scalpel/license.json

Usage:
    from code_scalpel.licensing import LicenseManager, Tier

    manager = LicenseManager()
    current_tier = manager.get_current_tier()

    if manager.is_feature_available("security_scan"):
        # Feature is available for current tier
        pass

TODO ITEMS: licensing/__init__.py
============================================================================
COMMUNITY TIER - Core Licensing Infrastructure (P0-P2)
============================================================================

# [P0_CRITICAL] Core tier detection:
#     - Detect tier from environment variables
#     - Support command-line tier override
#     - Fallback to COMMUNITY if unset
#     - Test count: 15 tests (tier detection)

# [P1_HIGH] License validation:
#     - Validate PRO/ENTERPRISE license keys
#     - Support offline validation
#     - Cache validation results
#     - Test count: 25 tests (validation)

# [P2_MEDIUM] Feature gating integration:
#     - Map features to minimum tiers
#     - Runtime feature availability checks
#     - Graceful degradation messaging
#     - Test count: 20 tests (feature gating)

============================================================================
PRO TIER - Commercial License Features (P1-P3)
============================================================================

# [P1_HIGH] License key management:
#     - License key format and encoding
#     - Key generation and signing
#     - Key revocation support
#     - Test count: 30 tests (key management)

# [P2_MEDIUM] Online validation:
#     - License server communication
#     - Periodic re-validation
#     - Grace period handling
#     - Test count: 25 tests (online validation)

# [P3_LOW] License analytics:
#     - Usage tracking and reporting
#     - License utilization metrics
#     - Compliance reporting
#     - Test count: 15 tests (analytics)

============================================================================
ENTERPRISE TIER - Advanced License Features (P2-P4)
============================================================================

# [P2_MEDIUM] Multi-seat licensing:
#     - Seat counting and limits
#     - Concurrent usage tracking
#     - Seat allocation management
#     - Test count: 25 tests (multi-seat)

# [P3_LOW] Organization management:
#     - Organization-level licenses
#     - Sub-organization delegation
#     - License pooling
#     - Test count: 20 tests (org management)

# [P4_LOW] Custom licensing:
#     - Custom tier definitions
#     - Feature bundle licensing
#     - Trial license support
#     - Test count: 15 tests (custom)

============================================================================
TOTAL ESTIMATED TESTS: 190 tests
============================================================================
"""

from enum import Enum


# [20251225_FEATURE] Tier enum for license levels
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
        return cls.COMMUNITY  # Default to COMMUNITY


# [20251225_FEATURE] Import from submodules
from .tier_detector import TierDetector, get_current_tier
from .license_manager import LicenseManager, LicenseInfo
from .validator import LicenseValidator, ValidationResult
from .cache import LicenseCache


__all__ = [
    # Tier enum
    "Tier",
    # Tier detection
    "TierDetector",
    "get_current_tier",
    # License management
    "LicenseManager",
    "LicenseInfo",
    # Validation
    "LicenseValidator",
    "ValidationResult",
    # Cache
    "LicenseCache",
]

__version__ = "1.0.0"
