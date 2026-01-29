"""Tier-based testing for code_policy_check MCP tool.

Tests verify that code_policy_check respects tier-based limits:
- Community: max 100 files, max 50 rules
- Pro: max 1000 files, max 200 rules
- Enterprise: unlimited files and rules

Also verifies compliance framework availability across tiers.

[20260124_TEST] Created comprehensive tier test suite for code_policy_check.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_code_policy_check_community_file_limit(community_tier):
    """Community tier limits to 100 files."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "community")
    limits = caps.get("limits", {})

    assert limits.get("max_files") == 100, "Community should limit to 100 files"


@pytest.mark.asyncio
async def test_code_policy_check_pro_file_limit(pro_tier):
    """Pro tier increases file limit to 1000."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "pro")
    limits = caps.get("limits", {})

    assert limits.get("max_files") == 1000, "Pro should allow 1000 files"


@pytest.mark.asyncio
async def test_code_policy_check_enterprise_unlimited(enterprise_tier):
    """Enterprise tier has no file limits."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "enterprise")
    limits = caps.get("limits", {})

    assert limits.get("max_files") is None, "Enterprise should have unlimited files"


@pytest.mark.asyncio
async def test_code_policy_check_community_rule_limit(community_tier):
    """Community tier limits to 50 rules."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "community")
    limits = caps.get("limits", {})

    assert limits.get("max_rules") == 50, "Community should limit to 50 rules"


@pytest.mark.asyncio
async def test_code_policy_check_pro_rule_limit(pro_tier):
    """Pro tier increases rule limit to 200."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "pro")
    limits = caps.get("limits", {})

    assert limits.get("max_rules") == 200, "Pro should allow 200 rules"


@pytest.mark.asyncio
async def test_code_policy_check_enterprise_rule_unlimited(enterprise_tier):
    """Enterprise tier has no rule limits."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("code_policy_check", "enterprise")
    limits = caps.get("limits", {})

    assert limits.get("max_rules") is None, "Enterprise should have unlimited rules"


@pytest.mark.asyncio
async def test_code_policy_check_community_basic_compliance(community_tier):
    """Community tier has only basic compliance framework."""
    from code_scalpel.licensing.features import has_capability

    # Community should have OWASP only
    assert has_capability("code_policy_check", "basic_compliance", "community")
    assert not has_capability("code_policy_check", "hipaa_compliance", "community")
    assert not has_capability("code_policy_check", "soc2_compliance", "community")


@pytest.mark.asyncio
async def test_code_policy_check_pro_compliance_frameworks(pro_tier):
    """Pro tier has extended compliance frameworks."""
    from code_scalpel.licensing.features import has_capability

    # Pro should have multiple compliance frameworks
    assert has_capability("code_policy_check", "basic_compliance", "pro")
    assert has_capability("code_policy_check", "extended_compliance", "pro")


@pytest.mark.asyncio
async def test_code_policy_check_enterprise_all_compliance(enterprise_tier):
    """Enterprise tier has all compliance frameworks."""
    from code_scalpel.licensing.features import has_capability

    compliance_frameworks = [
        "basic_compliance",
        "hipaa_compliance",
        "soc2_compliance",
        "gdpr_compliance",
        "pci_dss_compliance",
    ]

    for framework in compliance_frameworks:
        assert has_capability("code_policy_check", framework, "enterprise"), f"Enterprise should have {framework}"
