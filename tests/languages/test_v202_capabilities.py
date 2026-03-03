"""Tests for v2.0.2 C/C++/C# capability expansions.

Verifies that the four tools updated in v2.0.2 carry the correct capabilities
and limits across all three tiers:

  - unified_sink_detect  : C and C++ sink detection (limits.toml languages + features.toml)
  - generate_unit_tests  : Catch2/NUnit (Community+); Google Test/xUnit (Pro+)
  - code_policy_check    : clang-tidy + Roslyn (Community+); MISRA-C (Enterprise only)
  - scan_dependencies    : Conan, vcpkg (C/C++); NuGet (C#) — all tiers

[20260225_TEST] Created for v2.0.2 polyglot capability expansion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers to load TOML config files without depending on runtime licensing
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIMITS_TOML = PROJECT_ROOT / "src" / "code_scalpel" / "capabilities" / "limits.toml"
FEATURES_TOML = PROJECT_ROOT / "src" / "code_scalpel" / "capabilities" / "features.toml"

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        import tomllib  # type: ignore[no-redef]


def _load_limits() -> dict:
    with open(LIMITS_TOML, "rb") as fh:
        return tomllib.load(fh)


def _load_features() -> dict:
    with open(FEATURES_TOML, "rb") as fh:
        return tomllib.load(fh)


# ---------------------------------------------------------------------------
# unified_sink_detect — C/C++ language support
# ---------------------------------------------------------------------------


class TestUnifiedSinkDetectCLanguages:
    """unified_sink_detect should support C and C++ across all tiers (v2.0.2)."""

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_limits_toml_includes_c_and_cpp(self, tier):
        """limits.toml languages array must contain 'c' and 'cpp' for every tier."""
        limits = _load_limits()
        languages = limits[tier]["unified_sink_detect"]["languages"]
        assert "c" in languages, f"[{tier}] unified_sink_detect should support 'c'"
        assert "cpp" in languages, f"[{tier}] unified_sink_detect should support 'cpp'"

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_features_toml_has_c_sink_detection(self, tier):
        """features.toml must list 'c_sink_detection' capability for every tier."""
        features = _load_features()
        caps = features[tier]["unified_sink_detect"]["capabilities"]
        assert (
            "c_sink_detection" in caps
        ), f"[{tier}] unified_sink_detect capabilities missing 'c_sink_detection'"

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_features_toml_has_cpp_sink_detection(self, tier):
        """features.toml must list 'cpp_sink_detection' capability for every tier."""
        features = _load_features()
        caps = features[tier]["unified_sink_detect"]["capabilities"]
        assert (
            "cpp_sink_detection" in caps
        ), f"[{tier}] unified_sink_detect capabilities missing 'cpp_sink_detection'"

    def test_community_still_has_all_original_languages(self):
        """Adding C/C++ must not remove the original four languages."""
        limits = _load_limits()
        languages = limits["community"]["unified_sink_detect"]["languages"]
        for lang in ("python", "javascript", "typescript", "java"):
            assert lang in languages, f"unified_sink_detect Community lost '{lang}'"

    def test_community_max_sinks_unchanged(self):
        """Community sink limit (50) must remain unchanged."""
        limits = _load_limits()
        assert limits["community"]["unified_sink_detect"]["max_sinks"] == 50

    def test_pro_enterprise_max_sinks_unlimited(self):
        """Pro and Enterprise should have unlimited sinks (-1 sentinel)."""
        limits = _load_limits()
        assert limits["pro"]["unified_sink_detect"]["max_sinks"] == -1
        assert limits["enterprise"]["unified_sink_detect"]["max_sinks"] == -1


# ---------------------------------------------------------------------------
# generate_unit_tests — C/C++ and C# test framework support
# ---------------------------------------------------------------------------


class TestGenerateUnitTestsCLanguages:
    """generate_unit_tests should list C/C++/C# test frameworks (v2.0.2)."""

    # Catch2 (C/C++) and NUnit (C#): all tiers
    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    @pytest.mark.parametrize("framework", ["catch2_support", "nunit_support"])
    def test_all_tiers_have_basic_c_csharp_frameworks(self, tier, framework):
        """Catch2 and NUnit should be available at every tier."""
        features = _load_features()
        caps = features[tier]["generate_unit_tests"]["capabilities"]
        assert framework in caps, f"[{tier}] generate_unit_tests missing '{framework}'"

    # Google Test (C/C++) and xUnit (C#): Pro and Enterprise only
    @pytest.mark.parametrize("tier", ["pro", "enterprise"])
    @pytest.mark.parametrize("framework", ["googletest_support", "xunit_support"])
    def test_pro_enterprise_have_advanced_c_csharp_frameworks(self, tier, framework):
        """Google Test and xUnit should be available at Pro and Enterprise."""
        features = _load_features()
        caps = features[tier]["generate_unit_tests"]["capabilities"]
        assert framework in caps, f"[{tier}] generate_unit_tests missing '{framework}'"

    def test_community_does_not_have_googletest(self):
        """Google Test is a Pro+ framework and should NOT appear in Community."""
        features = _load_features()
        caps = features["community"]["generate_unit_tests"]["capabilities"]
        assert (
            "googletest_support" not in caps
        ), "googletest_support should be Pro+ only (Community lacks advanced test gen)"

    def test_community_does_not_have_xunit(self):
        """xUnit is a Pro+ framework and should NOT appear in Community."""
        features = _load_features()
        caps = features["community"]["generate_unit_tests"]["capabilities"]
        assert "xunit_support" not in caps, "xunit_support should be Pro+ only"

    def test_original_python_js_frameworks_preserved(self):
        """Adding C/C++/C# frameworks must not remove pytest, jest, etc."""
        features = _load_features()
        # Community must still have pytest
        community_caps = features["community"]["generate_unit_tests"]["capabilities"]
        assert "pytest_support" in community_caps
        # Pro must still have pytest, unittest, jest
        pro_caps = features["pro"]["generate_unit_tests"]["capabilities"]
        for fw in ("pytest_support", "unittest_support", "jest_support"):
            assert fw in pro_caps, f"Pro generate_unit_tests lost '{fw}'"
        # Enterprise must still have mocha
        ent_caps = features["enterprise"]["generate_unit_tests"]["capabilities"]
        assert "mocha_support" in ent_caps


