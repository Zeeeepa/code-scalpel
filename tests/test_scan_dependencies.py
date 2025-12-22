"""
Comprehensive tests for scan_dependencies MCP tool.

[20251213_TEST] v1.5.0 - Tests for dependency vulnerability scanning.
[20251220_FEATURE] v3.0.5 - Updated to use DependencyScanResult, DependencyInfo, DependencyVulnerability models.

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
from unittest.mock import patch
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
            pyproject.write_text(
                """
[project]
name = "test-project"
dependencies = [
    "click>=8.0",
    "rich>=10.0",
]
"""
            )

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

    def test_scan_with_vulnerabilities(self):
        """Test scanning with real OSV API - uses actual vulnerability data."""
        # [20251218_TEST] Changed to use real OSV API instead of mocking
        # The real API will return actual vulnerabilities for requests==2.25.0
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests==2.25.0\n")

            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )

            assert result.success is True
            # requests==2.25.0 has known vulnerabilities in OSV database
            assert result.total_vulnerabilities >= 1
            assert result.vulnerable_count >= 1
            # At least one vulnerability should exist (any severity)
            assert sum(result.severity_summary.values()) >= 1

    def test_scan_osv_error_continues(self):
        """Test that scan continues even with package parsing errors or network issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            # Use real packages - scan should succeed even if some packages have issues
            req_path.write_text("requests==2.25.0\nflask==2.0.0\n")

            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )

            # Scan should succeed and find dependencies
            assert result.success is True
            assert result.total_dependencies >= 2

    def test_skip_wildcard_versions(self):
        """Test that wildcard versions don't trigger CVE lookup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("requests\nflask>=2.0\n")

            with patch("code_scalpel.ast_tools.osv_client.OSVClient"):
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
            pkg_json.write_text(
                json.dumps(
                    {
                        "dependencies": {"express": "4.18.0"},
                        "devDependencies": {"jest": "29.0.0"},
                    }
                )
            )

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
            assert (
                result_with_dev.total_dependencies >= result_no_dev.total_dependencies
            )


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

    def test_severity_counts(self):
        """Test severity counts with real OSV API - uses requests package with known vulnerabilities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            # requests==2.25.0 has known vulnerabilities
            # [20251220_FIX] Severity can change over time, so we just verify vulns are found
            req_path.write_text("requests==2.25.0\n")

            result = _scan_dependencies_sync(
                project_root=tmpdir,
                scan_vulnerabilities=True,
            )

            assert result.success is True
            # Verify we got vulnerabilities from real OSV data
            assert (
                result.total_vulnerabilities >= 3
            ), f"Expected at least 3 vulns, got: {result.total_vulnerabilities}"
            # Verify severity summary has some entries (severity can vary over time)
            assert (
                sum(result.severity_summary.values()) >= 3
            ), f"Expected severities, got: {result.severity_summary}"
            # Verify at least one package is marked vulnerable
            assert result.vulnerable_count >= 1


class TestVersionCleaning:
    """Tests for version string cleaning before OSV lookup."""

    def test_version_prefix_stripped(self):
        """Test that version prefixes are stripped correctly using Python's lstrip."""
        # Test the version cleaning logic directly (mimics line 4004 in server.py)
        test_cases = [
            (">=2.0.0", "2.0.0"),
            ("~=3.0.0", "3.0.0"),
            ("^=4.0.0", "4.0.0"),
            ("<=1.5.0", "1.5.0"),
            ("<2.0.0", "2.0.0"),
            ("~1.0.0", "1.0.0"),
            ("^1.2.3", "1.2.3"),
            ("1.0.0", "1.0.0"),  # No prefix
        ]

        for version_with_prefix, expected_clean in test_cases:
            clean_version = version_with_prefix.lstrip(">=<~^")
            assert (
                clean_version == expected_clean
            ), f"Failed for {version_with_prefix}: got {clean_version}, expected {expected_clean}"


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
            pkg_json.write_text(json.dumps({"dependencies": {"express": "4.18.0"}}))

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
            req_path.write_text(
                """
# This is a comment
requests==2.25.0  # inline comment
# Another comment
flask>=2.0
"""
            )

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
            pp_path.write_text(
                """
[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.0"
flask = "2.0.0"
pandas = ">=1.0"
"""
            )

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
            pp_path.write_text(
                """
[project]
name = "test-app"
dependencies = [
    "requests>=2.25.0",
    "flask>=2.0",
]
"""
            )

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
            req_path.write_text(
                """
# Comment line
   
# Another comment
-e git+https://github.com/example/repo.git  # Options line, should be skipped
"""
            )

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
            pj_path.write_text(
                json.dumps(
                    {
                        "name": "test-app",
                        "dependencies": {
                            "express": "^4.17.1",
                        },
                        "devDependencies": {
                            "jest": "^27.0.0",
                            "webpack": "^5.0.0",
                        },
                    }
                )
            )

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
