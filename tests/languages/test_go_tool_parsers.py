"""Go static analysis tool parser tests.

Validates GoParserRegistry and all six Go tool parsers:
golangci-lint, gosec, staticcheck, go vet, golint, gofmt.

All parsers require no installed CLI tools — they operate on fixture data.

[20260303_TEST] Created for Stage 3 Go tool parsers (Work-Tracking.md).
"""

from __future__ import annotations

import json

import pytest

# ---------------------------------------------------------------------------
# GoParserRegistry
# ---------------------------------------------------------------------------


class TestGoParserRegistry:
    """Tests for GoParserRegistry.get_parser() dispatch."""

    @pytest.mark.parametrize(
        "tool_name",
        ["golangci-lint", "gosec", "staticcheck", "govet", "golint", "gofmt"],
    )
    def test_get_parser_known_tools(self, tool_name):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        registry = GoParserRegistry()
        parser = registry.get_parser(tool_name)
        assert parser is not None

    def test_get_parser_unknown_raises(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        registry = GoParserRegistry()
        with pytest.raises(ValueError, match="Unknown Go parser"):
            registry.get_parser("nonexistent-tool")


# ---------------------------------------------------------------------------
# GolangciLintParser
# ---------------------------------------------------------------------------


class TestGolangciLintParser:
    """Tests for GolangciLintParser."""

    _JSON_OUTPUT = json.dumps(
        {
            "Issues": [
                {
                    "FromLinter": "errcheck",
                    "Text": "Error return value of `os.Remove` is not checked",
                    "Pos": {"Filename": "main.go", "Line": 25, "Column": 3},
                    "Severity": "error",
                },
                {
                    "FromLinter": "staticcheck",
                    "Text": "SA4006: this value of `x` is never used",
                    "Pos": {"Filename": "util.go", "Line": 10, "Column": 1},
                    "Severity": "warning",
                },
            ]
        }
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("golangci-lint")

    def test_parse_json_output_basic(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        assert len(issues) == 2
        assert issues[0].file_path == "main.go"
        assert issues[0].line == 25
        assert issues[0].linter == "errcheck"

    def test_parse_json_output_empty(self):
        parser = self._get_parser()
        assert parser.parse_json_output("") == []
        assert parser.parse_json_output("{}") == []

    def test_categorize_by_linter(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        cats = parser.categorize_by_linter(issues)
        assert "errcheck" in cats
        assert "staticcheck" in cats
        assert len(cats["errcheck"]) == 1

    def test_filter_by_severity_error(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        errors = parser.filter_by_severity(issues, min_severity="error")
        assert all(getattr(i.severity, "value", i.severity) == "error" for i in errors)

    def test_execute_golangci_lint_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_golangci_lint(".") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "golangci-lint"
        assert data["total"] == 2

    def test_generate_report_text(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        text = parser.generate_report(issues, format="text")
        assert "main.go" in text
        assert "errcheck" in text


# ---------------------------------------------------------------------------
# GosecParser
# ---------------------------------------------------------------------------


class TestGosecParser:
    """Tests for GosecParser."""

    _JSON_OUTPUT = json.dumps(
        {
            "Golang gosec": {
                "Issues": [
                    {
                        "severity": "HIGH",
                        "confidence": "HIGH",
                        "cwe": {
                            "id": "89",
                            "url": "https://cwe.mitre.org/data/definitions/89.html",
                        },
                        "rule_id": "G202",
                        "details": "SQL query construction using format string",
                        "code": "db.Query(fmt.Sprintf(...))",
                        "file": "db/queries.go",
                        "line": "31",
                        "column": "0",
                    },
                    {
                        "severity": "MEDIUM",
                        "confidence": "HIGH",
                        "cwe": {
                            "id": "22",
                            "url": "https://cwe.mitre.org/data/definitions/22.html",
                        },
                        "rule_id": "G304",
                        "details": "File path provided as taint input",
                        "code": "os.Open(input)",
                        "file": "store/files.go",
                        "line": "20",
                        "column": "3",
                    },
                ],
                "Stats": {"files": 10, "lines": 500, "nosec": 2, "found": 2},
            }
        }
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("gosec")

    def test_parse_json_output_basic(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        assert len(issues) == 2
        assert issues[0].rule_id == "G202"
        assert issues[0].severity == "HIGH"
        assert issues[0].file_path == "db/queries.go"
        assert issues[0].line == 31

    def test_parse_json_cwe_extraction(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        assert issues[0].cwe_id == "CWE-89"
        assert issues[1].cwe_id == "CWE-22"

    def test_parse_json_output_empty(self):
        parser = self._get_parser()
        assert parser.parse_json_output("") == []

    def test_map_to_cwe(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        cwe_map = parser.map_to_cwe(issues)
        assert "CWE-89" in cwe_map
        assert len(cwe_map["CWE-89"]) == 1

    def test_categorize_by_severity(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        cats = parser.categorize_by_severity(issues)
        assert "HIGH" in cats
        assert "MEDIUM" in cats

    def test_get_security_stats(self):
        parser = self._get_parser()
        stats = parser.get_security_stats(self._JSON_OUTPUT)
        assert stats.files == 10
        assert stats.lines == 500
        assert stats.found == 2

    def test_execute_gosec_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_gosec(".") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "gosec"
        assert data["total"] == 2

    def test_filter_by_severity_high_only(self):
        parser = self._get_parser()
        issues = parser.parse_json_output(self._JSON_OUTPUT)
        high_only = parser.filter_by_severity(issues, min_severity="HIGH")
        assert len(high_only) == 1
        assert high_only[0].severity == "HIGH"


# ---------------------------------------------------------------------------
# StaticcheckParser
# ---------------------------------------------------------------------------


class TestStaticcheckParser:
    """Tests for StaticcheckParser (JSONL format)."""

    _JSONL = "\n".join(
        [
            json.dumps(
                {
                    "code": "SA1006",
                    "severity": "error",
                    "location": {"file": "main.go", "line": 15, "column": 3},
                    "message": "Printf with dynamic first argument and no further arguments",
                }
            ),
            json.dumps(
                {
                    "code": "S1000",
                    "severity": "error",
                    "location": {"file": "util.go", "line": 8, "column": 1},
                    "message": "Use plain channel send or receive instead of single-case select",
                }
            ),
        ]
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("staticcheck")

    def test_parse_jsonl_output_basic(self):
        parser = self._get_parser()
        findings = parser.parse_jsonl_output(self._JSONL)
        assert len(findings) == 2
        assert findings[0].code == "SA1006"
        assert findings[0].location.file == "main.go"
        assert findings[0].location.line == 15

    def test_parse_jsonl_empty(self):
        parser = self._get_parser()
        assert parser.parse_jsonl_output("") == []

    def test_categorize_by_code_sa(self):
        from code_scalpel.code_parsers.go_parsers.go_parsers_staticcheck import (
            CheckCategory,
        )

        parser = self._get_parser()
        findings = parser.parse_jsonl_output(self._JSONL)
        cats = parser.categorize_by_code(findings)
        assert CheckCategory.STATICCHECK in cats
        assert CheckCategory.SIMPLE in cats

    def test_execute_staticcheck_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_staticcheck("./...") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        findings = parser.parse_jsonl_output(self._JSONL)
        data = json.loads(parser.generate_report(findings, format="json"))
        assert data["tool"] == "staticcheck"
        assert data["total"] == 2


# ---------------------------------------------------------------------------
# GovetParser
# ---------------------------------------------------------------------------


class TestGovetParser:
    """Tests for GovetParser."""

    _VET_OUTPUT = (
        "./main.go:42:13: fmt.Sprintf format %d has arg x of wrong type float64\n"
        "./pkg/server.go:10: Printf format %T has arg of wrong type *Server\n"
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("govet")

    def test_parse_vet_output_basic(self):
        parser = self._get_parser()
        issues = parser.parse_vet_output(self._VET_OUTPUT)
        assert len(issues) == 2
        assert issues[0].file_path == "./main.go"
        assert issues[0].line == 42
        assert issues[0].column == 13

    def test_parse_vet_output_no_col(self):
        parser = self._get_parser()
        issues = parser.parse_vet_output("./foo.go:5: declared but not used\n")
        assert len(issues) == 1
        assert issues[0].column == 0

    def test_parse_vet_output_empty(self):
        parser = self._get_parser()
        assert parser.parse_vet_output("") == []

    def test_infer_analyzer_printf(self):
        parser = self._get_parser()
        issues = parser.parse_vet_output("./a.go:1:1: Printf format %d mismatch\n")
        assert issues[0].analyzer == "printf"

    def test_categorize_by_analyzer(self):
        parser = self._get_parser()
        issues = parser.parse_vet_output(self._VET_OUTPUT)
        cats = parser.categorize_by_analyzer(issues)
        assert "printf" in cats

    def test_execute_govet_no_go(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_govet("./...") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_vet_output(self._VET_OUTPUT)
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "go vet"
        assert data["total"] == len(issues)


# ---------------------------------------------------------------------------
# GolintParser
# ---------------------------------------------------------------------------


class TestGolintParser:
    """Tests for GolintParser (deprecated)."""

    _LINT_OUTPUT = (
        "main.go:12:1: exported function Hello should have comment or be unexported\n"
        'util.go:5:1: package comment should be of the form "Package util ..."\n'
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("golint")

    def test_parse_lint_output_basic(self):
        parser = self._get_parser()
        suggestions = parser.parse_lint_output(self._LINT_OUTPUT)
        assert len(suggestions) == 2
        assert suggestions[0].file_path == "main.go"
        assert suggestions[0].line == 12
        assert suggestions[0].column == 1

    def test_parse_lint_output_empty(self):
        parser = self._get_parser()
        assert parser.parse_lint_output("") == []

    def test_categorize_by_rule_exported(self):
        parser = self._get_parser()
        suggestions = parser.parse_lint_output(self._LINT_OUTPUT)
        cats = parser.categorize_by_rule(suggestions)
        # "exported" keyword triggers rule_hint="exported"
        assert "exported" in cats or "comment" in cats

    def test_deprecation_warning_present(self):
        parser = self._get_parser()
        assert parser.DEPRECATION_WARNING
        assert (
            "deprecated" in parser.DEPRECATION_WARNING.lower()
            or "archived" in parser.DEPRECATION_WARNING.lower()
        )

    def test_execute_golint_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_golint("./...") == []

    def test_generate_report_json_deprecated_flag(self):
        parser = self._get_parser()
        suggestions = parser.parse_lint_output(self._LINT_OUTPUT)
        data = json.loads(parser.generate_report(suggestions, format="json"))
        assert data["deprecated"] is True


# ---------------------------------------------------------------------------
# GofmtParser
# ---------------------------------------------------------------------------


class TestGofmtParser:
    """Tests for GofmtParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.go_parsers import GoParserRegistry

        return GoParserRegistry().get_parser("gofmt")

    def test_parse_file_list_basic(self):
        parser = self._get_parser()
        output = "main.go\nutil/helper.go\n"
        files = parser.parse_file_list(output)
        assert files == ["main.go", "util/helper.go"]

    def test_parse_file_list_empty(self):
        parser = self._get_parser()
        assert parser.parse_file_list("") == []
        assert parser.parse_file_list("   \n  \n") == []

    def test_execute_gofmt_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_gofmt(".") == []

    def test_get_diff_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.get_diff("main.go") == ""

    def test_check_files_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.check_files(["main.go"]) == []

    def test_generate_report_json(self):
        from code_scalpel.code_parsers.go_parsers.go_parsers_gofmt import (
            FormattingIssue,
        )

        parser = self._get_parser()
        issues = [FormattingIssue(file_path="main.go", diff="--- main.go")]
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "gofmt"
        assert data["total_unformatted"] == 1

    def test_generate_report_text(self):
        from code_scalpel.code_parsers.go_parsers.go_parsers_gofmt import (
            FormattingIssue,
        )

        parser = self._get_parser()
        issues = [FormattingIssue(file_path="main.go")]
        text = parser.generate_report(issues, format="text")
        assert text == "main.go"