# ---------------------------------------------------------------------------
# code_policy_check — clang-tidy, Roslyn, MISRA-C
# ---------------------------------------------------------------------------


class TestCodePolicyCheckCLanguages:
    """code_policy_check should include C/C++/C# linting capabilities (v2.0.2)."""

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_all_tiers_have_clang_tidy_rules(self, tier):
        """clang_tidy_rules should be available at all tiers."""
        features = _load_features()
        caps = features[tier]["code_policy_check"]["capabilities"]
        assert (
            "clang_tidy_rules" in caps
        ), f"[{tier}] code_policy_check missing 'clang_tidy_rules'"

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_all_tiers_have_roslyn_analyzer_rules(self, tier):
        """roslyn_analyzer_rules (C#) should be available at all tiers."""
        features = _load_features()
        caps = features[tier]["code_policy_check"]["capabilities"]
        assert (
            "roslyn_analyzer_rules" in caps
        ), f"[{tier}] code_policy_check missing 'roslyn_analyzer_rules'"

    def test_enterprise_has_misra_c_compliance(self):
        """MISRA-C is a safety-critical standard — Enterprise only."""
        features = _load_features()
        caps = features["enterprise"]["code_policy_check"]["capabilities"]
        assert (
            "misra_c_compliance" in caps
        ), "Enterprise code_policy_check missing 'misra_c_compliance'"

    def test_community_does_not_have_misra_c(self):
        """MISRA-C must NOT appear in Community (safety-critical compliance is Enterprise-only)."""
        features = _load_features()
        caps = features["community"]["code_policy_check"]["capabilities"]
        assert (
            "misra_c_compliance" not in caps
        ), "misra_c_compliance should be Enterprise-only"

    def test_pro_does_not_have_misra_c(self):
        """MISRA-C must NOT appear in Pro (safety-critical compliance is Enterprise-only)."""
        features = _load_features()
        caps = features["pro"]["code_policy_check"]["capabilities"]
        assert (
            "misra_c_compliance" not in caps
        ), "misra_c_compliance should be Enterprise-only"

    def test_original_python_js_linting_preserved(self):
        """Adding C/C++/C# linters must not remove pep8_validation and eslint_rules."""
        features = _load_features()
        for tier in ("community", "pro", "enterprise"):
            caps = features[tier]["code_policy_check"]["capabilities"]
            assert "pep8_validation" in caps, f"[{tier}] lost 'pep8_validation'"
            assert "eslint_rules" in caps, f"[{tier}] lost 'eslint_rules'"

    def test_enterprise_still_has_compliance_frameworks(self):
        """Adding C capabilities must not remove HIPAA/SOC2/PCI-DSS."""
        features = _load_features()
        ent_caps = features["enterprise"]["code_policy_check"]["capabilities"]
        for cap in ("hipaa_compliance", "soc2_compliance", "pci_dss_compliance"):
            assert cap in ent_caps, f"Enterprise code_policy_check lost '{cap}'"


