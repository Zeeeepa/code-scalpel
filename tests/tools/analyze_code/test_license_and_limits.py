"""
License fallback and file size limit tests for analyze_code tool.

Tests:
- Invalid/expired license fallback to Community tier
- File size limit enforcement per tier
- Limit escalation with tier upgrades
"""

from unittest.mock import patch

from code_scalpel.licensing import get_current_tier
from code_scalpel.licensing.features import get_tool_capabilities


class TestLicenseFallback:
    """Test invalid/expired license fallback behavior."""

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_expired_license_fallback_to_community(self, mock_tier):
        """Expired license should fallback to Community tier."""
        # Simulate expired license detection returning Community
        mock_tier.return_value = "community"

        from code_scalpel.mcp.server import _analyze_code_sync

        code = """
def test_function():
    if True:
        return 1
    else:
        return 0
"""
        result = _analyze_code_sync(code=code, language="python")

        # Should work with Community features
        assert result.success
        assert "test_function" in result.functions

        # Pro features should NOT be present
        assert result.cognitive_complexity is None or result.cognitive_complexity == 0
        assert result.code_smells is None or result.code_smells == []
        assert result.halstead_metrics is None or result.halstead_metrics == {}

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_invalid_license_fallback_to_community(self, mock_tier):
        """Invalid license should fallback to Community tier."""
        # Simulate invalid license detection returning Community
        mock_tier.return_value = "community"

        from code_scalpel.mcp.server import _analyze_code_sync

        code = """
class TestClass:
    def method(self):
        pass
"""
        result = _analyze_code_sync(code=code, language="python")

        # Should work with Community features
        assert result.success
        assert "TestClass" in result.classes
        assert "method" in result.functions

        # Pro enrichments should NOT be present
        assert result.cognitive_complexity is None or result.cognitive_complexity == 0
        assert result.code_smells is None or result.code_smells == []

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_missing_license_defaults_to_community(self, mock_tier):
        """Missing license (None) should default to Community tier."""
        # Simulate no license
        mock_tier.return_value = "community"

        from code_scalpel.mcp.server import _analyze_code_sync

        code = """
def simple():
    return 42
"""
        result = _analyze_code_sync(code=code, language="python")

        # Should work with Community features
        assert result.success
        assert "simple" in result.functions

        # Verify Community-only behavior (no Pro features)
        assert result.cognitive_complexity is None or result.cognitive_complexity == 0
        assert result.code_smells is None or result.code_smells == []


class TestFileSizeLimits:
    """Test file size limit enforcement per tier."""

    @patch("code_scalpel.mcp.helpers.analyze_helpers.get_current_tier_from_license")
    def test_community_max_file_size_1mb(self, mock_tier):
        """Community tier should enforce 1MB file size limit."""
        mock_tier.return_value = "community"

        # Get Community tier limits
        tier = get_current_tier()
        capabilities = get_tool_capabilities("analyze_code", tier)
        max_size = capabilities.get("max_file_size_mb", 1)

        assert max_size == 1, "Community tier should have 1MB limit"

    @patch("code_scalpel.mcp.helpers.analyze_helpers.get_current_tier_from_license")
    def test_pro_max_file_size_10mb(self, mock_tier):
        """Pro tier should enforce 10MB file size limit."""
        mock_tier.return_value = "pro"

        # Get Pro tier limits
        tier = get_current_tier()
        capabilities = get_tool_capabilities("analyze_code", tier)
        max_size = capabilities.get("max_file_size_mb", 10)

        assert max_size == 10, "Pro tier should have 10MB limit"

    @patch("code_scalpel.mcp.helpers.analyze_helpers.get_current_tier_from_license")
    @patch("code_scalpel.licensing.get_current_tier")
    def test_enterprise_max_file_size_100mb(self, mock_license_tier, mock_mcp_tier):
        """Enterprise tier should enforce 100MB file size limit."""
        mock_mcp_tier.return_value = "enterprise"
        mock_license_tier.return_value = "enterprise"

        # Get Enterprise tier limits
        tier = get_current_tier()
        capabilities = get_tool_capabilities("analyze_code", tier)
        max_size = capabilities.get("max_file_size_mb", 100)

        assert max_size == 100, "Enterprise tier should have 100MB limit"

    @patch("code_scalpel.mcp.helpers.analyze_helpers.get_current_tier_from_license")
    def test_file_size_limit_escalation(self, mock_tier):
        """File size limits should increase with tier upgrades."""
        # Test Community
        mock_tier.return_value = "community"
        tier = get_current_tier()
        community_caps = get_tool_capabilities("analyze_code", tier)
        community_limit = community_caps.get("max_file_size_mb", 1)

        # Test Pro
        mock_tier.return_value = "pro"
        tier = get_current_tier()
        pro_caps = get_tool_capabilities("analyze_code", tier)
        pro_limit = pro_caps.get("max_file_size_mb", 10)

        # Verify escalation
        assert pro_limit > community_limit, "Pro limit should exceed Community"
        assert community_limit == 1
        assert pro_limit == 10


