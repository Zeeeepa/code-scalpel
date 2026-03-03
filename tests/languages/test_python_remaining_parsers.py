"""
Tests for Python remaining parsers: safety, isort, vulture, radon, interrogate.

[20260303_FEATURE] Stage 4a test suite – no tools need to be installed.
All subprocess/shutil.which calls are mocked via monkeypatch.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from code_scalpel.code_parsers.python_parsers.python_parsers_safety import (
    DependencyVulnerability,
    SafetyParser,
    Vulnerability,
)
from code_scalpel.code_parsers.python_parsers.python_parsers_isort import (
    IsortParser,
)
from code_scalpel.code_parsers.python_parsers.python_parsers_vulture import (
    SourceLocation,
    UnusedItem,
    VultureParser,
    VultureReport,
)
from code_scalpel.code_parsers.python_parsers.python_parsers_radon import (
    RadonParser,
)
from code_scalpel.code_parsers.python_parsers.python_parsers_interrogate import (
    InterrogateParser,
)


# ---------------------------------------------------------------------------
# TestSafetyParser
# ---------------------------------------------------------------------------


class TestSafetyParser:
    def test_parse_json_output_basic(self):
        """parse_json_output returns DependencyVulnerability list from pip-audit JSON."""
        parser = SafetyParser()
        payload = json.dumps(
            {
                "dependencies": [
                    {
                        "name": "flask",
                        "version": "0.12.2",
                        "vulns": [
                            {
                                "id": "GHSA-abc",
                                "fix_versions": ["1.0"],
                                "description": "Flask XSS",
                            }
                        ],
                    }
                ]
            }
        )
        result = parser.parse_json_output(payload)
        assert len(result) == 1
        assert result[0].package_name == "flask"
        assert result[0].current_version == "0.12.2"
        assert result[0].vulnerabilities[0].cve_id == "GHSA-abc"

    def test_parse_json_output_empty(self):
        """parse_json_output returns [] for empty or invalid JSON."""
        parser = SafetyParser()
        assert parser.parse_json_output("") == []
        assert parser.parse_json_output("not-json") == []

    def test_generate_report_json(self):
        """generate_report returns valid JSON with expected keys."""
        parser = SafetyParser()
        dep = DependencyVulnerability(
            package_name="requests",
            current_version="2.0.0",
            vulnerabilities=[
                Vulnerability(
                    cve_id="CVE-2023-001",
                    package_name="requests",
                    advisory="Remote code exec",
                    fixed_versions=["2.1.0"],
                )
            ],
        )
        report_str = parser.generate_report([dep])
        data = json.loads(report_str)
        assert data["tool"] == "safety"
        assert data["total"] == 1
        assert len(data["vulnerabilities"]) == 1
        assert data["vulnerabilities"][0]["id"] == "CVE-2023-001"

    def test_execute_pip_audit_no_binary(self, monkeypatch):
        """execute_pip_audit returns [] when pip-audit is not on PATH."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = SafetyParser()
        result = parser.execute_pip_audit()
        assert result == []

    def test_analyze_requirements_graceful_missing_tool(self, monkeypatch, tmp_path):
        """analyze_requirements_file returns SafetyReport with error when no tool found."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        req = tmp_path / "requirements.txt"
        req.write_text("flask==0.12.2\n")
        parser = SafetyParser()
        report = parser.analyze_requirements_file(req)
        assert report.error is not None
        assert report.vulnerabilities == []


# ---------------------------------------------------------------------------
# TestIsortParser
# ---------------------------------------------------------------------------


class TestIsortParser:
    def test_parse_diff_output(self):
        """parse_diff_output extracts filenames from unified diff."""
        parser = IsortParser()
        diff = "--- src/utils.py\t2026-01-01\n+++ src/utils.py\t2026-01-01\n"
        files = parser.parse_diff_output(diff)
        assert "src/utils.py" in files

    def test_parse_diff_output_empty(self):
        """parse_diff_output returns [] for empty diff text."""
        parser = IsortParser()
        assert parser.parse_diff_output("") == []

    def test_check_files_sorted(self, monkeypatch, tmp_path):
        """check_files returns True for sorted file when isort exits 0."""
        parser = IsortParser()
        f = tmp_path / "sorted.py"
        f.write_text("import os\n")

        def fake_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            return m

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/isort")
        result = parser.check_files([f])
        assert result[str(f)] is True

    def test_check_files_unsorted(self, monkeypatch, tmp_path):
        """check_files returns False for unsorted file when isort exits 1."""
        parser = IsortParser()
        f = tmp_path / "unsorted.py"
        f.write_text("import sys\nimport os\n")

        def fake_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 1
            return m

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/isort")
        result = parser.check_files([f])
        assert result[str(f)] is False

    def test_execute_isort_no_binary(self, monkeypatch):
        """execute_isort returns [] when isort is not on PATH."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = IsortParser()
        assert parser.execute_isort() == []

    def test_generate_report_json(self):
        """generate_report returns valid JSON with expected structure."""
        parser = IsortParser()
        findings = [{"file": "a.py", "is_sorted": False}]
        data = json.loads(parser.generate_report(findings))
        assert data["tool"] == "isort"
        assert data["total_unsorted"] == 1
        assert "a.py" in data["files"]


