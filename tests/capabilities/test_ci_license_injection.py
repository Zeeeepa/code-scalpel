"""
Test capabilities resolver with CI environment and license injection.

Tests that demonstrate the resolver working correctly when licenses are
injected from GitHub Secrets during CI/CD testing.
"""

import os


from code_scalpel.capabilities.resolver import (
    get_all_capabilities,
    get_tool_capabilities,
)
from code_scalpel.mcp.server import _get_current_tier


class TestCapabilitiesWithProLicense:
    """Test capabilities when Pro tier license is present."""

    def test_pro_tier_shows_pro_tools(self, clear_all_caches, pro_license_path):
        """Pro license should enable Pro-specific tools."""
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(pro_license_path)

        try:
            # Get current tier from license
            tier = _get_current_tier()
            assert tier == "pro", f"Expected pro tier, got {tier}"

            # Get all capabilities for Pro tier
            capabilities = get_all_capabilities(tier)
            assert capabilities is not None
            assert len(capabilities) > 0

            # Pro tier should have more than 10 tools
            available_tools = sum(
                1 for tool in capabilities.values() if tool.get("available", False)
            )
            assert (
                available_tools >= 19
            ), f"Pro tier should have 19+ available tools, got {available_tools}"
        finally:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)

    def test_pro_tier_locks_enterprise_tools(self, clear_all_caches, pro_license_path):
        """Pro license should lock enterprise-only tools."""
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(pro_license_path)

        try:
            tier = _get_current_tier()
            assert tier == "pro"

            capabilities = get_all_capabilities(tier)

            # Find which tools are locked
            locked_tools = [
                tool_id
                for tool_id, cap in capabilities.items()
                if not cap.get("available", False)
            ]

            # Pro should have some locked tools (enterprise-only)
            assert len(locked_tools) > 0, "Pro tier should have locked tools"
            assert len(locked_tools) == 2, (
                f"Pro tier should lock exactly 2 tools, got {len(locked_tools)}: "
                f"{locked_tools}"
            )
        finally:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)

    def test_specific_pro_tool_has_limits(self, clear_all_caches, pro_license_path):
        """Pro tier tool should have limits defined."""
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(pro_license_path)

        try:
            # Get a specific tool capability (e.g., get_file_context which is available in Pro)
            tool_cap = get_tool_capabilities("get_file_context", "pro")
            assert tool_cap is not None
            assert tool_cap.get("available", False)
            assert "limits" in tool_cap

            limits = tool_cap.get("limits", {})
            # Pro has limits (e.g., max_lines)
            assert isinstance(limits, dict)
        finally:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)


class TestCapabilitiesWithEnterpriseLicense:
    """Test capabilities when Enterprise tier license is present."""

    def test_enterprise_tier_shows_all_tools(
        self, clear_all_caches, enterprise_license_path
    ):
        """Enterprise license should enable all available tools."""
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(enterprise_license_path)

        try:
            tier = _get_current_tier()
            assert tier == "enterprise", f"Expected enterprise tier, got {tier}"

            capabilities = get_all_capabilities(tier)
            assert capabilities is not None
            assert len(capabilities) > 0

            # Enterprise tier should have 14 available tools
            available_tools = sum(
                1 for tool in capabilities.values() if tool.get("available", False)
            )
            assert (
                available_tools == 14
            ), f"Enterprise tier should have 14 available tools, got {available_tools}"
        finally:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)

    def test_enterprise_has_focused_tool_set(
        self, clear_all_caches, enterprise_license_path
    ):
        """Enterprise tier has a focused set of tools (different than Pro, not superset)."""
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(enterprise_license_path)

        try:
            tier = _get_current_tier()
            assert tier == "enterprise"

            # Get Enterprise tool list
            enterprise_capabilities = get_all_capabilities("enterprise")
            enterprise_tools = {
                tool_id
                for tool_id, cap in enterprise_capabilities.items()
                if cap.get("available", False)
            }

            # Enterprise tier has specific tools available (14 tools)
            # (The tier structure is not hierarchical - different tiers have different capabilities)
            expected_tools = {
                "analyze_code",
                "code_policy_check",
                "crawl_project",
                "extract_code",
                "generate_unit_tests",
                "get_project_map",
                "scan_dependencies",
                "security_scan",
                "simulate_refactor",
                "symbolic_execute",
                "type_evaporation_scan",
                "unified_sink_detect",
                "update_symbol",
                "verify_policy_integrity",
            }

            assert enterprise_tools == expected_tools, (
                f"Enterprise tools mismatch. "
                f"Missing: {expected_tools - enterprise_tools}, "
                f"Extra: {enterprise_tools - expected_tools}"
            )
        finally:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)

    def test_enterprise_has_different_tools_than_pro(
        self, clear_all_caches, pro_license_path, enterprise_license_path
    ):
        """Enterprise and Pro tiers have different tool sets (not hierarchical)."""
        # Get Pro capabilities
        pro_cap = get_tool_capabilities("get_file_context", "pro")
        enterprise_cap = get_tool_capabilities("get_file_context", "enterprise")

        try:
            # Pro tier HAS get_file_context
            assert pro_cap.get(
                "available", False
            ), "Pro tier should have get_file_context available"

            # But Enterprise tier does NOT have get_file_context
            # (Enterprise has different, more focused tools)
            assert not enterprise_cap.get("available", False), (
                "Enterprise tier doesn't have get_file_context "
                "(tiers have different tools, not hierarchical)"
            )

            # But Enterprise should have other tools
            enterprise_analyze = get_tool_capabilities("analyze_code", "enterprise")
            assert enterprise_analyze.get(
                "available", False
            ), "Enterprise tier should have analyze_code available"
        finally:
            pass


class TestCapabilitiesWithoutLicense:
    """Test capabilities when no license is present (Community tier)."""

    def test_community_tier_has_basic_tools(self, clear_all_caches):
        """Community tier should have basic tools available."""
        # No license set, should default to community
        tier = _get_current_tier()
        assert tier == "community"

        capabilities = get_all_capabilities(tier)
        assert capabilities is not None

        # Community tier should have all 22 tools available
        available_tools = sum(
            1 for tool in capabilities.values() if tool.get("available", False)
        )
        assert (
            available_tools == 22
        ), f"Community tier should have all 22 tools, got {available_tools}"

    def test_community_tier_has_limits(self, clear_all_caches):
        """Community tools should have limits defined."""
        tier = _get_current_tier()
        assert tier == "community"

        tool_cap = get_tool_capabilities("get_file_context", tier)
        assert tool_cap is not None
        assert tool_cap.get("available", False)
        assert "limits" in tool_cap

    def test_all_22_tools_listed(self, clear_all_caches):
        """All 22 tools should be enumerated."""
        capabilities = get_all_capabilities("community")
        assert (
            len(capabilities) == 22
        ), f"Expected 22 tools total, got {len(capabilities)}"
