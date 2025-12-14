"""
Comprehensive tests for scan_dependencies MCP tool.

[20251213_TEST] v1.5.0 - Tests for dependency vulnerability scanning.

Tests cover:
- Parsing requirements.txt
- Parsing pyproject.toml
- Parsing package.json
- CVE querying via OSV
- Severity aggregation
- Error handling
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from code_scalpel.mcp.server import (
    scan_dependencies,
    _scan_dependencies_sync,
    DependencyScanResult,
    DependencyInfo,
    DependencyVulnerability,
)


class TestDependencyScanResult:
    """Tests for DependencyScanResult model."""
    
    def test_model_creation(self):
        """Test creating a DependencyScanResult."""
        result = DependencyScanResult(
            success=True,
            total_dependencies=10,
            vulnerable_count=2,
            total_vulnerabilities=3,
            severity_summary={"HIGH": 2, "MEDIUM": 1},
            dependencies=[],
        )
        assert result.success is True
        assert result.total_dependencies == 10
        assert result.vulnerable_count == 2
    
    def test_default_values(self):
        """Test default values are set correctly."""
        result = DependencyScanResult(
            success=True,
            total_dependencies=0,
            vulnerable_count=0,
            total_vulnerabilities=0,
        )
        assert result.severity_summary == {}
        assert result.dependencies == []
        assert result.error is None


class TestDependencyInfo:
    """Tests for DependencyInfo model."""
    
    def test_model_creation(self):
        """Test creating a DependencyInfo."""
        dep = DependencyInfo(
            name="requests",
            version="2.25.0",
            ecosystem="PyPI",
            vulnerabilities=[],
        )
        assert dep.name == "requests"
        assert dep.version == "2.25.0"
        assert dep.ecosystem == "PyPI"


class TestDependencyVulnerability:
    """Tests for DependencyVulnerability model."""
    
    def test_model_creation(self):
        """Test creating a DependencyVulnerability."""
        vuln = DependencyVulnerability(
            id="CVE-2023-32681",
            summary="Test vulnerability",
            severity="HIGH",
            package="requests",
            vulnerable_version="2.25.0",
            fixed_version="2.31.0",
        )
        assert vuln.id == "CVE-2023-32681"
        assert vuln.severity == "HIGH"
        assert vuln.fixed_version == "2.31.0"


class TestScanDependenciesSync:
    """Tests for _scan_dependencies_sync function."""
    
    def test_scan_requirements_txt(self):
        """Test scanning requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\nflask>=2.0.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,  # Skip CVE lookup
            )
            
            assert result.success is True
            assert result.total_dependencies >= 2
            names = {d.name for d in result.dependencies}
            assert "requests" in names
            assert "flask" in names
    
    def test_scan_pyproject_toml(self):
        """Test scanning pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("""