# ---------------------------------------------------------------------------
# TestVultureParser
# ---------------------------------------------------------------------------


class TestVultureParser:
    def test_parse_output_basic(self):
        """parse_output extracts UnusedItems from vulture text output."""
        parser = VultureParser()
        text = "myfile.py:10: unused function 'helper' (60% confidence)\n"
        items = parser.parse_output(text)
        assert len(items) == 1
        assert items[0].name == "helper"
        assert items[0].item_type == "function"
        assert items[0].location.line == 10
        assert items[0].confidence == 60

    def test_parse_output_empty_string(self):
        """parse_output returns [] for empty/unparseable output."""
        parser = VultureParser()
        assert parser.parse_output("") == []
        assert parser.parse_output("some random line without pattern") == []

    def test_categorize_dead_code(self):
        """categorize_dead_code buckets items by type."""
        parser = VultureParser()
        items = [
            UnusedItem(
                "fn1", "function", SourceLocation(line=1), confidence=80
            ),
            UnusedItem("Cls1", "class", SourceLocation(line=5), confidence=90),
            UnusedItem("x", "variable", SourceLocation(line=9), confidence=60),
        ]
        cats = parser.categorize_dead_code(items)
        assert len(cats["functions"]) == 1
        assert len(cats["classes"]) == 1
        assert len(cats["variables"]) == 1

    def test_filter_by_confidence(self):
        """filter_by_confidence removes items below the threshold."""
        parser = VultureParser()
        report = VultureReport(file_path="x.py")
        report.unused_functions = [
            UnusedItem("low", "function", SourceLocation(line=1), confidence=40),
            UnusedItem("high", "function", SourceLocation(line=2), confidence=90),
        ]
        filtered = parser.filter_by_confidence(report, min_confidence=80)
        assert len(filtered.unused_functions) == 1
        assert filtered.unused_functions[0].name == "high"

    def test_execute_vulture_no_binary(self, monkeypatch):
        """execute_vulture returns [] when vulture is not on PATH."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = VultureParser()
        assert parser.execute_vulture() == []

    def test_generate_report_json(self):
        """generate_report returns valid JSON with expected structure."""
        parser = VultureParser()
        items = [
            UnusedItem("do_stuff", "function", SourceLocation(line=42), confidence=80)
        ]
        data = json.loads(parser.generate_report(items))
        assert data["tool"] == "vulture"
        assert data["total"] == 1
        assert data["items"][0]["name"] == "do_stuff"


# ---------------------------------------------------------------------------
# TestRadonParser
# ---------------------------------------------------------------------------


class TestRadonParser:
    def test_parse_cc_json(self):
        """parse_cc_json extracts function entries from radon cc -j output."""
        parser = RadonParser()
        payload = json.dumps(
            {
                "example.py": [
                    {"type": "F", "name": "my_func", "lineno": 5, "complexity": 3, "rank": "A"}
                ]
            }
        )
        items = parser.parse_cc_json(payload)
        assert len(items) == 1
        assert items[0]["name"] == "my_func"
        assert items[0]["complexity"] == 3

    def test_parse_cc_json_invalid(self):
        """parse_cc_json returns [] for invalid JSON."""
        parser = RadonParser()
        assert parser.parse_cc_json("not-json") == []

    def test_parse_mi_json(self):
        """parse_mi_json extracts MI entries from radon mi -j output."""
        parser = RadonParser()
        payload = json.dumps(
            {"example.py": [{"name": "example.py", "mi": 85.2, "rank": "A"}]}
        )
        items = parser.parse_mi_json(payload)
        assert len(items) == 1
        assert items[0]["mi"] == pytest.approx(85.2)

    def test_categorize_by_grade(self):
        """categorize_by_grade groups items by rank field."""
        parser = RadonParser()
        items = [
            {"name": "simple", "complexity": 2, "rank": "A"},
            {"name": "complex", "complexity": 15, "rank": "C"},
        ]
        cats = parser.categorize_by_grade(items)
        assert len(cats["A"]) == 1
        assert len(cats["C"]) == 1

    def test_execute_radon_cc_no_binary(self, monkeypatch):
        """execute_radon_cc returns [] when radon is not on PATH."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = RadonParser()
        assert parser.execute_radon_cc() == []

    def test_generate_report_json(self):
        """generate_report returns valid JSON with expected structure."""
        parser = RadonParser()
        items = [{"name": "func", "complexity": 5, "rank": "A"}]
        data = json.loads(parser.generate_report(items))
        assert data["tool"] == "radon"
        assert data["total"] == 1
        assert data["items"][0]["name"] == "func"


