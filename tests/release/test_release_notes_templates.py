"""Tests for release notes template system."""

from __future__ import annotations

import json

import pytest

from code_scalpel.release.release_notes_templates import (
    ReleaseNotesTemplate,
    Template,
    TemplateRegistry,
)


class TestTemplate:
    """Test Template class."""

    def test_create_template(self):
        """Test creating a template."""
        template = Template(name="test", content="Hello {{name}}", variables=["name"])
        assert template.name == "test"
        assert template.content == "Hello {{name}}"

    def test_render_template(self):
        """Test rendering a template."""
        template = Template(name="test", content="Hello {{name}}", variables=["name"])
        result = template.render({"name": "World"})
        assert result == "Hello World"

    def test_render_missing_variable(self):
        """Test rendering with missing variable raises error."""
        template = Template(name="test", content="Hello {{name}}", variables=["name"])
        with pytest.raises(KeyError):
            template.render({})

    def test_render_multiple_variables(self):
        """Test rendering multiple variables."""
        template = Template(
            name="test",
            content="{{greeting}} {{name}}!",
            variables=["greeting", "name"],
        )
        result = template.render({"greeting": "Hello", "name": "World"})
        assert result == "Hello World!"

    def test_add_custom_formatter(self):
        """Test adding custom formatter."""
        template = Template(name="test", content="{{name}}", variables=["name"])
        template.add_formatter("name", str.upper)
        result = template.render({"name": "john"})
        assert result == "JOHN"

    def test_template_to_dict(self):
        """Test converting template to dict."""
        template = Template(name="test", content="content", variables=["var1"])
        result = template.to_dict()
        assert result["name"] == "test"
        assert result["content"] == "content"


class TestTemplateRegistry:
    """Test TemplateRegistry class."""

    def test_registry_loads_built_in(self):
        """Test that registry loads built-in templates."""
        registry = TemplateRegistry()
        templates = registry.list_available()
        assert "default" in templates
        assert "minimal" in templates
        assert "detailed" in templates
        assert "highlight-breaking-changes" in templates

    def test_get_template(self):
        """Test getting a template."""
        registry = TemplateRegistry()
        template = registry.get("default")
        assert template is not None
        assert template.name == "default"

    def test_get_nonexistent_template(self):
        """Test getting non-existent template returns None."""
        registry = TemplateRegistry()
        assert registry.get("nonexistent") is None

    def test_register_template(self):
        """Test registering a custom template."""
        registry = TemplateRegistry()
        template = Template(name="custom", content="{{var}}", variables=["var"])
        registry.register(template)
        assert registry.get("custom") == template

    def test_register_empty_name_raises_error(self):
        """Test that empty template name raises error."""
        registry = TemplateRegistry()
        template = Template(name="", content="content", variables=[])
        with pytest.raises(ValueError):
            registry.register(template)

    def test_list_available(self):
        """Test listing available templates."""
        registry = TemplateRegistry()
        templates = registry.list_available()
        assert len(templates) >= 4
        assert isinstance(templates, list)

    def test_create_custom(self):
        """Test creating custom template."""
        registry = TemplateRegistry()
        template = registry.create_custom("test", "Hello {{name}}")
        assert template.name == "test"
        assert registry.get("test") == template

    def test_create_custom_duplicate_name_raises_error(self):
        """Test creating duplicate name raises error."""
        registry = TemplateRegistry()
        registry.create_custom("test", "content")
        with pytest.raises(ValueError):
            registry.create_custom("test", "other content")

    def test_delete_template(self):
        """Test deleting a template."""
        registry = TemplateRegistry()
        registry.create_custom("test", "content")
        assert registry.delete("test")
        assert registry.get("test") is None

    def test_delete_nonexistent_template(self):
        """Test deleting non-existent template returns False."""
        registry = TemplateRegistry()
        assert not registry.delete("nonexistent")

    def test_delete_built_in_template_raises_error(self):
        """Test deleting built-in template raises error."""
        registry = TemplateRegistry()
        with pytest.raises(ValueError):
            registry.delete("default")

    def test_render_template(self):
        """Test rendering template from registry."""
        registry = TemplateRegistry()
        registry.create_custom("test", "Hello {{name}}", variables=["name"])
        result = registry.render_template("test", {"name": "World"})
        assert result == "Hello World"

    def test_render_nonexistent_template_raises_error(self):
        """Test rendering non-existent template raises error."""
        registry = TemplateRegistry()
        with pytest.raises(ValueError):
            registry.render_template("nonexistent", {})

    def test_extract_variables(self):
        """Test extracting variables from content."""
        content = "Hello {{name}}, welcome to {{place}}"
        vars = TemplateRegistry._extract_variables(content)
        assert "name" in vars
        assert "place" in vars

    def test_export_template(self, tmp_path):
        """Test exporting template to file."""
        registry = TemplateRegistry()
        registry.create_custom("test", "Hello {{name}}", variables=["name"])
        export_path = tmp_path / "test_template.json"
        registry.export_template("test", str(export_path))
        assert export_path.exists()
        data = json.loads(export_path.read_text())
        assert data["name"] == "test"

    def test_export_nonexistent_template_raises_error(self, tmp_path):
        """Test exporting non-existent template raises error."""
        registry = TemplateRegistry()
        with pytest.raises(ValueError):
            registry.export_template("nonexistent", str(tmp_path / "test.json"))

    def test_import_template(self, tmp_path):
        """Test importing template from file."""
        template_data = {
            "name": "imported",
            "content": "Test {{var}}",
            "variables": ["var"],
        }
        template_path = tmp_path / "template.json"
        template_path.write_text(json.dumps(template_data))

        registry = TemplateRegistry()
        imported = registry.import_template(str(template_path))
        assert imported.name == "imported"
        assert registry.get("imported") is not None

    def test_import_nonexistent_file_raises_error(self, tmp_path):
        """Test importing non-existent file raises error."""
        registry = TemplateRegistry()
        with pytest.raises(IOError):
            registry.import_template(str(tmp_path / "nonexistent.json"))


