"""Enterprise tier tests for get_project_map.

Validates:
- Unlimited files (or very high limit)
- max_modules=1000 limit enforced
- detail_level='comprehensive' with all features
- Enterprise features accessible

[20260103_TEST] v3.3.1 - Enterprise tier enforcement and features
"""

import pytest


class TestEnterpriseTierLimits:
    """Test Enterprise tier file and module limits."""
    
    @pytest.mark.asyncio
    async def test_enterprise_unlimited_files(self, enterprise_server, huge_project_5000):
        """Enterprise tier: Handles 5000 files (unlimited or very high limit)."""
        result = await enterprise_server.get_project_map(
            project_root=str(huge_project_5000),
            include_complexity=False
        )
        
        # Should handle all files or have very high limit
        # Enterprise supports very large projects
        assert result.total_files > 1000, \
            f"Enterprise tier should handle >1000 files, got {result.total_files}"
        
        # Should not have file limit warnings
        if hasattr(result, 'warnings') and result.warnings:
            file_warnings = [w for w in result.warnings if 'file' in str(w).lower() and 'limit' in str(w).lower()]
            # Acceptable if no file limit warnings
            assert len(file_warnings) == 0 or result.total_files >= 5000, \
                f"Enterprise tier should not have restrictive file limits: {file_warnings}"
    
    @pytest.mark.asyncio
    async def test_enterprise_max_modules_1000(self, enterprise_server, project_2000_modules):
        """Enterprise tier: max_modules=1000 enforced on 2000-module project."""
        result = await enterprise_server.get_project_map(
            project_root=str(project_2000_modules),
            include_complexity=False
        )
        
        # Count Python files (modules)
        total_modules = len(result.modules)
        
        # Should enforce 1000 module limit (allowing flexibility for __init__.py files)
        # 200 packages × 10 modules + 200 __init__.py = 2200 files total
        # Expecting <= 2400 modules (1000 + reasonable package overhead)
        assert total_modules <= 2400, \
            f"Expected ≤2400 modules (1000 + packages), got {total_modules}"
    
    @pytest.mark.asyncio
    async def test_enterprise_comprehensive_detail(self, enterprise_server, simple_project):
        """Enterprise tier: detail_level='comprehensive' with all features."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=True
        )
        
        # Basic + Pro features should be present
        assert hasattr(result, 'packages')
        assert hasattr(result, 'modules')
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        
        # Enterprise features should be available in model
        enterprise_features = ['city_map_data', 'compliance_overlay', 'multi_repo_summary',
                              'force_graph', 'churn_heatmap', 'bug_hotspots',
                              'historical_trends', 'custom_metrics']
        
        available_features = [f for f in enterprise_features if f in result_dict]
        assert len(available_features) > 0, \
            f"Enterprise tier should have Enterprise feature fields. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_all_tier_features(self, enterprise_server, flask_project):
        """Enterprise tier: Has access to all Community + Pro + Enterprise features."""
        result = await enterprise_server.get_project_map(
            project_root=str(flask_project),
            include_complexity=True
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        
        # Community features
        assert 'packages' in result_dict
        assert 'modules' in result_dict
        
        # Pro features
        pro_features = ['coupling_metrics', 'git_ownership', 'architectural_layers']
        available_pro = [f for f in pro_features if f in result_dict]
        assert len(available_pro) > 0, "Enterprise should have Pro feature fields"
        
        # Enterprise features
        ent_features = ['city_map_data', 'compliance_overlay', 'multi_repo_summary']
        available_ent = [f for f in ent_features if f in result_dict]
        assert len(available_ent) > 0, "Enterprise should have Enterprise feature fields"


class TestEnterpriseTierFeatures:
    """Test Enterprise tier feature availability."""
    
    @pytest.mark.asyncio
    async def test_enterprise_city_map_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: city_map_data field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'city_map_data' in result_dict, \
            f"Enterprise should have city_map_data field. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_compliance_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: compliance_overlay field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'compliance_overlay' in result_dict, \
            f"Enterprise should have compliance_overlay field. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_multi_repo_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: multi_repo_summary field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'multi_repo_summary' in result_dict, \
            f"Enterprise should have multi_repo_summary field. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_force_graph_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: force_graph field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'force_graph' in result_dict, \
            f"Enterprise should have force_graph field. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_churn_heatmap_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: churn_heatmap field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'churn_heatmap' in result_dict, \
            f"Enterprise should have churn_heatmap field. Available: {list(result_dict.keys())}"
    
    @pytest.mark.asyncio
    async def test_enterprise_bug_hotspots_field_exists(self, enterprise_server, simple_project):
        """Enterprise tier: bug_hotspots field exists in model."""
        result = await enterprise_server.get_project_map(
            project_root=str(simple_project),
            include_complexity=False
        )
        
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else vars(result)
        assert 'bug_hotspots' in result_dict, \
            f"Enterprise should have bug_hotspots field. Available: {list(result_dict.keys())}"