# ---------------------------------------------------------------------------
# scan_dependencies — Conan, vcpkg, NuGet
# ---------------------------------------------------------------------------


class TestScanDependenciesCLanguages:
    """scan_dependencies should support C/C++ (Conan, vcpkg) and C# (NuGet) — all tiers (v2.0.2)."""

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    @pytest.mark.parametrize(
        "capability", ["conan_scanning", "vcpkg_scanning", "nuget_scanning"]
    )
    def test_all_tiers_have_c_package_manager_scanning(self, tier, capability):
        """Conan, vcpkg, and NuGet scanning must be present at every tier."""
        features = _load_features()
        caps = features[tier]["scan_dependencies"]["capabilities"]
        assert capability in caps, f"[{tier}] scan_dependencies missing '{capability}'"

    def test_original_capabilities_preserved(self):
        """Adding package manager support must not remove existing capabilities."""
        features = _load_features()
        for tier in ("community", "pro", "enterprise"):
            caps = features[tier]["scan_dependencies"]["capabilities"]
            assert (
                "osv_vulnerability_detection" in caps
            ), f"[{tier}] scan_dependencies lost 'osv_vulnerability_detection'"
            assert (
                "severity_scoring" in caps
            ), f"[{tier}] scan_dependencies lost 'severity_scoring'"

    def test_enterprise_still_has_compliance_reporting(self):
        """Enterprise compliance_reporting must survive the capability additions."""
        features = _load_features()
        ent_caps = features["enterprise"]["scan_dependencies"]["capabilities"]
        assert "compliance_reporting" in ent_caps
        assert "policy_based_blocking" in ent_caps


# ---------------------------------------------------------------------------
# Cross-cutting: all four tools still define all three tiers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool",
    [
        "unified_sink_detect",
        "generate_unit_tests",
        "code_policy_check",
        "scan_dependencies",
    ],
)
@pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
def test_tool_still_has_all_tiers_in_features_toml(tool, tier):
    """Every updated tool must still define all three tier sections."""
    features = _load_features()
    assert tier in features, f"features.toml missing '{tier}' top-level section"
    assert tool in features[tier], f"features.toml [{tier}] missing tool '{tool}'"
    assert (
        "capabilities" in features[tier][tool]
    ), f"features.toml [{tier}.{tool}] missing 'capabilities' key"
    assert (
        len(features[tier][tool]["capabilities"]) > 0
    ), f"features.toml [{tier}.{tool}] has empty capabilities list"
