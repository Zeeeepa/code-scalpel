"""
Tests for get_file_context output metadata fields.

[20260111_TEST] v1.0 - Tests for tier_applied, max_context_lines_applied,
pro_features_enabled, and enterprise_features_enabled output fields.

These tests ensure that the tool correctly reports which tier configuration
was applied, enabling AI agents to understand the context of responses.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from code_scalpel.mcp.helpers.context_helpers import _get_file_context_sync


class TestOutputMetadataFieldsCommunity:
    """Test output metadata fields at Community tier."""

    def test_tier_applied_is_community(self, tmp_path):
        """Community tier reports tier_applied='community'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is True
        assert result.tier_applied == "community"

    def test_max_context_lines_applied_is_500(self, tmp_path):
        """Community tier reports max_context_lines_applied=500."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is True
        assert result.max_context_lines_applied == 500

    def test_pro_features_enabled_is_false(self, tmp_path):
        """Community tier reports pro_features_enabled=False."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is True
        assert result.pro_features_enabled is False

    def test_enterprise_features_enabled_is_false(self, tmp_path):
        """Community tier reports enterprise_features_enabled=False."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is True
        assert result.enterprise_features_enabled is False

    def test_community_tier_gating_verified(self, tmp_path):
        """Verify Community tier doesn't return Pro/Enterprise features."""
        test_file = tmp_path / "test.py"
        # Code with potential smells - long function
        test_file.write_text("def long_func():\n" + "    x = 1\n" * 60)

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is True
        assert result.tier_applied == "community"
        assert result.code_smells == []  # Not populated at Community
        assert result.doc_coverage is None
        assert result.maintainability_index is None


class TestOutputMetadataFieldsPro:
    """Test output metadata fields at Pro tier."""

    def test_tier_applied_is_pro(self, tmp_path):
        """Pro tier reports tier_applied='pro'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="pro")

        assert result.success is True
        assert result.tier_applied == "pro"

    def test_max_context_lines_applied_is_2000(self, tmp_path):
        """Pro tier reports max_context_lines_applied=2000."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="pro")

        assert result.success is True
        assert result.max_context_lines_applied == 2000

    def test_pro_features_enabled_is_true(self, tmp_path):
        """Pro tier reports pro_features_enabled=True."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="pro")

        assert result.success is True
        assert result.pro_features_enabled is True

    def test_enterprise_features_enabled_is_false(self, tmp_path):
        """Pro tier reports enterprise_features_enabled=False."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="pro")

        assert result.success is True
        assert result.enterprise_features_enabled is False

    def test_pro_tier_has_code_quality_metrics(self, tmp_path):
        """Verify Pro tier returns code quality metrics."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            '"""Module docstring."""\ndef hello():\n    """Func doc."""\n    pass\n'
        )

        result = _get_file_context_sync(str(test_file), tier="pro")

        assert result.success is True
        assert result.tier_applied == "pro"
        assert result.pro_features_enabled is True
        # Pro should have doc_coverage populated
        assert result.doc_coverage is not None
        assert result.maintainability_index is not None


class TestOutputMetadataFieldsEnterprise:
    """Test output metadata fields at Enterprise tier."""

    def test_tier_applied_is_enterprise(self, tmp_path):
        """Enterprise tier reports tier_applied='enterprise'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="enterprise")

        assert result.success is True
        assert result.tier_applied == "enterprise"

    def test_max_context_lines_applied_is_none(self, tmp_path):
        """Enterprise tier reports max_context_lines_applied=None (unlimited)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="enterprise")

        assert result.success is True
        assert result.max_context_lines_applied is None

    def test_pro_features_enabled_is_true(self, tmp_path):
        """Enterprise tier reports pro_features_enabled=True (includes Pro features)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="enterprise")

        assert result.success is True
        assert result.pro_features_enabled is True

    def test_enterprise_features_enabled_is_true(self, tmp_path):
        """Enterprise tier reports enterprise_features_enabled=True."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass\n")

        result = _get_file_context_sync(str(test_file), tier="enterprise")

        assert result.success is True
        assert result.enterprise_features_enabled is True

    def test_enterprise_tier_has_all_features(self, tmp_path):
        """Verify Enterprise tier returns all feature types."""
        test_file = tmp_path / "test.py"
        test_file.write_text('"""Module."""\ndef hello():\n    """Func."""\n    pass\n')

        result = _get_file_context_sync(str(test_file), tier="enterprise")

        assert result.success is True
        assert result.tier_applied == "enterprise"
        assert result.pro_features_enabled is True
        assert result.enterprise_features_enabled is True
        # Enterprise has Pro features
        assert result.doc_coverage is not None
        assert result.maintainability_index is not None


class TestOutputMetadataFieldsOnError:
    """Test that metadata fields are populated even on errors."""

    def test_file_not_found_includes_tier(self, tmp_path):
        """File not found error still reports tier_applied."""
        result = _get_file_context_sync("/nonexistent/file.py", tier="community")

        assert result.success is False
        assert result.tier_applied == "community"
        assert result.error is not None

    def test_file_not_found_includes_limits(self, tmp_path):
        """File not found error still reports max_context_lines_applied."""
        result = _get_file_context_sync("/nonexistent/file.py", tier="pro")

        assert result.success is False
        assert result.tier_applied == "pro"
        assert result.max_context_lines_applied == 2000

    def test_syntax_error_includes_metadata(self, tmp_path):
        """Syntax error result includes metadata fields."""
        test_file = tmp_path / "bad.py"
        test_file.write_text("def broken(\n")  # Syntax error

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is False
        assert result.tier_applied == "community"
        assert result.pro_features_enabled is False
        assert result.enterprise_features_enabled is False
        assert "syntax" in result.error.lower()

    def test_line_limit_exceeded_includes_metadata(self, tmp_path):
        """Line limit exceeded error includes metadata fields."""
        test_file = tmp_path / "large.py"
        # Create file with 600 lines (exceeds Community 500 limit)
        test_file.write_text("# line\n" * 600)

        result = _get_file_context_sync(str(test_file), tier="community")

        assert result.success is False
        assert result.tier_applied == "community"
        assert result.max_context_lines_applied == 500
        assert "500" in result.error


class TestOutputMetadataConsistency:
    """Test metadata field consistency across scenarios."""

    def test_metadata_present_in_all_success_responses(self, tmp_path):
        """All successful responses include metadata fields."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def func(): pass\n")

        for tier in ["community", "pro", "enterprise"]:
            result = _get_file_context_sync(str(test_file), tier=tier)

            assert result.success is True
            assert hasattr(result, "tier_applied")
            assert hasattr(result, "max_context_lines_applied")
            assert hasattr(result, "pro_features_enabled")
            assert hasattr(result, "enterprise_features_enabled")
            assert result.tier_applied == tier

    def test_metadata_values_match_tier_config(self, tmp_path):
        """Metadata values correctly reflect tier configuration."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def func(): pass\n")

        # Expected configurations
        expected = {
            "community": {"max": 500, "pro": False, "enterprise": False},
            "pro": {"max": 2000, "pro": True, "enterprise": False},
            "enterprise": {"max": None, "pro": True, "enterprise": True},
        }

        for tier, config in expected.items():
            result = _get_file_context_sync(str(test_file), tier=tier)

            assert result.tier_applied == tier
            assert result.max_context_lines_applied == config["max"]
            assert result.pro_features_enabled == config["pro"]
            assert result.enterprise_features_enabled == config["enterprise"]
