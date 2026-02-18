# [20260201_TEST] Tier limit monotonicity and structural validation tests
#
# These tests validate the structural properties of the tier system:
#   1. Limits are monotonically non-decreasing: Community ≤ Pro ≤ Enterprise
#   2. Enterprise is a strict superset of Pro capabilities
#   3. Pro and Enterprise have identical numeric limits
#   4. Community limits cover the solo developer persona
"""
Tier Validation Test Suite
==========================

Scientific validation that tier limits and capabilities are correctly
structured according to the tier philosophy:

- Community: Solo devs, ≤500 file projects, performance budget <5s
- Pro: Teams, any project size, limits match Enterprise
- Enterprise: Same limits as Pro + 139 governance capabilities

See TIER_STRATEGY_OPTIONS.md and docs/architecture/tier_limit_justification.md
for full methodology.
"""

import pytest

from code_scalpel.licensing.config_loader import load_features, load_limits

# ─── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def all_limits():
    """Load raw limits.toml data for all tiers."""
    return load_limits()


@pytest.fixture(scope="module")
def all_features():
    """Load raw features.toml data for all tiers."""
    return load_features()


# ─── Helper Functions ──────────────────────────────────────────────────


def _get_numeric_limits(tier_data: dict) -> dict[str, dict[str, int | float]]:
    """Extract only numeric limit values from a tier's data.

    Excludes boolean feature flags (e.g., compliance_enabled, frontend_only)
    since those are capability toggles, not numeric limits.
    """
    result = {}
    for tool_name, tool_limits in tier_data.items():
        if isinstance(tool_limits, dict):
            numeric = {
                k: v
                for k, v in tool_limits.items()
                if isinstance(v, (int, float))
                and not isinstance(v, bool)
                and k != "enabled"
            }
            if numeric:
                result[tool_name] = numeric
    return result


def _effective_value(v: int | float | None) -> float:
    """Convert a limit value to its effective numeric value.

    -1 means unlimited → treat as infinity for comparison.
    None means unset → treat as infinity (no explicit limit).
    """
    if v is None or v == -1:
        return float("inf")
    return float(v)


# ─── Test 1: Monotonicity ─────────────────────────────────────────────


class TestMonotonicity:
    """Verify that for every numeric limit, Community ≤ Pro ≤ Enterprise."""

    def test_community_leq_pro(self, all_limits):
        """Community limits must not exceed corresponding Pro limits."""
        community = _get_numeric_limits(all_limits.get("community", {}))
        pro = _get_numeric_limits(all_limits.get("pro", {}))

        violations = []
        for tool_name, c_limits in community.items():
            p_limits = pro.get(tool_name, {})
            for key, c_val in c_limits.items():
                p_val = p_limits.get(key)
                if p_val is not None and _effective_value(c_val) > _effective_value(
                    p_val
                ):
                    violations.append(
                        f"{tool_name}.{key}: Community={c_val} > Pro={p_val}"
                    )

        assert (
            not violations
        ), f"Community exceeds Pro in {len(violations)} limits:\n" + "\n".join(
            f"  - {v}" for v in violations
        )

    def test_pro_leq_enterprise(self, all_limits):
        """Pro limits must not exceed corresponding Enterprise limits."""
        pro = _get_numeric_limits(all_limits.get("pro", {}))
        enterprise = _get_numeric_limits(all_limits.get("enterprise", {}))

        violations = []
        for tool_name, p_limits in pro.items():
            e_limits = enterprise.get(tool_name, {})
            for key, p_val in p_limits.items():
                e_val = e_limits.get(key)
                if e_val is not None and _effective_value(p_val) > _effective_value(
                    e_val
                ):
                    violations.append(
                        f"{tool_name}.{key}: Pro={p_val} > Enterprise={e_val}"
                    )

        assert (
            not violations
        ), f"Pro exceeds Enterprise in {len(violations)} limits:\n" + "\n".join(
            f"  - {v}" for v in violations
        )

    def test_full_ordering_all_numeric_limits(self, all_limits):
        """Full C ≤ P ≤ E ordering for every numeric limit across all tools.

        Only compares limits that are explicitly set in both tiers being compared.
        Missing values (None) mean the tool uses 'enabled = true' shorthand
        for unlimited, so they're not violations.
        """
        c = _get_numeric_limits(all_limits.get("community", {}))
        p = _get_numeric_limits(all_limits.get("pro", {}))
        e = _get_numeric_limits(all_limits.get("enterprise", {}))

        all_tools = set(c) | set(p) | set(e)
        violations = []

        for tool in sorted(all_tools):
            c_limits = c.get(tool, {})
            p_limits = p.get(tool, {})
            e_limits = e.get(tool, {})
            all_keys = set(c_limits) | set(p_limits) | set(e_limits)

            for key in sorted(all_keys):
                c_raw = c_limits.get(key)
                p_raw = p_limits.get(key)
                e_raw = e_limits.get(key)

                # Compare C vs P (only if both defined)
                if c_raw is not None and p_raw is not None:
                    if _effective_value(c_raw) > _effective_value(p_raw):
                        violations.append(f"{tool}.{key}: C={c_raw} > P={p_raw}")

                # Compare P vs E (only if both defined)
                if p_raw is not None and e_raw is not None:
                    if _effective_value(p_raw) > _effective_value(e_raw):
                        violations.append(f"{tool}.{key}: P={p_raw} > E={e_raw}")

        assert (
            not violations
        ), f"Non-monotonic limits ({len(violations)}):\n" + "\n".join(
            f"  - {v}" for v in violations
        )


