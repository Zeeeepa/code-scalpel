"""Tests for analyze_deprecated_code.py script."""

import json

from scripts.analyze_deprecated_code import DeprecatedCodeAnalyzer


class TestAnalyzeDeprecatedCode:
    """Test suite for deprecated code analysis."""

    def test_detects_deprecation_markers(self, tmp_path):
        """Test detection of deprecation marker comments."""
        # Create test file with deprecation marker
        test_file = tmp_path / "deprecated.py"
        test_file.write_text("""
# [20260120_DEPRECATED] This function is deprecated
def old_function():
    pass

def new_function():
    pass
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(test_file)

        assert results["has_deprecation_marker"]
        assert any(
            "deprecated" in marker["text"].lower()
            for marker in results["deprecation_markers"]
        )

    def test_counts_imports_ast(self, tmp_path):
        """Test AST-based import counting."""
        # Create files with imports
        module_file = tmp_path / "module.py"
        module_file.write_text("""
import os
from pathlib import Path
""")

        importer_file = tmp_path / "importer.py"
        importer_file.write_text("""
import module
from module import os
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(importer_file)

        assert results["import_count"] > 0
        assert "module" in results["imports"]

    def test_detects_legacy_functions(self, tmp_path):
        """Test detection of legacy function definitions."""
        test_file = tmp_path / "legacy.py"
        test_file.write_text("""
# Legacy function without modern patterns
def old_style_function(arg1, arg2):
    return arg1 + arg2

def modern_function(arg1: int, arg2: int) -> int:
    return arg1 + arg2
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(test_file)

        assert len(results["legacy_functions"]) > 0
        assert "old_style_function" in results["legacy_functions"]

    def test_datetime_now_detection(self, tmp_path):
        """Test detection of datetime.now() without timezone."""
        test_file = tmp_path / "datetime_usage.py"
        test_file.write_text("""
import datetime

# Bad: no timezone
now = datetime.datetime.now()

# Good: with timezone
utc_now = datetime.datetime.now(datetime.timezone.utc)
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(test_file)

        assert results["has_datetime_now_without_tz"]
        assert len(results["datetime_now_locations"]) > 0

    def test_json_output_format(self, tmp_path):
        """Test JSON output generation."""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("# [20260120_DEPRECATED] test")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        inventory = analyzer.build_inventory()

        # Should be serializable
        json_str = json.dumps(inventory, indent=2)
        assert json_str

        # Should have expected structure
        assert "files" in inventory
        assert "summary" in inventory
        assert len(inventory["files"]) > 0

    def test_min_import_threshold_filtering(self, tmp_path):
        """Test filtering by minimum import threshold."""
        # Create files with varying import counts
        low_import_file = tmp_path / "low.py"
        low_import_file.write_text("import os")

        high_import_file = tmp_path / "high.py"
        high_import_file.write_text("""
import os
import sys
import pathlib
from datetime import datetime
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path, min_import_threshold=3)
        inventory = analyzer.build_inventory()

        # Only high import file should be included
        file_names = [f["file"] for f in inventory["files"]]
        assert "high.py" in file_names
        assert "low.py" not in file_names

    def test_caller_detection(self, tmp_path):
        """Test detection of callers to deprecated functions."""
        # Create deprecated function
        deprecated_file = tmp_path / "deprecated.py"
        deprecated_file.write_text("""
def deprecated_func():
    pass
""")

        # Create caller
        caller_file = tmp_path / "caller.py"
        caller_file.write_text("""
from deprecated import deprecated_func

deprecated_func()
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(deprecated_file)

        assert results["caller_count"] > 0
        assert "caller.py" in results["callers"]

    def test_migration_guidance_detection(self, tmp_path):
        """Test detection of migration guidance strings."""
        test_file = tmp_path / "migration.py"
        test_file.write_text("""
# TODO: migrate to new_function
# Migration: use new_module.new_function instead
def old_function():
    pass
""")

        analyzer = DeprecatedCodeAnalyzer(tmp_path)
        results = analyzer.analyze_file(test_file)

        assert results["has_migration_guidance"]
        assert len(results["migration_guidance"]) > 0
