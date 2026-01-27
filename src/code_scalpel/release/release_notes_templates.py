"""Release notes template customization and management.

Provides template-based release notes generation with support for:
- Template inheritance and composition
- Custom template variables and formatters
- Built-in template library
- Dynamic template rendering
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class Template:
    """Represents a release notes template.

    Attributes:
        name: Template name
        content: Template content with variables
        variables: List of required variables
        custom_formatters: Dict of custom formatting functions
        parent: Parent template to inherit from
    """

    name: str
    content: str
    variables: list[str] = field(default_factory=list)
    custom_formatters: dict[str, Callable[[str], str]] = field(default_factory=dict)
    parent: Optional[str] = None

    def render(self, context: dict[str, Any]) -> str:
        """Render template with given context.

        Args:
            context: Dictionary of variables to render

        Returns:
            Rendered template content

        Raises:
            KeyError: If required variable is missing
            TypeError: If value type is incompatible
        """
        result = self.content
        for var in self.variables:
            if var not in context:
                raise KeyError(f"Missing required variable: {var}")
            value = context[var]
            if var in self.custom_formatters:
                value = self.custom_formatters[var](str(value))
            result = result.replace(f"{{{{{var}}}}}", str(value))
        return result

    def add_formatter(self, variable: str, formatter: Callable[[str], str]) -> None:
        """Add custom formatter for a variable.

        Args:
            variable: Variable name
            formatter: Function to format the variable value
        """
        self.custom_formatters[variable] = formatter

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "content": self.content,
            "variables": self.variables,
            "parent": self.parent,
        }


class TemplateRegistry:
    """Manages a collection of release notes templates.

    Provides methods for:
    - Loading and storing templates
    - Template lookup and retrieval
    - Built-in template management
    - Template inheritance
    """

    def __init__(self):
        """Initialize template registry."""
        self.templates: dict[str, Template] = {}
        self._load_built_in_templates()

    def _load_built_in_templates(self) -> None:
        """Load built-in templates."""
        # Default template
        default_template = Template(
            name="default",
            content="""# {{title}}

Version {{version}} - Released {{date}}

## What's New

{{summary}}

## Features

{{features}}

## Bug Fixes

{{fixes}}

## Breaking Changes

{{breaking_changes}}

## Contributors

{{contributors}}

## Download

[GitHub Releases]({{github_url}})
""",
            variables=[
                "title",
                "version",
                "date",
                "summary",
                "features",
                "fixes",
                "breaking_changes",
                "contributors",
                "github_url",
            ],
        )

        # Minimal template
        minimal_template = Template(
            name="minimal",
            content="""# {{version}}

{{summary}}

{{features}}
""",
            variables=["version", "summary", "features"],
        )

        # Detailed template
        detailed_template = Template(
            name="detailed",
            content="""# Release {{version}}

**Released:** {{date}}

{{summary}}

## Features

{{features}}

## Improvements

{{improvements}}

## Bug Fixes

{{fixes}}

## Security Updates

{{security_updates}}

## Deprecations

{{deprecations}}

## Breaking Changes

{{breaking_changes}}

## Migration Guide

{{migration_guide}}

## Contributors

{{contributors}}

## Acknowledgments

{{acknowledgments}}

## Download

- [Source Code]({{github_url}})
- [PyPI Package]({{pypi_url}})
- [Docker Image]({{docker_url}})
""",
            variables=[
                "version",
                "date",
                "summary",
                "features",
                "improvements",
                "fixes",
                "security_updates",
                "deprecations",
                "breaking_changes",
                "migration_guide",
                "contributors",
                "acknowledgments",
                "github_url",
                "pypi_url",
                "docker_url",
            ],
        )

        # Breaking changes focused template
        breaking_template = Template(
            name="highlight-breaking-changes",
            content="""# {{version}} - BREAKING CHANGES

⚠️ This release contains breaking changes.

## Breaking Changes

{{breaking_changes}}

## Migration Guide

{{migration_guide}}

## New Features

{{features}}

## Bug Fixes

{{fixes}}

## Contributors