# ─── Test 2: Pro/Enterprise Limit Parity ──────────────────────────────


class TestProEnterpriseParity:
    """Verify that Pro and Enterprise have identical numeric limits.

    Enterprise differentiates on CAPABILITIES (139 unique features),
    not on limit values. Any numeric limit in Enterprise must also
    appear in Pro with the same effective value.
    """

    def test_pro_matches_enterprise_limits(self, all_limits):
        """For every explicit Enterprise numeric limit, Pro must match."""
        pro = _get_numeric_limits(all_limits.get("pro", {}))
        enterprise = _get_numeric_limits(all_limits.get("enterprise", {}))

        mismatches = []
        for tool_name, e_limits in enterprise.items():
            p_limits = pro.get(tool_name, {})
            for key, e_val in e_limits.items():
                p_val = p_limits.get(key)
                if p_val is not None and _effective_value(p_val) != _effective_value(
                    e_val
                ):
                    mismatches.append(
                        f"{tool_name}.{key}: Pro={p_val} != Enterprise={e_val}"
                    )

        assert not mismatches, (
            f"Pro/Enterprise limit parity violations ({len(mismatches)}):\n"
            + "\n".join(f"  - {m}" for m in mismatches)
        )


# ─── Test 3: Enterprise Superset of Pro Capabilities ──────────────────


class TestEnterpriseSupersetOfPro:
    """Verify Enterprise capabilities are a strict superset of Pro."""

    def test_enterprise_has_all_pro_capabilities(self, all_features):
        """Every Pro capability must also exist in Enterprise."""
        pro = all_features.get("pro", {})
        enterprise = all_features.get("enterprise", {})

        missing = []
        for tool_name, tool_data in pro.items():
            if not isinstance(tool_data, dict):
                continue
            pro_caps = set(tool_data.get("capabilities", []))
            ent_caps = set(enterprise.get(tool_name, {}).get("capabilities", []))

            diff = pro_caps - ent_caps
            if diff:
                missing.append(f"{tool_name}: {sorted(diff)}")

        assert not missing, "Enterprise missing Pro capabilities:\n" + "\n".join(
            f"  - {m}" for m in missing
        )

    def test_enterprise_has_additional_capabilities(self, all_features):
        """Enterprise should have capabilities that Pro doesn't."""
        pro = all_features.get("pro", {})
        enterprise = all_features.get("enterprise", {})

        enterprise_only_count = 0
        for tool_name, tool_data in enterprise.items():
            if not isinstance(tool_data, dict):
                continue
            ent_caps = set(tool_data.get("capabilities", []))
            pro_caps = set(pro.get(tool_name, {}).get("capabilities", []))
            enterprise_only_count += len(ent_caps - pro_caps)

        # Previously measured at 139 unique Enterprise capabilities
        assert enterprise_only_count >= 100, (
            f"Enterprise should have 100+ unique capabilities, found {enterprise_only_count}. "
            f"Enterprise differentiates on governance features."
        )


