"""Tests for GitHub release automation."""

from __future__ import annotations

import os
from unittest.mock import Mock, patch

import pytest

from code_scalpel.release.github_releases import GitHubReleaseManager


class TestGitHubReleaseManagerInit:
    """Test GitHubReleaseManager initialization."""

    def test_init_with_token_and_repo_url(self):
        """Test initialization with explicit token and repo URL."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )
            assert manager.token == "test_token"
            assert manager.repo_url == "owner/repo"

    def test_init_with_env_token(self):
        """Test initialization with token from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            with patch("code_scalpel.release.github_releases.Github"):
                manager = GitHubReleaseManager(repo_url="owner/repo")
                assert manager.token == "env_token"

    def test_init_missing_token_raises_error(self):
        """Test that missing token raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("code_scalpel.release.github_releases.Github"):
                with pytest.raises(ValueError, match="GitHub token required"):
                    GitHubReleaseManager(repo_url="owner/repo")

    def test_init_missing_pygithub_raises_error(self):
        """Test that missing PyGithub raises ImportError."""
        with patch("code_scalpel.release.github_releases.Github", None):
            with pytest.raises(ImportError, match="PyGithub is required"):
                GitHubReleaseManager(token="test_token", repo_url="owner/repo")

    def test_init_with_git_origin(self):
        """Test initialization detects repo from git origin."""
        with patch(
            "code_scalpel.release.github_releases.GitHubReleaseManager._get_origin_repo_url",
            return_value="https://github.com/owner/repo.git",
        ):
            with patch("code_scalpel.release.github_releases.Github"):
                manager = GitHubReleaseManager(token="test_token")
                assert manager.repo_url == "owner/repo"

    def test_normalize_repo_url_owner_repo_format(self):
        """Test normalizing owner/repo format."""
        result = GitHubReleaseManager._normalize_repo_url("owner/repo")
        assert result == "owner/repo"

    def test_normalize_repo_url_https_format(self):
        """Test normalizing HTTPS URL."""
        result = GitHubReleaseManager._normalize_repo_url(
            "https://github.com/owner/repo"
        )
        assert result == "owner/repo"

    def test_normalize_repo_url_https_with_git_suffix(self):
        """Test normalizing HTTPS URL with .git suffix."""
        result = GitHubReleaseManager._normalize_repo_url(
            "https://github.com/owner/repo.git"
        )
        assert result == "owner/repo"

    def test_normalize_repo_url_ssh_format(self):
        """Test normalizing SSH URL."""
        result = GitHubReleaseManager._normalize_repo_url(
            "git@github.com:owner/repo.git"
        )
        assert result == "owner/repo"

    def test_get_origin_repo_url_success(self):
        """Test successful retrieval of git origin URL."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="https://github.com/owner/repo.git\n",
            )
            result = GitHubReleaseManager._get_origin_repo_url()
            assert result == "https://github.com/owner/repo.git"

    def test_get_origin_repo_url_git_not_found(self):
        """Test handling when git origin is not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout="")
            result = GitHubReleaseManager._get_origin_repo_url()
            assert result is None


class TestGitHubReleaseManagerAuth:
    """Test GitHub authentication verification."""

    def test_verify_auth_success(self):
        """Test successful authentication verification."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the GitHub user
            mock_user = Mock()
            mock_user.login = "testuser"
            mock_user.name = "Test User"
            mock_user.type = "User"
            manager.github.get_user.return_value = mock_user

            result = manager.verify_auth()
            assert result["login"] == "testuser"
            assert result["name"] == "Test User"
            assert result["type"] == "User"

    def test_verify_auth_no_name(self):
        """Test authentication with user that has no name."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the GitHub user without name
            mock_user = Mock()
            mock_user.login = "testuser"
            mock_user.name = None
            mock_user.type = "User"
            manager.github.get_user.return_value = mock_user

            result = manager.verify_auth()
            assert result["login"] == "testuser"
            assert result["name"] == "testuser"

    def test_verify_auth_failure(self):
        """Test authentication failure."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="invalid_token",
                repo_url="owner/repo",
            )

            # Mock github.get_user to raise an exception
            manager.github.get_user.side_effect = RuntimeError("Bad credentials")

            with pytest.raises(RuntimeError, match="Bad credentials"):
                manager.verify_auth()


