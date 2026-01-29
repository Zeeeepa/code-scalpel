"""Git history analyzer for release automation.

Provides utilities to query commit history, find last release tags,
and extract commits between versions.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitTag:
    """Represents a git tag."""

    name: str  # Full tag name (e.g., "v1.2.3")
    commit: str  # Commit hash
    message: Optional[str] = None  # Tag message if annotated

    @property
    def version(self) -> str:
        """Extract version from tag name.

        Assumes tag follows vX.Y.Z format.
        """
        if self.name.startswith("v"):
            return self.name[1:]
        return self.name


class GitHistoryAnalyzer:
    """Analyzes git history for release automation."""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path

    def get_latest_tag(self, pattern: str = "v*") -> Optional[GitTag]:
        """Get the latest git tag matching pattern.

        Args:
            pattern: Tag pattern (e.g., "v*")

        Returns:
            Latest matching tag, or None if no tags found
        """
        try:
            # Get latest tag matching pattern
            result = subprocess.run(
                ["git", "-C", self.repo_path, "describe", "--tags", "--match", pattern],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return None

            tag_name = result.stdout.strip().split("-")[0]  # Handle "v1.0.0-5-gabcdef" format

            # Get commit hash for tag
            commit_result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-list", "-n", "1", tag_name],
                capture_output=True,
                text=True,
                check=False,
            )

            if commit_result.returncode != 0:
                return None

            commit = commit_result.stdout.strip()
            return GitTag(name=tag_name, commit=commit)

        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    def get_commits_since_tag(self, tag: Optional[str] = None, **kwargs) -> list[str]:
        """Get commit messages since a tag.

        Args:
            tag: Tag to start from (None = from all commits)
            **kwargs: Additional git log arguments

        Returns:
            List of commit messages
        """
        if tag:
            range_spec = f"{tag}..HEAD"
        else:
            range_spec = "HEAD"

        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    self.repo_path,
                    "log",
                    range_spec,
                    "--oneline",
                    "--pretty=format:%B",
                    "--reverse",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return []

            # Split by commit boundaries (oneline output shows "hash message")
            # But we want full messages, so use the %B format
            lines = result.stdout.strip().split("\n\n")
            return [commit.strip() for commit in lines if commit.strip()]

        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def get_all_commits(self) -> list[str]:
        """Get all commits in repository.

        Returns:
            List of commit messages
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    self.repo_path,
                    "log",
                    "--pretty=format:%B",
                    "--reverse",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return []

            lines = result.stdout.strip().split("\n\n")
            return [commit.strip() for commit in lines if commit.strip()]

        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def get_commit_count(self, since_tag: Optional[str] = None) -> int:
        """Get commit count since tag.

        Args:
            since_tag: Tag to count from (None = all commits)

        Returns:
            Number of commits
        """
        commits = self.get_commits_since_tag(since_tag)
        return len(commits)

    def get_current_branch(self) -> Optional[str]:
        """Get current branch name.

        Returns:
            Branch name or None if detached
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return None

            branch = result.stdout.strip()
            if branch == "HEAD":
                return None  # Detached head
            return branch

        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    def get_current_commit(self) -> Optional[str]:
        """Get current commit hash.

        Returns:
            Short commit hash or None
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return None

            return result.stdout.strip()

        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    def is_dirty(self) -> bool:
        """Check if working directory has uncommitted changes.

        Returns:
            True if dirty, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=False,
            )

            return bool(result.stdout.strip())

        except (subprocess.SubprocessError, FileNotFoundError):
            return True  # Assume dirty if we can't check

    def tag_exists(self, tag: str) -> bool:
        """Check if tag exists.

        Args:
            tag: Tag name

        Returns:
            True if tag exists
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", tag],
                capture_output=True,
                check=False,
            )

            return result.returncode == 0

        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def create_tag(self, tag: str, message: str = "") -> bool:
        """Create an annotated tag.

        Args:
            tag: Tag name
            message: Tag message (empty = lightweight tag)

        Returns:
            True if successful
        """
        try:
            if message:
                subprocess.run(
                    ["git", "-C", self.repo_path, "tag", "-a", tag, "-m", message],
                    check=True,
                )
            else:
                subprocess.run(
                    ["git", "-C", self.repo_path, "tag", tag],
                    check=True,
                )
            return True

        except (subprocess.SubprocessError, FileNotFoundError):
            return False