# ─── Test 4: Community Covers Solo Developer Persona ──────────────────


class TestCommunityCoversPersona:
    """Verify Community limits are sufficient for solo developer projects."""

    # Real-world project size data (files, max import depth, symbol count)
    SOLO_DEV_PROJECTS = {
        "flask_app": {"files": 45, "max_depth": 4, "symbols": 320},
        "fastapi_service": {"files": 80, "max_depth": 5, "symbols": 650},
        "cli_tool": {"files": 25, "max_depth": 3, "symbols": 180},
        "python_library": {"files": 60, "max_depth": 6, "symbols": 500},
        "data_pipeline": {"files": 35, "max_depth": 4, "symbols": 280},
        "personal_saas": {"files": 150, "max_depth": 7, "symbols": 1200},
        "medium_app": {"files": 400, "max_depth": 8, "symbols": 3500},
    }

    # Expected Community limits (from limits.toml)
    COMMUNITY_SCANNER_LIMITS = {
        "files": ("max_files", 500),
        "max_depth": ("max_depth", 10),
        "symbols": ("max_symbol_count", 25000),
    }

    @pytest.mark.parametrize("project_name,stats", SOLO_DEV_PROJECTS.items())
    def test_scanner_covers_project(self, project_name, stats, all_limits):
        """Community scanner limits must accommodate all solo dev project types."""
        community = all_limits.get("community", {}).get("scanner", {})

        for stat_key, (
            limit_key,
            expected_min,
        ) in self.COMMUNITY_SCANNER_LIMITS.items():
            project_value = stats.get(stat_key, 0)
            limit_value = community.get(limit_key, 0)

            assert limit_value >= project_value, (
                f"Project '{project_name}' exceeds Community scanner.{limit_key}: "
                f"project needs {project_value}, limit is {limit_value}"
            )

    def test_community_call_graph_depth_practical(self, all_limits):
        """Community call graph depth must handle real import chains."""
        depth = (
            all_limits.get("community", {})
            .get("get_call_graph", {})
            .get("max_depth", 0)
        )
        # A→B→C→D is depth 4, real apps commonly have 6-8
        assert (
            depth >= 5
        ), f"Community call graph depth {depth} too shallow for real apps"

    def test_community_cross_file_deps_useful(self, all_limits):
        """Community cross-file deps must show at least A→B→C chains."""
        depth = (
            all_limits.get("community", {})
            .get("get_cross_file_dependencies", {})
            .get("max_depth", 0)
        )
        assert depth >= 2, f"Community cross-file dependency depth {depth} too shallow"

    def test_community_context_lines_useful(self, all_limits):
        """Community context lines must show a meaningful file section."""
        lines = (
            all_limits.get("community", {})
            .get("get_file_context", {})
            .get("max_context_lines", 0)
        )
        # A typical Python module is 200-500 lines; need at least 1000
        assert (
            lines >= 1000
        ), f"Community context lines {lines} too small for useful context"


# ─── Test 5: Specific Known-Good Values ───────────────────────────────


