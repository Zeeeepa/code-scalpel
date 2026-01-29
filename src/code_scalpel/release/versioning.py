"""Semantic versioning with conventional commits support.

Analyzes commit history to determine version bumps following
semantic versioning (major.minor.patch) based on conventional commit types.

Conventional Commit Format:
- feat: New feature (minor bump)
- fix: Bug fix (patch bump)
- feat!: Breaking change (major bump)
- fix!: Breaking change (major bump)
- BREAKING CHANGE: footer indicates breaking change (major bump)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConventionalCommit:
    """Parsed conventional commit."""

    type: str  # feat, fix, docs, style, refactor, perf, test, chore, ci
    scope: Optional[str]  # Optional scope in parentheses
    description: str
    body: Optional[str]
    footer: Optional[str]
    breaking: bool  # Has ! suffix or BREAKING CHANGE footer
    message: str  # Full message

    @classmethod
    def parse(cls, message: str) -> Optional[ConventionalCommit]:
        """Parse a commit message into ConventionalCommit.

        Args:
            message: Full commit message (subject + body + footer)

        Returns:
            ConventionalCommit if valid conventional commit, None otherwise
        """
        lines = message.split("\n")
        subject = lines[0]

        # Pattern: type(scope)!: description or type!: description
        # or: type(scope): description or type: description
        pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci)(\(.+?\))?(!)?:\s*(.+)$"
        match = re.match(pattern, subject)

        if not match:
            return None

        commit_type = match.group(1)
        scope = match.group(2)
        if scope:
            scope = scope[1:-1]  # Remove parentheses
        breaking = match.group(3) == "!"
        description = match.group(4)

        # Get body and footer
        body = None
        footer = None
        if len(lines) > 2:
            body = "\n".join(lines[1:-1]).strip() if len(lines) > 2 else None
            footer = lines[-1] if lines[-1].startswith(("BREAKING CHANGE:", "Closes #")) else None

        # Check for BREAKING CHANGE footer
        if footer and footer.startswith("BREAKING CHANGE:"):
            breaking = True

        return cls(
            type=commit_type,
            scope=scope,
            description=description,
            body=body,
            footer=footer,
            breaking=breaking,
            message=message,
        )

    def is_breaking(self) -> bool:
        """Check if this is a breaking change."""
        return self.breaking or (self.type == "feat" and self.breaking)

    def is_feature(self) -> bool:
        """Check if this is a feature commit."""
        return self.type == "feat"

    def is_fix(self) -> bool:
        """Check if this is a bug fix commit."""
        return self.type == "fix"


@dataclass
class VersionBump:
    """Represents a version bump."""

    major: int
    minor: int
    patch: int
    current: str

    @property
    def new_version(self) -> str:
        """Get the new version string."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def bump_type(self) -> str:
        """Get the type of bump (MAJOR, MINOR, PATCH)."""
        # Parse current version
        parts = self.current.split(".")
        current_major = int(parts[0])
        current_minor = int(parts[1])
        current_patch = int(parts[2])

        if self.major > current_major:
            return "MAJOR"
        elif self.minor > current_minor:
            return "MINOR"
        elif self.patch > current_patch:
            return "PATCH"
        else:
            return "NONE"


class SemanticVersioner:
    """Manages semantic versioning based on conventional commits."""

    def __init__(self, current_version: str):
        """Initialize with current version.

        Args:
            current_version: Current version string (e.g., "1.2.3")
        """
        self.current_version = current_version
        parts = current_version.split(".")
        self.major = int(parts[0])
        self.minor = int(parts[1])
        self.patch = int(parts[2])

    def analyze_commits(self, commits: list[str]) -> VersionBump:
        """Analyze commits to determine version bump.

        Args:
            commits: List of commit messages

        Returns:
            VersionBump with new version

        Rules:
        - BREAKING CHANGE (! or footer) -> major bump
        - feat: -> minor bump
        - fix: -> patch bump
        - Other (docs, style, etc.) -> no bump
        """
        has_breaking = False
        has_feature = False
        has_fix = False

        for message in commits:
            commit = ConventionalCommit.parse(message)
            if not commit:
                continue

            if commit.is_breaking():
                has_breaking = True
            elif commit.is_feature():
                has_feature = True
            elif commit.is_fix():
                has_fix = True

        # Determine bump
        new_major = self.major
        new_minor = self.minor
        new_patch = self.patch

        if has_breaking:
            new_major += 1
            new_minor = 0
            new_patch = 0
        elif has_feature:
            new_minor += 1
            new_patch = 0
        elif has_fix:
            new_patch += 1

        return VersionBump(
            major=new_major,
            minor=new_minor,
            patch=new_patch,
            current=self.current_version,
        )

    def classify_commits(self, commits: list[str]) -> dict[str, list[ConventionalCommit]]:
        """Classify commits by type.

        Args:
            commits: List of commit messages

        Returns:
            Dict mapping type to list of commits
        """
        classified: dict[str, list[ConventionalCommit]] = {
            "breaking": [],
            "features": [],
            "fixes": [],
            "other": [],
        }

        for message in commits:
            commit = ConventionalCommit.parse(message)
            if not commit:
                continue

            if commit.is_breaking():
                classified["breaking"].append(commit)
            elif commit.is_feature():
                classified["features"].append(commit)
            elif commit.is_fix():
                classified["fixes"].append(commit)
            else:
                classified["other"].append(commit)

        return classified
