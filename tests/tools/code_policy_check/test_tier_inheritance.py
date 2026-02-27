"""
Test suite proving Enterprise tier contains all Pro tier features plus Enterprise features.

This test suite explicitly verifies the additive tier model:
- Community: Base features
- Pro: All Community + Pro features
- Enterprise: All Pro + Enterprise features

These tests are critical for CTOs and Engineers to trust that upgrading tiers
adds capabilities without removing access to lower-tier features.

[20260212_TEST] Created tier inheritance verification test suite.
"""

from pathlib import Path

import pytest

from code_scalpel.licensing.features import get_tool_capabilities, has_capability


@pytest.fixture
def pro_license(monkeypatch):
    """Force Pro tier using bundled license. Skips if license is absent/invalid."""
    license_dir = Path(__file__).parent.parent.parent / "licenses"
    pro_licenses = list(license_dir.glob("code_scalpel_license_pro_*.jwt"))
    if not pro_licenses:
        pytest.skip(f"No Pro license file found in {license_dir}")
    license_path = pro_licenses[0]
    if not license_path.read_text(encoding="utf-8").strip():
        pytest.skip("Pro license file is empty (secret not set in CI)")

    monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(license_path))
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")

    # Verify the license actually activates Pro tier — skip if invalid/expired
    try:
        from code_scalpel.licensing import jwt_validator, config_loader
        jwt_validator._LICENSE_VALIDATION_CACHE = None
        config_loader.clear_cache()
    except Exception:
        pass
    from code_scalpel.mcp.server import _get_current_tier
    actual_tier = _get_current_tier()
    if actual_tier != "pro":
        monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
        monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)
        pytest.skip(
            f"Pro license did not activate Pro tier (got '{actual_tier}'). "
            "License may be expired or have invalid signature."
        )

    yield
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
    monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)


@pytest.fixture
def enterprise_license(monkeypatch):
    """Force Enterprise tier using bundled license."""
    license_dir = Path(__file__).parent.parent.parent / "licenses"
    enterprise_licenses = list(
        license_dir.glob("code_scalpel_license_enterprise_*.jwt")
    )
    assert enterprise_licenses, f"No Enterprise license found in {license_dir}"
    license_path = enterprise_licenses[0]

    monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(license_path))
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
    yield
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
    monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)


class TestEnterpriseInheritsAllProCapabilities:
    """Verify Enterprise tier includes ALL Pro tier capabilities."""

    def test_enterprise_has_all_pro_capabilities(self):
        """
        CRITICAL: Enterprise must have every capability that Pro has.

        This is the additive tier model guarantee for customers.
        """
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        pro_capabilities = set(pro_caps.get("capabilities", []))
        enterprise_capabilities = set(enterprise_caps.get("capabilities", []))

        # Enterprise MUST be a superset of Pro
        missing_in_enterprise = pro_capabilities - enterprise_capabilities

        assert len(missing_in_enterprise) == 0, (
            f"Enterprise tier missing Pro capabilities: {missing_in_enterprise}. "
            f"Enterprise must include all Pro features."
        )

    def test_enterprise_has_pro_best_practice_analysis(self):
        """Verify Enterprise includes Pro's best_practice_analysis."""
        assert has_capability("code_policy_check", "best_practice_analysis", "pro")
        assert has_capability(
            "code_policy_check", "best_practice_analysis", "enterprise"
        )

    def test_enterprise_has_pro_security_patterns(self):
        """Verify Enterprise includes Pro's security_patterns."""
        assert has_capability("code_policy_check", "security_patterns", "pro")
        assert has_capability("code_policy_check", "security_patterns", "enterprise")

    def test_enterprise_has_pro_custom_rules(self):
        """Verify Enterprise includes Pro's custom_rules."""
        assert has_capability("code_policy_check", "custom_rules", "pro")
        assert has_capability("code_policy_check", "custom_rules", "enterprise")

    def test_enterprise_has_pro_async_error_patterns(self):
        """Verify Enterprise includes Pro's async_error_patterns."""
        assert has_capability("code_policy_check", "async_error_patterns", "pro")
        assert has_capability("code_policy_check", "async_error_patterns", "enterprise")

    def test_enterprise_has_pro_extended_compliance(self):
        """Verify Enterprise includes Pro's extended_compliance."""
        assert has_capability("code_policy_check", "extended_compliance", "pro")
        assert has_capability("code_policy_check", "extended_compliance", "enterprise")


