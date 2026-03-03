"""C++ static-analysis tool parser tests.

Validates CppParserRegistry and all six C++ tool parsers:
Cppcheck, clang-tidy, Clang Static Analyzer, cpplint, Coverity, SonarQube.

All parsers require no installed CLI tools — they operate on fixture data.

[20260303_TEST] Created for Phase 2 C++ tool parsers (Work-Tracking.md).
"""

from __future__ import annotations

import json
import textwrap

import pytest


# ---------------------------------------------------------------------------
# CppParserRegistry
# ---------------------------------------------------------------------------


class TestCppParserRegistry:
    """Tests for CppParserRegistry.get_parser() dispatch."""

    @pytest.mark.parametrize(
        "tool_name",
        [
            "cppcheck",
            "clang-tidy",
            "clang_tidy",
            "clang-sa",
            "clang-static-analyzer",
            "cpplint",
            "coverity",
            "sonarqube",
            "sonar",
        ],
    )
    def test_get_parser_known_tools(self, tool_name):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        parser = registry.get_parser(tool_name)
        assert parser is not None

    def test_get_parser_unknown_raises(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        with pytest.raises(ValueError, match=r"Unknown C\+\+ parser tool"):
            registry.get_parser("nonexistent-tool")

    def test_analyze_returns_dict(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        results = registry.analyze(".")
        assert isinstance(results, dict)
        for key, val in results.items():
            assert isinstance(val, list)

    def test_analyze_selected_tools(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        results = registry.analyze(".", tools=["cppcheck", "cpplint"])
        assert set(results.keys()) == {"cppcheck", "cpplint"}

    def test_toplevel_lazy_import_cppcheck(self):
        from code_scalpel.code_parsers.cpp_parsers import CppcheckParser

        assert CppcheckParser is not None

    def test_toplevel_lazy_import_sonarqube(self):
        from code_scalpel.code_parsers.cpp_parsers import SonarQubeCppParser

        assert SonarQubeCppParser is not None


# ---------------------------------------------------------------------------
# CppcheckParser
# ---------------------------------------------------------------------------

_CPPCHECK_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <results version="2">
        <cppcheck version="2.13"/>
        <errors>
            <error id="memLeak" severity="error"
                   msg="Memory leak: ptr" verbose="Memory leak detected">
                <location file="src/main.cpp" line="42" column="5"/>
            </error>
            <error id="arrayIndexOutOfBounds" severity="error"
                   msg="Array access out of bounds" verbose="Array 'buf' accessed at index 10" cwe="125">
                <location file="src/utils.cpp" line="17" column="9"/>
            </error>
            <error id="redundantCopy" severity="style"
                   msg="Redundant data copied" verbose="Redundant copy for performance">
                <location file="src/main.cpp" line="88" column="1"/>
            </error>
        </errors>
    </results>
""")


class TestCppcheckParser:
    """Tests for CppcheckParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("cppcheck")

    def test_parse_xml_string_basic(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        assert len(issues) == 3

    def test_parse_xml_file_paths(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        paths = {i.file_path for i in issues}
        assert "src/main.cpp" in paths
        assert "src/utils.cpp" in paths

    def test_parse_xml_line_numbers(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        assert issues[0].line_number == 42
        assert issues[1].line_number == 17

    def test_parse_xml_cwe_extraction(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        # arrayIndexOutOfBounds has cwe="125"
        array_issue = next(i for i in issues if i.issue_id == "arrayIndexOutOfBounds")
        assert array_issue.cwe_id == "CWE-125"

    def test_parse_xml_invalid_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_xml_string("not xml at all") == []

    def test_parse_xml_empty_errors_returns_empty(self):
        xml = '<?xml version="1.0"?><results version="2"><errors></errors></results>'
        parser = self._get_parser()
        assert parser.parse_xml_string(xml) == []

    def test_execute_cppcheck_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        from pathlib import Path

        assert parser.execute_cppcheck([Path(".")]) == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        report = parser.generate_report(issues, format="json")
        data = json.loads(report)
        assert data["tool"] == "cppcheck"
        assert len(data["issues"]) == 3

    def test_generate_report_text(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        text = parser.generate_report(issues, format="text")
        assert "main.cpp" in text
        assert "memLeak" in text

    def test_categorize_issues(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        cats = parser.categorize_issues(issues)
        assert isinstance(cats, dict)
        # At least memory and performance categories should have entries
        all_issues = [i for lst in cats.values() for i in lst]
        assert len(all_issues) == 3

    def test_map_to_cwe(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        cwe_map = parser.map_to_cwe(issues)
        assert "CWE-125" in cwe_map

    def test_sarif_output(self):
        parser = self._get_parser()
        issues = parser.parse_xml_string(_CPPCHECK_XML)
        sarif_str = parser.generate_report(issues, format="sarif")
        sarif = json.loads(sarif_str)
        assert isinstance(sarif, dict)
        assert "runs" in sarif


# ---------------------------------------------------------------------------
# ClangTidyParser
# ---------------------------------------------------------------------------

_CLANG_TIDY_OUTPUT = textwrap.dedent("""\
    src/main.cpp:12:5: warning: use of auto is redundant [modernize-use-auto]
      auto x = 42;
        ^
    src/utils.cpp:25:9: warning: function 'foo' has cognitive complexity of 15 [readability-function-cognitive-complexity]
    src/main.cpp:55:3: error: use nullptr instead of 0 for pointers [modernize-use-nullptr]
""")


class TestClangTidyParser:
    """Tests for ClangTidyParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("clang-tidy")

    def test_parse_diagnostic_output_basic(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        assert len(checks) == 3

    def test_parse_diagnostic_file_paths(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        paths = {c.file_path for c in checks}
        assert "src/main.cpp" in paths
        assert "src/utils.cpp" in paths

    def test_parse_diagnostic_line_numbers(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        first = checks[0]
        assert first.line_number == 12
        assert first.column == 5

    def test_parse_diagnostic_check_ids(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        check_ids = {c.check_id for c in checks}
        assert "modernize-use-auto" in check_ids
        assert "modernize-use-nullptr" in check_ids

    def test_parse_diagnostic_severity(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        severities = {c.severity for c in checks}
        assert "warning" in severities
        assert "error" in severities

    def test_parse_empty_output_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_diagnostic_output("") == []

    def test_parse_output_no_match_lines_skipped(self):
        parser = self._get_parser()
        output = "   ^  \n  some unrelated line\n"
        assert parser.parse_diagnostic_output(output) == []

    def test_categorize_checks(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        cats = parser.categorize_checks(checks)
        assert isinstance(cats, dict)
        all_checks = [c for lst in cats.values() for c in lst]
        assert len(all_checks) == 3

    def test_execute_clang_tidy_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        from pathlib import Path

        assert parser.execute_clang_tidy([Path("src/main.cpp")]) == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        report = parser.generate_report(checks, format="json")
        data = json.loads(report)
        assert data["tool"] == "clang-tidy"
        assert data["summary"]["total"] == 3

    def test_generate_report_text(self):
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        text = parser.generate_report(checks, format="text")
        assert "main.cpp" in text

    def test_modernization_level_field_accessible(self):
        # modernization_level is set to None when the check name does not
        # embed a versioned suffix (cpp11/14/17/20). The field must exist.
        parser = self._get_parser()
        checks = parser.parse_diagnostic_output(_CLANG_TIDY_OUTPUT)
        modernize = [c for c in checks if c.check_id.startswith("modernize-")]
        assert modernize
        # The attribute is always present; its value may be None for generic checks.
        assert hasattr(modernize[0], "modernization_level")


# ---------------------------------------------------------------------------
# ClangStaticAnalyzerParser
# ---------------------------------------------------------------------------


class TestClangStaticAnalyzerParser:
    """Tests for ClangStaticAnalyzerParser (scan-build / plist)."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("clang-sa")

    def test_instantiation(self):
        parser = self._get_parser()
        assert parser is not None

    def test_execute_scan_build_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        from pathlib import Path

        result = parser.execute_scan_build([Path(".")])
        assert result == []

    def test_parse_clang_output_no_crash(self):
        parser = self._get_parser()
        # parse_clang_output operates on AST dump; should not raise.
        parser.parse_clang_output("### Section\n## Entity\nsome line\n")

    def test_parse_plist_report_missing_file(self, tmp_path):
        parser = self._get_parser()
        result = parser.parse_plist_report(tmp_path / "missing.plist")
        assert result == []

    def test_parse_html_report_dir_empty(self, tmp_path):
        parser = self._get_parser()
        result = parser.parse_html_report_dir(tmp_path)
        assert result == []

    def test_filter_memory_bugs_empty(self):
        parser = self._get_parser()
        assert parser.filter_memory_bugs([]) == []

    def test_generate_report_no_findings(self):
        parser = self._get_parser()
        report = parser.generate_report([], format="json")
        data = json.loads(report)
        assert data["summary"]["total"] == 0

    def test_generate_report_text_empty(self):
        parser = self._get_parser()
        text = parser.generate_report([], format="text")
        assert "clang" in text.lower() or "0" in text

    def test_get_parser_alias_clang_static_analyzer(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        p1 = registry.get_parser("clang-sa")
        p2 = registry.get_parser("clang-static-analyzer")
        assert type(p1) is type(p2)


# ---------------------------------------------------------------------------
# CppLintParser
# ---------------------------------------------------------------------------

_CPPLINT_OUTPUT = textwrap.dedent("""\
    src/main.cpp:42:  Missing space before \t  [whitespace/tab] [1]
    src/utils.cpp:10:  Lines should be <= 80 characters long  [whitespace/line_length] [2]
    src/main.cpp:88:  Include the directory when naming header files  [build/include] [4]
    Done processing src/main.cpp
    Total errors found: 3
""")


class TestCppLintParser:
    """Tests for CppLintParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("cpplint")

    def test_parse_cpplint_output_basic(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        assert len(violations) == 3

    def test_parse_cpplint_file_paths(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        paths = {v.file_path for v in violations}
        assert "src/main.cpp" in paths
        assert "src/utils.cpp" in paths

    def test_parse_cpplint_line_numbers(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        assert violations[0].line_number == 42

    def test_parse_cpplint_empty_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_cpplint_output("") == []

    def test_parse_cpplint_confidence_levels(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        confs = {v.confidence for v in violations}
        assert 1 in confs
        assert 4 in confs

    def test_execute_cpplint_no_binary(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        from pathlib import Path

        assert parser.execute_cpplint([Path("src/main.cpp")]) == []

    def test_categorize_violations(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        cats = parser.categorize_violations(violations)
        assert isinstance(cats, dict)
        total = sum(len(v) for v in cats.values())
        assert total == 3

    def test_calculate_style_score(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        score = parser.calculate_style_score(violations, total_lines=100)
        assert 0.0 <= score <= 100.0

    def test_generate_report_json(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        report = parser.generate_report(violations, format="json")
        data = json.loads(report)
        assert data["tool"] == "cpplint"
        assert data["summary"]["total"] == 3

    def test_generate_report_text(self):
        parser = self._get_parser()
        violations = parser.parse_cpplint_output(_CPPLINT_OUTPUT)
        text = parser.generate_report(violations, format="text")
        assert "main.cpp" in text


# ---------------------------------------------------------------------------
# CoverityParser
# ---------------------------------------------------------------------------

_COVERITY_JSON = json.dumps(
    {
        "issues": [
            {
                "mergeKey": "10001",
                "checkerName": "NULL_RETURNS",
                "severity": "high",
                "cwe": "476",
                "events": [
                    {
                        "filePathname": "src/engine.cpp",
                        "lineNumber": 55,
                        "eventDescription": "Return value is NULL.",
                    }
                ],
            },
            {
                "mergeKey": "10002",
                "checkerName": "RESOURCE_LEAK",
                "severity": "medium",
                "events": [
                    {
                        "filePathname": "src/io.cpp",
                        "lineNumber": 30,
                        "eventDescription": "Resource acquired but never released.",
                    }
                ],
            },
            {
                "mergeKey": "10003",
                "checkerName": "TAINTED_DATA",
                "severity": "high",
                "cwe": "89",
                "events": [
                    {
                        "filePathname": "src/db.cpp",
                        "lineNumber": 77,
                        "eventDescription": "Tainted string used in SQL query.",
                    }
                ],
            },
        ]
    }
)


class TestCoverityParser:
    """Tests for CoverityParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("coverity")

    def test_parse_json_string_basic(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        assert len(defects) == 3

    def test_parse_json_string_file_paths(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        paths = {d.file_path for d in defects}
        assert "src/engine.cpp" in paths
        assert "src/io.cpp" in paths

    def test_parse_json_string_line_numbers(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        assert defects[0].line_number == 55
        assert defects[1].line_number == 30

    def test_parse_json_cwe_extraction(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        null_def = next(d for d in defects if "NULL" in d.defect_id or d.cwe_id == "CWE-476")
        assert null_def.cwe_id == "CWE-476"

    def test_parse_json_invalid_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_json_string("not json") == []

    def test_parse_json_empty_issues_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_json_string('{"issues": []}') == []

    def test_parse_coverity_json_merged_defects_key(self):
        parser = self._get_parser()
        data = {
            "mergedDefects": [
                {
                    "mergeKey": "20001",
                    "checkerName": "MEMORY_LEAK",
                    "severity": "high",
                    "events": [
                        {
                            "filePathname": "src/alloc.cpp",
                            "lineNumber": 10,
                            "eventDescription": "Leak detected.",
                        }
                    ],
                }
            ]
        }
        defects = parser.parse_coverity_json(data)
        assert len(defects) == 1
        assert defects[0].file_path == "src/alloc.cpp"

    def test_categorize_defects(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        cats = parser.categorize_defects(defects)
        assert isinstance(cats, dict)
        all_def = [d for lst in cats.values() for d in lst]
        assert len(all_def) == 3

    def test_map_to_cwe(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        cwe_map = parser.map_to_cwe(defects)
        assert "CWE-476" in cwe_map
        assert "CWE-89" in cwe_map

    def test_analyze_security_risks(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        summary = parser.analyze_security_risks(defects)
        assert summary["total_defects"] == 3
        assert summary["security_defects"] >= 1

    def test_to_sarif_output(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        sarif_str = parser.generate_report(defects, format="sarif")
        sarif = json.loads(sarif_str)
        assert "runs" in sarif

    def test_generate_report_json(self):
        parser = self._get_parser()
        defects = parser.parse_json_string(_COVERITY_JSON)
        report = parser.generate_report(defects, format="json")
        data = json.loads(report)
        assert data["tool"] == "coverity"
        assert data["summary"]["total"] == 3

    def test_execute_coverity_raises_not_implemented(self):
        """Coverity requires a licensed install; execute_coverity raises NotImplementedError."""
        parser = self._get_parser()
        from pathlib import Path

        with pytest.raises(NotImplementedError):
            parser.execute_coverity([Path(".")])


# ---------------------------------------------------------------------------
# SonarQubeCppParser
# ---------------------------------------------------------------------------

_SONAR_JSON = json.dumps(
    {
        "issues": [
            {
                "key": "AYZabc001",
                "rule": "cpp:S5766",
                "severity": "CRITICAL",
                "component": "project:src/main.cpp",
                "line": 42,
                "message": "Null dereference detected.",
                "effort": "10min",
                "debt": "10min",
                "type": "BUG",
                "tags": ["cwe", "sans-top25"],
            },
            {
                "key": "AYZabc002",
                "rule": "cpp:S2068",
                "severity": "BLOCKER",
                "component": "project:src/config.cpp",
                "line": 15,
                "message": "Hardcoded credentials found.",
                "effort": "30min",
                "debt": "30min",
                "type": "VULNERABILITY",
                "tags": ["cwe"],
            },
            {
                "key": "AYZabc003",
                "rule": "cpp:S1135",
                "severity": "INFO",
                "component": "project:src/todo.cpp",
                "line": 77,
                "message": "Complete the task associated with this TODO comment.",
                "effort": "0min",
                "debt": "0min",
                "type": "CODE_SMELL",
                "tags": [],
            },
        ]
    }
)


class TestSonarQubeCppParser:
    """Tests for SonarQubeCppParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        return CppParserRegistry().get_parser("sonarqube")

    def test_parse_issues_json_basic(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        assert len(issues) == 3

    def test_parse_issues_json_fields(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        first = issues[0]
        assert first.rule == "cpp:S5766"
        assert first.severity == "CRITICAL"
        assert first.line == 42
        assert "null" in first.message.lower()

    def test_parse_issues_json_types(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        types = {i.issue_type for i in issues}
        assert "BUG" in types
        assert "VULNERABILITY" in types
        assert "CODE_SMELL" in types

    def test_parse_issues_json_invalid_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_issues_json("not json") == []

    def test_parse_issues_json_empty_returns_empty(self):
        parser = self._get_parser()
        assert parser.parse_issues_json('{"issues": []}') == []

    def test_get_vulnerabilities(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        vulns = parser.get_vulnerabilities(issues)
        assert len(vulns) == 1
        assert vulns[0].rule == "cpp:S2068"

    def test_get_bugs(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        bugs = parser.get_bugs(issues)
        assert len(bugs) == 1
        assert bugs[0].rule == "cpp:S5766"

    def test_get_by_severity(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        critical = parser.get_by_severity(issues, "CRITICAL")
        assert len(critical) == 1

    def test_map_to_cwe_known_rule(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        cwe_map = parser.map_to_cwe(issues)
        # cpp:S5766 → CWE-476, cpp:S2068 → CWE-798
        assert "CWE-476" in cwe_map or "CWE-798" in cwe_map

    def test_categorize_issues(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        cats = parser.categorize_issues(issues)
        assert isinstance(cats, dict)

    def test_to_sarif(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        sarif_str = parser.generate_report(issues, format="sarif")
        sarif = json.loads(sarif_str)
        assert "runs" in sarif

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        report = parser.generate_report(issues, format="json")
        data = json.loads(report)
        assert data["tool"] == "sonarqube"
        assert data["summary"]["total"] == 3

    def test_generate_report_text(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(_SONAR_JSON)
        text = parser.generate_report(issues, format="text")
        assert "main.cpp" in text or "project:src/main.cpp" in text

    def test_get_metrics_empty(self):
        parser = self._get_parser()
        metrics = parser.get_metrics({})
        assert hasattr(metrics, "bugs")

    def test_parse_issues_from_file_missing(self, tmp_path):
        parser = self._get_parser()
        result = parser.parse_issues_from_file(tmp_path / "missing.json")
        assert result == []
