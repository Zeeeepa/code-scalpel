"""Tests for automated changelog generation system."""

from __future__ import annotations

from datetime import datetime

import pytest

from code_scalpel.release.changelog_generator import (
    ChangeEntry,
    ChangeType,
    ChangelogFormat,
    ChangelogGenerator,
    ChangelogSection,
)


class TestChangeEntry:
    """Test ChangeEntry dataclass."""

    def test_create_change_entry(self):
        """Test creating a change entry."""
        entry = ChangeEntry(
            message="Add new feature",
            type=ChangeType.FEATURE,
            commit_hash="abc123",
            author="John Doe",
            date=datetime.now(),
        )
        assert entry.message == "Add new feature"
        assert entry.type == ChangeType.FEATURE
        assert entry.commit_hash == "abc123"
        assert entry.author == "John Doe"

    def test_create_change_entry_with_issue(self):
        """Test creating entry with issue number."""
        entry = ChangeEntry(
            message="Fix bug #123",
            type=ChangeType.FIX,
            commit_hash="def456",
            author="Jane Doe",
            date=datetime.now(),
            issue_number="123",
        )
        assert entry.issue_number == "123"

    def test_create_change_entry_with_breaking_details(self):
        """Test creating entry with breaking change details."""
        entry = ChangeEntry(
            message="BREAKING CHANGE: API redesign",
            type=ChangeType.BREAKING,
            commit_hash="ghi789",
            author="Bob Smith",
            date=datetime.now(),
            breaking_details="API v1 no longer supported",
        )
        assert entry.breaking_details == "API v1 no longer supported"

    def test_change_entry_to_dict(self):
        """Test converting entry to dictionary."""
        now = datetime.now()
        entry = ChangeEntry(
            message="Test change",
            type=ChangeType.FEATURE,
            commit_hash="hash123",
            author="Test Author",
            date=now,
            issue_number="42",
        )
        result = entry.to_dict()
        assert result["message"] == "Test change"
        assert result["type"] == "Features"
        assert result["issue_number"] == "42"

    def test_change_entry_to_dict_no_issue(self):
        """Test to_dict with no issue number."""
        entry = ChangeEntry(
            message="Test change",
            type=ChangeType.FIX,
            commit_hash="hash456",
            author="Test Author",
            date=datetime.now(),
        )
        result = entry.to_dict()
        assert result["issue_number"] is None


class TestChangelogSection:
    """Test ChangelogSection class."""

    def test_create_section(self):
        """Test creating a changelog section."""
        now = datetime.now()
        section = ChangelogSection(
            title="Version 1.0.0",
            version="1.0.0",
            date=now,
        )
        assert section.title == "Version 1.0.0"
        assert section.version == "1.0.0"
        assert len(section.entries) == 0

    def test_add_entry_to_section(self):
        """Test adding entry to section."""
        section = ChangelogSection(
            title="Version 1.0.0",
            version="1.0.0",
            date=datetime.now(),
        )
        entry = ChangeEntry(
            message="Test feature",
            type=ChangeType.FEATURE,
            commit_hash="hash123",
            author="Author",
            date=datetime.now(),
        )
        section.add_entry(entry)
        assert len(section.entries) == 1
        assert section.entries[0] == entry

    def test_entries_by_type_empty(self):
        """Test grouping entries by type when empty."""
        section = ChangelogSection(
            title="Version 1.0.0",
            version="1.0.0",
            date=datetime.now(),
        )
        result = section.entries_by_type()
        assert len(result) == 0

    def test_entries_by_type_with_entries(self):
        """Test grouping entries by type with mixed entries."""
        section = ChangelogSection(
            title="Version 1.0.0",
            version="1.0.0",
            date=datetime.now(),
        )
        now = datetime.now()
        entry1 = ChangeEntry("Feature 1", ChangeType.FEATURE, "hash1", "Author", now)
        entry2 = ChangeEntry("Feature 2", ChangeType.FEATURE, "hash2", "Author", now)
        entry3 = ChangeEntry("Fix 1", ChangeType.FIX, "hash3", "Author", now)

        section.add_entry(entry1)
        section.add_entry(entry2)
        section.add_entry(entry3)

        result = section.entries_by_type()
        assert len(result[ChangeType.FEATURE]) == 2
        assert len(result[ChangeType.FIX]) == 1
        assert ChangeType.BREAKING not in result

    def test_section_to_dict(self):
        """Test converting section to dictionary."""
        now = datetime.now()
        section = ChangelogSection(
            title="Version 1.0.0",
            version="1.0.0",
            date=now,
        )
        result = section.to_dict()
        assert result["title"] == "Version 1.0.0"
        assert result["version"] == "1.0.0"
        assert result["entries"] == []


