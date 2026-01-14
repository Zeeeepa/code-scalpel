"""
Tests for get_call_graph tier enforcement and output metadata.

[20260111_TEST] v1.0 validation - Ensure tier limits, capabilities, and metadata
are properly enforced and populated.
"""

from unittest.mock import patch

import pytest

from src.code_scalpel.mcp.server import CallGraphResultModel, get_call_graph


class TestOutputMetadataFields:
    """Test that output metadata fields are present and correctly populated."""

    @pytest.mark.asyncio
    async def test_basic_call_graph_includes_metadata(self, tmp_path):
        """Basic call graph should include all metadata fields."""
        # Create a simple project
        main_file = tmp_path / "main.py"
        main_file.write_text(
            """
def main():
    helper()

def helper():
    return 42
"""
        )
        result = await get_call_graph(project_root=str(tmp_path), depth=5)

        assert result.success is True
        # Verify metadata fields exist and have correct types
        assert hasattr(result, "tier_applied")
        assert hasattr(result, "max_depth_applied")
        assert hasattr(result, "max_nodes_applied")
        assert hasattr(result, "advanced_resolution_enabled")
        assert hasattr(result, "enterprise_metrics_enabled")

        # Verify values are reasonable
        assert result.tier_applied in ("community", "pro", "enterprise")
        assert isinstance(result.advanced_resolution_enabled, bool)
        assert isinstance(result.enterprise_metrics_enabled, bool)

    @pytest.mark.asyncio
    async def test_metadata_reflects_actual_limits(self, tmp_path):
        """Metadata should accurately reflect applied limits."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        result = await get_call_graph(project_root=str(tmp_path), depth=10)

        assert result.success is True
        # max_depth_applied should reflect tier limits
        # Enterprise has None (unlimited), Pro has 50, Community has 3
        if result.tier_applied == "enterprise":
            assert result.max_depth_applied is None
            assert result.max_nodes_applied is None
        elif result.tier_applied == "pro":
            assert result.max_depth_applied == 50
            assert result.max_nodes_applied == 500
        else:  # community
            assert result.max_depth_applied == 3
            assert result.max_nodes_applied == 50


class TestMetadataFieldTypes:
    """Test the data types of metadata fields in the model."""

    def test_call_graph_result_model_has_metadata_fields(self):
        """CallGraphResultModel should define all metadata fields."""
        fields = CallGraphResultModel.model_fields

        # Check all metadata fields exist
        assert "tier_applied" in fields
        assert "max_depth_applied" in fields
        assert "max_nodes_applied" in fields
        assert "advanced_resolution_enabled" in fields
        assert "enterprise_metrics_enabled" in fields

    def test_metadata_fields_have_defaults(self):
        """Metadata fields should have sensible defaults."""
        result = CallGraphResultModel(
            success=True,
        )

        # Verify defaults are applied
        assert result.tier_applied == "community"  # Default tier
        assert result.max_depth_applied is None  # No limit by default
        assert result.max_nodes_applied is None  # No limit by default
        assert result.advanced_resolution_enabled is False  # Disabled by default
        assert result.enterprise_metrics_enabled is False  # Disabled by default

    def test_metadata_fields_can_be_set(self):
        """Metadata fields should accept valid values."""
        result = CallGraphResultModel(
            success=True,
            tier_applied="pro",
            max_depth_applied=50,
            max_nodes_applied=500,
            advanced_resolution_enabled=True,
            enterprise_metrics_enabled=False,
        )

        assert result.tier_applied == "pro"
        assert result.max_depth_applied == 50
        assert result.max_nodes_applied == 500
        assert result.advanced_resolution_enabled is True
        assert result.enterprise_metrics_enabled is False


class TestTierEnforcement:
    """Test that tier limits are properly enforced."""

    @pytest.mark.asyncio
    async def test_community_tier_depth_limit(self, tmp_path):
        """Community tier should enforce max_depth=3."""
        # Create a deeply nested call chain
        main_file = tmp_path / "main.py"
        main_file.write_text(
            """
def level_0():
    level_1()

def level_1():
    level_2()

def level_2():
    level_3()

def level_3():
    level_4()

def level_4():
    level_5()