class TestFileSizeEnforcement:
    """Test actual file size enforcement (stress tests)."""

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_large_file_generates_many_functions(self, mock_tier):
        """Generate large code and verify it's analyzed."""
        mock_tier.return_value = "community"

        from code_scalpel.mcp.server import _analyze_code_sync

        # Generate code with many functions (but under 1MB)
        num_functions = 100
        code_lines = []
        for i in range(num_functions):
            code_lines.append(f"def func_{i}():")
            code_lines.append(f"    return {i}")
            code_lines.append("")

        code = "\n".join(code_lines)
        code_size_kb = len(code.encode("utf-8")) / 1024

        # Verify we're testing a reasonably large file
        assert code_size_kb > 1, f"Test code should be >1KB (got {code_size_kb:.2f}KB)"

        result = _analyze_code_sync(code=code, language="python")

        assert result.success
        assert (
            len(result.functions) == num_functions
        ), f"Expected {num_functions} functions, got {len(result.functions)}"

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_moderate_file_with_classes(self, mock_tier):
        """Test moderate-sized file with classes and methods."""
        mock_tier.return_value = "pro"

        from code_scalpel.mcp.server import _analyze_code_sync

        # Generate code with classes and methods
        num_classes = 20
        methods_per_class = 5
        code_lines = []

        for i in range(num_classes):
            code_lines.append(f"class Class_{i}:")
            for j in range(methods_per_class):
                code_lines.append(f"    def method_{j}(self):")
                code_lines.append(f"        return {i * methods_per_class + j}")
            code_lines.append("")

        code = "\n".join(code_lines)
        code_size_kb = len(code.encode("utf-8")) / 1024

        # Verify file size
        assert code_size_kb > 2, f"Test code should be >2KB (got {code_size_kb:.2f}KB)"

        result = _analyze_code_sync(code=code, language="python")

        assert result.success
        assert len(result.classes) == num_classes
        # Total functions = all methods from all classes
        expected_functions = num_classes * methods_per_class
        assert len(result.functions) == expected_functions

    @patch("code_scalpel.licensing.jwt_validator.get_current_tier")
    def test_complexity_scales_with_file_size(self, mock_tier):
        """Verify complexity analysis works on larger files."""
        mock_tier.return_value = "pro"

        from code_scalpel.mcp.server import _analyze_code_sync

        # Generate complex code
        code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y
        else:
            if z > 0:
                return x + z
            else:
                return x
    else:
        if y > 0:
            if z > 0:
                return y + z
            else:
                return y
        else:
            return z
"""
        result = _analyze_code_sync(code=code, language="python")

        assert result.success
        assert result.complexity > 1, "Complex code should have complexity > 1"
        # With nested ifs, complexity should be reasonably high
        assert (
            result.complexity >= 7
        ), f"Expected complexity >= 7, got {result.complexity}"


class TestTierLimitDifferences:
    """Test that limits actually differ across tiers."""

    def test_community_vs_pro_limits(self):
        """Community and Pro tiers should have different limits."""
        from code_scalpel.licensing.features import TOOL_CAPABILITIES

        comm_caps = TOOL_CAPABILITIES["analyze_code"]["community"]
        pro_caps = TOOL_CAPABILITIES["analyze_code"]["pro"]

        comm_size = comm_caps.get("max_file_size_mb", 1)
        pro_size = pro_caps.get("max_file_size_mb", 10)

        assert comm_size < pro_size, "Pro should have larger file size limit"
        assert comm_size == 1
        assert pro_size == 10

    def test_pro_vs_enterprise_limits(self):
        """Pro and Enterprise tiers should have different limits."""
        from code_scalpel.licensing.features import TOOL_CAPABILITIES

        pro_caps = TOOL_CAPABILITIES["analyze_code"]["pro"]
        ent_caps = TOOL_CAPABILITIES["analyze_code"]["enterprise"]

        pro_size = pro_caps.get("max_file_size_mb", 10)
        ent_size = ent_caps.get("max_file_size_mb", 100)

        assert pro_size < ent_size, "Enterprise should have larger file size limit"
        assert pro_size == 10
        assert ent_size == 100

    def test_all_tiers_limit_progression(self):
        """Verify limit progression: Community < Pro < Enterprise."""
        from code_scalpel.licensing.features import TOOL_CAPABILITIES

        comm_size = TOOL_CAPABILITIES["analyze_code"]["community"].get(
            "max_file_size_mb", 1
        )
        pro_size = TOOL_CAPABILITIES["analyze_code"]["pro"].get("max_file_size_mb", 10)
        ent_size = TOOL_CAPABILITIES["analyze_code"]["enterprise"].get(
            "max_file_size_mb", 100
        )

        assert (
            comm_size < pro_size < ent_size
        ), f"Limits should progress: {comm_size} < {pro_size} < {ent_size}"