class TestChangelogGeneratorInit:
    """Test ChangelogGenerator initialization."""

    def test_init_with_defaults(self):
        """Test initializing with default project directory."""
        generator = ChangelogGenerator()
        assert generator.project_dir.is_absolute()
        assert len(generator.sections) == 0

    def test_init_with_custom_project_dir(self, tmp_path):
        """Test initializing with custom project directory."""
        generator = ChangelogGenerator(str(tmp_path))
        assert generator.project_dir == tmp_path.resolve()


class TestChangelogGeneratorCategorization:
    """Test message categorization."""

    def test_categorize_feature(self):
        """Test categorizing feature message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("feat: add new feature") == ChangeType.FEATURE
        )
        assert (
            generator._categorize_message("feat(api): add endpoint")
            == ChangeType.FEATURE
        )
        assert generator._categorize_message("This is a #feature") == ChangeType.FEATURE

    def test_categorize_fix(self):
        """Test categorizing fix message."""
        generator = ChangelogGenerator()
        assert generator._categorize_message("fix: resolve issue") == ChangeType.FIX
        assert generator._categorize_message("fix(api): patch bug") == ChangeType.FIX
        assert generator._categorize_message("bug #fix") == ChangeType.FIX

    def test_categorize_breaking(self):
        """Test categorizing breaking change."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("BREAKING CHANGE: API redesign")
            == ChangeType.BREAKING
        )
        assert (
            generator._categorize_message("BREAKING-CHANGE: remove endpoint")
            == ChangeType.BREAKING
        )

    def test_categorize_security(self):
        """Test categorizing security message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("security: fix vulnerability")
            == ChangeType.SECURITY
        )
        assert (
            generator._categorize_message("security(auth): update token handling")
            == ChangeType.SECURITY
        )

    def test_categorize_documentation(self):
        """Test categorizing documentation message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("docs: update README")
            == ChangeType.DOCUMENTATION
        )
        assert (
            generator._categorize_message("docs(api): add examples")
            == ChangeType.DOCUMENTATION
        )

    def test_categorize_performance(self):
        """Test categorizing performance message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("perf: optimize database")
            == ChangeType.PERFORMANCE
        )
        assert (
            generator._categorize_message("perf(search): improve query speed")
            == ChangeType.PERFORMANCE
        )

    def test_categorize_refactor(self):
        """Test categorizing refactor message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("refactor: restructure code")
            == ChangeType.REFACTOR
        )
        assert (
            generator._categorize_message("refactor(api): simplify logic")
            == ChangeType.REFACTOR
        )

    def test_categorize_deprecation(self):
        """Test categorizing deprecation message."""
        generator = ChangelogGenerator()
        assert (
            generator._categorize_message("deprecate: old API")
            == ChangeType.DEPRECATION
        )
        assert (
            generator._categorize_message("deprecated function")
            == ChangeType.DEPRECATION
        )

    def test_categorize_unknown(self):
        """Test categorizing unknown message type."""
        generator = ChangelogGenerator()
        assert generator._categorize_message("random message") == ChangeType.OTHER


class TestChangelogGeneratorIssueExtraction:
    """Test issue number extraction."""

    def test_extract_issue_number(self):
        """Test extracting issue number."""
        generator = ChangelogGenerator()
        assert generator._extract_issue_number("Fix bug #123") == "123"
        assert generator._extract_issue_number("Resolves #456") == "456"

    def test_extract_issue_no_match(self):
        """Test extracting when no issue number present."""
        generator = ChangelogGenerator()
        assert generator._extract_issue_number("No issue here") is None

    def test_extract_multiple_issue_numbers(self):
        """Test extracting when multiple issue numbers present."""
        generator = ChangelogGenerator()
        # Should return first match
        assert generator._extract_issue_number("Fixes #123 and #456") == "123"


class TestChangelogGeneratorBreakingDetails:
    """Test breaking change details extraction."""

    def test_extract_breaking_details(self):
        """Test extracting breaking change details."""
        generator = ChangelogGenerator()
        result = generator._extract_breaking_details("BREAKING CHANGE: API v1 removed")
        assert result is not None and "API v1 removed" in result

    def test_extract_breaking_details_hyphen(self):
        """Test extracting with hyphenated BREAKING-CHANGE."""
        generator = ChangelogGenerator()
        result = generator._extract_breaking_details(
            "BREAKING-CHANGE: endpoint changed"
        )
        assert result is not None

    def test_extract_breaking_no_match(self):
        """Test extracting when no breaking change present."""
        generator = ChangelogGenerator()
        assert generator._extract_breaking_details("Regular message") is None


