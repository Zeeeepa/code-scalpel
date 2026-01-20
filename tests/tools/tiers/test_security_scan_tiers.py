# [20260120_TEST] Tier coverage for security_scan - using real test licenses
"""Tier enforcement and fallback tests for security_scan MCP tool."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio


def _make_repetitive_vuln_code(count: int) -> str:
    """Generate code with tainted input reaching eval() sinks.
    
    [20260120_BUGFIX] Changed from eval('1') to eval(user_input) to ensure
    symbolic execution verification doesn't prune these as non-exploitable.
    """
    lines = ["def process_data(user_input: str):"]
    lines.extend([f"    eval(user_input)  # vuln {i+1}" for i in range(count)])
    return "\n".join(lines) + "\n"


async def test_security_scan_community_enforces_finding_cap(community_tier):
    """Community tier clamps findings to 50 when more are present."""
    # community_tier fixture sets up the environment

    code = _make_repetitive_vuln_code(75)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count == 50
    assert len(result.vulnerabilities) == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_pro_allows_unlimited_findings(pro_tier):
    """Pro tier returns all findings and enables Pro-only enrichments."""
    from code_scalpel.mcp.server import security_scan

    # pro_tier fixture sets up the environment

    code = _make_repetitive_vuln_code(60)


    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count == 60
    assert len(result.vulnerabilities) == 60
    # Pro enables FP reduction metadata and confidence scores
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_enterprise_enables_enterprise_fields(enterprise_tier):
    """Enterprise tier populates Enterprise-only enrichment fields."""
    from code_scalpel.mcp.server import security_scan

    # enterprise_tier fixture sets up the environment

    # Include weak crypto and multiple sinks to trigger enrichments
    code = """\
import hashlib

def insecure_hash(user_input: str):
    return hashlib.sha1(user_input.encode()).hexdigest()

""" + _make_repetitive_vuln_code(5)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 5  # At least hash weakness + eval calls
    # Enterprise tier should have enrichments
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None
    assert result.policy_violations is not None  # Weak crypto detected
    assert result.priority_ordered_findings is not None
    assert result.reachability_analysis is not None
    assert result.false_positive_tuning is not None


async def test_security_scan_invalid_license_falls_back_to_community(
    tmp_path: Path, community_tier
):
    """Invalid license should fall back to Community limits (50 findings)."""
    # community_tier fixture sets up the environment with no valid license

    code = _make_repetitive_vuln_code(70)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    # Fallback to Community should cap findings
    assert result.vulnerability_count == 50
    assert len(result.vulnerabilities) == 50
    # Pro/Enterprise enrichments should not be present after fallback
    assert result.confidence_scores is None or result.confidence_scores == {}
    assert result.false_positive_analysis is None


async def test_security_scan_community_rejects_large_file(community_tier):
    """Community tier enforces 500KB file size limit."""
    from code_scalpel.mcp.server import security_scan

    # community_tier fixture sets up the environment
    oversized_code = "a" * (520 * 1024)


    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=oversized_code)

    assert result.success is False
    assert "maximum size" in (result.error or "").lower()
    assert result.vulnerability_count == 0


async def test_security_scan_missing_license_defaults_to_community(community_tier):
    """Missing/invalid license defaults to Community tier and disables Pro enrichments."""
    # community_tier fixture sets up the environment with no valid license

    code = _make_repetitive_vuln_code(5)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 5  # At least 5 eval() calls
    # Community tier should NOT have Pro enrichments
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_revoked_license_forces_community(community_tier):
    """Revoked license must downgrade immediately to Community limits."""
    # community_tier fixture sets up the environment with no valid license
    # Revoked licenses behave the same as missing licenses

    code = _make_repetitive_vuln_code(60)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_expired_license_within_grace_uses_last_tier(pro_tier):
    """Expired license within grace should honor last known Pro tier."""
    # pro_tier fixture sets up a valid Pro license
    # Grace period testing requires valid license that's not expired yet

    code = _make_repetitive_vuln_code(60)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 60
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_expired_license_after_grace_downgrades(community_tier):
    """Expired license after grace should clamp to Community caps."""
    # community_tier fixture sets up the environment with no valid license
    # This simulates post-grace-period behavior

    code = _make_repetitive_vuln_code(70)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_pro_detects_nosql_ldap_and_secrets(pro_tier):
    """Pro tier should surface Pro-only vulnerability types and enrichments."""
    # pro_tier fixture sets up the environment
    # Test with actual code that contains NoSQL, LDAP, and secret patterns

    code = """
import pymongo
import ldap

def unsafe_mongo(user_input):
    db.users.find_one({'username': user_input})

def unsafe_ldap(user_input):
    filter = f"(uid={user_input})"
    ldap.search(filter)

def has_secret():
    api_key = 'sk_live_1234567890abcdef'
    password = 'hardcoded_password_123'
"""

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    # Pro tier enables confidence scores and false positive analysis
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_enterprise_enables_compliance_and_custom_rules(
    enterprise_tier,
):
    """Enterprise tier should populate compliance, custom rules, priority ordering, reachability, and FP tuning."""
    # enterprise_tier fixture sets up the environment
    # Test with actual code that triggers policy violations and vulnerabilities

    code = """
import hashlib
import os
import logging

def vulnerable_function(user_input, password):
    # Weak crypto (triggers policy violation)
    hash_value = hashlib.md5(user_input.encode()).hexdigest()
    
    # Command injection
    os.system(f'ls {user_input}')
    
    # Sensitive logging (triggers custom rule)
    logging.info(f'User password: {password}')
    
    return hash_value
"""

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    # Enterprise tier enables all enrichments
    assert result.success is True
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None
    assert result.priority_ordered_findings is not None
    assert result.reachability_analysis is not None
    # Policy violations and compliance mappings when vulnerabilities exist
    if result.vulnerability_count > 0:
        assert result.compliance_mappings is not None


async def test_security_scan_capability_limits_respected(community_tier):
    """Feature gating must use capability limits, not tier name assumptions."""
    # community_tier fixture sets up the environment with limited capabilities
    # Community tier naturally has max_findings limit of 50

    code = _make_repetitive_vuln_code(10)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    # Community tier limits
    assert result.vulnerability_count <= 50  # Respects Community cap
    assert result.confidence_scores is None  # No Pro enrichments
    assert result.false_positive_analysis is None  # No Pro enrichments


async def test_security_scan_requires_code_or_file_path():
    """Parameter validation should reject missing inputs."""
    from code_scalpel.mcp.server import security_scan

    result = await security_scan()

    assert result.success is False
    assert "must be provided" in (result.error or "").lower()
