"""GitHub release automation - Create and manage releases on GitHub.

Handles:
- Creating GitHub releases with release notes
- Uploading release assets (wheels, source distributions)
- Publishing releases
- Verifying GitHub authentication
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

try:
    from github import Github, GithubException, Repository
except ImportError:
    Github = None  # type: ignore
    GithubException = None  # type: ignore
    Repository = None  # type: ignore


class GitHubReleaseManager:
    """Manages GitHub releases via GitHub API."""

    def __init__(self, token: Optional[str] = None, repo_url: Optional[str] = None):
        """Initialize GitHub release manager.

        Args:
            token: GitHub personal access token. Defaults to GITHUB_TOKEN env var.
            repo_url: Repository URL (e.g., "owner/repo" or full HTTPS URL).
                     Defaults to origin remote in current git repo.

        Raises:
            ImportError: If PyGithub is not installed
            ValueError: If token is not provided and GITHUB_TOKEN env var not set
            ValueError: If repo_url cannot be determined
        """
        if Github is None:
            raise ImportError(
                "PyGithub is required for GitHub release automation. " "Install with: pip install PyGithub"
            )

        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token required. Pass 'token' argument or set GITHUB_TOKEN " "environment variable."
            )

        self.repo_url = repo_url or self._get_origin_repo_url()
        if not self.repo_url:
            raise ValueError("Repository URL required. Pass 'repo_url' argument or ensure " "git origin remote is set.")

        # Normalize repo URL to owner/repo format
        self.repo_url = self._normalize_repo_url(self.repo_url)

        self.github = Github(self.token)
        self.repo: Any = self.github.get_repo(self.repo_url)

    @staticmethod
    def _normalize_repo_url(url: str) -> str:
        """Normalize repository URL to owner/repo format.

        Args:
            url: Repository URL (can be HTTPS, SSH, or owner/repo format)

        Returns:
            Normalized URL in format "owner/repo"
        """
        # SSH format: git@github.com:owner/repo.git
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "").replace(".git", "")
            return url

        # HTTPS format: https://github.com/owner/repo or https://github.com/owner/repo.git
        if url.startswith("https://github.com/"):
            url = url.replace("https://github.com/", "").replace(".git", "")
            return url

        # Already in owner/repo format or other format
        return url.replace(".git", "")

    @staticmethod
    def _get_origin_repo_url() -> Optional[str]:
        """Get repository URL from git origin remote.

        Returns:
            Repository URL or None if not found
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def verify_auth(self) -> dict[str, str]:
        """Verify GitHub authentication.

        Returns:
            Dict with auth information (login, name, etc.)

        Raises:
            RuntimeError: If authentication fails
        """
        try:
            user = self.github.get_user()
            return {
                "login": user.login,
                "name": user.name or user.login,
                "type": user.type,
            }
        except Exception as e:
            raise RuntimeError(f"GitHub authentication failed: {str(e)}") from e

    def create_release(
        self,
        tag: str,
        title: str,
        body: str,
        draft: bool = False,
        prerelease: bool = False,
    ) -> dict[str, str]:
        """Create a GitHub release.

        Args:
            tag: Git tag name (e.g., "v1.2.3")
            title: Release title/name
            body: Release notes (markdown)
            draft: If True, create as draft release
            prerelease: If True, mark as prerelease

        Returns:
            Dict with release information:
            - url: Release URL
            - id: Release ID
            - tag: Tag name
            - title: Release title
            - assets_url: URL for uploading assets

        Raises:
            GithubException: If release creation fails
        """
        try:
            release = self.repo.create_git_release(
                tag=tag,
                name=title,
                message=body,
                draft=draft,
                prerelease=prerelease,
            )

            return {
                "url": release.html_url,
                "id": str(release.id),
                "tag": release.tag_name,
                "title": release.title or tag,
                "assets_url": release.upload_url,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create GitHub release: {str(e)}") from e

    def upload_asset(self, release_tag: str, file_path: str | Path) -> dict[str, str]:
        """Upload an asset to a release.

        Args:
            release_tag: Git tag name of the release
            file_path: Path to file to upload

        Returns:
            Dict with asset information:
            - name: Asset filename
            - url: Asset download URL
            - size: File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If upload fails
        """
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Asset file not found: {path_obj}")

        try:
            # Get the release by tag
            release = self.repo.get_release(release_tag)

            # Upload the asset
            asset = release.upload_asset(
                name=path_obj.name,
                asset_type="application/octet-stream",
            )

            return {
                "name": asset.name,
                "url": asset.browser_download_url,
                "size": str(asset.size),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to upload asset: {str(e)}") from e

    def upload_assets(self, release_tag: str, asset_paths: list[str]) -> list[dict[str, str]]:
        """Upload multiple assets to a release.

        Args:
            release_tag: Git tag name of the release
            asset_paths: List of paths to files to upload

        Returns:
            List of dicts with asset information for each uploaded file
        """
        results = []
        for asset_path in asset_paths:
            try:
                result = self.upload_asset(release_tag, asset_path)
                results.append(result)
            except (FileNotFoundError, RuntimeError) as e:
                results.append(
                    {
                        "name": Path(asset_path).name,
                        "error": str(e),
                    }
                )
        return results

    def publish_release(self, release_tag: str) -> dict[str, str]:
        """Publish a draft release (make it public).

        Args:
            release_tag: Git tag name of the release

        Returns:
            Dict with updated release information

        Raises:
            RuntimeError: If publish fails
        """
        try:
            release = self.repo.get_release(release_tag)
            updated = release.edit(draft=False)

            return {
                "tag": updated.tag_name,
                "title": updated.title or release_tag,
                "url": updated.html_url,
                "draft": str(updated.draft),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to publish release: {str(e)}") from e

    def get_release(self, release_tag: str) -> dict[str, str]:
        """Get information about a release.

        Args:
            release_tag: Git tag name of the release

        Returns:
            Dict with release information

        Raises:
            RuntimeError: If release not found
        """
        try:
            release = self.repo.get_release(release_tag)

            return {
                "tag": release.tag_name,
                "title": release.title or release_tag,
                "url": release.html_url,
                "draft": str(release.draft),
                "prerelease": str(release.prerelease),
                "created_at": str(release.created_at),
                "assets_count": str(len(release.get_assets())),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get release: {str(e)}") from e

    def delete_release(self, release_tag: str) -> bool:
        """Delete a release.

        Args:
            release_tag: Git tag name of the release

        Returns:
            True if successfully deleted

        Raises:
            RuntimeError: If deletion fails
        """
        try:
            release = self.repo.get_release(release_tag)
            release.delete()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete release: {str(e)}") from e
