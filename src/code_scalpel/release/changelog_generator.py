"""Automated changelog generation with template support.

Provides comprehensive changelog generation from commit history with support for:
- Multiple output formats (Markdown, HTML, JSON)
- Template-based customization
- Categorization of changes (Features, Fixes, Breaking Changes, etc.)
- Section organization and filtering
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class ChangeType(str, Enum):
    """Types of changes in changelog."""

    FEATURE = "Features"
    FIX = "Fixes"
    BREAKING = "Breaking Changes"
    SECURITY = "Security"
    DEPRECATION = "Deprecations"
    PERFORMANCE = "Performance"
    DOCUMENTATION = "Documentation"
    REFACTOR = "Refactoring"
    OTHER = "Other"


class ChangelogFormat(str, Enum):
    """Supported changelog output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


@dataclass
class ChangeEntry:
    """Represents a single change entry.

    Attributes:
        message: The change message
        type: Type of change (feature, fix, breaking, etc.)
        commit_hash: Associated git commit hash
        author: Author of the change
        date: Date of the change
        issue_number: Associated issue number (optional)
        breaking_details: Details about breaking changes (optional)
    """

    message: str
    type: ChangeType
    commit_hash: str
    author: str
    date: datetime
    issue_number: Optional[str] = None
    breaking_details: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return {
            "message": self.message,
            "type": self.type.value,
            "commit_hash": self.commit_hash,
            "author": self.author,
            "date": self.date.isoformat(),
            "issue_number": self.issue_number,
            "breaking_details": self.breaking_details,
        }


@dataclass
class ChangelogSection:
    """Represents a section in the changelog.

    Attributes:
        title: Section title
        version: Version number
        date: Release date
        entries: List of change entries
    """

    title: str
    version: str
    date: datetime
    entries: list[ChangeEntry] = field(default_factory=list)

    def add_entry(self, entry: ChangeEntry) -> None:
        """Add a change entry to this section.

        Args:
            entry: The change entry to add
        """
        self.entries.append(entry)

    def entries_by_type(self) -> dict[ChangeType, list[ChangeEntry]]:
        """Get entries grouped by change type.

        Returns:
            Dictionary mapping change types to lists of entries
        """
        grouped = {}
        for change_type in ChangeType:
            grouped[change_type] = [e for e in self.entries if e.type == change_type]
        return {k: v for k, v in grouped.items() if v}

    def to_dict(self) -> dict:
        """Convert section to dictionary."""
        return {
            "title": self.title,
            "version": self.version,
            "date": self.date.isoformat(),
            "entries": [e.to_dict() for e in self.entries],
        }


