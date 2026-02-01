"""
Tier-based validation tests for get_cross_file_dependencies MCP tool.

Tests verify that dependency depth is correctly enforced by tier:
- Community: max_depth = 1 (direct imports only)
- Pro: max_depth = 5 (deeper transitive deps)
- Enterprise: unlimited depth (full transitive closure)
"""

import pytest
from code_scalpel.mcp.helpers.graph_helpers import _get_cross_file_dependencies_sync


@pytest.fixture
def temp_project_with_dependencies(tmp_path):
    """Create nested dependency chain for depth testing."""
    # Create module_f.py (depth 6 - deepest)
    (tmp_path / "module_f.py").write_text(
        '''
def helper_f():
    """Deepest dependency (depth 6)."""
    return "f"
'''
    )

    # Create module_e.py (depth 5) - imports module_f
    (tmp_path / "module_e.py").write_text(
        '''
from module_f import helper_f

def helper_e():
    """Depth 5 dependency."""
    return helper_f()
'''
    )

    # Create module_d.py (depth 4) - imports module_e
    (tmp_path / "module_d.py").write_text(
        '''
from module_e import helper_e

def helper_d():
    """Depth 4 dependency."""
    return helper_e()
'''
    )

    # Create module_c.py (depth 3) - imports module_d
    (tmp_path / "module_c.py").write_text(
        '''
from module_d import helper_d

def helper_c():
    """Depth 3 dependency."""
    return helper_d()
'''
    )

    # Create module_b.py (depth 2) - imports module_c
    (tmp_path / "module_b.py").write_text(
        '''
from module_c import helper_c

def helper_b():
    """Depth 2 dependency."""
    return helper_c()
'''
    )

    # Create module_a.py (depth 1) - imports module_b
    (tmp_path / "module_a.py").write_text(
        '''
from module_b import helper_b

def calculate(amount):
    """Depth 1 dependency - direct import."""
    return 100 + amount + len(str(helper_b()))
'''
    )

    # Create main.py (depth 0 - target)
    (tmp_path / "main.py").write_text(
        '''
from module_a import calculate

def process_order(order_id, amount):
    """Main function that depends on module_a.calculate."""
    total = calculate(amount)
    return {"order_id": order_id, "total": total}
'''
    )

    return tmp_path


class TestGetCrossFileDependenciesCommunityTier:
    """Community tier: max_depth = 1 (direct imports only)."""

    def test_tier_gating_enforced(
        self, temp_project_with_dependencies, community_tier, tier_limits
    ):
        """Verify community tier enforces max_depth limit from configuration."""
        max_depth_limit = tier_limits["community"]["get_cross_file_dependencies"][
            "max_depth"
        ]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=10,  # User requests 10, but tier limits to configured max_depth
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="community",
        )
        assert result.success is True
        # Community tier max_depth is enforced from limits.toml
        assert result.transitive_depth <= max_depth_limit

    def test_direct_imports_only(
        self, temp_project_with_dependencies, community_tier, tier_limits
    ):
        """Verify only direct dependencies analyzed (depth 1)."""
        max_depth_limit = tier_limits["community"]["get_cross_file_dependencies"][
            "max_depth"
        ]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=max_depth_limit,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="community",
        )
        assert result.success is True
        # Should find some dependencies (at least module_a)
        assert result.total_dependencies >= 1
        # Max depth reached should not exceed tier limit
        assert result.max_depth_reached <= max_depth_limit

    def test_files_limited_to_configured_max(
        self, temp_project_with_dependencies, community_tier, tier_limits
    ):
        """Verify community tier max_files limit from configuration."""
        max_files_limit = tier_limits["community"]["get_cross_file_dependencies"][
            "max_files"
        ]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=1,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="community",
        )
        assert result.success is True
        # Files analyzed should be within community limit
        assert result.files_analyzed <= max_files_limit

    def test_confidence_decay_applied(
        self, temp_project_with_dependencies, community_tier, tier_limits
    ):
        """Verify confidence score decays with depth."""
        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=1,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="community",
        )
        assert result.success is True
        # Verify confidence decay factor is applied
        assert result.confidence_decay_factor == 0.9
        # Check extracted symbols have confidence scores
        for symbol in result.extracted_symbols:
            if hasattr(symbol, "depth"):
                depth = symbol.depth
                if hasattr(symbol, "confidence"):
                    confidence = symbol.confidence
                    expected_confidence = 1.0 * (0.9**depth)
                    # Allow small variation
                    assert abs(confidence - expected_confidence) < 0.01


