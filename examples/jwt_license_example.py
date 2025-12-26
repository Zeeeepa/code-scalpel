"""
JWT License Validation Example - Demonstrates JWT-based license validation.

[20251225_FEATURE] v3.3.0 - JWT license validation system examples

This example shows how to:
1. Generate JWT license keys for testing
2. Validate licenses and check tier
3. Use license validation in tool handlers
4. Handle expired licenses and grace periods
5. Work with environment variables and license files
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_scalpel.licensing import (
    JWTLicenseValidator,
    get_current_tier,
    get_license_info,
    get_tool_capabilities,
)
from code_scalpel.licensing.jwt_generator import generate_license


def example_1_generate_test_licenses():
    """Example 1: Generate test licenses for development."""
    print("=" * 80)
    print("Example 1: Generating Test Licenses")
    print("=" * 80)

    # Generate a Pro license valid for 365 days
    pro_license = generate_license(
        tier="pro",
        customer_id="test_customer_123",
        organization="Test Organization",
        duration_days=365,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    print(f"\nPro License (HS256):")
    print(f"Token: {pro_license[:50]}...{pro_license[-20:]}")
    print(f"Length: {len(pro_license)} characters")

    # Generate an Enterprise license
    enterprise_license = generate_license(
        tier="enterprise",
        customer_id="test_customer_456",
        organization="Enterprise Corp",
        seats=50,
        duration_days=730,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    print(f"\nEnterprise License (HS256):")
    print(f"Token: {enterprise_license[:50]}...{enterprise_license[-20:]}")
    print(f"Seats: 50")
    print(f"Duration: 730 days")

    # Save to file
    license_file = Path(".scalpel-license-test")
    license_file.write_text(pro_license)
    print(f"\nSaved Pro license to: {license_file.absolute()}")

    return pro_license, enterprise_license


def example_2_validate_from_string():
    """Example 2: Validate license token directly."""
    print("\n" + "=" * 80)
    print("Example 2: Validating License Token")
    print("=" * 80)

    # Generate a test license
    token = generate_license(
        tier="pro",
        customer_id="test_user",
        organization="Test Org",
        duration_days=30,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    # Create validator with HS256
    validator = JWTLicenseValidator(
        algorithm=JWTAlgorithm.HS256, secret_key="test_secret_key_12345"
    )

    # Validate token
    result = validator.validate_token(token)

    print(f"\nValidation Result:")
    print(f"  Tier: {result.tier}")
    print(f"  Valid: {result.is_valid}")
    print(f"  Customer ID: {result.customer_id}")
    print(f"  Organization: {result.organization}")
    print(f"  Features: {len(result.features)} features")
    print(f"  Expires in: {result.days_until_expiration} days")
    print(f"  Expiration date: {result.expiration.strftime('%Y-%m-%d')}")


def example_3_validate_from_file():
    """Example 3: Validate license from file."""
    print("\n" + "=" * 80)
    print("Example 3: Validating License from File")
    print("=" * 80)

    # Generate and save license
    token = generate_license(
        tier="pro",
        customer_id="file_test_user",
        duration_days=365,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    license_file = Path(".scalpel-license")
    license_file.write_text(token)
    print(f"\nCreated license file: {license_file.absolute()}")

    # Validate from file
    validator = JWTLicenseValidator(
        algorithm=JWTAlgorithm.HS256, secret_key="test_secret_key_12345"
    )

    result = validator.validate()

    print(f"\nValidation Result:")
    print(f"  Tier: {result.tier}")
    print(f"  Valid: {result.is_valid}")
    print(f"  Source: License file (.scalpel-license)")

    # Clean up
    license_file.unlink()
    print(f"\nCleaned up license file")


def example_4_validate_from_environment():
    """Example 4: Validate license from environment variable."""
    print("\n" + "=" * 80)
    print("Example 4: Validating License from Environment Variable")
    print("=" * 80)

    # Generate license
    token = generate_license(
        tier="enterprise",
        customer_id="env_test_user",
        organization="Environment Testing Inc",
        seats=100,
        duration_days=730,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    # Set environment variable
    os.environ["CODE_SCALPEL_LICENSE_KEY"] = token
    print(f"\nSet CODE_SCALPEL_LICENSE_KEY environment variable")

    # Validate
    validator = JWTLicenseValidator(
        algorithm=JWTAlgorithm.HS256, secret_key="test_secret_key_12345"
    )

    result = validator.validate()

    print(f"\nValidation Result:")
    print(f"  Tier: {result.tier}")
    print(f"  Valid: {result.is_valid}")
    print(f"  Organization: {result.organization}")
    print(f"  Seats: {result.seats}")
    print(f"  Source: Environment variable")

    # Clean up
    del os.environ["CODE_SCALPEL_LICENSE_KEY"]


def example_5_expired_license_grace_period():
    """Example 5: Handle expired license with grace period."""
    print("\n" + "=" * 80)
    print("Example 5: Expired License with Grace Period")
    print("=" * 80)

    # Generate expired license (negative duration)
    from datetime import datetime, timedelta
    import jwt

    # Create claims for expired license
    now = datetime.utcnow()
    expired_date = now - timedelta(days=3)  # Expired 3 days ago

    claims = {
        "iss": "code-scalpel-licensing",
        "sub": "expired_test_user",
        "tier": "pro",
        "features": ["cognitive_complexity", "context_aware_scanning"],
        "exp": int(expired_date.timestamp()),
        "iat": int((expired_date - timedelta(days=365)).timestamp()),
    }

    expired_token = jwt.encode(claims, "test_secret_key_12345", algorithm="HS256")

    print(f"\nGenerated expired license (expired 3 days ago)")

    # Validate expired license
    validator = JWTLicenseValidator(
        algorithm=JWTAlgorithm.HS256, secret_key="test_secret_key_12345"
    )

    result = validator.validate_token(expired_token)

    print(f"\nValidation Result:")
    print(f"  Tier: {result.tier}")
    print(f"  Valid: {result.is_valid}")
    print(f"  Expired: {result.is_expired}")
    print(f"  Days since expiration: {abs(result.days_until_expiration)}")
    print(f"  In grace period: {result.is_in_grace_period} (7-day grace)")

    # Check tier - should still be Pro during grace period
    tier = validator.get_current_tier()
    print(f"\n  Current tier (with grace): {tier}")


def example_6_tool_handler_integration():
    """Example 6: Using license validation in tool handlers."""
    print("\n" + "=" * 80)
    print("Example 6: Tool Handler Integration Pattern")
    print("=" * 80)

    # Simulate different tiers
    tiers = ["community", "pro", "enterprise"]

    for tier in tiers:
        print(f"\n--- Simulating {tier.upper()} tier ---")

        # Generate appropriate license
        if tier == "community":
            # No license for community
            token = None
        else:
            token = generate_license(
                tier=tier,
                customer_id=f"{tier}_user",
                organization=f"{tier.title()} Organization",
                duration_days=365,
                algorithm="HS256",
                secret_key="test_secret_key_12345",
            )

        # Set up environment
        if token:
            os.environ["CODE_SCALPEL_LICENSE_KEY"] = token
        else:
            os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)

        # Tool handler pattern
        current_tier = get_current_tier()
        caps = get_tool_capabilities("security_scan", current_tier)

        print(f"  Current tier: {current_tier}")
        print(f"  Capabilities: {list(caps.get('capabilities', []))[:3]}...")
        print(f"  Limits: {caps.get('limits', {})}")

        # Clean up
        os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)


def example_7_license_info_api():
    """Example 7: Get detailed license information."""
    print("\n" + "=" * 80)
    print("Example 7: Detailed License Information API")
    print("=" * 80)

    # Generate a license with all fields
    token = generate_license(
        tier="enterprise",
        customer_id="api_test_user",
        organization="API Testing Corp",
        seats=25,
        duration_days=90,
        algorithm="HS256",
        secret_key="test_secret_key_12345",
    )

    os.environ["CODE_SCALPEL_LICENSE_KEY"] = token

    # Get detailed info
    info = get_license_info()

    print(f"\nLicense Information:")
    print(f"  Tier: {info['tier']}")
    print(f"  Valid: {info['is_valid']}")
    print(f"  Customer ID: {info['customer_id']}")
    print(f"  Organization: {info['organization']}")
    print(f"  Seats: {info['seats']}")
    print(f"  Features: {len(info['features'])} features")
    print(f"    - {info['features'][:3]}")
    print(f"  Expiration: {info['expiration']}")
    print(f"  Days until expiration: {info['days_until_expiration']}")
    print(f"  Expired: {info['is_expired']}")
    print(f"  Grace period: {info['is_in_grace_period']}")

    # Clean up
    del os.environ["CODE_SCALPEL_LICENSE_KEY"]


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("JWT License Validation Examples")
    print("Code Scalpel v3.3.0")
    print("=" * 80)

    try:
        example_1_generate_test_licenses()
        example_2_validate_from_string()
        example_3_validate_from_file()
        example_4_validate_from_environment()
        example_5_expired_license_grace_period()
        example_6_tool_handler_integration()
        example_7_license_info_api()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Import at runtime to handle optional dependency
    try:
        import jwt
        from code_scalpel.licensing.jwt_validator import JWTAlgorithm
    except ImportError:
        print("ERROR: PyJWT not installed.")
        print("Install with: pip install PyJWT cryptography")
        sys.exit(1)

    main()