def level_5():
    pass
"""
        )
        with patch(
            "src.code_scalpel.mcp.server._get_current_tier", return_value="community"
        ):
            result = await get_call_graph(project_root=str(tmp_path), depth=10)

        assert result.success is True
        assert result.tier_applied == "community"
        assert result.max_depth_applied == 3  # Community limit
        # Depth should be clamped to 3 even if requested 10

    @pytest.mark.asyncio
    async def test_pro_tier_higher_limits(self, tmp_path):
        """Pro tier should have higher limits than Community."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        with patch("src.code_scalpel.mcp.server._get_current_tier", return_value="pro"):
            result = await get_call_graph(project_root=str(tmp_path), depth=10)

        assert result.success is True
        assert result.tier_applied == "pro"
        assert result.max_depth_applied == 50  # Pro limit
        assert result.max_nodes_applied == 500  # Pro limit

    @pytest.mark.asyncio
    async def test_enterprise_tier_unlimited(self, tmp_path):
        """Enterprise tier should have unlimited (None) limits."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        with patch(
            "src.code_scalpel.mcp.server._get_current_tier", return_value="enterprise"
        ):
            result = await get_call_graph(project_root=str(tmp_path), depth=100)

        assert result.success is True
        assert result.tier_applied == "enterprise"
        assert result.max_depth_applied is None  # Unlimited
        assert result.max_nodes_applied is None  # Unlimited


class TestCapabilityFlags:
    """Test that capability flags are correctly set based on tier."""

    @pytest.mark.asyncio
    async def test_community_no_advanced_resolution(self, tmp_path):
        """Community tier should not have advanced resolution."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        with patch(
            "src.code_scalpel.mcp.server._get_current_tier", return_value="community"
        ):
            result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert result.advanced_resolution_enabled is False
        assert result.enterprise_metrics_enabled is False

    @pytest.mark.asyncio
    async def test_pro_has_advanced_resolution(self, tmp_path):
        """Pro tier should have advanced resolution enabled."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        with patch("src.code_scalpel.mcp.server._get_current_tier", return_value="pro"):
            result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert result.advanced_resolution_enabled is True
        assert result.enterprise_metrics_enabled is False  # Pro doesn't have this

    @pytest.mark.asyncio
    async def test_enterprise_has_all_features(self, tmp_path):
        """Enterprise tier should have all capabilities enabled."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        with patch(
            "src.code_scalpel.mcp.server._get_current_tier", return_value="enterprise"
        ):
            result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert result.advanced_resolution_enabled is True
        assert result.enterprise_metrics_enabled is True


class TestTruncationMetadata:
    """Test truncation metadata is properly populated."""

    @pytest.mark.asyncio
    async def test_no_truncation_when_within_limits(self, tmp_path):
        """When within limits, truncation fields should indicate no truncation."""
        main_file = tmp_path / "main.py"
        main_file.write_text(
            """
def foo():
    bar()

def bar():
    pass
"""
        )
        result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert result.total_nodes is not None
        assert result.nodes_truncated is False
        assert result.truncation_warning is None

    @pytest.mark.asyncio
    async def test_truncation_fields_present(self, tmp_path):
        """Truncation metadata fields should always be present."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert hasattr(result, "total_nodes")
        assert hasattr(result, "total_edges")
        assert hasattr(result, "nodes_truncated")
        assert hasattr(result, "edges_truncated")
        assert hasattr(result, "truncation_warning")


class TestEnterpriseMetrics:
    """Test enterprise-only metrics."""

    @pytest.mark.asyncio
    async def test_hot_nodes_field_exists(self, tmp_path):
        """Hot nodes field should exist even if empty."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert hasattr(result, "hot_nodes")
        assert isinstance(result.hot_nodes, list)

    @pytest.mark.asyncio
    async def test_dead_code_candidates_field_exists(self, tmp_path):
        """Dead code candidates field should exist even if empty."""
        main_file = tmp_path / "main.py"
        main_file.write_text("def foo(): pass")

        result = await get_call_graph(project_root=str(tmp_path))

        assert result.success is True
        assert hasattr(result, "dead_code_candidates")
        assert isinstance(result.dead_code_candidates, list)
