"""
Licensing Module - License management and validation for Code Scalpel.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.
[20251225_FEATURE] v3.3.0 - Added JWT-based license validation

Implements the open-core licensing model for COMMUNITY/PRO/ENTERPRISE tiers.

This module provides:
- JWTLicenseValidator: Industry-standard JWT license validation (NEW in v3.3.0)
- LicenseManager: Central license validation and management
- LicenseValidator: Legacy license key verification
- LicenseCache: Cached license state for performance
- TierDetector: Environment-based tier detection

JWT License Architecture (v3.3.0+):
    Uses industry-standard JWT tokens with RS256/HS256 signing.
    License keys are cryptographically signed and tamper-proof.
    Community tier is free and requires no license.
    Pro/Enterprise tiers require valid JWT tokens.
    
    JWT Claims Structure:
    {
        "iss": "code-scalpel-licensing",
        "sub": "customer_id",
        "tier": "pro" | "enterprise",
        "features": [...],
        "exp": timestamp,
        "iat": timestamp
    }

Configuration:
    - Environment variable: CODE_SCALPEL_LICENSE_KEY (JWT token)
    - License file: .scalpel-license (JWT token)
    - User config: ~/.config/code-scalpel/license
    - Fallback: COMMUNITY tier (no license required)

Usage (v3.3.0+):
    from code_scalpel.licensing import get_current_tier, get_license_info
    
    # Simple tier check
    tier = get_current_tier()  # Returns: "community", "pro", or "enterprise"
    
    # Detailed license info
    info = get_license_info()
    print(f"Tier: {info['tier']}")
    print(f"Valid: {info['is_valid']}")
    print(f"Expires: {info['days_until_expiration']} days")

COMPLETED ITEMS: licensing/__init__.py (v3.0.5 - 2025-12-25)
============================================================================
COMMUNITY TIER - Core Licensing Infrastructure (P0-P2)
============================================================================

# [COMPLETED] [P0_CRITICAL] Core tier detection:
#     - Detect tier from environment variables (TierDetector.detect())
#     - Support command-line tier override (via CODE_SCALPEL_TIER env var)
#     - Fallback to COMMUNITY if unset (Tier.COMMUNITY default)
#     - Test count: 15 tests (tier detection)

# [COMPLETED] [P1_HIGH] License validation:
#     - Validate PRO/ENTERPRISE license keys (LicenseValidator.validate())
#     - Support offline validation (HMAC-SHA256 signature verification)
#     - Cache validation results (LicenseCache with persistence)
#     - Test count: 25 tests (validation)

# [COMPLETED] [P2_MEDIUM] Feature gating integration:
#     - Map features to minimum tiers (LicenseManager.is_feature_available())
#     - Runtime feature availability checks (tier-based feature gating)
#     - Graceful degradation messaging (upgrade prompts)
#     - Test count: 20 tests (feature gating)

============================================================================
PRO TIER - Commercial License Features (P1-P3)
============================================================================

# [COMPLETED] [P1_HIGH] License key management:
#     - License key format and encoding (base64-encoded JSON with HMAC-SHA256)
#     - Key generation and signing (LicenseValidator._generate_signature())
#     - Key revocation support (LicenseCache.invalidate_by_license_key())
#     - Test count: 30 tests (key management)

# [COMPLETED] [P2_MEDIUM] Online validation:
#     - License server communication (LicenseValidator.validate_online())
#     - Periodic re-validation (TTL-based with cache expiration)
#     - Grace period handling (LicenseManager.check_expiration() with 30-day grace)
#     - Test count: 25 tests (online validation)

# [COMPLETED] [P3_LOW] License analytics:
#     - Usage tracking and reporting (LicenseManager._save_state() with user tracking)
#     - License utilization metrics (LicenseManager.get_concurrent_usage())
#     - Compliance reporting (seat count and organization hierarchy)
#     - Test count: 15 tests (analytics)

============================================================================
ENTERPRISE TIER - Advanced License Features (P2-P4)
============================================================================

# [COMPLETED] [P2_MEDIUM] Multi-seat licensing:
#     - Seat counting and limits (LicenseManager.add_user() with max_seats validation)
#     - Concurrent usage tracking (LicenseManager.get_concurrent_usage() with active users)
#     - Seat allocation management (LicenseManager.remove_user() for cleanup)
#     - Test count: 25 tests (multi-seat)

# [COMPLETED] [P3_LOW] Organization management:
#     - Organization-level licenses (TierDetector._detect_from_organization())
#     - Sub-organization delegation (TierDetector._load_org_hierarchy() with parent lookup)
#     - License pooling (shared organization tiers)
#     - Test count: 20 tests (org management)

# [COMPLETED] [P4_LOW] Custom licensing:
#     - Custom tier definitions (TierDetector.set_custom_tier())
#     - Feature bundle licensing (LicenseValidator._evaluate_custom_rules())
#     - Trial license support (LicenseManager.check_expiration() with expiration dates)
#     - Test count: 15 tests (custom)

============================================================================
TOTAL ESTIMATED TESTS: 190 tests
============================================================================
"""

from enum import Enum
from typing import TYPE_CHECKING

# [20251225_FEATURE] Import from submodules
# Use TYPE_CHECKING to avoid circular import issues during runtime
if TYPE_CHECKING:
    from .tier_detector import TierDetector, get_current_tier
    from .license_manager import LicenseManager, LicenseInfo
    from .validator import LicenseValidator, ValidationResult
    from .cache import LicenseCache
else:
    # Runtime imports after Tier enum is defined
    pass


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


# [20251225_FEATURE] Runtime imports after Tier enum definition
from .tier_detector import TierDetector, get_current_tier as legacy_get_current_tier
from .license_manager import LicenseManager, LicenseInfo
from .validator import LicenseValidator, ValidationResult
from .cache import LicenseCache
from .features import (
    get_tool_capabilities,
    has_capability,
    get_all_tools_for_tier,
    TOOL_CAPABILITIES,
)

# [20251225_FEATURE] v3.3.0 - JWT license validation
from .jwt_validator import (
    JWTLicenseValidator,
    JWTLicenseData,
    JWTAlgorithm,
    get_current_tier,
    get_license_info,
)


__all__ = [
    # Tier enum
    "Tier",
    # JWT validation (NEW in v3.3.0 - PRIMARY)
    "JWTLicenseValidator",
    "JWTLicenseData",
    "JWTAlgorithm",
    "get_current_tier",  # Primary function for v3.3.0+
    "get_license_info",
    # Legacy tier detection
    "TierDetector",
    "legacy_get_current_tier",
    # License management
    "LicenseManager",
    "LicenseInfo",
    # Validation
    "LicenseValidator",
    "ValidationResult",
    # Cache
    "LicenseCache",
    # Feature capabilities
    "get_tool_capabilities",
    "has_capability",
    "get_all_tools_for_tier",
    "TOOL_CAPABILITIES",
]

__version__ = "1.0.0"
