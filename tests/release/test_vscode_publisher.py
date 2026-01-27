"""Tests for VSCodeExtensionPublisher class.

Covers initialization, building, publishing, and version management.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from code_scalpel.release.vscode_publisher import VSCodeExtensionPublisher


class TestVSCodeExtensionPublisherInit:
    """Tests for VSCodeExtensionPublisher initialization."""

    def test_init_with_defaults(self, tmp_path):
        """Test initialization with default values."""
        # Create extension structure
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.2.3",
        )

        assert publisher.project_dir == tmp_path
        assert publisher.extension_dir == ext_dir
        assert publisher.version == "1.2.3"

    def test_init_with_custom_extension_dir(self, tmp_path):
        """Test initialization with custom extension directory."""
        # Create extension structure
        custom_dir = tmp_path / "my-extension"
        custom_dir.mkdir()
        (custom_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            extension_dir="my-extension",
            version="1.0.0",
        )

        assert publisher.extension_dir == custom_dir

    def test_init_missing_version_raises_error(self, tmp_path):
        """Test that missing version raises ValueError."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        with pytest.raises(ValueError, match="Version is required"):
            VSCodeExtensionPublisher(
                project_dir=str(tmp_path),
                version="",
            )

    def test_init_missing_extension_dir_raises_error(self, tmp_path):
        """Test that missing extension directory raises ValueError."""
        with pytest.raises(ValueError, match="Extension directory not found"):
            VSCodeExtensionPublisher(
                project_dir=str(tmp_path),
                version="1.0.0",
            )

    def test_init_missing_package_json_raises_error(self, tmp_path):
        """Test that missing package.json raises ValueError."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()

        with pytest.raises(ValueError, match="package.json not found"):
            VSCodeExtensionPublisher(
                project_dir=str(tmp_path),
                version="1.0.0",
            )


class TestVSCodeExtensionPublisherVersioning:
    """Tests for version management."""

    def test_get_extension_version(self, tmp_path):
        """Test reading version from package.json."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "2.1.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        assert publisher.get_extension_version() == "2.1.0"

    def test_update_extension_version(self, tmp_path):
        """Test updating version in package.json."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="2.0.0",
        )

        result = publisher.update_extension_version("2.0.0")

        assert result is True
        updated_content = (ext_dir / "package.json").read_text()
        assert '"version": "2.0.0"' in updated_content

    def test_update_extension_version_invalid_format(self, tmp_path):
        """Test that invalid version format raises error."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with pytest.raises(ValueError, match="Invalid version format"):
            publisher.update_extension_version("invalid")

    def test_update_extension_version_dry_run(self, tmp_path):
        """Test dry-run mode doesn't modify file."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("builtins.print"):
            result = publisher.update_extension_version("2.0.0", dry_run=True)

        assert result is True
        # File should not be modified
        content = (ext_dir / "package.json").read_text()
        assert '"version": "1.0.0"' in content


class TestVSCodeExtensionPublisherBuilding:
    """Tests for extension building."""

    def test_build_extension_success(self, tmp_path):
        """Test successful extension build."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            # Mock npm ci
            mock_run.side_effect = [
                Mock(returncode=0),  # npm ci
                Mock(returncode=1, stderr="not found"),  # vscode:prepublish
                Mock(returncode=0, stdout="Built successfully"),  # vsce package
            ]

            # Create mock VSIX file
            (ext_dir / "test-1.0.0.vsix").touch()

            result = publisher.build_extension()

            assert "vsix_file" in result
            assert "build_output" in result
            assert result["build_output"] == "Built successfully"

    def test_build_extension_npm_failure(self, tmp_path):
        """Test build failure with npm error."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="npm is not installed"):
                publisher.build_extension()

    def test_build_extension_vsce_failure(self, tmp_path):
        """Test build failure with vsce error."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # npm ci
                Mock(returncode=1, stderr="not found"),  # vscode:prepublish
                Mock(returncode=1, stderr="vsce error"),  # vsce package
            ]

            with pytest.raises(RuntimeError, match="vsce package failed"):
                publisher.build_extension()

    def test_build_extension_dry_run(self, tmp_path):
        """Test dry-run mode."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            with patch("builtins.print"):
                result = publisher.build_extension(dry_run=True)

            assert result["vsix_file"] == ""
            assert result["build_output"] == ""
            mock_run.assert_not_called()


class TestVSCodeExtensionPublisherPublishing:
    """Tests for extension publishing."""

    def test_publish_extension_success(self, tmp_path):
        """Test successful extension publish."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
            vsce_token="test-token",
        )

        with patch.object(publisher, "build_extension") as mock_build:
            mock_build.return_value = {
                "vsix_file": "test-1.0.0.vsix",
                "build_output": "Built",
            }

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="Published")

                result = publisher.publish_extension()

                assert result["version"] == "1.0.0"
                assert "vsix_file" in result
                assert "publish_output" in result

    def test_publish_extension_missing_token(self, tmp_path):
        """Test that missing token raises error."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with pytest.raises(ValueError, match="VSCE_PAT token required"):
            publisher.publish_extension()

    def test_publish_extension_failure(self, tmp_path):
        """Test publish failure."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
            vsce_token="test-token",
        )

        with patch.object(publisher, "build_extension") as mock_build:
            mock_build.return_value = {
                "vsix_file": "test-1.0.0.vsix",
                "build_output": "Built",
            }

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr="Publish failed")

                with pytest.raises(RuntimeError, match="vsce publish failed"):
                    publisher.publish_extension()

    def test_publish_extension_dry_run(self, tmp_path):
        """Test dry-run mode."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "1.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
            vsce_token="test-token",
        )

        with patch.object(publisher, "build_extension") as mock_build:
            mock_build.return_value = {
                "vsix_file": "test-1.0.0.vsix",
                "build_output": "Built",
            }

            with patch("subprocess.run"):
                with patch("builtins.print"):
                    result = publisher.publish_extension(dry_run=True)

                assert result["version"] == "1.0.0"
                assert result["publish_output"] == ""


class TestVSCodeExtensionPublisherStatus:
    """Tests for status checks."""

    def test_get_publish_status(self, tmp_path):
        """Test getting publication status."""
        ext_dir = tmp_path / "vscode-extension"
        ext_dir.mkdir()
        (ext_dir / "package.json").write_text('{"name": "test", "version": "2.0.0"}')

        publisher = VSCodeExtensionPublisher(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        status = publisher.get_publish_status()

        assert status["version"] == "1.0.0"
        assert status["package_version"] == "2.0.0"
        assert str(tmp_path) in status["project_dir"]
        assert str(ext_dir) in status["extension_dir"]
        assert status["has_package_json"] == "True"

    def test_version_validation(self):
        """Test version format validation."""
        assert VSCodeExtensionPublisher._is_valid_version("1.0.0") is True
        assert VSCodeExtensionPublisher._is_valid_version("2.5.10") is True
        assert VSCodeExtensionPublisher._is_valid_version("0.0.1") is True
        assert VSCodeExtensionPublisher._is_valid_version("1.0") is False
        assert VSCodeExtensionPublisher._is_valid_version("1.0.0.0") is False
        assert VSCodeExtensionPublisher._is_valid_version("invalid") is False
