"""Tests for DockerImageBuilder class.

Covers initialization, image building, authentication, and publishing.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from code_scalpel.release.docker_builder import DockerImageBuilder


class TestDockerImageBuilderInit:
    """Tests for DockerImageBuilder initialization."""

    def test_init_with_defaults(self, tmp_path):
        """Test initialization with default values."""
        # Create Dockerfile
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.2.3",
        )

        assert builder.project_dir == tmp_path
        assert builder.version == "1.2.3"
        assert builder.registry == "docker.io"
        assert builder.image_names == ["code-scalpel"]
        assert builder.username == ""
        assert builder.password_or_token == ""

    def test_init_with_custom_values(self, tmp_path):
        """Test initialization with custom values."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="2.0.0",
            registry="ghcr.io",
            image_names=["my-image", "my-app"],
            username="testuser",
            password_or_token="testtoken",
        )

        assert builder.version == "2.0.0"
        assert builder.registry == "ghcr.io"
        assert builder.image_names == ["my-image", "my-app"]
        assert builder.username == "testuser"
        assert builder.password_or_token == "testtoken"

    def test_init_missing_version_raises_error(self, tmp_path):
        """Test that missing version raises ValueError."""
        (tmp_path / "Dockerfile").touch()

        with pytest.raises(ValueError, match="Version is required"):
            DockerImageBuilder(
                project_dir=str(tmp_path),
                version="",
            )

    def test_init_missing_dockerfile_raises_error(self, tmp_path):
        """Test that missing Dockerfile raises ValueError."""
        with pytest.raises(ValueError, match="Dockerfile not found"):
            DockerImageBuilder(
                project_dir=str(tmp_path),
                version="1.0.0",
            )

    def test_project_dir_resolves_relative_path(self, tmp_path):
        """Test that relative project paths are resolved."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=".",
            version="1.0.0",
        )

        assert builder.project_dir.is_absolute()


class TestDockerImageBuilderBuild:
    """Tests for image building functionality."""

    def test_build_image_success(self, tmp_path):
        """Test successful image build."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.2.3",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Build successful")

            result = builder.build_image(
                dockerfile="Dockerfile",
                image_name="code-scalpel",
            )

            assert result["image_name"] == "docker.io/code-scalpel"
            assert result["version_tag"] == "docker.io/code-scalpel:1.2.3"
            assert result["latest_tag"] == "docker.io/code-scalpel:latest"
            assert result["build_output"] == "Build successful"

            # Verify docker build command was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "docker" in call_args
            assert "build" in call_args

    def test_build_image_custom_dockerfile(self, tmp_path):
        """Test building with custom Dockerfile."""
        (tmp_path / "Dockerfile").touch()
        (tmp_path / "Dockerfile.rest").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")

            result = builder.build_image(
                dockerfile="Dockerfile.rest",
                image_name="code-scalpel-rest",
            )

            assert result["image_name"] == "docker.io/code-scalpel-rest"

    def test_build_image_failure_raises_error(self, tmp_path):
        """Test that build failure raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stderr="Build failed",
                stdout="",
            )

            with pytest.raises(RuntimeError, match="Docker build failed"):
                builder.build_image()

    def test_build_image_not_found_raises_error(self, tmp_path):
        """Test that missing Dockerfile raises FileNotFoundError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with pytest.raises(FileNotFoundError):
            builder.build_image(dockerfile="NonExistent.dockerfile")

    def test_build_image_docker_not_installed_raises_error(self, tmp_path):
        """Test that missing Docker raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="Docker is not installed"):
                builder.build_image()

    def test_build_image_dry_run(self, tmp_path):
        """Test dry-run mode doesn't execute commands."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            with patch("builtins.print"):
                result = builder.build_image(dry_run=True)

            assert result["build_output"] == ""
            mock_run.assert_not_called()