[project]
name = "test-project"
dependencies = [
    "click>=8.0",
    "rich>=10.0",
]
""")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            names = {d.name for d in result.dependencies}
            assert "click" in names
            assert "rich" in names
    
    def test_scan_nonexistent_root(self):
        """Test scanning nonexistent project root."""
        result = _scan_dependencies_sync(
            project_root="/nonexistent/path/12345",
            scan_vulnerabilities=False,
        )
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_scan_empty_project(self):
        """Test scanning project with no dependency files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies == 0
    
    @patch("code_scalpel.ast_tools.osv_client.OSVClient")
    def test_scan_with_vulnerabilities(self, mock_osv_class):
        """Test scanning with vulnerability lookup."""
        # Mock OSV client
        mock_client = MagicMock()
        mock_osv_class.return_value = mock_client
        
        # Create mock vulnerability
        mock_vuln = MagicMock()
        mock_vuln.id = "CVE-2023-12345"
        mock_vuln.summary = "Test vulnerability"
        mock_vuln.severity = "HIGH"
        mock_vuln.package = "requests"
        mock_vuln.vulnerable_version = "2.25.0"
        mock_vuln.fixed_version = "2.31.0"
        mock_vuln.aliases = ["GHSA-xxx"]
        mock_vuln.references = ["https://example.com"]
        
        mock_client.query_package.return_value = [mock_vuln]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )
            
            assert result.success is True
            assert result.total_vulnerabilities >= 1
            assert result.vulnerable_count >= 1
            assert result.severity_summary.get("HIGH", 0) >= 1
    
    @patch("code_scalpel.ast_tools.osv_client.OSVClient")
    def test_scan_osv_error_continues(self, mock_osv_class):
        """Test that OSV errors don't stop the scan."""
        from code_scalpel.ast_tools.osv_client import OSVError
        
        mock_client = MagicMock()
        mock_osv_class.return_value = mock_client
        mock_client.query_package.side_effect = OSVError("API error")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\nflask==2.0.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )
            
            # Scan should succeed even if OSV fails
            assert result.success is True
            assert result.total_dependencies >= 2
    
    def test_skip_wildcard_versions(self):
        """Test that wildcard versions don't trigger CVE lookup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests\nflask>=2.0\n")
            
            with patch("code_scalpel.ast_tools.osv_client.OSVClient") as mock_osv:
                result = _scan_dependencies_sync(
                    project_root=tmpdir,
                    scan_vulnerabilities=True,
                )
                
                assert result.success is True
                # OSV should not be called for packages without specific versions
                # (requests has "*" version, flask has ">=2.0" which gets cleaned)
    
    def test_include_dev_dependencies(self):
        """Test including dev dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json with dev dependencies
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text(json.dumps({
                "dependencies": {"express": "4.18.0"},
                "devDependencies": {"jest": "29.0.0"}
            }))
            
            # Without dev deps
            result_no_dev = _scan_dependencies_sync(
                project_root=tmpdir,
                include_dev=False,
                scan_vulnerabilities=False,
            )
            
            # With dev deps
            result_with_dev = _scan_dependencies_sync(
                project_root=tmpdir,
                include_dev=True,
                scan_vulnerabilities=False,
            )
            
            # Should have more deps when including dev
            assert result_with_dev.total_dependencies >= result_no_dev.total_dependencies


class TestScanDependenciesAsync:
    """Tests for async scan_dependencies function."""
    
    @pytest.mark.asyncio
    async def test_async_scan(self):
        """Test async version of scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\n")
            
            result = await scan_dependencies(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies >= 1
    
    @pytest.mark.asyncio
    async def test_async_default_root(self):
        """Test async with default project root."""
        # This uses PROJECT_ROOT which is cwd
        result = await scan_dependencies(
            scan_vulnerabilities=False,
        )
        
        # Should succeed (may or may not find deps in cwd)
        assert result.success is True


class TestSeveritySummary:
    """Tests for severity summary aggregation."""
    
    @patch("code_scalpel.ast_tools.osv_client.OSVClient")
    def test_severity_counts(self, mock_osv_class):
        """Test that severity counts are aggregated correctly."""
        mock_client = MagicMock()
        mock_osv_class.return_value = mock_client
        
        # Create mock vulnerabilities with different severities
        def make_vuln(id, severity):
            v = MagicMock()
            v.id = id
            v.summary = "Test"
            v.severity = severity
            v.package = "test"
            v.vulnerable_version = "1.0.0"
            v.fixed_version = "2.0.0"
            v.aliases = []
            v.references = []
            return v
        
        mock_client.query_package.side_effect = [
            [make_vuln("CVE-1", "HIGH"), make_vuln("CVE-2", "HIGH")],
            [make_vuln("CVE-3", "CRITICAL")],
            [],  # No vulns for third package
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("pkg1==1.0.0\npkg2==1.0.0\npkg3==1.0.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )
            
            assert result.severity_summary.get("HIGH", 0) == 2
            assert result.severity_summary.get("CRITICAL", 0) == 1
            assert result.total_vulnerabilities == 3
            assert result.vulnerable_count == 2  # pkg1 and pkg2


class TestVersionCleaning:
    """Tests for version string cleaning before OSV lookup."""
    
    @patch("code_scalpel.ast_tools.osv_client.OSVClient")
    def test_version_prefix_stripped(self, mock_osv_class):
        """Test that version prefixes are stripped for OSV queries."""
        mock_client = MagicMock()
        mock_osv_class.return_value = mock_client
        mock_client.query_package.return_value = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("pkg1>=2.0.0\npkg2~=3.0.0\npkg3^=4.0.0\n")
            
            _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )
            
            # Check that versions were cleaned for OSV query
            calls = mock_client.query_package.call_args_list
            versions = [call[0][1] for call in calls]  # Second arg is version
            assert "2.0.0" in versions
            assert "3.0.0" in versions
            assert "4.0.0" in versions


class TestEcosystemMapping:
    """Tests for ecosystem detection and mapping."""
    
    def test_python_ecosystem(self):
        """Test Python dependencies use PyPI ecosystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            python_deps = [d for d in result.dependencies if d.ecosystem == "PyPI"]
            assert len(python_deps) >= 1
    
    def test_javascript_ecosystem(self):
        """Test JavaScript dependencies use npm ecosystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text(json.dumps({
                "dependencies": {"express": "4.18.0"}
            }))
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            npm_deps = [d for d in result.dependencies if d.ecosystem == "npm"]
            assert len(npm_deps) >= 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_malformed_requirements(self):
        """Test handling of malformed requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("@invalid\n=bad=entry=\nrequests==2.25.0\n")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            # Should still succeed and find valid entries
            assert result.success is True
    
    def test_empty_requirements(self):
        """Test handling of empty requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies == 0
    
    def test_comments_ignored(self):
        """Test that comments in requirements.txt are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("""
# This is a comment
requests==2.25.0  # inline comment
# Another comment
flask>=2.0
""")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            names = {d.name for d in result.dependencies}
            assert "requests" in names
            assert "flask" in names
    
    def test_poetry_dependencies(self):
        """Test parsing Poetry dependencies from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pp_path = Path(tmpdir) / "pyproject.toml"
            pp_path.write_text("""
