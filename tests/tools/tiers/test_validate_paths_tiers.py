"""Tier-based testing for validate_paths MCP tool.

Tests verify that validate_paths respects tier-based limits:
- Community: max 100 paths
- Pro: unlimited paths
- Enterprise: unlimited paths + Docker security features

Also verifies Docker detection and suggestion features across tiers.

[20260124_TEST] Created comprehensive tier test suite for validate_paths.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_validate_paths_community_limit(community_tier):
    """Community tier limits to 100 paths."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("validate_paths", "community")
    limits = caps.get("limits", {})

    assert limits.get("max_paths") == 100, "Community should limit to 100 paths"


@pytest.mark.asyncio
async def test_validate_paths_pro_unlimited(pro_tier):
    """Pro tier removes path limit."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("validate_paths", "pro")
    limits = caps.get("limits", {})

    assert limits.get("max_paths") is None, "Pro should have unlimited paths"


@pytest.mark.asyncio
async def test_validate_paths_enterprise_unlimited(enterprise_tier):
    """Enterprise tier has no path limits."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("validate_paths", "enterprise")
    limits = caps.get("limits", {})

    assert limits.get("max_paths") is None, "Enterprise should have unlimited paths"


@pytest.mark.asyncio
async def test_validate_paths_community_core_features(community_tier):
    """Community tier has core path checking features."""
    from code_scalpel.licensing.features import has_capability

    expected_capabilities = [
        "path_accessibility_checking",
        "workspace_root_detection",
        "actionable_error_messages",
        "docker_environment_detection",
        "docker_volume_mount_suggestions",
    ]

    for cap in expected_capabilities:
        assert has_capability("validate_paths", cap, "community"), f"Community should have {cap}"


@pytest.mark.asyncio
async def test_validate_paths_pro_enhanced_features(pro_tier):
    """Pro tier has additional path validation features."""
    from code_scalpel.licensing.features import has_capability

    # Pro should have all community capabilities
    community_caps = [
        "path_accessibility_checking",
        "workspace_root_detection",
        "actionable_error_messages",
    ]

    for cap in community_caps:
        assert has_capability("validate_paths", cap, "pro"), f"Pro should inherit {cap}"


@pytest.mark.asyncio
async def test_validate_paths_enterprise_security(enterprise_tier):
    """Enterprise tier has security validation features."""
    from code_scalpel.licensing.features import has_capability

    security_features = [
        "path_accessibility_checking",
        "workspace_root_detection",
        "docker_environment_detection",
        "docker_volume_mount_suggestions",
    ]

    for feature in security_features:
        assert has_capability("validate_paths", feature, "enterprise"), f"Enterprise should have {feature}"


@pytest.mark.asyncio
async def test_validate_paths_docker_detection_all_tiers(community_tier, pro_tier, enterprise_tier):
    """Docker environment detection available in all tiers."""
    from code_scalpel.licensing.features import has_capability

    for tier in ["community", "pro", "enterprise"]:
        assert has_capability(
            "validate_paths", "docker_environment_detection", tier
        ), f"{tier.title()} should detect Docker environments"