class TestChangelogGeneratorEntry:
    """Test adding entries to changelog."""

    def test_add_entry(self):
        """Test adding a single entry."""
        generator = ChangelogGenerator()
        entry = generator.add_entry(
            message="New feature",
            version="1.0.0",
            commit_hash="abc123",
            author="Author Name",
        )
        assert entry.message == "New feature"
        assert len(generator.sections) == 1
        assert len(generator.sections[0].entries) == 1

    def test_add_entry_with_custom_date(self):
        """Test adding entry with custom date."""
        generator = ChangelogGenerator()
        custom_date = datetime(2024, 1, 15)
        entry = generator.add_entry(
            message="Old feature",
            version="0.5.0",
            commit_hash="def456",
            author="Old Author",
            date=custom_date,
        )
        assert entry.date == custom_date

    def test_add_entry_auto_categorizes(self):
        """Test that add_entry auto-categorizes messages."""
        generator = ChangelogGenerator()
        entry = generator.add_entry(
            message="feat: new API endpoint",
            version="1.0.0",
            commit_hash="hash123",
            author="Author",
        )
        assert entry.type == ChangeType.FEATURE

    def test_add_entry_to_existing_section(self):
        """Test adding multiple entries to same section."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature 1", "1.0.0", "hash1", "Author")
        generator.add_entry("Fix bug", "1.0.0", "hash2", "Author")
        assert len(generator.sections) == 1
        assert len(generator.sections[0].entries) == 2

    def test_add_entry_to_different_sections(self):
        """Test adding entries to different versions."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        generator.add_entry("Fix", "2.0.0", "hash2", "Author")
        assert len(generator.sections) == 2


class TestChangelogGeneratorSections:
    """Test section management."""

    def test_create_section(self):
        """Test creating a new section."""
        generator = ChangelogGenerator()
        section = generator.create_section("1.0.0")
        assert section.version == "1.0.0"
        assert section.title == "Version 1.0.0"
        assert len(generator.sections) == 1

    def test_create_section_with_custom_title(self):
        """Test creating section with custom title."""
        generator = ChangelogGenerator()
        section = generator.create_section("1.0.0", title="Release 1.0.0")
        assert section.title == "Release 1.0.0"

    def test_create_section_with_custom_date(self):
        """Test creating section with custom date."""
        generator = ChangelogGenerator()
        custom_date = datetime(2024, 1, 15)
        section = generator.create_section("1.0.0", date=custom_date)
        assert section.date == custom_date


class TestChangelogGeneratorFormatting:
    """Test changelog formatting in different formats."""

    def test_generate_markdown(self):
        """Test generating Markdown changelog."""
        generator = ChangelogGenerator()
        generator.add_entry("feat: add feature", "1.0.0", "hash1", "Author")
        generator.add_entry("fix: fix bug", "1.0.0", "hash2", "Author")
        result = generator.generate()
        assert "# Changelog" in result
        assert "Features" in result
        assert "Fixes" in result

    def test_format_markdown(self):
        """Test explicit Markdown format."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature X", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.MARKDOWN)
        assert "# Changelog" in result

    def test_format_html(self):
        """Test HTML format."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature X", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.HTML)
        assert "<div class='changelog'>" in result
        assert "<h1>Changelog</h1>" in result

    def test_format_json(self):
        """Test JSON format."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature X", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.JSON)
        assert "changelog" in result
        assert "Feature X" in result

    def test_format_unsupported_raises_error(self):
        """Test that unsupported format raises error."""
        generator = ChangelogGenerator()
        with pytest.raises((ValueError, TypeError)):
            generator.format_changelog("unsupported")  # type: ignore


class TestChangelogGeneratorMarkdownFormat:
    """Test Markdown formatting in detail."""

    def test_markdown_includes_version_info(self):
        """Test that Markdown includes version information."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        result = generator.generate()
        assert "Version 1.0.0" in result

    def test_markdown_includes_issue_links(self):
        """Test that Markdown includes issue links."""
        generator = ChangelogGenerator()
        generator.add_entry("Fix bug #123", "1.0.0", "hash1", "Author")
        result = generator.generate()
        assert "#123" in result

    def test_markdown_includes_breaking_changes(self):
        """Test that Markdown includes breaking change details."""
        generator = ChangelogGenerator()
        generator.add_breaking_change(
            title="API redesign",
            description="Endpoint structure changed",
            version="2.0.0",
            commit_hash="hash1",
            author="Author",
        )
        result = generator.generate()
        assert "Breaking Changes" in result

    def test_markdown_sections_ordered(self):
        """Test that changelog sections are properly ordered."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "2.0.0", "hash2", "Author")
        generator.add_entry("Fix", "1.0.0", "hash1", "Author")
        result = generator.generate()
        # First added should appear first
        assert result.find("2.0.0") < result.find("1.0.0")


class TestChangelogGeneratorHTMLFormat:
    """Test HTML formatting in detail."""

    def test_html_structure(self):
        """Test HTML has proper structure."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.HTML)
        assert result.startswith("<div class='changelog'>")
        assert result.endswith("</div>\n")

    def test_html_includes_categories(self):
        """Test HTML includes change type categories."""
        generator = ChangelogGenerator()
        generator.add_entry("feat: feature", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.HTML)
        assert "<h3>Features</h3>" in result


