"""
Tier Detector - Detect current license tier from environment.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.

This module provides tier detection from multiple sources:
1. Environment variable: CODE_SCALPEL_TIER
2. Config file: .code-scalpel/license.json
3. Default: COMMUNITY

TODO ITEMS: tier_detector.py
============================================================================
COMMUNITY TIER (P0-P2)
============================================================================
# [P0_CRITICAL] Environment variable detection
# [P1_HIGH] Config file detection
# [P1_HIGH] Default tier fallback
# [P2_MEDIUM] Tier validation and logging

============================================================================
PRO TIER (P1-P3)
============================================================================
# [P1_HIGH] License key tier extraction
# [P2_MEDIUM] Multiple config file locations
# [P3_LOW] Tier caching

============================================================================
ENTERPRISE TIER (P2-P4)
============================================================================
# [P2_MEDIUM] Organization-based tier detection
# [P3_LOW] Tier inheritance from parent orgs
# [P4_LOW] Custom tier definitions
============================================================================
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# [20251225_FEATURE] Import Tier from parent module to avoid circular import
# We use a string import here since __init__.py imports this module
class Tier:
    """Placeholder - real Tier enum is in __init__.py"""

    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierDetectionResult:
    """Result of tier detection."""

    tier: str
    source: str  # "environment", "config", "license", "default"
    confidence: float  # 0.0 to 1.0
    details: Optional[str] = None


class TierDetector:
    """
    Detect the current license tier from environment and configuration.

    Priority order:
    1. Environment variable CODE_SCALPEL_TIER (highest)
    2. Config file .code-scalpel/license.json
    3. Default to COMMUNITY (lowest)
    """

    ENV_VAR = "CODE_SCALPEL_TIER"
    CONFIG_PATHS = [
        ".code-scalpel/license.json",
        "~/.code-scalpel/license.json",
        "/etc/code-scalpel/license.json",
    ]

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the tier detector.

        Args:
            config_dir: Optional custom config directory
        """
        self.config_dir = config_dir
        self._cached_result: Optional[TierDetectionResult] = None

    def detect(self, force_refresh: bool = False) -> TierDetectionResult:
        """
        Detect the current tier.

        Args:
            force_refresh: If True, bypass cache and re-detect

        Returns:
            TierDetectionResult with tier and source
        """
        if self._cached_result and not force_refresh:
            return self._cached_result

        # Priority 1: Environment variable
        env_tier = self._detect_from_environment()
        if env_tier:
            self._cached_result = env_tier
            return env_tier

        # Priority 2: Config file
        config_tier = self._detect_from_config()
        if config_tier:
            self._cached_result = config_tier
            return config_tier

        # Priority 3: Default
        default_tier = TierDetectionResult(
            tier=Tier.COMMUNITY,
            source="default",
            confidence=1.0,
            details="No tier configuration found, defaulting to COMMUNITY",
        )
        self._cached_result = default_tier
        return default_tier

    def _detect_from_environment(self) -> Optional[TierDetectionResult]:
        """Detect tier from environment variable."""
        tier_value = os.environ.get(self.ENV_VAR)
        if not tier_value:
            return None

        tier_lower = tier_value.lower().strip()
        valid_tiers = {Tier.COMMUNITY, Tier.PRO, Tier.ENTERPRISE}

        if tier_lower in valid_tiers:
            logger.debug(
                f"Detected tier '{tier_lower}' from environment variable {self.ENV_VAR}"
            )
            return TierDetectionResult(
                tier=tier_lower,
                source="environment",
                confidence=1.0,
                details=f"Set via {self.ENV_VAR}={tier_value}",
            )
        else:
            logger.warning(f"Invalid tier '{tier_value}' in {self.ENV_VAR}, ignoring")
            return None

    def _detect_from_config(self) -> Optional[TierDetectionResult]:
        """Detect tier from config file."""
        config_paths = self.CONFIG_PATHS.copy()

        # Add custom config dir if specified
        if self.config_dir:
            config_paths.insert(0, str(self.config_dir / "license.json"))

        for config_path_str in config_paths:
            config_path = Path(config_path_str).expanduser()
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)

                    tier_value = config.get("tier", "").lower().strip()
                    valid_tiers = {Tier.COMMUNITY, Tier.PRO, Tier.ENTERPRISE}

                    if tier_value in valid_tiers:
                        logger.debug(
                            f"Detected tier '{tier_value}' from config file {config_path}"
                        )
                        return TierDetectionResult(
                            tier=tier_value,
                            source="config",
                            confidence=0.9,
                            details=f"Loaded from {config_path}",
                        )
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Error reading config file {config_path}: {e}")

        return None

    def get_tier_string(self) -> str:
        """Get the current tier as a string."""
        result = self.detect()
        return result.tier

    def is_pro_or_higher(self) -> bool:
        """Check if current tier is PRO or ENTERPRISE."""
        tier = self.get_tier_string()
        return tier in {Tier.PRO, Tier.ENTERPRISE}

    def is_enterprise(self) -> bool:
        """Check if current tier is ENTERPRISE."""
        return self.get_tier_string() == Tier.ENTERPRISE


# [20251225_FEATURE] Convenience function for quick tier detection
def get_current_tier() -> str:
    """
    Get the current license tier.

    Returns:
        Tier string: "community", "pro", or "enterprise"
    """
    detector = TierDetector()
    return detector.get_tier_string()