class TestDockerImageBuilderAuthentication:
    """Tests for Docker registry authentication."""

    def test_authenticate_success(self, tmp_path):
        """Test successful authentication."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
            username="testuser",
            password_or_token="testtoken",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = builder.authenticate()

            assert result is True
            mock_run.assert_called_once()

    def test_authenticate_missing_credentials_raises_error(self, tmp_path):
        """Test that missing credentials raises ValueError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with pytest.raises(ValueError, match="Username and password"):
            builder.authenticate()

    def test_authenticate_failure_raises_error(self, tmp_path):
        """Test that authentication failure raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
            username="testuser",
            password_or_token="badtoken",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stderr="Authentication failed",
                stdout="",
            )

            with pytest.raises(RuntimeError, match="Authentication failed"):
                builder.authenticate()

    def test_authenticate_docker_not_installed_raises_error(self, tmp_path):
        """Test that missing Docker raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
            username="testuser",
            password_or_token="testtoken",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="Docker is not installed"):
                builder.authenticate()

    def test_authenticate_dry_run(self, tmp_path):
        """Test dry-run mode doesn't execute commands."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
            username="testuser",
            password_or_token="testtoken",
        )

        with patch("subprocess.run") as mock_run:
            with patch("builtins.print"):
                result = builder.authenticate(dry_run=True)

            assert result is True
            mock_run.assert_not_called()


class TestDockerImageBuilderPush:
    """Tests for image pushing functionality."""

    def test_push_image_success(self, tmp_path):
        """Test successful image push."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Push successful")

            result = builder.push_image("docker.io/code-scalpel:1.0.0")

            assert result["image_tag"] == "docker.io/code-scalpel:1.0.0"
            assert result["push_output"] == "Push successful"

    def test_push_image_failure_raises_error(self, tmp_path):
        """Test that push failure raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stderr="Push failed",
                stdout="",
            )

            with pytest.raises(RuntimeError, match="Docker push failed"):
                builder.push_image("docker.io/code-scalpel:1.0.0")

    def test_push_image_docker_not_installed_raises_error(self, tmp_path):
        """Test that missing Docker raises RuntimeError."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            with pytest.raises(RuntimeError, match="Docker is not installed"):
                builder.push_image("docker.io/code-scalpel:1.0.0")

    def test_push_image_dry_run(self, tmp_path):
        """Test dry-run mode doesn't execute commands."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch("subprocess.run") as mock_run:
            with patch("builtins.print"):
                result = builder.push_image(
                    "docker.io/code-scalpel:1.0.0", dry_run=True
                )

            assert result["push_output"] == ""
            mock_run.assert_not_called()


class TestDockerImageBuilderPublish:
    """Tests for complete release publishing."""

    def test_publish_release_build_only(self, tmp_path):
        """Test publishing with build only (skip push)."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.2.3",
        )

        with patch.object(builder, "build_image") as mock_build:
            mock_build.return_value = {
                "image_name": "docker.io/code-scalpel",
                "version_tag": "docker.io/code-scalpel:1.2.3",
                "latest_tag": "docker.io/code-scalpel:latest",
                "build_output": "",
            }

            with patch("builtins.print"):
                result = builder.publish_release(skip_push=True)

            assert result["version"] == "1.2.3"
            assert len(result["images_built"]) == 1
            assert len(result["images_pushed"]) == 0

    def test_publish_release_with_rest_api_image(self, tmp_path):
        """Test publishing with both main and REST API images."""
        (tmp_path / "Dockerfile").touch()
        (tmp_path / "Dockerfile.rest").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch.object(builder, "build_image") as mock_build:
            mock_build.return_value = {
                "image_name": "docker.io/image",
                "version_tag": "docker.io/image:1.0.0",
                "latest_tag": "docker.io/image:latest",
                "build_output": "",
            }

            with patch("builtins.print"):
                result = builder.publish_release(skip_push=True)

            # Should call build_image twice (main + rest)
            assert mock_build.call_count == 2
            assert len(result["images_built"]) == 2

    def test_publish_release_with_push(self, tmp_path):
        """Test publishing with push to registry."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
            username="testuser",
            password_or_token="testtoken",
        )

        with patch.object(builder, "build_image") as mock_build:
            mock_build.return_value = {
                "image_name": "docker.io/code-scalpel",
                "version_tag": "docker.io/code-scalpel:1.0.0",
                "latest_tag": "docker.io/code-scalpel:latest",
                "build_output": "",
            }

            with patch.object(builder, "authenticate") as mock_auth:
                with patch.object(builder, "push_image") as mock_push:
                    with patch("builtins.print"):
                        builder.publish_release(skip_push=False)

                    assert mock_auth.called
                    # Should push version tag and latest tag
                    assert mock_push.call_count >= 2

    def test_publish_release_dry_run(self, tmp_path):
        """Test dry-run mode."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        with patch.object(builder, "build_image") as mock_build:
            mock_build.return_value = {
                "image_name": "docker.io/code-scalpel",
                "version_tag": "docker.io/code-scalpel:1.0.0",
                "latest_tag": "docker.io/code-scalpel:latest",
                "build_output": "",
            }

            with patch("builtins.print"):
                result = builder.publish_release(dry_run=True)

            assert result["version"] == "1.0.0"


class TestDockerImageBuilderStatus:
    """Tests for build status functionality."""

    def test_get_build_status(self, tmp_path):
        """Test getting build status."""
        (tmp_path / "Dockerfile").touch()
        (tmp_path / "Dockerfile.rest").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.2.3",
            registry="ghcr.io",
        )

        status = builder.get_build_status()

        assert status["version"] == "1.2.3"
        assert str(tmp_path) in status["project_dir"]
        assert status["registry"] == "ghcr.io"
        assert status["has_dockerfile"] == "True"
        assert status["has_rest_dockerfile"] == "True"

    def test_get_build_status_no_rest_dockerfile(self, tmp_path):
        """Test build status without REST Dockerfile."""
        (tmp_path / "Dockerfile").touch()

        builder = DockerImageBuilder(
            project_dir=str(tmp_path),
            version="1.0.0",
        )

        status = builder.get_build_status()

        assert status["has_dockerfile"] == "True"
        assert status["has_rest_dockerfile"] == "False"
