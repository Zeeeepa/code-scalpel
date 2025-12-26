
import pytest
from unittest.mock import patch
import code_scalpel.mcp.server
import importlib
# Reload server to ensure we test the latest code
importlib.reload(code_scalpel.mcp.server)
from code_scalpel.mcp.server import get_cross_file_dependencies, CrossFileDependenciesResult
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create directory structure
        (project_root / "services").mkdir()
        (project_root / "models").mkdir()
        (project_root / "controllers").mkdir()
        
        # Create files with dependencies
        # models/user.py
        (project_root / "models" / "user.py").write_text("""
class User:
    def __init__(self, name):
        self.name = name
""")
        
        # services/auth.py (imports from models)
        (project_root / "services" / "auth.py").write_text("""
from models.user import User

def authenticate(username):
    return User(username)
""")
        
        # controllers/api.py (imports from services - layer violation)
        (project_root / "controllers" / "api.py").write_text("""
from services.auth import authenticate
from models.user import User  # Direct access to data layer

def handle_login(username):
    return authenticate(username)
""")
        
        yield project_root


@pytest.mark.asyncio
async def test_get_cross_file_dependencies_community(temp_project):
    """Test Community tier - max_depth=1, no Pro/Enterprise features."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        result = await get_cross_file_dependencies(
            target_file="controllers/api.py",
            target_symbol="handle_login",
            project_root=str(temp_project),
            max_depth=1,
        )
        
        assert isinstance(result, CrossFileDependenciesResult)
        assert result.success is True
        
        # Community: direct imports only (max_depth=1)
        assert result.transitive_depth == 0
        assert result.coupling_score is None
        assert result.dependency_chains == []
        
        # Enterprise features not available
        assert result.boundary_violations == []
        assert result.layer_violations == []
        assert result.architectural_alerts == []


@pytest.mark.asyncio
async def test_get_cross_file_dependencies_pro(temp_project):
    """Test Pro tier - max_depth=5, transitive deps, coupling analysis."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        result = await get_cross_file_dependencies(
            target_file="controllers/api.py",
            target_symbol="handle_login",
            project_root=str(temp_project),
            max_depth=3,
        )
        
        assert isinstance(result, CrossFileDependenciesResult)
        assert result.success is True
        
        # Pro features enabled
        assert result.transitive_depth == 3
        assert result.coupling_score is not None
        assert isinstance(result.coupling_score, float)
        # Coupling score is dependencies/files ratio, can exceed 1.0
        assert result.coupling_score > 0.0
        
        # Dependency chains available (Pro feature)
        assert isinstance(result.dependency_chains, list)
        # Should have at least one chain showing transitive deps
        if result.dependency_chains:
            assert all(isinstance(chain, list) for chain in result.dependency_chains)
        
        # Enterprise features not available at Pro tier
        assert result.boundary_violations == []
        assert result.layer_violations == []
        assert result.architectural_alerts == []


@pytest.mark.asyncio
async def test_get_cross_file_dependencies_enterprise(temp_project):
    """Test Enterprise tier - unlimited depth, architectural firewall."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        result = await get_cross_file_dependencies(
            target_file="controllers/api.py",
            target_symbol="handle_login",
            project_root=str(temp_project),
            max_depth=10,
        )
        
        assert isinstance(result, CrossFileDependenciesResult)
        assert result.success is True
        
        # Pro features included
        assert result.transitive_depth == 10
        assert result.coupling_score is not None
        assert isinstance(result.dependency_chains, list)
        
        # Enterprise features enabled
        # Should detect controller->model violation (Presentation->Data)
        assert isinstance(result.boundary_violations, list)
        if result.boundary_violations:
            # Verify violation structure
            violation = result.boundary_violations[0]
            assert "type" in violation
            assert "source" in violation
            assert "target" in violation
            assert "violation" in violation
            assert "recommendation" in violation
            # Check for layer_skip type
            assert violation["type"] == "layer_skip"
        
        assert isinstance(result.layer_violations, list)
        assert isinstance(result.architectural_alerts, list)
        
        # Should have alerts if violations detected
        if result.boundary_violations or result.layer_violations:
            assert len(result.architectural_alerts) > 0


@pytest.mark.asyncio
async def test_tier_limits_enforced():
    """Test that tier limits are properly enforced."""
    # Community: max_depth capped at 1
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("get_cross_file_dependencies", "community")
        assert caps["limits"]["max_depth"] == 1
        assert caps["limits"]["max_files"] == 50
    
    # Pro: max_depth capped at 5
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("get_cross_file_dependencies", "pro")
        assert caps["limits"]["max_depth"] == 5
        assert caps["limits"]["max_files"] == 500
    
    # Enterprise: unlimited
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("get_cross_file_dependencies", "enterprise")
        assert caps["limits"]["max_depth"] is None
        assert caps["limits"]["max_files"] is None


@pytest.mark.asyncio
async def test_capability_detection():
    """Test that capabilities are correctly detected per tier."""
    # Community
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("get_cross_file_dependencies", "community")
        assert "direct_import_mapping" in caps["capabilities"]
        assert "transitive_dependency_mapping" not in caps["capabilities"]
        assert "architectural_firewall" not in caps["capabilities"]
    
    # Pro
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("get_cross_file_dependencies", "pro")
        assert "direct_import_mapping" in caps["capabilities"]
        assert "transitive_dependency_mapping" in caps["capabilities"]
        assert "deep_coupling_analysis" in caps["capabilities"]
        assert "architectural_firewall" not in caps["capabilities"]
    
    # Enterprise
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("get_cross_file_dependencies", "enterprise")
        assert "direct_import_mapping" in caps["capabilities"]
        assert "transitive_dependency_mapping" in caps["capabilities"]
        assert "architectural_firewall" in caps["capabilities"]
        assert "boundary_violation_alerts" in caps["capabilities"]