# ---------------------------------------------------------------------------
# TestInterrogateParser
# ---------------------------------------------------------------------------


class TestInterrogateParser:
    def test_parse_json_output(self):
        """parse_json_output converts interrogate JSON list to list of dicts."""
        parser = InterrogateParser()
        payload = json.dumps(
            [
                {
                    "filename": "src/utils.py",
                    "docstring_coverage": 75.0,
                    "missing": ["function:helper", "class:MyClass"],
                }
            ]
        )
        result = parser.parse_json_output(payload)
        assert len(result) == 1
        assert result[0]["filename"] == "src/utils.py"
        assert result[0]["docstring_coverage"] == 75.0

    def test_parse_json_output_invalid(self):
        """parse_json_output returns [] for invalid JSON."""
        parser = InterrogateParser()
        assert parser.parse_json_output("") == []
        assert parser.parse_json_output("---") == []

    def test_get_coverage_summary(self):
        """get_coverage_summary computes avg_coverage and file list."""
        parser = InterrogateParser()
        results = [
            {"filename": "a.py", "docstring_coverage": 80.0},
            {"filename": "b.py", "docstring_coverage": 60.0},
        ]
        summary = parser.get_coverage_summary(results)
        assert summary["total_files"] == 2
        assert summary["avg_coverage"] == pytest.approx(70.0)
        assert "a.py" in summary["files"]

    def test_list_missing_docstrings(self):
        """list_missing_docstrings flattens missing entries across all files."""
        parser = InterrogateParser()
        results = [
            {"filename": "a.py", "missing": ["function:foo", "class:Bar"]},
            {"filename": "b.py", "missing": ["function:baz"]},
        ]
        missing = parser.list_missing_docstrings(results)
        assert "function:foo" in missing
        assert "function:baz" in missing
        assert len(missing) == 3

    def test_execute_interrogate_no_binary(self, monkeypatch):
        """execute_interrogate returns [] when interrogate is not on PATH."""
        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = InterrogateParser()
        assert parser.execute_interrogate() == []

    def test_generate_report_json(self):
        """generate_report returns valid JSON with expected structure."""
        parser = InterrogateParser()
        findings = [{"filename": "src/main.py", "docstring_coverage": 50.0, "missing": []}]
        data = json.loads(parser.generate_report(findings))
        assert data["tool"] == "interrogate"
        assert data["total"] == 1
        assert data["avg_coverage"] == pytest.approx(50.0)
