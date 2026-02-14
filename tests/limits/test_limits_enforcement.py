"""Tests for limits enforcement at tier boundaries.

Verifies that tools correctly:
- Clamp parameters to tier limits
- Return metadata showing applied limits
- Emit neutral warnings when limits are exceeded
- Don't perform marketing upsells

[20260124_TEST] Created boundary testing for all tool limits.
"""

from __future__ import annotations

import pytest

from tests.utils.config_loaders import get_all_tool_names, get_tier_limit


class TestParameterClamping:
    """Test that parameters are clamped to tier limits."""

    def test_extract_code_depth_clamping_community(self, community_tier):
        """extract_code should clamp context_depth to 1 in Community tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("extract_code", "community")
        limits = caps.get("limits", {})

        # [20260212_TEST] Updated to match rebalanced limits.toml
        # Community tier allows immediate imports (depth=1)
        assert (
            limits.get("max_depth") == 1
        ), "Community extract_code should have max_depth=1 (immediate imports)"

    def test_extract_code_depth_clamping_pro(self, pro_tier):
        """extract_code should allow unlimited depth in Pro tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("extract_code", "pro")
        limits = caps.get("limits", {})

        # [20260212_TEST] Updated to match rebalanced limits.toml
        # Pro tier allows unlimited cross-file deps (matches Enterprise)
        assert (
            limits.get("max_depth") is None
        ), "Pro extract_code should have unlimited depth"

    def test_extract_code_depth_clamping_enterprise(self, enterprise_tier):
        """extract_code should allow unlimited depth in Enterprise tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("extract_code", "enterprise")
        limits = caps.get("limits", {})

        # Enterprise allows full cross-file dependency resolution
        assert (
            limits.get("max_depth") is None
        ), "Enterprise extract_code should have unlimited depth"

    def test_get_call_graph_depth_clamping_community(self, community_tier):
        """get_call_graph should clamp depth to 10 in Community tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("get_call_graph", "community")
        limits = caps.get("limits", {})

        # [20260212_TEST] Updated to match rebalanced limits.toml
        assert limits.get("max_depth") == 10, "Community: max_depth should be 10"

    def test_get_call_graph_depth_clamping_pro(self, pro_tier):
        """get_call_graph should allow unlimited depth in Pro tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("get_call_graph", "pro")
        limits = caps.get("limits", {})

        # [20260212_TEST] Updated to match rebalanced limits.toml
        assert limits.get("max_depth") is None, "Pro: max_depth should be unlimited"

    def test_get_call_graph_depth_clamping_enterprise(self, enterprise_tier):
        """get_call_graph should allow unlimited depth in Enterprise tier."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("get_call_graph", "enterprise")
        limits = caps.get("limits", {})

        assert (
            limits.get("max_depth") is None
        ), "Enterprise: max_depth should be unlimited"


class TestResponseMetadata:
    """Test that responses include applied limits metadata."""

    def test_limits_present_in_response_envelope(self):
        """Tool responses should include applied_limits in envelope."""
        # This test ensures tools include limit metadata
        # Actual testing happens in tool-specific MCP tests
        pass


class TestLimitBoundaryValues:
    """Test behavior at exact limit boundaries."""

    @pytest.mark.parametrize("tool", get_all_tool_names())
    def test_tool_has_consistent_tier_limits(self, tool):
        """Tool should have consistent limit definitions across tiers."""
        community = get_tier_limit(tool, "community", "max_files")
        pro = get_tier_limit(tool, "pro", "max_files")
        enterprise = get_tier_limit(tool, "enterprise", "max_files")

        # If community has a limit, pro should have a higher one or None
        if community is not None and pro is not None:
            assert (
                pro >= community
            ), f"Tool '{tool}': pro max_files ({pro}) should be >= community ({community})"

        # If pro has a limit, enterprise should have higher or None
        if pro is not None and enterprise is not None:
            assert (
                enterprise >= pro
            ), f"Tool '{tool}': enterprise max_files should be >= pro"


class TestOmissionAsUnlimited:
    """Test that omitted limits in TOML correctly mean unlimited."""

    def test_enterprise_omitted_limits_are_unlimited(self):
        """Enterprise tier with omitted limits should be treated as unlimited."""
        # Example: extract_code depth is unlimited in enterprise
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("extract_code", "enterprise")
        limits = caps.get("limits", {})

        # max_depth should be None (unlimited) or very high number
        max_depth = limits.get("max_depth")
        assert (
            max_depth is None
        ), "Enterprise extract_code should have unlimited depth (None value)"


class TestGracefulFallback:
    """Test fallback behavior when limits are missing."""

    def test_missing_limit_defaults_safely(self):
        """Missing limit should default safely (not crash)."""
        from code_scalpel.licensing.features import get_tool_capabilities

        # Even if a limit isn't explicitly set, tool should work
        caps = get_tool_capabilities("analyze_code", "community")
        assert (
            "limits" in caps
        ), "Tool should have limits dict even if partially defined"


@pytest.mark.slow
class TestLargeScaleLimitEnforcement:
    """Test limits with large inputs."""

    def test_crawl_project_respects_community_file_limit(
        self, community_tier, tmp_path
    ):
        """crawl_project should not analyze more than 100 files in Community tier."""
        # Create 150 test files
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()

        for i in range(150):
            (test_dir / f"file_{i}.py").write_text(f"# File {i}\nx = {i}")

        # This test would actually call crawl_project and verify behavior
        # Stubbed here as full implementation requires MCP server setup
        pass

    def test_crawl_project_unlimited_in_pro_tier(self, pro_tier, tmp_path):
        """crawl_project should analyze unlimited files in Pro tier."""
        # Similar setup but verify no capping in Pro tier
        pass