class TestReleaseNotesTemplate:
    """Test ReleaseNotesTemplate class."""

    def test_load_template(self):
        """Test loading a template."""
        template_manager = ReleaseNotesTemplate()
        template = template_manager.load_template("default")
        assert template.name == "default"

    def test_load_nonexistent_raises_error(self):
        """Test loading non-existent template raises error."""
        template_manager = ReleaseNotesTemplate()
        with pytest.raises(ValueError):
            template_manager.load_template("nonexistent")

    def test_render_default_template(self):
        """Test rendering default template."""
        template_manager = ReleaseNotesTemplate()
        context = {
            "title": "Version 1.0.0",
            "version": "1.0.0",
            "date": "2024-01-15",
            "summary": "Initial release",
            "features": "- Feature 1\n- Feature 2",
            "fixes": "- Fix 1",
            "breaking_changes": "None",
            "contributors": "John Doe",
            "github_url": "https://github.com/example",
        }
        result = template_manager.render("default", context)
        assert "1.0.0" in result
        assert "Initial release" in result

    def test_render_minimal_template(self):
        """Test rendering minimal template."""
        template_manager = ReleaseNotesTemplate()
        context = {
            "version": "2.0.0",
            "summary": "Major release",
            "features": "- New API",
        }
        result = template_manager.render("minimal", context)
        assert "2.0.0" in result
        assert "Major release" in result

    def test_list_available(self):
        """Test listing available templates."""
        template_manager = ReleaseNotesTemplate()
        templates = template_manager.list_available()
        assert len(templates) >= 4

    def test_create_custom(self):
        """Test creating custom template."""
        template_manager = ReleaseNotesTemplate()
        custom = template_manager.create_custom("my_template", "Version: {{version}}")
        assert custom.name == "my_template"

    def test_get_default_context(self):
        """Test getting default context."""
        template_manager = ReleaseNotesTemplate()
        context = template_manager.get_default_context("1.0.0")
        assert context["version"] == "1.0.0"
        assert "date" in context
        assert context["title"] == "Version 1.0.0"

    def test_render_missing_context_variable_raises_error(self):
        """Test rendering with missing context variable raises error."""
        template_manager = ReleaseNotesTemplate()
        context = {"version": "1.0.0"}  # Missing other required variables
        with pytest.raises(KeyError):
            template_manager.render("default", context)

    def test_render_custom_template(self):
        """Test rendering custom template."""
        template_manager = ReleaseNotesTemplate()
        template_manager.create_custom("custom", "Release {{version}}")
        result = template_manager.render("custom", {"version": "3.0.0"})
        assert result == "Release 3.0.0"


class TestBuiltInTemplates:
    """Test built-in templates."""

    def test_default_template_structure(self):
        """Test default template has expected structure."""
        template_manager = ReleaseNotesTemplate()
        template = template_manager.load_template("default")
        assert "# {{title}}" in template.content
        assert "Features" in template.content
        assert "Bug Fixes" in template.content

    def test_detailed_template_structure(self):
        """Test detailed template has comprehensive sections."""
        template_manager = ReleaseNotesTemplate()
        template = template_manager.load_template("detailed")
        assert "Migration Guide" in template.content
        assert "Security Updates" in template.content

    def test_breaking_template_highlights_breaking(self):
        """Test breaking changes template highlights them."""
        template_manager = ReleaseNotesTemplate()
        template = template_manager.load_template("highlight-breaking-changes")
        assert "BREAKING" in template.content

    def test_minimal_template_is_simple(self):
        """Test minimal template is concise."""
        template_manager = ReleaseNotesTemplate()
        template = template_manager.load_template("minimal")
        # Minimal template should have fewer lines than default
        assert len(template.content.split("\n")) < len(template_manager.load_template("default").content.split("\n"))
