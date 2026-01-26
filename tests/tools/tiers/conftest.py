# [20250101_TEST] Tier testing fixtures for Code Scalpel
"""
Fixtures for tier-based testing.

These fixtures enable testing tier-specific functionality by either:
1. Using real license files from tests/licenses/ (preferred)
2. Mocking _get_current_tier() as fallback

License files must be generated with the correct signing key.

[20260102_BUGFIX] pytest-asyncio 1.3.0 compatibility:
- Removed custom event_loop fixture (conflicts with built-in)
- Use pytest.ini asyncio_mode=auto with asyncio_default_test_loop_scope=function
- Add autouse fixture to clear tier caches between tests
"""

from pathlib import Path

import pytest

from tests.utils.tier_setup import activate_tier, clear_tier_caches


@pytest.fixture(autouse=True)
def clear_tier_cache():
    """
    Clear tier detection cache before and after each test.

    This ensures that tier environment variable changes or mocked tier
    functions work correctly across sequential tests without cache leakage.

    [20260102_BUGFIX] Fixes: Tests were picking up cached tier from previous test
    """
    # Clear the JWT validation cache BEFORE test
    from code_scalpel.licensing import jwt_validator

    jwt_validator._LICENSE_VALIDATION_CACHE = None

    # Clear the config loader cache BEFORE test
    from code_scalpel.licensing import config_loader

    config_loader.clear_cache()

    yield

    # Cleanup AFTER test
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()


# Paths to test license files (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# [20260106_TEST] Prefer signed fixture licenses that validate against vault-prod-2026-01
PRO_LICENSE_PATH = (
    PROJECT_ROOT / "tests/licenses/code_scalpel_license_pro_20260101_190345.jwt"
)
ENTERPRISE_LICENSE_PATH = (
    PROJECT_ROOT / "tests/licenses/code_scalpel_license_enterprise_20260101_190754.jwt"
)

# Fallback to archive if tests/licenses doesn't have valid ones
ARCHIVE_PRO_LICENSE = (
    PROJECT_ROOT
    / ".code-scalpel/archive/code_scalpel_license_pro_final_test_pro_1766982522.jwt"
)


def _find_valid_license(tier: str) -> Path | None:
    """Find a valid license file for the given tier."""
    from code_scalpel.licensing.jwt_validator import JWTLicenseValidator

    validator = JWTLicenseValidator()

    # Check standard test locations
    if tier == "pro":
        candidates = [
            PRO_LICENSE_PATH,
            PROJECT_ROOT
            / "tests/licenses/code_scalpel_license_pro_20260101_170435.jwt",
            ARCHIVE_PRO_LICENSE,
        ]
    elif tier == "enterprise":
        candidates = [
            ENTERPRISE_LICENSE_PATH,
            PROJECT_ROOT
            / "tests/licenses/code_scalpel_license_enterprise_20260101_170506.jwt",
        ]
    else:
        return None

    for path in candidates:
        if path.exists():
            try:
                token = path.read_text().strip()
                result = validator.validate_token(token)
                if result.is_valid and result.tier == tier:
                    return path
            except Exception as e:
                # Log validation failures for debugging
                import logging

                logging.debug(f"License validation failed for {path.name}: {e}")
                continue

    return None


@pytest.fixture
def pro_tier():
    """
    Fixture that sets up Pro tier for testing.

    Uses a real license file if available, otherwise mocks tier via environment.

    [20260121_FIX] Don't skip the fixture itself - activate_tier handles fallback
    """
    # Activate Pro tier via license file or env fallback
    license_path = activate_tier("pro", skip_if_missing=False)
    try:
        yield {
            "tier": "pro",
            "license_path": license_path,
            "is_mocked": license_path is None,
        }
    finally:
        clear_tier_caches()


@pytest.fixture
def enterprise_tier():
    """
    Fixture that sets up Enterprise tier for testing.

    Uses a real license file if available, otherwise mocks tier via environment.

    [20260121_FIX] Don't skip the fixture itself - activate_tier handles fallback
    """
    # Activate Enterprise tier via license file or env fallback
    license_path = activate_tier("enterprise", skip_if_missing=False)
    try:
        yield {
            "tier": "enterprise",
            "license_path": license_path,
            "is_mocked": license_path is None,
        }
    finally:
        clear_tier_caches()


@pytest.fixture
def community_tier():
    """
    Fixture that sets up Community tier for testing.

    Ensures no license is loaded by disabling license discovery AND
    removing any LICENSE_PATH that might point to a valid license.
    """
    # Activate community tier via env settings
    activate_tier("community")
    try:
        yield {"tier": "community", "license_path": None, "is_mocked": False}
    finally:
        clear_tier_caches()


@pytest.fixture
def tier_limits():
    """
    Fixture that loads tier limits from configuration (limits.toml).

    Provides a mapping of tier -> tool -> limits dict.
    This ensures tests read from the actual configuration, not hardcoded values.

    [20260127_FEATURE] Decouples tests from hardcoded limit values.
    When limits.toml changes, tests automatically adapt.

    Supports all 22 Code Scalpel tools.

    Example:
        def test_something(tier_limits):
            max_depth = tier_limits["community"]["get_cross_file_dependencies"]["max_depth"]
            assert result.transitive_depth <= max_depth
    """
    from code_scalpel.licensing.features import get_tool_capabilities

    tiers = ["community", "pro", "enterprise"]
    # All 22 tools from limits.toml
    tools = [
        "analyze_code",
        "code_policy_check",
        "crawl_project",
        "cross_file_security_scan",
        "extract_code",
        "generate_unit_tests",
        "get_call_graph",
        "get_cross_file_dependencies",
        "get_file_context",
        "get_graph_neighborhood",
        "get_project_map",
        "get_symbol_references",
        "rename_symbol",
        "scan_dependencies",
        "security_scan",
        "simulate_refactor",
        "symbolic_execute",
        "type_evaporation_scan",
        "unified_sink_detect",
        "update_symbol",
        "validate_paths",
        "verify_policy_integrity",
    ]

    limits_dict = {}
    for tier in tiers:
        limits_dict[tier] = {}
        for tool in tools:
            capabilities = get_tool_capabilities(tool, tier) or {}
            limits = capabilities.get("limits", {}) or {}
            limits_dict[tier][tool] = limits

    return limits_dict
