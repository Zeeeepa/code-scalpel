"""
License Validator - License key validation for Code Scalpel.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.

This module provides license key validation for PRO and ENTERPRISE tiers.
COMMUNITY tier does not require license validation.

TODO ITEMS: validator.py
============================================================================
COMMUNITY TIER (P0-P2)
============================================================================
# [P0_CRITICAL] Basic validation interface
# [P1_HIGH] COMMUNITY tier always valid
# [P2_MEDIUM] Validation result caching

============================================================================
PRO TIER (P1-P3)
============================================================================
# [P1_HIGH] License key format validation
# [P1_HIGH] License signature verification
# [P2_MEDIUM] Offline validation support
# [P2_MEDIUM] Online validation fallback
# [P3_LOW] License expiration checking

============================================================================
ENTERPRISE TIER (P2-P4)
============================================================================
# [P2_MEDIUM] Organization binding
# [P2_MEDIUM] Seat limit enforcement
# [P3_LOW] Hardware fingerprinting
# [P3_LOW] License server integration
# [P4_LOW] Custom validation rules
============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """License validation status."""

    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    NOT_REQUIRED = "not_required"  # COMMUNITY tier
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of license validation."""

    status: ValidationStatus
    tier: str
    message: str
    expiration_date: Optional[datetime] = None
    organization: Optional[str] = None
    seats: Optional[int] = None

    @property
    def is_valid(self) -> bool:
        """Check if license is valid."""
        return self.status in {ValidationStatus.VALID, ValidationStatus.NOT_REQUIRED}


class LicenseValidator:
    """
    Validate license keys for Code Scalpel.

    COMMUNITY tier does not require validation.
    PRO/ENTERPRISE tiers require valid license keys.

    Usage:
        validator = LicenseValidator()
        result = validator.validate("SCALPEL-PRO-XXXX-XXXX-XXXX")

        if result.is_valid:
            print(f"License valid for tier: {result.tier}")
        else:
            print(f"Validation failed: {result.message}")
    """

    # License key prefix format: SCALPEL-{TIER}-{KEY}
    KEY_PREFIX = "SCALPEL"

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate(
        self, license_key: Optional[str] = None, tier: str = "community"
    ) -> ValidationResult:
        """
        Validate a license key.

        Args:
            license_key: The license key to validate (optional for COMMUNITY)
            tier: The claimed tier

        Returns:
            ValidationResult with status and details
        """
        # COMMUNITY tier doesn't require license
        if tier.lower() == "community":
            return ValidationResult(
                status=ValidationStatus.NOT_REQUIRED,
                tier="community",
                message="COMMUNITY tier does not require a license key",
            )

        # PRO/ENTERPRISE require license key
        if not license_key:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                tier=tier,
                message=f"{tier.upper()} tier requires a valid license key",
            )

        # Validate key format
        format_result = self._validate_format(license_key)
        if not format_result.is_valid:
            return format_result

        # Extract tier from key
        key_tier = self._extract_tier(license_key)
        if key_tier != tier.lower():
            return ValidationResult(
                status=ValidationStatus.INVALID,
                tier=tier,
                message=f"License key is for {key_tier.upper()} tier, not {tier.upper()}",
            )

        # Validate signature (placeholder for actual implementation)
        signature_result = self._validate_signature(license_key)
        if not signature_result.is_valid:
            return signature_result

        # All checks passed
        return ValidationResult(
            status=ValidationStatus.VALID,
            tier=key_tier,
            message=f"License valid for {key_tier.upper()} tier",
        )

    def _validate_format(self, license_key: str) -> ValidationResult:
        """Validate license key format."""
        parts = license_key.split("-")

        # Expected format: SCALPEL-{TIER}-{XXXX}-{XXXX}-{XXXX}
        if len(parts) < 5:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                tier="unknown",
                message="Invalid license key format",
            )

        if parts[0] != self.KEY_PREFIX:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                tier="unknown",
                message=f"Invalid license key prefix (expected {self.KEY_PREFIX})",
            )

        tier = parts[1].lower()
        if tier not in {"pro", "enterprise"}:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                tier="unknown",
                message=f"Invalid tier in license key: {tier}",
            )

        return ValidationResult(
            status=ValidationStatus.VALID, tier=tier, message="Format valid"
        )

    def _extract_tier(self, license_key: str) -> str:
        """Extract tier from license key."""
        parts = license_key.split("-")
        if len(parts) >= 2:
            return parts[1].lower()
        return "unknown"

    def _validate_signature(self, license_key: str) -> ValidationResult:
        """
        Validate license key signature.

        Note: This is a placeholder. In production, this would verify
        a cryptographic signature against a public key.
        """
        # For now, accept any well-formatted key
        # TODO [PRO]: Implement actual signature verification
        tier = self._extract_tier(license_key)

        return ValidationResult(
            status=ValidationStatus.VALID,
            tier=tier,
            message="Signature valid (placeholder implementation)",
        )

    def validate_offline(self, license_key: str) -> ValidationResult:
        """
        Validate license key without network access.

        Uses cached validation data or embedded signatures.
        """
        # For now, delegate to regular validation
        tier = self._extract_tier(license_key)
        return self.validate(license_key, tier)