{{contributors}}
""",
            variables=[
                "version",
                "breaking_changes",
                "migration_guide",
                "features",
                "fixes",
                "contributors",
            ],
        )

        self.register(default_template)
        self.register(minimal_template)
        self.register(detailed_template)
        self.register(breaking_template)

    def register(self, template: Template) -> None:
        """Register a template.

        Args:
            template: Template to register

        Raises:
            ValueError: If template name is empty
        """
        if not template.name:
            raise ValueError("Template name cannot be empty")
        self.templates[template.name] = template

    def get(self, name: str) -> Optional[Template]:
        """Get template by name.

        Args:
            name: Template name

        Returns:
            Template if found, None otherwise
        """
        return self.templates.get(name)

    def list_available(self) -> list[str]:
        """List all available template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def create_custom(
        self,
        name: str,
        content: str,
        variables: Optional[list[str]] = None,
    ) -> Template:
        """Create a custom template.

        Args:
            name: Template name
            content: Template content
            variables: List of required variables

        Returns:
            Created template

        Raises:
            ValueError: If template name already exists
        """
        if name in self.templates:
            raise ValueError(f"Template '{name}' already exists")
        if variables is None:
            variables = self._extract_variables(content)
        template = Template(name=name, content=content, variables=variables)
        self.register(template)
        return template

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of template to render
            context: Context variables for rendering

        Returns:
            Rendered content

        Raises:
            ValueError: If template not found
            KeyError: If required variable missing
        """
        template = self.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        return template.render(context)

    def delete(self, name: str) -> bool:
        """Delete a template.

        Args:
            name: Template name

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If trying to delete built-in template
        """
        if name in ["default", "minimal", "detailed", "highlight-breaking-changes"]:
            raise ValueError(f"Cannot delete built-in template '{name}'")
        if name in self.templates:
            del self.templates[name]
            return True
        return False

    def export_template(self, name: str, file_path: str) -> None:
        """Export template to file.

        Args:
            file_path: Path to export to

        Raises:
            ValueError: If template not found
            IOError: If file cannot be written
        """
        template = self.get(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = template.to_dict()
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def import_template(self, file_path: str) -> Template:
        """Import template from file.

        Args:
            file_path: Path to import from

        Returns:
            Imported template

        Raises:
            IOError: If file cannot be read
            ValueError: If template data is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise IOError(f"File not found: {file_path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        template = Template(
            name=data["name"],
            content=data["content"],
            variables=data.get("variables", []),
        )
        self.register(template)
        return template

    @staticmethod
    def _extract_variables(content: str) -> list[str]:
        """Extract variable names from template content.

        Args:
            content: Template content

        Returns:
            List of variable names
        """
        import re

        pattern = r"\{\{(\w+)\}\}"
        matches = re.findall(pattern, content)
        return list(set(matches))  # Return unique variables


class ReleaseNotesTemplate:
    """Main interface for release notes template operations.

    Provides high-level methods for:
    - Loading templates
    - Rendering release notes
    - Managing template library
    - Custom template creation
    """

    def __init__(self):
        """Initialize release notes template manager."""
        self.registry = TemplateRegistry()

    def load_template(self, name: str) -> Template:
        """Load a template by name.

        Args:
            name: Template name

        Returns:
            The template

        Raises:
            ValueError: If template not found
        """
        template = self.registry.get(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        return template

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render release notes from template.

        Args:
            template_name: Template to use
            context: Context variables

        Returns:
            Rendered release notes

        Raises:
            ValueError: If template not found
            KeyError: If required variable missing
        """
        return self.registry.render_template(template_name, context)

    def list_available(self) -> list[str]:
        """List available templates.

        Returns:
            List of template names
        """
        return self.registry.list_available()

    def create_custom(
        self,
        name: str,
        content: str,
        variables: Optional[list[str]] = None,
    ) -> Template:
        """Create custom template.

        Args:
            name: Template name
            content: Template content
            variables: Required variables

        Returns:
            Created template
        """
        return self.registry.create_custom(name, content, variables)

    def get_default_context(self, version: str) -> dict[str, Any]:
        """Get default context for template rendering.

        Args:
            version: Version string

        Returns:
            Default context dictionary
        """
        now = datetime.now()
        return {
            "version": version,
            "date": now.strftime("%Y-%m-%d"),
            "title": f"Version {version}",
            "summary": "",
            "features": "",
            "fixes": "",
            "breaking_changes": "",
            "contributors": "",
            "github_url": "",
            "pypi_url": "",
            "docker_url": "",
        }
