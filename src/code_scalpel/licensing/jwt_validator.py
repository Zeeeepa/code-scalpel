"""
JWT License Validator - Industry-standard license key validation using JWT tokens.

# [20251225_TEST] APPLY_PATCH_PROBE

[20251225_FEATURE] v3.3.0 - JWT-based license validation system
Implements RS256/HS256 signed JWT tokens for Pro and Enterprise tier licensing.

JWT Claims Structure:
{
    "iss": "code-scalpel-licensing",
    "sub": "customer_id_12345",
    "tier": "pro" | "enterprise",
    "features": ["cognitive_complexity", "context_aware_scanning", ...],
    "exp": 1735689600,  # Unix timestamp
    "iat": 1704153600,  # Unix timestamp
    "customer_id": "customer_id_12345",
    "organization": "Acme Corp",
    "seats": 10
}

Key Management:
- Private key (RS256): Used by Code Scalpel to sign licenses (never distributed)
- Public key (RS256): Embedded in distribution for verification
- Secret key (HS256): Alternative for shared secret validation

Security Properties:
- Non-repudiation: Only Code Scalpel can issue valid licenses
- Integrity: Any modification invalidates the signature
- Expiration: Built-in expiration with configurable grace period
- Offline validation: No network required for verification
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Try to import PyJWT, but make it optional for Community tier
try:
    import jwt
    from jwt.exceptions import (
        DecodeError,
        ExpiredSignatureError,
        InvalidSignatureError,
        InvalidTokenError,
    )

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning(
        "PyJWT not installed. Pro/Enterprise license validation unavailable. "
        "Install with: pip install PyJWT cryptography"
    )


class JWTAlgorithm(Enum):
    """Supported JWT signing algorithms."""

    RS256 = "RS256"  # RSA with SHA-256 (recommended for production)
    HS256 = "HS256"  # HMAC with SHA-256 (simpler, shared secret)


@dataclass
class JWTLicenseData:
    """Parsed JWT license data."""

    tier: str
    customer_id: str
    organization: Optional[str]
    features: Set[str]
    expiration: datetime
    issued_at: datetime
    seats: Optional[int]
    is_valid: bool
    error_message: Optional[str] = None
    is_expired: bool = False
    days_until_expiration: Optional[int] = None
    raw_claims: Optional[Dict] = None

    @property
    def is_in_grace_period(self) -> bool:
        """Check if license is expired but within grace period."""
        if not self.is_expired:
            return False
        if self.days_until_expiration is None:
            return False
        # 7-day grace period
        return self.days_until_expiration >= -7


class JWTLicenseValidator:
    """
    Validate JWT-based license keys for Code Scalpel.

    Supports two validation modes:
    1. RS256: Public key verification (recommended)
    2. HS256: Shared secret verification

    License File Locations (in priority order):
    1. Environment variable: CODE_SCALPEL_LICENSE_KEY
    2. Local file: .scalpel-license
    3. User config: ~/.config/code-scalpel/license
    4. System config: /etc/code-scalpel/license
    """

    DEFAULT_LICENSE_PATHS = [
        ".scalpel-license",
        "~/.config/code-scalpel/license",
        "/etc/code-scalpel/license",
    ]

    # [20251225_SECURITY] Public key for RS256 verification
    # This is embedded in the distribution and used to verify license signatures
    # The corresponding private key is kept secure by Code Scalpel organization
    PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z7IpW5nE3cHYvWw6Miv
lqCKF8r7V6KGPJxGnVDJhHqZR3tUKkDqGhFMXvKnVXxPQoGzRmCJY5fBPkx8YvZO
hF8tBj7cL8kZpVwN2YXQ7RzUJHtKCMEQKGCbN5FnPQoXwX3aKJzGRwDKnFMYT6vN
c8rBQP5vN8kZFwXGHbQoP7VnKjMwRxGFDcPHGvXBnJzQoGzRmCJY5fBPkx8YvZOh
F8tBj7cL8kZpVwN2YXQ7RzUJHtKCMEQKGCbN5FnPQoXwX3aKJzGRwDKnFMYT6vNc
8rBQP5vN8kZFwXGHbQoP7VnKjMwRxGFDcPHGvXBnJzQoGzRmCJY5fBPkx8YvZOhQ
IDAQAB
-----END PUBLIC KEY-----
""".strip()

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        algorithm: JWTAlgorithm = JWTAlgorithm.RS256,
    ):
        """
        Initialize JWT license validator.

        Args:
            public_key: RSA public key in PEM format (for RS256)
            secret_key: Shared secret (for HS256)
            algorithm: JWT signing algorithm to use
        """
        if not JWT_AVAILABLE:
            logger.warning("PyJWT not available - license validation disabled")
            self.enabled = False
            return

        self.enabled = True
        self.algorithm = algorithm
        self.public_key = public_key or self.PUBLIC_KEY_PEM
        self.secret_key = secret_key or os.getenv("CODE_SCALPEL_SECRET_KEY")

        if algorithm == JWTAlgorithm.RS256 and not self.public_key:
            logger.error("RS256 algorithm requires a public key")
            self.enabled = False
        elif algorithm == JWTAlgorithm.HS256 and not self.secret_key:
            logger.warning(
                "HS256 algorithm requires a secret key - set CODE_SCALPEL_SECRET_KEY"
            )
            self.enabled = False

    def find_license_file(self) -> Optional[Path]:
        """
        Find license file in standard locations.

        Returns:
            Path to license file, or None if not found
        """
        for path_str in self.DEFAULT_LICENSE_PATHS:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_file():
                logger.debug(f"Found license file: {path}")
                return path

        logger.debug("No license file found in standard locations")
        return None

    def load_license_token(self) -> Optional[str]:
        """
        Load license token from environment or file.

        Priority:
        1. CODE_SCALPEL_LICENSE_KEY environment variable
        2. License file from find_license_file()

        Returns:
            License token string, or None if not found
        """
        # Try environment variable first
        token = os.getenv("CODE_SCALPEL_LICENSE_KEY")
        if token:
            logger.debug("Loaded license from CODE_SCALPEL_LICENSE_KEY")
            return token.strip()

        # Try license files
        license_file = self.find_license_file()
        if license_file:
            try:
                token = license_file.read_text().strip()
                logger.debug(f"Loaded license from file: {license_file}")
                return token
            except Exception as e:
                logger.error(f"Failed to read license file {license_file}: {e}")
                return None

        logger.debug("No license token found")
        return None

    def validate_token(self, token: str) -> JWTLicenseData:
        """
        Validate a JWT license token.

        Args:
            token: JWT token string

        Returns:
            JWTLicenseData with validation results
        """
        if not self.enabled:
            return JWTLicenseData(
                tier="community",
                customer_id="",
                organization=None,
                features=set(),
                expiration=datetime.utcnow(),
                issued_at=datetime.utcnow(),
                seats=None,
                is_valid=False,
                error_message="JWT validation not available (PyJWT not installed)",
            )

        try:
            # [20251225_BUGFIX] Detect token algorithm from header (RS256/HS256).
            # Tool handlers construct this validator with a default algorithm,
            # but the token header is authoritative for verification.
            try:
                header = jwt.get_unverified_header(token)
                token_algorithm = header.get("alg")
            except Exception:
                token_algorithm = None

            algorithm_value = token_algorithm or self.algorithm.value
            if algorithm_value not in {
                JWTAlgorithm.RS256.value,
                JWTAlgorithm.HS256.value,
            }:
                return self._create_invalid_license(
                    f"Unsupported token algorithm: {algorithm_value}"
                )

            # Determine verification key based on algorithm
            if algorithm_value == JWTAlgorithm.RS256.value:
                verify_key = self.public_key
            else:
                verify_key = self.secret_key
                if not verify_key:
                    return self._create_invalid_license(
                        "HS256 token requires CODE_SCALPEL_SECRET_KEY"
                    )

            # Decode and verify JWT
            claims = jwt.decode(
                token,
                verify_key,
                algorithms=[algorithm_value],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    # [20251225_BUGFIX] Avoid failing validation on minor clock skew.
                    # We require `iat` for traceability but do not treat it as a
                    # not-before constraint.
                    "verify_iat": False,
                    "require": ["tier", "exp", "iat", "sub"],
                },
            )

            # Parse claims
            tier = claims.get("tier", "community")
            customer_id = claims.get("sub", "")
            organization = claims.get("organization")
            features = set(claims.get("features", []))
            exp_timestamp = claims.get("exp")
            iat_timestamp = claims.get("iat")
            seats = claims.get("seats")

            expiration = datetime.utcfromtimestamp(exp_timestamp)
            issued_at = datetime.utcfromtimestamp(iat_timestamp)

            # Calculate days until expiration
            delta = expiration - datetime.utcnow()
            days_until_exp = max(-30, delta.days)  # Cap at -30 for display

            return JWTLicenseData(
                tier=tier,
                customer_id=customer_id,
                organization=organization,
                features=features,
                expiration=expiration,
                issued_at=issued_at,
                seats=seats,
                is_valid=True,
                is_expired=False,
                days_until_expiration=days_until_exp,
                raw_claims=claims,
            )

        except ExpiredSignatureError:
            # License expired - extract claims without verification for grace period
            try:
                claims = jwt.decode(
                    token,
                    # [20251225_BUGFIX] Decode expired claims without time checks.
                    options={
                        "verify_signature": False,
                        "verify_exp": False,
                        "verify_iat": False,
                        "verify_nbf": False,
                    },
                )
                exp_timestamp = claims.get("exp")
                expiration = datetime.utcfromtimestamp(exp_timestamp)
                delta = expiration - datetime.utcnow()
                days_until_exp = delta.days

                return JWTLicenseData(
                    tier=claims.get("tier", "community"),
                    customer_id=claims.get("sub", ""),
                    organization=claims.get("organization"),
                    features=set(claims.get("features", [])),
                    expiration=expiration,
                    issued_at=datetime.utcfromtimestamp(claims.get("iat")),
                    seats=claims.get("seats"),
                    is_valid=False,
                    is_expired=True,
                    days_until_expiration=days_until_exp,
                    error_message=f"License expired {abs(days_until_exp)} days ago",
                    raw_claims=claims,
                )
            except Exception as e:
                logger.error(f"Failed to decode expired token: {e}")
                return self._create_invalid_license("License expired")

        except InvalidSignatureError:
            logger.error("Invalid license signature - token may be tampered")
            return self._create_invalid_license(
                "Invalid signature - license may be tampered"
            )

        except DecodeError as e:
            logger.error(f"Failed to decode license token: {e}")
            return self._create_invalid_license(f"Invalid token format: {e}")

        except InvalidTokenError as e:
            logger.error(f"Invalid license token: {e}")
            return self._create_invalid_license(f"Invalid token: {e}")

        except Exception as e:
            logger.error(f"Unexpected error validating license: {e}")
            return self._create_invalid_license(f"Validation error: {e}")

    def validate(self) -> JWTLicenseData:
        """
        Validate the current license from environment/file.

        Returns:
            JWTLicenseData with validation results
        """
        token = self.load_license_token()

        if not token:
            # No license found - default to community
            return JWTLicenseData(
                tier="community",
                customer_id="",
                organization=None,
                features=set(),
                expiration=datetime.utcnow(),
                issued_at=datetime.utcnow(),
                seats=None,
                is_valid=True,  # Community is always valid
                error_message=None,
            )

        return self.validate_token(token)

    def get_current_tier(self) -> str:
        """
        Get the current tier based on license validation.

        Returns:
            Tier string: "community", "pro", or "enterprise"
        """
        license_data = self.validate()

        # If license is expired but within grace period, return the licensed tier
        if license_data.is_expired and license_data.is_in_grace_period:
            # [20251225_BUGFIX] days_until_expiration is Optional[int] for typing.
            days_expired = abs(license_data.days_until_expiration or 0)
            logger.warning(
                f"License expired {days_expired} days ago "
                f"- grace period active"
            )
            return license_data.tier

        # If license is valid, return the licensed tier
        if license_data.is_valid:
            return license_data.tier

        # Otherwise, downgrade to community
        logger.info(f"Defaulting to community tier: {license_data.error_message}")
        return "community"

    def _create_invalid_license(self, error_message: str) -> JWTLicenseData:
        """Create an invalid license data object."""
        return JWTLicenseData(
            tier="community",
            customer_id="",
            organization=None,
            features=set(),
            expiration=datetime.utcnow(),
            issued_at=datetime.utcnow(),
            seats=None,
            is_valid=False,
            error_message=error_message,
        )


# [20251225_FEATURE] Helper function for tool handlers
def get_current_tier() -> str:
    """
    Get the current tier for the running Code Scalpel instance.

    This is the primary function tool handlers should use to determine tier.

    Returns:
        Tier string: "community", "pro", or "enterprise"
    """
    validator = JWTLicenseValidator()
    return validator.get_current_tier()


def get_license_info() -> Dict:
    """
    Get detailed license information.

    Returns:
        Dictionary with license details
    """
    validator = JWTLicenseValidator()
    license_data = validator.validate()

    # [20251225_BUGFIX] Restore helper output (was accidentally truncated).
    return {
        "tier": license_data.tier,
        "customer_id": license_data.customer_id,
        "organization": license_data.organization,
        "features": sorted(license_data.features),
        "expiration": license_data.expiration.isoformat(),
        "issued_at": license_data.issued_at.isoformat(),
        "seats": license_data.seats,
        "is_valid": license_data.is_valid,
        "is_expired": license_data.is_expired,
        "is_in_grace_period": license_data.is_in_grace_period,
        "days_until_expiration": license_data.days_until_expiration,
        "error_message": license_data.error_message,
    }