class TestChangelogGeneratorJSONFormat:
    """Test JSON formatting in detail."""

    def test_json_is_valid(self):
        """Test that output is valid JSON."""
        import json as json_lib

        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        result = generator.format_changelog(ChangelogFormat.JSON)
        data = json_lib.loads(result)
        assert "changelog" in data

    def test_json_includes_all_fields(self):
        """Test that JSON includes all entry fields."""
        import json as json_lib

        generator = ChangelogGenerator()
        generator.add_entry("fix: resolved issue #42", "1.0.0", "hash123", "John Doe")
        result = generator.format_changelog(ChangelogFormat.JSON)
        data = json_lib.loads(result)
        entry = data["changelog"][0]["entries"][0]
        assert entry["message"] == "fix: resolved issue #42"
        assert entry["type"] == "Fixes"
        assert entry["author"] == "John Doe"


class TestChangelogGeneratorGetChangelog:
    """Test getting changelog content."""

    def test_get_all_changelog(self):
        """Test getting all changelog content."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        result = generator.get_changelog()
        assert "Feature" in result

    def test_get_specific_version_changelog(self):
        """Test getting changelog for specific version."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature 1", "1.0.0", "hash1", "Author")
        generator.add_entry("Feature 2", "2.0.0", "hash2", "Author")
        result = generator.get_changelog(version="1.0.0")
        assert "Feature 1" in result
        assert "Feature 2" not in result

    def test_get_nonexistent_version_changelog(self):
        """Test getting changelog for non-existent version."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        result = generator.get_changelog(version="3.0.0")
        assert "No changelog found" in result


class TestChangelogGeneratorBreakingChanges:
    """Test breaking change functionality."""

    def test_add_breaking_change(self):
        """Test adding a breaking change."""
        generator = ChangelogGenerator()
        generator.add_breaking_change(
            title="API v1 removed",
            description="Use API v2 instead",
            version="2.0.0",
            commit_hash="hash1",
            author="Author",
        )
        assert len(generator.sections) == 1
        entries = generator.sections[0].entries
        assert len(entries) == 1
        assert entries[0].type == ChangeType.BREAKING
        assert "API v1 removed" in entries[0].message

    def test_breaking_change_in_changelog(self):
        """Test that breaking changes appear in changelog."""
        generator = ChangelogGenerator()
        generator.add_breaking_change(
            title="Database schema change",
            description="Table structure modified",
            version="1.5.0",
            commit_hash="hash1",
            author="Author",
        )
        result = generator.generate()
        assert "Breaking Changes" in result
        assert "Database schema change" in result


class TestChangelogGeneratorExport:
    """Test exporting changelog to files."""

    def test_export_to_markdown_file(self, tmp_path):
        """Test exporting to Markdown file."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        output_file = tmp_path / "CHANGELOG.md"
        generator.export_to_file(str(output_file), ChangelogFormat.MARKDOWN)
        assert output_file.exists()
        content = output_file.read_text()
        assert "# Changelog" in content

    def test_export_to_html_file(self, tmp_path):
        """Test exporting to HTML file."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        output_file = tmp_path / "CHANGELOG.html"
        generator.export_to_file(str(output_file), ChangelogFormat.HTML)
        assert output_file.exists()
        content = output_file.read_text()
        assert "<div class='changelog'>" in content

    def test_export_to_json_file(self, tmp_path):
        """Test exporting to JSON file."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        output_file = tmp_path / "CHANGELOG.json"
        generator.export_to_file(str(output_file), ChangelogFormat.JSON)
        assert output_file.exists()
        content = output_file.read_text()
        assert '"changelog"' in content

    def test_export_creates_directories(self, tmp_path):
        """Test that export creates necessary directories."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        nested_path = tmp_path / "deep" / "nested" / "CHANGELOG.md"
        generator.export_to_file(str(nested_path))
        assert nested_path.exists()


class TestChangelogGeneratorClear:
    """Test clearing changelog."""

    def test_clear_sections(self):
        """Test clearing all sections."""
        generator = ChangelogGenerator()
        generator.add_entry("Feature", "1.0.0", "hash1", "Author")
        assert len(generator.sections) > 0
        generator.clear_sections()
        assert len(generator.sections) == 0
