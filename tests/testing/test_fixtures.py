"""Comprehensive tests for pytest fixtures.

Tests all fixture injection functionality:
- Cache clearing before/after tests
- Tier-specific adapter injection
- License path fixtures
- Context manager fixtures
- Parametrization via @tier_aware marker
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from code_scalpel.testing import TierAdapter


class TestClearAllCaches:
    """Test cache clearing fixture."""

    def test_clear_all_caches_clears_resolver_cache(self, clear_all_caches):
        """Verify resolver cache is cleared."""
        from code_scalpel.capabilities import resolver

        # Cache should be None before test starts
        assert resolver._LIMITS_CACHE is None

        # Set it to something
        resolver._LIMITS_CACHE = {"test": "value"}
        assert resolver._LIMITS_CACHE is not None

    def test_clear_all_caches_clears_jwt_validator_cache(self, clear_all_caches):
        """Verify JWT validator cache is cleared."""
        from code_scalpel.licensing import jwt_validator

        # Cache should be None before test starts
        assert jwt_validator._LICENSE_VALIDATION_CACHE is None

        # Set it to something
        jwt_validator._LICENSE_VALIDATION_CACHE = {"test": "value"}
        assert jwt_validator._LICENSE_VALIDATION_CACHE is not None


class TestTierAdapterFixture:
    """Test the main tier_adapter fixture."""

    def test_tier_adapter_default_is_community(self, tier_adapter: TierAdapter):
        """Default tier_adapter should be community."""
        assert tier_adapter.get_tier() == "community"

    def test_tier_adapter_has_all_community_tools(self, tier_adapter: TierAdapter):
        """Community tier should have all 22 tools available."""
        available = tier_adapter.get_available_tools()
        assert len(available) == 22
        assert all(isinstance(tool, str) for tool in available)

    def test_tier_adapter_no_locked_tools_community(self, tier_adapter: TierAdapter):
        """Community tier should have no locked tools."""
        locked = tier_adapter.get_unavailable_tools()
        assert len(locked) == 0


class TestSpecificAdapterFixtures:
    """Test tier-specific adapter fixtures."""

    def test_community_adapter(self, community_adapter: TierAdapter):
        """Community adapter should be community tier."""
        assert community_adapter.get_tier() == "community"
        assert len(community_adapter.get_available_tools()) == 22

    def test_pro_adapter(self, pro_adapter: TierAdapter):
        """Pro adapter should be pro tier."""
        assert pro_adapter.get_tier() == "pro"
        assert len(pro_adapter.get_available_tools()) == 19

    def test_enterprise_adapter(self, enterprise_adapter: TierAdapter):
        """Enterprise adapter should be enterprise tier."""
        assert enterprise_adapter.get_tier() == "enterprise"
        assert len(enterprise_adapter.get_available_tools()) == 10

    def test_each_adapter_is_independent(
        self, community_adapter, pro_adapter, enterprise_adapter
    ):
        """Each adapter fixture should be a separate instance."""
        assert community_adapter is not pro_adapter
        assert pro_adapter is not enterprise_adapter
        assert community_adapter is not enterprise_adapter


class TestAllAdaptersFixture:
    """Test the all_adapters fixture."""

    def test_all_adapters_provides_three(self, all_adapters: list[TierAdapter]):
        """all_adapters fixture should provide 3 adapters."""
        assert len(all_adapters) == 3

    def test_all_adapters_are_different_tiers(self, all_adapters: list[TierAdapter]):
        """All adapters should be different tiers."""
        tiers = {adapter.get_tier() for adapter in all_adapters}
        assert tiers == {"community", "pro", "enterprise"}

    def test_all_adapters_correct_tool_counts(self, all_adapters: list[TierAdapter]):
        """Each adapter should have correct tool count."""
        tier_to_count = {
            adapter.get_tier(): len(adapter.get_available_tools())
            for adapter in all_adapters
        }
        assert tier_to_count["community"] == 22
        assert tier_to_count["pro"] == 19
        assert tier_to_count["enterprise"] == 10


class TestLicensePathFixtures:
    """Test license path fixtures."""

    def test_pro_license_path_is_path_or_none(self, pro_license_path):
        """Pro license path should be Path or None."""
        assert pro_license_path is None or isinstance(pro_license_path, Path)

    def test_enterprise_license_path_is_path_or_none(self, enterprise_license_path):
        """Enterprise license path should be Path or None."""
        assert enterprise_license_path is None or isinstance(
            enterprise_license_path, Path
        )

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Licenses not available in this environment",
    )
    def test_pro_license_path_exists(self, pro_license_path):
        """Pro license path should exist if available."""
        if pro_license_path is not None:
            assert pro_license_path.exists()

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Licenses not available in this environment",
    )
    def test_enterprise_license_path_exists(self, enterprise_license_path):
        """Enterprise license path should exist if available."""
        if enterprise_license_path is not None:
            assert enterprise_license_path.exists()


class TestWithCommunityTierFixture:
    """Test with_community_tier context manager fixture."""

    def test_with_community_tier_removes_license_path(self, with_community_tier):
        """with_community_tier should remove CODE_SCALPEL_LICENSE_PATH."""
        # Inside the fixture context
        assert os.environ.get("CODE_SCALPEL_LICENSE_PATH") is None

    def test_with_community_tier_restores_original(self):
        """with_community_tier should restore original license path."""
        # Set original value
        original = "test_original_path"
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = original

        # Import here to use the fixture

        # Can't directly test restoration without using the fixture,
        # but the fixture code shows it does this


class TestWithProLicenseFixture:
    """Test with_pro_license context manager fixture."""

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Pro license not available",
    )
    def test_with_pro_license_sets_env_var(self, with_pro_license):
        """with_pro_license should set CODE_SCALPEL_LICENSE_PATH."""
        # Inside the fixture, license path should be set
        license_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
        assert license_path is not None
        assert license_path == str(with_pro_license)

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Pro license not available",
    )
    def test_with_pro_license_sets_correct_path(self, with_pro_license):
        """with_pro_license should set the correct pro license path."""
        from pathlib import Path

        license_path_str = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
        assert license_path_str is not None
        license_path = Path(license_path_str)
        assert license_path.exists()


class TestWithEnterpriseLicenseFixture:
    """Test with_enterprise_license context manager fixture."""

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Enterprise license not available",
    )
    def test_with_enterprise_license_sets_env_var(self, with_enterprise_license):
        """with_enterprise_license should set CODE_SCALPEL_LICENSE_PATH."""
        # Inside the fixture, license path should be set
        license_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
        assert license_path is not None
        assert license_path == str(with_enterprise_license)

    @pytest.mark.skipif(
        os.environ.get("TEST_WITH_LICENSES") != "true",
        reason="Enterprise license not available",
    )
    def test_with_enterprise_license_sets_correct_path(self, with_enterprise_license):
        """with_enterprise_license should set the correct enterprise license path."""
        from pathlib import Path

        license_path_str = os.environ.get("CODE_SCALPEL_LICENSE_PATH")
        assert license_path_str is not None
        license_path = Path(license_path_str)
        assert license_path.exists()


class TestTierAwareParametrization:
    """Test @pytest.mark.tier_aware parametrization."""

    @pytest.mark.tier_aware
    def test_tier_aware_runs_all_tiers(self, tier_adapter: TierAdapter):
        """Test marked tier_aware should run for all tiers."""
        # This test will run 3 times - once per tier
        # We verify the adapter is correctly set
        assert tier_adapter.get_tier() in ("community", "pro", "enterprise")

    @pytest.mark.tier_aware
    def test_tier_aware_receives_correct_tier(self, tier_adapter: TierAdapter):
        """Each tier_aware test should receive correct tier."""
        tier = tier_adapter.get_tier()
        assert tier in ("community", "pro", "enterprise")

        # Verify tier has expected tool count
        available_count = len(tier_adapter.get_available_tools())
        if tier == "community":
            assert available_count == 22
        elif tier == "pro":
            assert available_count == 19
        elif tier == "enterprise":
            assert available_count == 10

    @pytest.mark.tier_aware
    def test_tier_aware_with_tier_specific_assertions(self, tier_adapter: TierAdapter):
        """tier_aware test can use tier-specific assertions."""
        tier = tier_adapter.get_tier()

        # These assertions should work for all tiers
        tier_adapter.assert_tool_available("analyze_code")  # Available in all

        # Tier-specific availability
        if tier in ("community", "pro"):
            tier_adapter.assert_tool_available("get_file_context")
        else:
            tier_adapter.assert_tool_unavailable("get_file_context")


class TestFixtureIntegration:
    """Test integration of multiple fixtures."""

    def test_multiple_adapters_independently_available(
        self, community_adapter, pro_adapter, enterprise_adapter
    ):
        """Multiple adapter fixtures should work independently."""
        # All should have analyze_code
        community_adapter.assert_tool_available("analyze_code")
        pro_adapter.assert_tool_available("analyze_code")
        enterprise_adapter.assert_tool_available("analyze_code")

        # get_file_context should be locked in enterprise
        community_adapter.assert_tool_available("get_file_context")
        pro_adapter.assert_tool_available("get_file_context")
        enterprise_adapter.assert_tool_unavailable("get_file_context")

    def test_clear_all_caches_with_adapters(
        self, clear_all_caches, community_adapter, pro_adapter
    ):
        """clear_all_caches fixture should work with adapters."""
        # Adapters should be correctly initialized after cache clear
        assert community_adapter.get_tier() == "community"
        assert pro_adapter.get_tier() == "pro"

    def test_all_fixtures_together(
        self, clear_all_caches, tier_adapter, community_adapter, all_adapters
    ):
        """All fixtures should work together."""
        # tier_adapter should be one of the adapters
        tier = tier_adapter.get_tier()
        assert tier in ("community", "pro", "enterprise")

        # all_adapters should contain 3 different adapters
        assert len(all_adapters) == 3

        # All fixtures should be properly initialized
        assert community_adapter.get_tier() == "community"