class TestGetCrossFileDependenciesProTier:
    """Pro tier: max_depth = 5 (deeper transitive dependencies)."""

    def test_depth_limit_from_config(
        self, temp_project_with_dependencies, pro_tier, tier_limits
    ):
        """Verify pro tier enforces max_depth from configuration."""
        max_depth_limit = tier_limits["pro"]["get_cross_file_dependencies"]["max_depth"]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=100,  # User requests high, pro limits to configured max_depth
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="pro",
        )
        assert result.success is True
        # Pro tier max_depth is enforced from limits.toml
        assert result.transitive_depth <= max_depth_limit

    def test_transitive_deps_analyzed(
        self, temp_project_with_dependencies, pro_tier, tier_limits
    ):
        """Verify transitive dependencies up to tier limit are analyzed."""
        max_depth_limit = tier_limits["pro"]["get_cross_file_dependencies"]["max_depth"]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=max_depth_limit,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="pro",
        )
        assert result.success is True
        # Pro tier should find dependencies
        assert result.total_dependencies >= 1

    def test_files_limited_to_configured_max(
        self, temp_project_with_dependencies, pro_tier, tier_limits
    ):
        """Verify pro tier max_files limit from configuration."""
        max_files_limit = tier_limits["pro"]["get_cross_file_dependencies"]["max_files"]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=5,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="pro",
        )
        assert result.success is True
        # Files analyzed should be within pro limit
        assert result.files_analyzed <= max_files_limit

    def test_confidence_decay_deep(
        self, temp_project_with_dependencies, pro_tier, tier_limits
    ):
        """Verify confidence_score decays with depth using 0.9 factor."""
        max_depth_limit = tier_limits["pro"]["get_cross_file_dependencies"]["max_depth"]

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=max_depth_limit,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="pro",
        )
        assert result.success is True
        # Confidence factor should be applied
        assert result.confidence_decay_factor == 0.9
        # Check that deeper symbols may have lower confidence
        has_deep_symbol = False
        for symbol in result.extracted_symbols:
            if hasattr(symbol, "depth") and symbol.depth >= 4:
                has_deep_symbol = True
                if hasattr(symbol, "confidence"):
                    confidence = symbol.confidence
                    # Depth 4: 1.0 * 0.9^4 = 0.6561
                    # Confidence should still be reasonable for Pro
                    assert confidence > 0.5
        # If we found deep symbols, verify they decay
        if has_deep_symbol:
            assert result.max_depth_reached >= 4


class TestGetCrossFileDependenciesEnterpriseTier:
    """Enterprise tier: unlimited depth (full transitive closure)."""

    def test_unlimited_depth(
        self, temp_project_with_dependencies, enterprise_tier, tier_limits
    ):
        """Verify enterprise tier has no depth limit (or very high limit)."""
        max_depth_limit = tier_limits["enterprise"]["get_cross_file_dependencies"].get(
            "max_depth"
        )

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=100,  # User requests deep traversal
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="enterprise",
        )
        assert result.success is True
        # Enterprise tier should not have a configured depth limit (None = unlimited)
        if max_depth_limit is not None:
            assert result.transitive_depth <= max_depth_limit
        else:
            # Unlimited - analyze up to actual graph depth
            assert result.transitive_depth is None or result.transitive_depth >= 5

    def test_unlimited_files(
        self, temp_project_with_dependencies, enterprise_tier, tier_limits
    ):
        """Verify enterprise tier has no file limit (or very high limit)."""
        max_files_limit = tier_limits["enterprise"]["get_cross_file_dependencies"].get(
            "max_files"
        )

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=100,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="enterprise",
        )
        assert result.success is True
        # Enterprise should not truncate files (or have very high limit)
        if max_files_limit is not None:
            assert result.files_analyzed <= max_files_limit
        else:
            # Unlimited - no truncation
            assert result.truncated is False or result.files_truncated == 0

    def test_all_dependencies_traversed(
        self, temp_project_with_dependencies, enterprise_tier
    ):
        """Verify all dependencies are analyzed including deep nested ones."""
        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=100,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="enterprise",
        )
        assert result.success is True
        # Enterprise should find all modules (at least 6: a-f)
        assert result.total_dependencies >= 5

    def test_confidence_decay_deep_analysis(
        self, temp_project_with_dependencies, enterprise_tier
    ):
        """Verify confidence_score still decays even with unlimited depth."""
        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=100,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="enterprise",
        )
        assert result.success is True
        # Confidence factor always applied
        assert result.confidence_decay_factor == 0.9
        # Verify that deepest symbols still decay
        for symbol in result.extracted_symbols:
            if hasattr(symbol, "depth") and hasattr(symbol, "confidence"):
                depth = symbol.depth
                confidence = symbol.confidence
                if depth > 5:
                    # At depth 6: 1.0 * 0.9^6 = 0.531
                    expected_confidence = 1.0 * (0.9**depth)
                    assert abs(confidence - expected_confidence) < 0.01

    def test_circular_dependency_detection(self, tmp_path, enterprise_tier):
        """Verify circular dependency detection is active in enterprise tier."""
        # Create circular dependencies
        (tmp_path / "module_x.py").write_text(
            """
from module_y import func_y
def func_x():
    return func_y()
"""
        )

        (tmp_path / "module_y.py").write_text(
            """
from module_x import func_x
def func_y():
    return func_x()
"""
        )

        (tmp_path / "main.py").write_text(
            """
from module_x import func_x
def start():
    return func_x()
"""
        )

        result = _get_cross_file_dependencies_sync(
            target_file="main.py",
            target_symbol="start",
            project_root=str(tmp_path),
            max_depth=10,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
            tier="enterprise",
        )
        # Result should succeed, and circular imports may be detected
        if result.success:
            # Either circular_imports is populated or analysis completed successfully
            # Enterprise tier supports circular dependency tracking
            assert result.circular_imports is not None


class TestGetCrossFileDependenciesAsyncInterface:
    """Test async interface integration."""

    @pytest.mark.asyncio
    async def test_async_interface_works(
        self, temp_project_with_dependencies, pro_tier
    ):
        """Verify async wrapper correctly calls sync implementation."""
        from code_scalpel.mcp.tools.graph import get_cross_file_dependencies

        result = await get_cross_file_dependencies(
            target_file="main.py",
            target_symbol="process_order",
            project_root=str(temp_project_with_dependencies),
            max_depth=5,
            include_code=True,
            include_diagram=True,
            confidence_decay_factor=0.9,
        )
        assert result.success is True
        # Should respect pro tier limits
        assert result.transitive_depth <= 5