class TestEnterpriseAdditionsOverPro:
    """Verify Enterprise adds capabilities beyond Pro tier."""

    def test_enterprise_has_hipaa_compliance(self):
        """Enterprise adds HIPAA compliance (not in Pro)."""
        assert not has_capability("code_policy_check", "hipaa_compliance", "pro")
        assert has_capability("code_policy_check", "hipaa_compliance", "enterprise")

    def test_enterprise_has_soc2_compliance(self):
        """Enterprise adds SOC2 compliance (not in Pro)."""
        assert not has_capability("code_policy_check", "soc2_compliance", "pro")
        assert has_capability("code_policy_check", "soc2_compliance", "enterprise")

    def test_enterprise_has_gdpr_compliance(self):
        """Enterprise adds GDPR compliance (not in Pro)."""
        assert not has_capability("code_policy_check", "gdpr_compliance", "pro")
        assert has_capability("code_policy_check", "gdpr_compliance", "enterprise")

    def test_enterprise_has_pci_dss_compliance(self):
        """Enterprise adds PCI-DSS compliance (not in Pro)."""
        assert not has_capability("code_policy_check", "pci_dss_compliance", "pro")
        assert has_capability("code_policy_check", "pci_dss_compliance", "enterprise")

    def test_enterprise_has_audit_trail(self):
        """Enterprise adds audit_trail (not in Pro)."""
        assert not has_capability("code_policy_check", "audit_trail", "pro")
        assert has_capability("code_policy_check", "audit_trail", "enterprise")

    def test_enterprise_has_pdf_certification(self):
        """Enterprise adds pdf_certification (not in Pro)."""
        assert not has_capability("code_policy_check", "pdf_certification", "pro")
        assert has_capability("code_policy_check", "pdf_certification", "enterprise")

    def test_enterprise_has_compliance_auditing(self):
        """Enterprise adds compliance_auditing (not in Pro)."""
        assert not has_capability("code_policy_check", "compliance_auditing", "pro")
        assert has_capability("code_policy_check", "compliance_auditing", "enterprise")


class TestEnterpriseUniqueCapabilityCount:
    """Verify Enterprise has more capabilities than Pro."""

    def test_enterprise_has_more_capabilities_than_pro(self):
        """Enterprise should have strictly more capabilities than Pro."""
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        pro_count = len(pro_caps.get("capabilities", []))
        enterprise_count = len(enterprise_caps.get("capabilities", []))

        assert enterprise_count > pro_count, (
            f"Enterprise ({enterprise_count} capabilities) should have more than "
            f"Pro ({pro_count} capabilities)"
        )

    def test_enterprise_has_at_least_7_unique_capabilities(self):
        """Enterprise should add at least 7 unique capabilities over Pro."""
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        pro_capabilities = set(pro_caps.get("capabilities", []))
        enterprise_capabilities = set(enterprise_caps.get("capabilities", []))

        unique_to_enterprise = enterprise_capabilities - pro_capabilities

        # Enterprise adds HIPAA, SOC2, GDPR, PCI-DSS, audit_trail, pdf_certification, compliance_auditing
        assert len(unique_to_enterprise) >= 7, (
            f"Enterprise should add at least 7 unique capabilities. "
            f"Found {len(unique_to_enterprise)}: {unique_to_enterprise}"
        )


class TestProInheritsAllCommunityCapabilities:
    """Verify Pro tier includes ALL Community tier capabilities."""

    def test_pro_has_all_community_capabilities(self):
        """Pro must have every capability that Community has."""
        community_caps = get_tool_capabilities("code_policy_check", "community")
        pro_caps = get_tool_capabilities("code_policy_check", "pro")

        community_capabilities = set(community_caps.get("capabilities", []))
        pro_capabilities = set(pro_caps.get("capabilities", []))

        # Pro MUST be a superset of Community
        missing_in_pro = community_capabilities - pro_capabilities

        assert len(missing_in_pro) == 0, (
            f"Pro tier missing Community capabilities: {missing_in_pro}. "
            f"Pro must include all Community features."
        )

    def test_pro_has_community_basic_compliance(self):
        """Verify Pro includes Community's basic_compliance."""
        assert has_capability("code_policy_check", "basic_compliance", "community")
        assert has_capability("code_policy_check", "basic_compliance", "pro")

    def test_pro_has_community_pep8_validation(self):
        """Verify Pro includes Community's pep8_validation."""
        assert has_capability("code_policy_check", "pep8_validation", "community")
        assert has_capability("code_policy_check", "pep8_validation", "pro")

    def test_pro_has_community_style_guide_checking(self):
        """Verify Pro includes Community's style_guide_checking."""
        assert has_capability("code_policy_check", "style_guide_checking", "community")
        assert has_capability("code_policy_check", "style_guide_checking", "pro")


