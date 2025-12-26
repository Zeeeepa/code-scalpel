import pytest
from unittest.mock import patch, MagicMock
from code_scalpel.mcp.server import get_project_map, ProjectMapResult

@pytest.mark.asyncio
async def test_get_project_map_community():
    with patch("code_scalpel.licensing.tier_detector.get_current_tier", return_value="community"):
        result = await get_project_map(project_root=".")
        assert isinstance(result, ProjectMapResult)
        assert result.module_relationships is None
        assert result.architectural_layers is None
        assert result.city_map_data is None

@pytest.mark.asyncio
async def test_get_project_map_pro():
    with patch("code_scalpel.licensing.tier_detector.get_current_tier", return_value="pro"):
        result = await get_project_map(project_root=".")
        assert isinstance(result, ProjectMapResult)
        assert result.module_relationships is not None
        assert result.architectural_layers is not None
        assert result.city_map_data is None

@pytest.mark.asyncio
async def test_get_project_map_enterprise():
    with patch("code_scalpel.licensing.tier_detector.get_current_tier", return_value="enterprise"):
        result = await get_project_map(project_root=".")
        assert isinstance(result, ProjectMapResult)
        assert result.module_relationships is not None
        assert result.architectural_layers is not None
        assert result.city_map_data is not None
        assert result.churn_heatmap is not None
        assert result.bug_hotspots is not None
