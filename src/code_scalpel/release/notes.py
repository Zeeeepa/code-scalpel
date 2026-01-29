"""Release notes generator from commit history.

Generates structured release notes from conventional commits,
organized by category (breaking changes, features, fixes, etc.).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from code_scalpel.release.versioning import ConventionalCommit


class ReleaseNotesGenerator:
    """Generates release notes from commits."""

    def __init__(self, version: str, date: Optional[str] = None):
        """Initialize generator.

        Args:
            version: Version string (e.g., "1.3.0")
            date: Release date (format: YYYY-MM-DD). Defaults to today.
        """
        self.version = version
        self.date = date or datetime.now().strftime("%Y-%m-%d")

    def generate(
        self,
        commits: list[str],
        sections: Optional[dict[str, str]] = None,
    ) -> str:
        """Generate release notes from commits.

        Args:
            commits: List of commit messages
            sections: Optional dict mapping categories to display names

        Returns:
            Formatted release notes markdown
        """
        if sections is None:
            sections = {
                "breaking": "🚨 BREAKING CHANGES",
                "features": "✨ Features",
                "fixes": "🐛 Bug Fixes",
                "other": "📝 Other Changes",
            }

        # Parse and classify commits
        breaking_commits = []
        feature_commits = []
        fix_commits = []
        other_commits = []

        for message in commits:
            commit = ConventionalCommit.parse(message)
            if not commit:
                continue

            if commit.is_breaking():
                breaking_commits.append(commit)
            elif commit.is_feature():
                feature_commits.append(commit)
            elif commit.is_fix():
                fix_commits.append(commit)
            else:
                other_commits.append(commit)

        # Build markdown
        lines = [f"## [{self.version}] - {self.date}\n"]

        # Breaking changes
        if breaking_commits:
            lines.append(f"\n### {sections['breaking']}\n")
            for commit in breaking_commits:
                lines.append(self._format_commit(commit, highlight=True))

        # Features
        if feature_commits:
            lines.append(f"\n### {sections['features']}\n")
            for commit in feature_commits:
                lines.append(self._format_commit(commit))

        # Fixes
        if fix_commits:
            lines.append(f"\n### {sections['fixes']}\n")
            for commit in fix_commits:
                lines.append(self._format_commit(commit))

        # Other
        if other_commits:
            lines.append(f"\n### {sections['other']}\n")
            for commit in other_commits:
                lines.append(self._format_commit(commit))

        return "".join(lines)

    def _format_commit(self, commit: ConventionalCommit, highlight: bool = False) -> str:
        """Format a single commit for release notes.

        Args:
            commit: Parsed commit
            highlight: Whether to highlight (e.g., breaking changes)

        Returns:
            Formatted commit line
        """
        prefix = "- **"
        if highlight:
            prefix = "- **⚠️ "

        scope_str = f"({commit.scope})" if commit.scope else ""
        breaking_str = " ⚠️ BREAKING" if commit.is_breaking() else ""

        return f"{prefix}{commit.type.upper()}{scope_str}**: {commit.description}{breaking_str}\n"


class ChangelogManager:
    """Manages CHANGELOG.md file."""

    UNRELEASED_HEADER = "## [Unreleased]\n"

    def __init__(self, filepath: str = "CHANGELOG.md"):
        """Initialize manager.

        Args:
            filepath: Path to CHANGELOG.md file
        """
        self.filepath = filepath

    def read(self) -> str:
        """Read changelog content."""
        try:
            with open(self.filepath, "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._default_changelog()

    def write(self, content: str) -> None:
        """Write changelog content."""
        with open(self.filepath, "w") as f:
            f.write(content)

    def insert_release(self, release_notes: str, keep_unreleased: bool = True) -> None:
        """Insert release notes into changelog.

        Args:
            release_notes: Formatted release notes markdown
            keep_unreleased: Whether to keep Unreleased section
        """
        content = self.read()

        # Find where to insert (after Unreleased section if present)
        if self.UNRELEASED_HEADER in content:
            insert_pos = content.find(self.UNRELEASED_HEADER) + len(self.UNRELEASED_HEADER)
            if not keep_unreleased:
                # Remove Unreleased section
                next_version_pos = content.find("## [", insert_pos)
                if next_version_pos > 0:
                    insert_pos = next_version_pos
                else:
                    insert_pos = len(content)
        else:
            # Find first version entry
            insert_pos = content.find("## [")
            if insert_pos < 0:
                insert_pos = len(content)

        # Insert release notes
        new_content = content[:insert_pos] + release_notes + "\n" + content[insert_pos:]

        self.write(new_content)

    def _default_changelog(self) -> str:
        """Generate default changelog template."""
        return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