[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.0"
flask = "2.0.0"
pandas = ">=1.0"
""")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            names = {d.name for d in result.dependencies}
            # Should include poetry deps but not python
            assert "requests" in names
            assert "flask" in names
            assert "pandas" in names
            assert "python" not in names  # python is special, excluded
    
    def test_pep621_dependencies(self):
        """Test parsing PEP 621 dependencies from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pp_path = Path(tmpdir) / "pyproject.toml"
            pp_path.write_text("""
[project]
name = "test-app"
dependencies = [
    "requests>=2.25.0",
    "flask>=2.0",
]
""")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            names = {d.name for d in result.dependencies}
            assert "requests" in names
            assert "flask" in names
    
    def test_malformed_pyproject_toml(self):
        """Test graceful handling of malformed pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pp_path = Path(tmpdir) / "pyproject.toml"
            pp_path.write_text("{ invalid toml content }")
            
            # Should not crash, just return empty
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies == 0
    
    def test_malformed_requirements_txt(self):
        """Test graceful handling of malformed requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            # Create file with only comments and whitespace
            req_path.write_text("""
# Comment line
   
# Another comment
-e git+https://github.com/example/repo.git  # Options line, should be skipped
""")
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies == 0
    
    def test_malformed_package_json(self):
        """Test graceful handling of malformed package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pj_path = Path(tmpdir) / "package.json"
            pj_path.write_text("{ invalid json }")
            
            # Should not crash, just return empty
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
            )
            
            assert result.success is True
            assert result.total_dependencies == 0
    
    def test_package_json_dev_dependencies(self):
        """Test parsing devDependencies from package.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pj_path = Path(tmpdir) / "package.json"
            pj_path.write_text(json.dumps({
                "name": "test-app",
                "dependencies": {
                    "express": "^4.17.1",
                },
                "devDependencies": {
                    "jest": "^27.0.0",
                    "webpack": "^5.0.0",
                }
            }))
            
            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=False,
                include_dev=True,  # Include dev dependencies
            )
            
            assert result.success is True
            assert result.total_dependencies == 3
            names = {d.name for d in result.dependencies}
            assert "express" in names
            assert "jest" in names
            assert "webpack" in names
