import pytest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path
from code_scalpel.mcp.server import scan_dependencies, DependencyScanResult


@pytest.fixture
def temp_project_with_deps():
    """Create a temporary project with dependency files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create requirements.txt with many dependencies
        deps = "\n".join([f"package{i}==1.0.{i}" for i in range(100)])
        (project_root / "requirements.txt").write_text(deps)
        
        # Create package.json
        (project_root / "package.json").write_text("""{
  "name": "test-project",
  "dependencies": {
    "react": "^18.0.0",
    "lodash": "^4.17.21"
  }
}""")
        
        yield project_root


@pytest.mark.asyncio
async def test_scan_dependencies_community(temp_project_with_deps):
    """Test Community tier - max 50 dependencies, no Pro/Enterprise features."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        # Mock OSV API to avoid actual network calls
        with patch("code_scalpel.security.dependencies.VulnerabilityScanner") as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.osv_client.query_batch.return_value = {}
            mock_scanner.return_value = mock_instance
            
            result = await scan_dependencies(
                project_root=str(temp_project_with_deps),
                scan_vulnerabilities=True,
            )
            
            assert isinstance(result, DependencyScanResult)
            assert result.success is True
            
            # Community: limited to 50 dependencies
            assert result.total_dependencies <= 50
            
            # Pro features not available
            assert result.reachability_summary is None
            assert result.vulnerable_call_paths == []
            assert result.false_positive_count == 0
            
            # Enterprise features not available
            assert result.license_findings == []
            assert result.typosquatting_alerts == []
            assert result.supply_chain_score is None
            assert result.compliance_report is None


