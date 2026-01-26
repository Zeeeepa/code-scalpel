"""Tier-based testing for verify_policy_integrity MCP tool.

Tests verify that verify_policy_integrity respects tier-based limits:
- Community: basic verification only, max 50 policy files
- Pro: signature validation enabled, max 200 policy files
- Enterprise: full integrity check with audit logging, unlimited files

Also verifies feature availability across tiers (tamper detection, audit logging, etc).

[20260126_TEST] Created comprehensive tier test suite for verify_policy_integrity.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_verify_policy_integrity_community_basic_only(community_tier):
    """Community tier has only basic verification."""
    from code_scalpel.licensing.features import has_capability

    assert has_capability("verify_policy_integrity", "basic_verification", "community")
    assert not has_capability(
        "verify_policy_integrity", "signature_validation", "community"
    )
    assert not has_capability("verify_policy_integrity", "audit_logging", "community")


@pytest.mark.asyncio
async def test_verify_policy_integrity_pro_signature_validation(pro_tier):
    """Pro tier enables signature validation."""
    from code_scalpel.licensing.features import has_capability

    assert has_capability("verify_policy_integrity", "basic_verification", "pro")
    assert has_capability("verify_policy_integrity", "signature_validation", "pro")
    assert not has_capability("verify_policy_integrity", "audit_logging", "pro")


@pytest.mark.asyncio
async def test_verify_policy_integrity_enterprise_full_check(enterprise_tier):
    """Enterprise tier has full integrity check with audit logging."""
    from code_scalpel.licensing.features import has_capability

    assert has_capability("verify_policy_integrity", "basic_verification", "enterprise")
    assert has_capability(
        "verify_policy_integrity", "signature_validation", "enterprise"
    )
    assert has_capability(
        "verify_policy_integrity", "full_integrity_check", "enterprise"
    )
    assert has_capability("verify_policy_integrity", "audit_logging", "enterprise")


@pytest.mark.asyncio
async def test_verify_policy_integrity_community_file_limit(community_tier):
    """Community tier limits to 50 policy files."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "community")
    limits = caps.get("limits", {})

    assert (
        limits.get("max_policy_files") == 50
    ), "Community should limit to 50 policy files"


@pytest.mark.asyncio
async def test_verify_policy_integrity_pro_file_limit(pro_tier):
    """Pro tier increases file limit to 200."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "pro")
    limits = caps.get("limits", {})

    assert limits.get("max_policy_files") == 200, "Pro should allow 200 policy files"


@pytest.mark.asyncio
async def test_verify_policy_integrity_enterprise_unlimited(enterprise_tier):
    """Enterprise tier has no file limits."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "enterprise")
    limits = caps.get("limits", {})

    assert (
        limits.get("max_policy_files") is None
    ), "Enterprise should have unlimited policy files"


@pytest.mark.asyncio
async def test_verify_policy_integrity_community_no_tamper_detection(community_tier):
    """Community tier does not have tamper detection."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "community")
    limits = caps.get("limits", {})

    assert (
        limits.get("tamper_detection") is False
    ), "Community should not have tamper detection"


@pytest.mark.asyncio
async def test_verify_policy_integrity_pro_tamper_detection(pro_tier):
    """Pro tier enables tamper detection."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "pro")
    limits = caps.get("limits", {})

    assert limits.get("tamper_detection") is True, "Pro should have tamper detection"


@pytest.mark.asyncio
async def test_verify_policy_integrity_enterprise_tamper_detection(enterprise_tier):
    """Enterprise tier has tamper detection enabled."""
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("verify_policy_integrity", "enterprise")
    limits = caps.get("limits", {})

    assert (
        limits.get("tamper_detection") is True
    ), "Enterprise should have tamper detection"
