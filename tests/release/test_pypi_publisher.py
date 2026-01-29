"""Tests for PyPI publishing."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from code_scalpel.release.pypi_publisher import PyPIPublisher


class TestPyPIPublisherInit:
    """Test PyPIPublisher initialization."""

    def test_init_with_token_and_project_dir(self):
        """Test initialization with explicit token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )
            assert publisher.pypi_token == "test_token"
            assert publisher.project_dir == Path(tmpdir)

    def test_init_with_env_token(self):
        """Test initialization with token from environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            with patch.dict(os.environ, {"PYPI_TOKEN": "env_token"}):
                publisher = PyPIPublisher(project_dir=tmpdir)
                assert publisher.pypi_token == "env_token"

    def test_init_missing_pyproject_raises_error(self):
        """Test that missing pyproject.toml raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
                PyPIPublisher(project_dir=tmpdir, pypi_token="test_token")

    def test_init_missing_token_raises_error(self):
        """Test that missing token raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="PyPI token required"):
                    PyPIPublisher(project_dir=tmpdir)


class TestPyPIPublisherVersions:
    """Test getting package version and name."""

    def test_get_package_version(self):
        """Test getting package version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.2.3'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )
            version = publisher.get_package_version()
            assert version == "1.2.3"

    def test_get_package_name(self):
        """Test getting package name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'my-package'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )
            name = publisher.get_package_name()
            assert name == "my-package"

    def test_get_version_missing_raises_error(self):
        """Test that missing version raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )
            with pytest.raises(ValueError, match="Version not found"):
                publisher.get_package_version()

    def test_get_name_missing_raises_error(self):
        """Test that missing name raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )
            with pytest.raises(ValueError, match="Package name not found"):
                publisher.get_package_name()


class TestPyPIPublisherDist:
    """Test distribution handling."""

    def test_clean_dist(self):
        """Test cleaning distribution directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake dist directory
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")
            (dist_dir / "test-1.0.0.tar.gz").write_text("sdist")

            # Clean
            publisher.clean_dist()

            assert not dist_dir.exists()

    def test_get_upload_status_no_distributions(self):
        """Test upload status with no distributions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            status = publisher.get_upload_status()
            assert status["status"] == "no-distributions"
            assert status["count"] == "0"

    def test_get_upload_status_with_distributions(self):
        """Test upload status with distributions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake distributions
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")
            (dist_dir / "test-1.0.0.tar.gz").write_text("sdist")

            status = publisher.get_upload_status()
            assert status["status"] == "ready"
            assert status["count"] == "2"


class TestPyPIPublisherBuild:
    """Test building distributions."""

    def test_build_distributions_success(self):
        """Test successful distribution build."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            with patch("subprocess.run") as mock_run:

                def run_side_effect(*args, **kwargs):
                    # Create the dist directory and files after clean
                    dist_dir = Path(tmpdir) / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")
                    (dist_dir / "test-1.0.0.tar.gz").write_text("sdist")
                    return Mock(returncode=0, stderr="")

                mock_run.side_effect = run_side_effect

                result = publisher.build_distributions()

                assert "wheel" in result
                assert "sdist" in result
                assert result["wheel"].endswith(".whl")
                assert result["sdist"].endswith(".tar.gz")

    def test_build_distributions_failure(self):
        """Test distribution build failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="Build failed",
                )

                with pytest.raises(RuntimeError, match="Build failed"):
                    publisher.build_distributions()

    def test_build_distributions_missing_build_module(self):
        """Test handling missing build module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError()

                with pytest.raises(RuntimeError, match="build module not found"):
                    publisher.build_distributions()


class TestPyPIPublisherVerify:
    """Test package verification."""

    def test_verify_package_success(self):
        """Test successful package verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake wheel
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="")

                result = publisher.verify_package()

                assert result["status"] == "valid"
                assert "test" in result["file"]

    def test_verify_package_failure(self):
        """Test package verification failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake wheel
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="Invalid metadata",
                )

                with pytest.raises(RuntimeError, match="verification failed"):
                    publisher.verify_package()

    def test_verify_package_no_wheel_found(self):
        """Test verification when no wheel is found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create empty dist directory
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()

            with pytest.raises(RuntimeError, match="No wheel file found"):
                publisher.verify_package()


class TestPyPIPublisherUpload:
    """Test uploading to PyPI."""

    def test_upload_to_pypi_success(self):
        """Test successful upload to PyPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake distributions
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")
            (dist_dir / "test-1.0.0.tar.gz").write_text("sdist")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Uploading distributions to PyPI",
                )

                result = publisher.upload_to_pypi()

                assert result["status"] == "success"
                assert result["mode"] == "production"

    def test_upload_to_pypi_dry_run(self):
        """Test dry-run upload to PyPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake distributions
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="[DRY RUN] Would upload",
                )

                result = publisher.upload_to_pypi(dry_run=True)

                assert result["status"] == "dry-run"
                assert result["mode"] == "dry-run"

                # Verify --dry-run flag was passed
                call_args = mock_run.call_args[0][0]
                assert "--dry-run" in call_args

    def test_upload_to_pypi_failure(self):
        """Test upload failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[project]\nname = 'test'\nversion = '1.0.0'\n")

            publisher = PyPIPublisher(
                project_dir=tmpdir,
                pypi_token="test_token",
            )

            # Create fake distributions
            dist_dir = Path(tmpdir) / "dist"
            dist_dir.mkdir()
            (dist_dir / "test-1.0.0-py3-none-any.whl").write_text("wheel")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="Authentication failed",
                )

                with pytest.raises(RuntimeError, match="Upload failed"):
                    publisher.upload_to_pypi()
