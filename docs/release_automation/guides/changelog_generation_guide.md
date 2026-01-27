# Changelog Generation Guide

## Overview

Learn how to generate changelogs automatically from commit messages.

## Quick Start

```python
from code_scalpel.release.changelog_generator import ChangelogGenerator, ChangelogFormat

generator = ChangelogGenerator()

# Add entries
generator.add_entry(
    message="feat: add new API endpoint",
    version="1.0.0",
    commit_hash="abc123",
    author="John Doe"
)

# Generate and export
generator.export_to_file("CHANGELOG.md", ChangelogFormat.MARKDOWN)
generator.export_to_file("CHANGELOG.html", ChangelogFormat.HTML)
```

## Commit Message Conventions

Prefix commit messages with keywords:

- `feat:` - New feature
- `fix:` - Bug fix
- `BREAKING CHANGE:` - Breaking change
- `docs:` - Documentation
- `perf:` - Performance improvement
- `refactor:` - Code refactoring

Example:
```
feat: add user authentication
fix: resolve memory leak in cache
BREAKING CHANGE: renamed API endpoints
```

## Advanced Usage

### Adding Breaking Changes

```python
generator.add_breaking_change(
    title="API v1 Deprecated",
    description="Use API v2 instead. Migration guide at docs/migration.md",
    version="2.0.0",
    commit_hash="def456",
    author="Jane Smith"
)
```

### Custom Sections

```python
section = generator.create_section(
    version="1.5.0",
    title="Version 1.5.0 - Beta Release",
    date=datetime(2024, 1, 15)
)
```

### Multiple Formats

```python
# Generate all formats
markdown = generator.format_changelog(ChangelogFormat.MARKDOWN)
html = generator.format_changelog(ChangelogFormat.HTML)
json_data = generator.format_changelog(ChangelogFormat.JSON)
```

## Template Integration

Combine with release notes templates:

```python
from code_scalpel.release.release_notes_templates import ReleaseNotesTemplate

template_mgr = ReleaseNotesTemplate()
context = template_mgr.get_default_context("1.0.0")
context["features"] = generator.get_changelog(version="1.0.0")

release_notes = template_mgr.render("default", context)
```