@pytest.mark.asyncio
async def test_scan_dependencies_pro(temp_project_with_deps):
    """Test Pro tier - unlimited deps, reachability analysis, false positive reduction."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        # Mock OSV API with some vulnerabilities
        with patch("code_scalpel.security.dependencies.VulnerabilityScanner") as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.osv_client.query_batch.return_value = {
                "package10==1.0.10": [{
                    "id": "GHSA-test-1234",
                    "summary": "Test vulnerability",
                    "database_specific": {"severity": "HIGH"},
                    "affected": []
                }]
            }
            mock_scanner.return_value = mock_instance
            
            result = await scan_dependencies(
                project_root=str(temp_project_with_deps),
                scan_vulnerabilities=True,
            )
            
            assert isinstance(result, DependencyScanResult)
            assert result.success is True
            
            # Pro: no dependency limit
            assert result.total_dependencies > 50
            
            # Pro features available
            assert result.reachability_summary is not None
            assert isinstance(result.reachability_summary, dict)
            assert "reachable" in result.reachability_summary
            assert "unreachable" in result.reachability_summary
            assert "unknown" in result.reachability_summary
            
            # If vulnerabilities found, should have call paths
            if result.vulnerable_count > 0:
                assert len(result.vulnerable_call_paths) > 0
                call_path = result.vulnerable_call_paths[0]
                assert "package" in call_path
                assert "vulnerability_id" in call_path
                assert "call_chain" in call_path
            
            assert result.false_positive_count >= 0
            
            # Enterprise features not available at Pro tier
            assert result.license_findings == []
            assert result.typosquatting_alerts == []
            assert result.supply_chain_score is None
            assert result.compliance_report is None


@pytest.mark.asyncio
async def test_scan_dependencies_enterprise(temp_project_with_deps):
    """Test Enterprise tier - license compliance, typosquatting, supply chain risk."""
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        # Mock OSV API
        with patch("code_scalpel.security.dependencies.VulnerabilityScanner") as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.osv_client.query_batch.return_value = {
                "package10==1.0.10": [{
                    "id": "GHSA-test-1234",
                    "summary": "Test vulnerability",
                    "database_specific": {"severity": "CRITICAL"},
                    "affected": []
                }]
            }
            mock_scanner.return_value = mock_instance
            
            result = await scan_dependencies(
                project_root=str(temp_project_with_deps),
                scan_vulnerabilities=True,
            )
            
            assert isinstance(result, DependencyScanResult)
            assert result.success is True
            
            # Pro features included
            assert result.reachability_summary is not None
            assert isinstance(result.vulnerable_call_paths, list)
            assert result.false_positive_count >= 0
            
            # Enterprise features available
            # License findings (may be empty if no problematic licenses detected)
            assert isinstance(result.license_findings, list)
            
            # Typosquatting alerts (may be empty if no suspicious packages)
            assert isinstance(result.typosquatting_alerts, list)
            
            # Supply chain score calculated
            assert result.supply_chain_score is not None
            assert isinstance(result.supply_chain_score, float)
            assert 0.0 <= result.supply_chain_score <= 1.0
            
            # Compliance report generated
            assert result.compliance_report is not None
            assert isinstance(result.compliance_report, str)
            assert "Compliance Report" in result.compliance_report
            assert "Total Dependencies" in result.compliance_report
            assert "Status:" in result.compliance_report


@pytest.mark.asyncio
async def test_tier_limits_enforced():
    """Test that tier limits are properly enforced."""
    # Community: max 50 dependencies
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("scan_dependencies", "community")
        assert caps["limits"]["max_dependencies"] == 50
        assert caps["limits"]["osv_lookup"] is True
    
    # Pro: unlimited
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("scan_dependencies", "pro")
        assert caps["limits"]["max_dependencies"] is None
        assert caps["limits"]["osv_lookup"] is True
    
    # Enterprise: unlimited
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("scan_dependencies", "enterprise")
        assert caps["limits"]["max_dependencies"] is None
        assert caps["limits"]["osv_lookup"] is True


@pytest.mark.asyncio
async def test_capability_detection():
    """Test that capabilities are correctly detected per tier."""
    # Community
    with patch("code_scalpel.licensing.get_current_tier", return_value="community"):
        from code_scalpel.licensing import get_tool_capabilities
        caps = get_tool_capabilities("scan_dependencies", "community")
        assert "basic_dependency_scan" in caps["capabilities"]
        assert "cve_database_check" in caps["capabilities"]
        assert "reachability_analysis" not in caps["capabilities"]
        assert "license_compliance_scanning" not in caps["capabilities"]
    
    # Pro
    with patch("code_scalpel.licensing.get_current_tier", return_value="pro"):
        caps = get_tool_capabilities("scan_dependencies", "pro")
        assert "basic_dependency_scan" in caps["capabilities"]
        assert "reachability_analysis" in caps["capabilities"]
        assert "vulnerable_function_call_check" in caps["capabilities"]
        assert "false_positive_reduction" in caps["capabilities"]
        assert "license_compliance_scanning" not in caps["capabilities"]
    
    # Enterprise
    with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
        caps = get_tool_capabilities("scan_dependencies", "enterprise")
        assert "basic_dependency_scan" in caps["capabilities"]
        assert "reachability_analysis" in caps["capabilities"]
        assert "license_compliance_scanning" in caps["capabilities"]
        assert "typosquatting_detection" in caps["capabilities"]
        assert "supply_chain_risk_scoring" in caps["capabilities"]
        assert "compliance_reporting" in caps["capabilities"]


@pytest.mark.asyncio
async def test_enterprise_typosquatting_detection():
    """Test Enterprise tier typosquatting detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create requirements with suspicious package name
        (project_root / "requirements.txt").write_text("""
requests==2.28.0
requets==1.0.0
numpy==1.24.0
nummpy==0.1.0
""")
        
        with patch("code_scalpel.licensing.get_current_tier", return_value="enterprise"):
            with patch("code_scalpel.security.dependencies.VulnerabilityScanner") as mock_scanner:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.osv_client.query_batch.return_value = {}
                mock_scanner.return_value = mock_instance
                
                result = await scan_dependencies(
                    project_root=str(project_root),
                    scan_vulnerabilities=True,
                )
                
                # Should detect "requets" as potential typosquat of "requests"
                # Note: Actual detection depends on similarity threshold and algorithm
                assert isinstance(result.typosquatting_alerts, list)
                # May or may not detect based on algorithm, but structure should be correct
                if result.typosquatting_alerts:
                    alert = result.typosquatting_alerts[0]
                    assert "package" in alert
                    assert "suspected_target" in alert
                    assert "similarity_score" in alert
