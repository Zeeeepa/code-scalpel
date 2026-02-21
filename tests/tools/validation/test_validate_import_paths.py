"""Tests for validate_import_paths.py script."""

import json

from scripts.validate_import_paths import ImportPathValidator


class TestValidateImportPaths:
    """Test suite for import path validation."""

    def test_detects_deprecated_imports(self, tmp_path):
        """Test detection of deprecated import patterns."""
        # Create test file with deprecated import
        test_file = tmp_path / "deprecated_import.py"
        test_file.write_text(
            """
# Old import pattern
from code_scalpel.server import some_function

# Correct import
from code_scalpel.mcp.tools.new_module import some_function
"""
        )

        validator = ImportPathValidator(tmp_path)
        results = validator.validate_file(test_file)

        assert len(results["deprecated_imports"]) > 0
        assert any("server" in imp["text"] for imp in results["deprecated_imports"])

    def test_categorizes_by_file_type(self, tmp_path):
        """Test categorization of files by type."""
        # Create different file types
        source_file = tmp_path / "src" / "code_scalpel" / "module.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("from code_scalpel.server import func")

        test_file = tmp_path / "tests" / "test_module.py"
        test_file.parent.mkdir()
        test_file.write_text("from code_scalpel.server import func")

        doc_file = tmp_path / "docs" / "example.py"
        doc_file.parent.mkdir()
        doc_file.write_text("from code_scalpel.server import func")

        validator = ImportPathValidator(tmp_path)
        inventory = validator.build_inventory()

        # Check categorization
        source_issues = [f for f in inventory["files"] if f["category"] == "source"]
        test_issues = [f for f in inventory["files"] if f["category"] == "test"]
        doc_issues = [f for f in inventory["files"] if f["category"] == "doc"]

        assert len(source_issues) > 0
        assert len(test_issues) > 0
        assert len(doc_issues) > 0

    def test_provides_fix_suggestions(self, tmp_path):
        """Test generation of fix suggestions."""
        test_file = tmp_path / "broken.py"
        test_file.write_text(
            """
from code_scalpel.server import old_tool
import code_scalpel.old_helpers as helpers
"""
        )

        validator = ImportPathValidator(tmp_path)
        results = validator.validate_file(test_file)

        assert len(results["fix_suggestions"]) > 0
        for suggestion in results["fix_suggestions"]:
            assert "old" in suggestion["original"]
            assert "new" in suggestion["suggested"] or "mcp" in suggestion["suggested"]

    def test_whitelist_filtering(self, tmp_path):
        """Test filtering using whitelist."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from allowed_old import func")

        # Whitelist the old import
        whitelist = ["allowed_old"]

        validator = ImportPathValidator(tmp_path, whitelist=whitelist)
        results = validator.validate_file(test_file)

        # Should not detect as deprecated
        assert len(results["deprecated_imports"]) == 0

    def test_json_output_format(self, tmp_path):
        """Test JSON output generation."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from code_scalpel.server import func")

        validator = ImportPathValidator(tmp_path)
        inventory = validator.build_inventory()

        # Should be serializable
        json_str = json.dumps(inventory, indent=2)
        assert json_str

        # Should have expected structure
        assert "files" in inventory
        assert "summary" in inventory
        assert "critical_findings" in inventory

    def test_critical_findings_in_source(self, tmp_path):
        """Test that source files with deprecated imports are marked critical."""
        source_file = tmp_path / "src" / "code_scalpel" / "critical.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("from code_scalpel.server import func")

        test_file = tmp_path / "tests" / "not_critical.py"
        test_file.parent.mkdir()
        test_file.write_text("from code_scalpel.server import func")

        validator = ImportPathValidator(tmp_path)
        inventory = validator.build_inventory()

        critical_files = [f["file"] for f in inventory["critical_findings"]]
        assert "src/code_scalpel/critical.py" in critical_files
        assert "tests/not_critical.py" not in critical_files

    def test_detects_relative_imports(self, tmp_path):
        """Test detection of problematic relative imports."""
        test_file = tmp_path / "package" / "sub" / "module.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text(
            """
from ..server import func
from . import sibling
"""
        )

        validator = ImportPathValidator(tmp_path)
        results = validator.validate_file(test_file)

        # Should detect the relative import to server
        assert len(results["relative_imports"]) > 0

    def test_suggests_canonical_imports(self, tmp_path):
        """Test suggestion of canonical new import paths."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
# Old patterns
from code_scalpel.server import analyze_code
import code_scalpel.helpers as helpers
"""
        )

        validator = ImportPathValidator(tmp_path)
        results = validator.validate_file(test_file)

        suggestions = results["fix_suggestions"]
        assert len(suggestions) >= 2

        # Check specific suggestions
        server_suggestion = next(
            (s for s in suggestions if "server" in s["original"]), None
        )
        helpers_suggestion = next(
            (s for s in suggestions if "helpers" in s["original"]), None
        )

        assert server_suggestion
        assert "mcp.tools" in server_suggestion["suggested"]
        assert helpers_suggestion
        assert "mcp.helpers" in helpers_suggestion["suggested"]