class ChangelogGenerator:
    """Generate changelogs from commit history with template support.

    Provides methods for:
    - Parsing commit messages to extract changes
    - Categorizing changes by type
    - Generating formatted output
    - Supporting multiple output formats
    """

    # Patterns for identifying change types in commit messages
    CHANGE_PATTERNS = {
        ChangeType.FEATURE: r"^feat[\(\:]|#feature",
        ChangeType.FIX: r"^fix[\(\:]|#fix",
        ChangeType.BREAKING: r"BREAKING[\s-]CHANGE|#breaking",
        ChangeType.SECURITY: r"^security[\(\:]|#security",
        ChangeType.DEPRECATION: r"^deprecate[\(\:]|deprecated|#deprecation",
        ChangeType.PERFORMANCE: r"^perf[\(\:]|#performance",
        ChangeType.DOCUMENTATION: r"^docs[\(\:]|#docs",
        ChangeType.REFACTOR: r"^refactor[\(\:]|#refactor",
    }

    # Pattern for issue numbers
    ISSUE_PATTERN = r"#(\d+)"

    def __init__(self, project_dir: str = "."):
        """Initialize changelog generator.

        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = Path(project_dir).resolve()
        self.sections: list[ChangelogSection] = []
        self._commit_cache: dict[str, str] = {}

    def add_entry(
        self,
        message: str,
        version: str,
        commit_hash: str,
        author: str,
        date: Optional[datetime] = None,
    ) -> ChangeEntry:
        """Add a single change entry to the changelog.

        Args:
            message: The change message
            version: Version this change belongs to
            commit_hash: Git commit hash
            author: Author of the change
            date: Date of the change (defaults to now)

        Returns:
            The created ChangeEntry

        Raises:
            ValueError: If version section doesn't exist
        """
        if date is None:
            date = datetime.now()

        change_type = self._categorize_message(message)
        issue_number = self._extract_issue_number(message)
        breaking_details = None
        if change_type == ChangeType.BREAKING:
            breaking_details = self._extract_breaking_details(message)

        entry = ChangeEntry(
            message=message,
            type=change_type,
            commit_hash=commit_hash,
            author=author,
            date=date,
            issue_number=issue_number,
            breaking_details=breaking_details,
        )

        # Find or create section
        section = self._get_or_create_section(version, date)
        section.add_entry(entry)

        return entry

    def create_section(
        self,
        version: str,
        title: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> ChangelogSection:
        """Create a new changelog section for a version.

        Args:
            version: Version number
            title: Optional custom title (defaults to version)
            date: Release date (defaults to now)

        Returns:
            The created ChangelogSection
        """
        if date is None:
            date = datetime.now()

        if title is None:
            title = f"Version {version}"

        section = ChangelogSection(title=title, version=version, date=date)
        self.sections.append(section)
        return section

    def generate(self) -> str:
        """Generate complete changelog in Markdown format.

        Returns:
            Formatted changelog as string
        """
        return self.format_changelog(ChangelogFormat.MARKDOWN)

    def format_changelog(self, format_type: ChangelogFormat = ChangelogFormat.MARKDOWN) -> str:
        """Format changelog in specified format.

        Args:
            format_type: Output format (markdown, html, json)

        Returns:
            Formatted changelog

        Raises:
            ValueError: If format type is unsupported
        """
        if format_type == ChangelogFormat.MARKDOWN:
            return self._format_markdown()
        elif format_type == ChangelogFormat.HTML:
            return self._format_html()
        elif format_type == ChangelogFormat.JSON:
            return self._format_json()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def get_changelog(self, version: Optional[str] = None) -> str:
        """Get changelog for specific version or all versions.

        Args:
            version: Optional version to filter by

        Returns:
            Changelog content
        """
        if version:
            sections = [s for s in self.sections if s.version == version]
            if not sections:
                return f"No changelog found for version {version}"
        else:
            sections = self.sections

        return self._format_sections(sections)

    def add_breaking_change(
        self,
        title: str,
        description: str,
        version: str,
        commit_hash: str,
        author: str,
    ) -> None:
        """Add a breaking change entry with detailed description.

        Args:
            title: Breaking change title
            description: Detailed description of the breaking change
            version: Version affected
            commit_hash: Git commit hash
            author: Author of the change
        """
        self.add_entry(
            message=f"BREAKING CHANGE: {title}",
            version=version,
            commit_hash=commit_hash,
            author=author,
        )

    def _categorize_message(self, message: str) -> ChangeType:
        """Categorize a message by change type.

        Args:
            message: The commit message

        Returns:
            The categorized ChangeType
        """
        message_lower = message.lower()
        for change_type, pattern in self.CHANGE_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                return change_type
        return ChangeType.OTHER

    def _extract_issue_number(self, message: str) -> Optional[str]:
        """Extract issue number from message.

        Args:
            message: The commit message

        Returns:
            Issue number if found, None otherwise
        """
        match = re.search(self.ISSUE_PATTERN, message)
        return match.group(1) if match else None

    def _extract_breaking_details(self, message: str) -> Optional[str]:
        """Extract breaking change details from message.

        Args:
            message: The commit message

        Returns:
            Breaking change details if found
        """
        match = re.search(r"BREAKING[\s-]CHANGE[:\s]+(.+?)(?:\n|$)", message, re.IGNORECASE)
        return match.group(1) if match else None

    def _get_or_create_section(self, version: str, date: datetime) -> ChangelogSection:
        """Get existing section or create new one.

        Args:
            version: Version number
            date: Date for new section

        Returns:
            The section
        """
        for section in self.sections:
            if section.version == version:
                return section
        return self.create_section(version, date=date)

    def _format_markdown(self) -> str:
        """Format changelog as Markdown.

        Returns:
            Markdown formatted changelog
        """
        lines = ["# Changelog\n"]
        for section in self.sections:
            lines.append(f"## {section.title}\n")
            lines.append(f"**Released:** {section.date.strftime('%Y-%m-%d')}\n")

            entries_by_type = section.entries_by_type()
            for change_type in ChangeType:
                if change_type in entries_by_type:
                    lines.append(f"\n### {change_type.value}\n")
                    for entry in entries_by_type[change_type]:
                        issue_link = f" ([#{entry.issue_number}])" if entry.issue_number else ""
                        lines.append(f"- {entry.message}{issue_link}\n")
                        if entry.breaking_details:
                            lines.append(f"  - **Breaking:** {entry.breaking_details}\n")

        return "".join(lines)

    def _format_html(self) -> str:
        """Format changelog as HTML.

        Returns:
            HTML formatted changelog
        """
        lines = ["<div class='changelog'>\n", "<h1>Changelog</h1>\n"]
        for section in self.sections:
            lines.append("<div class='section'>\n")
            lines.append(f"<h2>{section.title}</h2>\n")
            lines.append(f"<p class='date'>Released: {section.date.strftime('%Y-%m-%d')}</p>\n")

            entries_by_type = section.entries_by_type()
            for change_type in ChangeType:
                if change_type in entries_by_type:
                    lines.append("<div class='category'>\n")
                    lines.append(f"<h3>{change_type.value}</h3>\n")
                    lines.append("<ul>\n")
                    for entry in entries_by_type[change_type]:
                        issue_link = (
                            f" (<a href='#issue-{entry.issue_number}'>#{entry.issue_number}</a>)"
                            if entry.issue_number
                            else ""
                        )
                        lines.append(f"<li>{entry.message}{issue_link}")
                        if entry.breaking_details:
                            lines.append(f"<br><strong>Breaking:</strong> {entry.breaking_details}")
                        lines.append("</li>\n")
                    lines.append("</ul>\n")
                    lines.append("</div>\n")

            lines.append("</div>\n")

        lines.append("</div>\n")
        return "".join(lines)

    def _format_json(self) -> str:
        """Format changelog as JSON.

        Returns:
            JSON formatted changelog
        """
        data = {"changelog": [section.to_dict() for section in self.sections]}
        return json.dumps(data, indent=2)

    def _format_sections(self, sections: list[ChangelogSection]) -> str:
        """Format a list of sections.

        Args:
            sections: List of sections to format

        Returns:
            Formatted sections as string
        """
        if not sections:
            return ""

        lines = []
        for section in sections:
            lines.append(f"## {section.title}\n")
            lines.append(f"**Released:** {section.date.strftime('%Y-%m-%d')}\n")

            entries_by_type = section.entries_by_type()
            for change_type in ChangeType:
                if change_type in entries_by_type:
                    lines.append(f"\n### {change_type.value}\n")
                    for entry in entries_by_type[change_type]:
                        lines.append(f"- {entry.message}\n")

        return "".join(lines)

    def export_to_file(
        self,
        file_path: str,
        format_type: ChangelogFormat = ChangelogFormat.MARKDOWN,
    ) -> None:
        """Export changelog to file.

        Args:
            file_path: Path to write the changelog
            format_type: Output format

        Raises:
            IOError: If file cannot be written
        """
        output = self.format_changelog(format_type)
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

    def clear_sections(self) -> None:
        """Clear all sections from the changelog."""
        self.sections.clear()