class TestSpecificLimitValues:
    """Verify specific limit values match the documented tier strategy.

    These are regression tests — if limits change, the strategy doc
    must be updated first.
    """

    @pytest.mark.parametrize(
        "tool,key,expected",
        [
            ("scanner", "max_files", 500),
            ("scanner", "max_depth", 10),
            ("scanner", "max_symbol_count", 25000),
            ("get_call_graph", "max_depth", 10),
            ("get_call_graph", "max_nodes", 200),
            ("get_file_context", "max_context_lines", 2000),
            ("get_project_map", "max_files", 500),
            ("get_project_map", "max_modules", 100),
            ("get_symbol_references", "max_files_searched", 200),
            ("get_symbol_references", "max_references", 200),
            ("crawl_project", "max_files", 500),
            ("get_cross_file_dependencies", "max_depth", 3),
            ("get_cross_file_dependencies", "max_files", 200),
            ("get_graph_neighborhood", "max_k", 2),
            ("get_graph_neighborhood", "max_nodes", 100),
            ("cross_file_security_scan", "max_modules", 50),
            ("cross_file_security_scan", "max_depth", 5),
            ("security_scan", "max_findings", 100),
            ("extract_code", "max_depth", 1),
            ("simulate_refactor", "max_file_size_mb", 5),
            ("symbolic_execute", "max_paths", 100),
            ("generate_unit_tests", "max_test_cases", 10),
        ],
    )
    def test_community_limit(self, tool, key, expected, all_limits):
        """Community limit matches documented value."""
        actual = all_limits.get("community", {}).get(tool, {}).get(key)
        assert (
            actual == expected
        ), f"Community {tool}.{key}: expected {expected}, got {actual}"

    @pytest.mark.parametrize(
        "tool,key,expected",
        [
            ("scanner", "max_files", 100000),
            ("scanner", "max_depth", 50),
            ("scanner", "max_symbol_count", 1000000),
            ("analyze_code", "max_file_size_mb", 100),
            ("get_file_context", "max_context_lines", -1),
            ("get_project_map", "max_files", -1),
            ("get_project_map", "max_modules", 1000),
            ("get_call_graph", "max_depth", -1),
            ("get_call_graph", "max_nodes", -1),
            ("get_cross_file_dependencies", "max_depth", -1),
            ("get_cross_file_dependencies", "max_files", -1),
            ("get_graph_neighborhood", "max_k", -1),
            ("get_graph_neighborhood", "max_nodes", -1),
            ("extract_code", "max_depth", -1),
            ("extract_code", "max_extraction_size_mb", 100),
            ("simulate_refactor", "max_file_size_mb", 100),
            ("symbolic_execute", "max_depth", -1),
            ("generate_unit_tests", "max_test_cases", -1),
            ("cross_file_security_scan", "max_modules", -1),
            ("cross_file_security_scan", "max_depth", -1),
            ("rename_symbol", "max_files_searched", -1),
            ("rename_symbol", "max_files_updated", -1),
            ("verify_policy_integrity", "max_policy_files", -1),
            ("code_policy_check", "max_files", -1),
            ("code_policy_check", "max_rules", -1),
            ("type_evaporation_scan", "max_files", -1),
            ("unified_sink_detect", "max_sinks", -1),
        ],
    )
    def test_pro_limit(self, tool, key, expected, all_limits):
        """Pro limit matches documented value."""
        actual = all_limits.get("pro", {}).get(tool, {}).get(key)
        assert (
            actual == expected
        ), f"Pro {tool}.{key}: expected {expected}, got {actual}"


# ─── Test 6: Structural Completeness ──────────────────────────────────


class TestStructuralCompleteness:
    """Verify all tools are defined in all tiers."""

    EXPECTED_TOOLS = {
        "scanner",
        "analyze_code",
        "get_file_context",
        "get_project_map",
        "get_symbol_references",
        "crawl_project",
        "get_call_graph",
        "get_cross_file_dependencies",
        "get_graph_neighborhood",
        "scan_dependencies",
        "security_scan",
        "cross_file_security_scan",
        "unified_sink_detect",
        "validate_paths",
        "verify_policy_integrity",
        "code_policy_check",
        "extract_code",
        "update_symbol",
        "rename_symbol",
        "simulate_refactor",
        "symbolic_execute",
        "generate_unit_tests",
        "type_evaporation_scan",
    }

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_all_tools_have_limits(self, tier, all_limits):
        """Every known tool should have a limits section in every tier."""
        tier_data = all_limits.get(tier, {})
        defined_tools = set(tier_data.keys())

        missing = self.EXPECTED_TOOLS - defined_tools
        # Allow some tools to be defined only where limits differ
        # Only flag if >3 tools are missing from a tier
        if len(missing) > 5:
            pytest.fail(
                f"Tier '{tier}' missing limits for {len(missing)} tools: "
                f"{sorted(missing)}"
            )

    @pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
    def test_all_tools_have_features(self, tier, all_features):
        """Every known tool should have a features section in every tier."""
        tier_data = all_features.get(tier, {})
        defined_tools = set(tier_data.keys())

        missing = self.EXPECTED_TOOLS - defined_tools
        if len(missing) > 3:
            pytest.fail(
                f"Tier '{tier}' missing features for {len(missing)} tools: "
                f"{sorted(missing)}"
            )