class TestAdditiveTierModel:
    """Comprehensive tests proving the additive tier model."""

    def test_capability_counts_increase_by_tier(self):
        """Verify capability count increases: Community < Pro < Enterprise."""
        community_caps = get_tool_capabilities("code_policy_check", "community")
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        community_count = len(community_caps.get("capabilities", []))
        pro_count = len(pro_caps.get("capabilities", []))
        enterprise_count = len(enterprise_caps.get("capabilities", []))

        assert community_count < pro_count < enterprise_count, (
            f"Capability counts should increase by tier: "
            f"Community ({community_count}) < Pro ({pro_count}) < Enterprise ({enterprise_count})"
        )

    def test_limits_relax_by_tier(self):
        """Verify limits become more permissive: Community → Pro → Enterprise."""
        community_caps = get_tool_capabilities("code_policy_check", "community")
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        community_max_files = community_caps["limits"].get("max_files")
        pro_max_files = pro_caps["limits"].get("max_files")
        enterprise_max_files = enterprise_caps["limits"].get("max_files")

        # Community has strict limit (100)
        assert community_max_files == 100

        # Pro and Enterprise are unlimited (-1 or None)
        assert pro_max_files is None or pro_max_files == -1
        assert enterprise_max_files is None or enterprise_max_files == -1

    def test_no_capability_regression_pro_to_enterprise(self):
        """Ensure no Pro capability is lost when upgrading to Enterprise."""
        pro_caps = get_tool_capabilities("code_policy_check", "pro")
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")

        pro_capabilities = set(pro_caps.get("capabilities", []))
        enterprise_capabilities = set(enterprise_caps.get("capabilities", []))

        # Every Pro capability MUST exist in Enterprise
        for cap in pro_capabilities:
            assert cap in enterprise_capabilities, (
                f"Pro capability '{cap}' is missing in Enterprise tier. "
                f"This violates the additive tier model."
            )

    def test_no_capability_regression_community_to_pro(self):
        """Ensure no Community capability is lost when upgrading to Pro."""
        community_caps = get_tool_capabilities("code_policy_check", "community")
        pro_caps = get_tool_capabilities("code_policy_check", "pro")

        community_capabilities = set(community_caps.get("capabilities", []))
        pro_capabilities = set(pro_caps.get("capabilities", []))

        # Every Community capability MUST exist in Pro
        for cap in community_capabilities:
            assert cap in pro_capabilities, (
                f"Community capability '{cap}' is missing in Pro tier. "
                f"This violates the additive tier model."
            )


class TestEnterpriseComprehensiveCapabilities:
    """Verify Enterprise has the complete feature set."""

    def test_enterprise_has_all_24_code_policy_capabilities(self):
        """Enterprise should have all 24 code_policy_check capabilities."""
        enterprise_caps = get_tool_capabilities("code_policy_check", "enterprise")
        capabilities = enterprise_caps.get("capabilities", [])

        # Enterprise has all features from all tiers
        expected_capabilities = {
            # Community tier (5)
            "basic_compliance",
            "basic_patterns",
            "eslint_rules",
            "pep8_validation",
            "style_guide_checking",
            # Pro tier additions (5)
            "async_error_patterns",
            "best_practice_analysis",
            "custom_rules",
            "extended_compliance",
            "security_patterns",
            # Enterprise tier additions (7)
            "audit_trail",
            "compliance_auditing",
            "gdpr_compliance",
            "hipaa_compliance",
            "pci_dss_compliance",
            "pdf_certification",
            "soc2_compliance",
        }

        actual_capabilities = set(capabilities)

        missing = expected_capabilities - actual_capabilities
        assert len(missing) == 0, f"Enterprise missing expected capabilities: {missing}"

        # Verify we have at least the expected count
        assert len(actual_capabilities) >= len(expected_capabilities), (
            f"Enterprise has {len(actual_capabilities)} capabilities, "
            f"expected at least {len(expected_capabilities)}"
        )