class TestGitHubReleaseManagerCreateRelease:
    """Test creating GitHub releases."""

    def test_create_release_success(self):
        """Test successful release creation."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the release
            mock_release = Mock()
            mock_release.html_url = "https://github.com/owner/repo/releases/v1.0.0"
            mock_release.id = 12345
            mock_release.tag_name = "v1.0.0"
            mock_release.title = "Release 1.0.0"
            mock_release.upload_url = "https://uploads.github.com/repos/owner/repo/releases/12345/assets{?name,label}"

            manager.repo.create_git_release.return_value = mock_release

            result = manager.create_release(
                tag="v1.0.0",
                title="Release 1.0.0",
                body="## Changelog\n- Feature 1",
            )

            assert result["tag"] == "v1.0.0"
            assert result["title"] == "Release 1.0.0"
            assert "v1.0.0" in result["url"]
            assert result["id"] == "12345"

    def test_create_release_with_draft(self):
        """Test creating a draft release."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            mock_release = Mock()
            mock_release.html_url = "https://github.com/owner/repo/releases/v1.0.0"
            mock_release.id = 12345
            mock_release.tag_name = "v1.0.0"
            mock_release.title = "Release 1.0.0"
            mock_release.upload_url = (
                "https://uploads.github.com/repos/owner/repo/releases/12345/assets"
            )

            manager.repo.create_git_release.return_value = mock_release

            manager.create_release(
                tag="v1.0.0",
                title="Release 1.0.0",
                body="Test",
                draft=True,
            )

            # Verify draft parameter was passed
            manager.repo.create_git_release.assert_called_once()
            call_kwargs = manager.repo.create_git_release.call_args[1]
            assert call_kwargs["draft"] is True

    def test_create_release_with_prerelease(self):
        """Test creating a prerelease."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            mock_release = Mock()
            mock_release.html_url = "https://github.com/owner/repo/releases/v1.0.0-beta"
            mock_release.id = 12346
            mock_release.tag_name = "v1.0.0-beta"
            mock_release.title = "Release 1.0.0-beta"
            mock_release.upload_url = (
                "https://uploads.github.com/repos/owner/repo/releases/12346/assets"
            )

            manager.repo.create_git_release.return_value = mock_release

            manager.create_release(
                tag="v1.0.0-beta",
                title="Release 1.0.0-beta",
                body="Beta release",
                prerelease=True,
            )

            # Verify prerelease parameter was passed
            call_kwargs = manager.repo.create_git_release.call_args[1]
            assert call_kwargs["prerelease"] is True


class TestGitHubReleaseManagerAssets:
    """Test uploading assets to releases."""

    def test_upload_asset_success(self):
        """Test successful asset upload."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Create a temporary file
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".whl") as f:
                f.write(b"wheel content")
                temp_file = f.name

            try:
                # Mock the release and asset
                mock_release = Mock()
                mock_asset = Mock()
                mock_asset.name = "package-1.0.0-py3-none-any.whl"
                mock_asset.browser_download_url = "https://github.com/owner/repo/releases/download/v1.0.0/package-1.0.0-py3-none-any.whl"
                mock_asset.size = 1024

                mock_release.upload_asset.return_value = mock_asset
                manager.repo.get_release.return_value = mock_release

                result = manager.upload_asset("v1.0.0", temp_file)

                assert result["name"] == "package-1.0.0-py3-none-any.whl"
                assert result["size"] == "1024"
                assert "download" in result["url"]
            finally:
                os.unlink(temp_file)

    def test_upload_asset_file_not_found(self):
        """Test uploading non-existent file."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            with pytest.raises(FileNotFoundError, match="Asset file not found"):
                manager.upload_asset("v1.0.0", "/nonexistent/file.whl")

    def test_upload_multiple_assets(self):
        """Test uploading multiple assets."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            import tempfile

            # Create temporary files
            temp_files = []
            for i in range(2):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i}.whl") as f:
                    f.write(b"wheel content")
                    temp_files.append(f.name)

            try:
                # Mock release and assets
                mock_release = Mock()
                mock_asset = Mock()
                mock_asset.name = "package.whl"
                mock_asset.browser_download_url = "https://example.com/download"
                mock_asset.size = 1024

                mock_release.upload_asset.return_value = mock_asset
                manager.repo.get_release.return_value = mock_release

                result = manager.upload_assets("v1.0.0", temp_files)

                assert len(result) == 2
                assert all("name" in r for r in result)
            finally:
                for f in temp_files:
                    os.unlink(f)


class TestGitHubReleaseManagerPublish:
    """Test publishing releases."""

    def test_publish_release_success(self):
        """Test successful release publication."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the release
            mock_release = Mock()
            mock_updated = Mock()
            mock_updated.tag_name = "v1.0.0"
            mock_updated.title = "Release 1.0.0"
            mock_updated.html_url = "https://github.com/owner/repo/releases/v1.0.0"
            mock_updated.draft = False

            mock_release.edit.return_value = mock_updated
            manager.repo.get_release.return_value = mock_release

            result = manager.publish_release("v1.0.0")

            assert result["tag"] == "v1.0.0"
            assert result["draft"] == "False"
            mock_release.edit.assert_called_once_with(draft=False)


class TestGitHubReleaseManagerGetRelease:
    """Test getting release information."""

    def test_get_release_success(self):
        """Test getting release information."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the release
            mock_release = Mock()
            mock_release.tag_name = "v1.0.0"
            mock_release.title = "Release 1.0.0"
            mock_release.html_url = "https://github.com/owner/repo/releases/v1.0.0"
            mock_release.draft = False
            mock_release.prerelease = False
            mock_release.created_at = "2023-01-01T00:00:00Z"
            mock_release.get_assets.return_value = [Mock(), Mock()]

            manager.repo.get_release.return_value = mock_release

            result = manager.get_release("v1.0.0")

            assert result["tag"] == "v1.0.0"
            assert result["draft"] == "False"
            assert result["prerelease"] == "False"
            assert result["assets_count"] == "2"


class TestGitHubReleaseManagerDelete:
    """Test deleting releases."""

    def test_delete_release_success(self):
        """Test successful release deletion."""
        with patch("code_scalpel.release.github_releases.Github"):
            manager = GitHubReleaseManager(
                token="test_token",
                repo_url="owner/repo",
            )

            # Mock the release
            mock_release = Mock()
            manager.repo.get_release.return_value = mock_release

            result = manager.delete_release("v1.0.0")

            assert result is True
            mock_release.delete.assert_called_once()
