"""
Fixture injection system for tier-aware tests.

Provides pytest fixtures that automatically:
- Inject tier-aware test adapters
- Set up and tear down licenses
- Clear caches between tests
- Parametrize tests across tiers
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator, Literal, Optional

import pytest

from code_scalpel.testing.adapters.tier_adapter import TierAdapter

Tier = Literal["community", "pro", "enterprise"]


@pytest.fixture
def clear_all_caches():
    """Clear all tier and capability caches before and after test."""
    from code_scalpel.capabilities import resolver
    from code_scalpel.licensing import config_loader, jwt_validator

    # Clear before test
    resolver._LIMITS_CACHE = None
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()

    yield

    # Clear after test
    resolver._LIMITS_CACHE = None
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()


@pytest.fixture
def community_adapter(clear_all_caches) -> TierAdapter:
    """Provide a community tier adapter."""
    return TierAdapter("community")


@pytest.fixture
def pro_adapter(clear_all_caches) -> TierAdapter:
    """Provide a pro tier adapter."""
    return TierAdapter("pro")


@pytest.fixture
def enterprise_adapter(clear_all_caches) -> TierAdapter:
    """Provide an enterprise tier adapter."""
    return TierAdapter("enterprise")


@pytest.fixture
def all_adapters(clear_all_caches) -> list[TierAdapter]:
    """Provide adapters for all tiers."""
    return [
        TierAdapter("community"),
        TierAdapter("pro"),
        TierAdapter("enterprise"),
    ]


@pytest.fixture
def pro_license_path() -> Optional[Path]:
    """Provide path to pro test license if available.

    Returns:
        Path to pro license, or None if not found
    """
    from tests.utils.tier_setup import _find_license_for_tier

    return _find_license_for_tier("pro")


@pytest.fixture
def enterprise_license_path() -> Optional[Path]:
    """Provide path to enterprise test license if available.

    Returns:
        Path to enterprise license, or None if not found
    """
    from tests.utils.tier_setup import _find_license_for_tier

    return _find_license_for_tier("enterprise")


@pytest.fixture
def with_pro_license(clear_all_caches, pro_license_path) -> Generator[str, None, None]:
    """Context manager fixture that temporarily sets Pro license.

    Automatically:
    - Sets CODE_SCALPEL_LICENSE_PATH to pro license
    - Clears caches before and after
    - Restores original license path

    Example:
        def test_pro_feature(with_pro_license):
            # Code here runs with Pro license active
            from code_scalpel.mcp.server import _get_current_tier
            assert _get_current_tier() == "pro"
    """
    if pro_license_path is None:
        pytest.skip("Pro license not available")

    original_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
    os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(pro_license_path)

    try:
        yield str(pro_license_path)
    finally:
        if original_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = original_path


@pytest.fixture
def with_enterprise_license(clear_all_caches, enterprise_license_path) -> Generator[str, None, None]:
    """Context manager fixture that temporarily sets Enterprise license.

    Automatically:
    - Sets CODE_SCALPEL_LICENSE_PATH to enterprise license
    - Clears caches before and after
    - Restores original license path

    Example:
        def test_enterprise_feature(with_enterprise_license):
            # Code here runs with Enterprise license active
            from code_scalpel.mcp.server import _get_current_tier
            assert _get_current_tier() == "enterprise"
    """
    if enterprise_license_path is None:
        pytest.skip("Enterprise license not available")

    original_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
    os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(enterprise_license_path)

    try:
        yield str(enterprise_license_path)
    finally:
        if original_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = original_path


@pytest.fixture
def with_community_tier(clear_all_caches) -> Generator[None, None, None]:
    """Context manager fixture that temporarily sets Community tier.

    Automatically:
    - Removes CODE_SCALPEL_LICENSE_PATH (forces community tier)
    - Clears caches before and after
    - Restores original license path

    Example:
        def test_community_feature(with_community_tier):
            # Code here runs with Community tier (no license)
            from code_scalpel.mcp.server import _get_current_tier
            assert _get_current_tier() == "community"
    """
    original_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
    os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)

    try:
        yield
    finally:
        if original_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = original_path


def pytest_generate_tests(metafunc):
    """Pytest hook to parametrize tier-aware tests.

    If a test is marked with @pytest.mark.tier_aware, automatically
    parametrize it to run with all tiers.

    Example:
        @pytest.mark.tier_aware
        def test_all_tiers(tier_adapter):
            # This test will run 3 times, once per tier
            pass
    """
    if "tier_adapter" in metafunc.fixturenames:
        # Check if test is marked as tier_aware
        if metafunc.definition.get_closest_marker("tier_aware"):
            tiers = ["community", "pro", "enterprise"]
            metafunc.parametrize("tier_adapter", tiers, indirect=True)


@pytest.fixture
def tier_adapter(request, clear_all_caches) -> TierAdapter:
    """Provide a tier adapter for the current test.

    Automatically clears caches before and after test.

    When used with @pytest.mark.tier_aware, provides different tier
    adapters for each test run.

    Example:
        def test_something(tier_adapter):
            if tier_adapter.tool_available("get_file_context"):
                # Test available features
                pass
            else:
                # Test locked features
                pass

        @pytest.mark.tier_aware
        def test_all_tiers(tier_adapter):
            # Runs with community, pro, and enterprise adapters
            pass
    """
    # Check if this is a parametrized request
    if hasattr(request, "param") and isinstance(request.param, str):
        tier: Tier = request.param  # type: ignore[assignment]
    else:
        tier = "community"

    return TierAdapter(tier)
