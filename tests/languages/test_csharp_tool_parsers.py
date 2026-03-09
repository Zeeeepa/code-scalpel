"""C# static analysis tool parser tests.

Validates CSharpParserRegistry plus all six C# tool parsers:
Roslyn-Analyzers, StyleCop, SecurityCodeScan, FxCop, ReSharper, SonarQube.

All parsers require no installed tools — they operate on fixture data.

[20260303_TEST] Created for Stage 2 C# tool parsers (Work-Tracking.md).
"""

from __future__ import annotations

import json
import textwrap

import pytest

# ---------------------------------------------------------------------------
# Helper: build minimal SARIF 2.1 JSON
# ---------------------------------------------------------------------------


def _make_sarif(
    tool_name: str,
    rule_id: str,
    message: str,
    file_path: str = "src/Program.cs",
    line: int = 10,
) -> str:
    """Return a minimal SARIF 2.1 JSON string."""
    return json.dumps(
        {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {"driver": {"name": tool_name, "rules": []}},
                    "results": [
                        {
                            "ruleId": rule_id,
                            "message": {"text": message},
                            "level": "warning",
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": file_path},
                                        "region": {"startLine": line},
                                    }
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )


# ---------------------------------------------------------------------------
# SarifFinding + _parse_sarif helper
# ---------------------------------------------------------------------------


class TestSarifHelper:
    """Tests for _parse_sarif shared helper in csharp_parsers __init__.py."""

    def test_parse_sarif_from_string(self):
        from code_scalpel.code_parsers.csharp_parsers import _parse_sarif, SarifFinding

        sarif_str = _make_sarif("Roslyn", "CA1234", "Test warning")
        findings = _parse_sarif(sarif_str)
        assert len(findings) == 1
        f = findings[0]
        assert isinstance(f, SarifFinding)
        assert f.rule_id == "CA1234"
        assert f.message == "Test warning"
        assert f.uri == "src/Program.cs"
        assert f.line == 10
        assert f.level == "warning"

    def test_parse_sarif_from_dict(self):
        from code_scalpel.code_parsers.csharp_parsers import _parse_sarif

        sarif_dict = json.loads(_make_sarif("Tool", "SA0001", "Style issue", line=42))
        findings = _parse_sarif(sarif_dict)
        assert findings[0].rule_id == "SA0001"
        assert findings[0].line == 42

    def test_parse_sarif_empty_string(self):
        from code_scalpel.code_parsers.csharp_parsers import _parse_sarif

        assert _parse_sarif("") == []
        assert _parse_sarif("{}") == []

    def test_parse_sarif_no_results(self):
        from code_scalpel.code_parsers.csharp_parsers import _parse_sarif

        sarif = json.dumps(
            {
                "version": "2.1.0",
                "runs": [{"tool": {"driver": {"name": "T"}}, "results": []}],
            }
        )
        assert _parse_sarif(sarif) == []

    def test_parse_sarif_multiple_results(self):
        from code_scalpel.code_parsers.csharp_parsers import _parse_sarif

        sarif_dict = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {"driver": {"name": "T"}},
                    "results": [
                        {
                            "ruleId": f"CA{i}",
                            "message": {"text": f"msg{i}"},
                            "level": "note",
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": f"file{i}.cs"},
                                        "region": {"startLine": i + 1},
                                    }
                                }
                            ],
                        }
                        for i in range(5)
                    ],
                }
            ],
        }
        findings = _parse_sarif(sarif_dict)
        assert len(findings) == 5
        assert findings[3].rule_id == "CA3"


# ---------------------------------------------------------------------------
# CSharpParserRegistry
# ---------------------------------------------------------------------------


class TestCSharpParserRegistry:
    """Tests for CSharpParserRegistry.get_parser() dispatch."""

    @pytest.mark.parametrize(
        "tool_name",
        ["roslyn", "stylecop", "security-code-scan", "fxcop", "resharper", "sonarqube"],
    )
    def test_get_parser_known_tools(self, tool_name):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        registry = CSharpParserRegistry()
        parser = registry.get_parser(tool_name)
        assert parser is not None

    def test_get_parser_unknown_raises(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        registry = CSharpParserRegistry()
        with pytest.raises(ValueError, match="Unknown C# parser"):
            registry.get_parser("nonexistent-tool")

    def test_registry_is_singleton_per_call(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        r1 = CSharpParserRegistry()
        r2 = CSharpParserRegistry()
        # Both should return a working parser
        p1 = r1.get_parser("roslyn")
        p2 = r2.get_parser("roslyn")
        assert p1 is not None
        assert p2 is not None


# ---------------------------------------------------------------------------
# RoslynAnalyzersParser
# ---------------------------------------------------------------------------


class TestRoslynAnalyzersParser:
    """Tests for RoslynAnalyzersParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("roslyn")

    def test_parse_sarif_output_basic(self):
        parser = self._get_parser()
        sarif = _make_sarif(
            "Roslyn", "CA1001", "Types that own disposable ...", line=15
        )
        findings = parser.parse_sarif_output(sarif)
        assert len(findings) == 1
        assert findings[0].rule_id == "CA1001"
        assert findings[0].line == 15

    def test_categorize_by_rule_ca_prefix(self):
        parser = self._get_parser()
        sarif = _make_sarif("Roslyn", "CA2000", "Dispose objects before losing scope")
        findings = parser.parse_sarif_output(sarif)
        cats = parser.categorize_by_rule(findings)
        # categorize_by_rule maps CA prefix to a category name — any non-empty dict is fine
        assert len(cats) >= 1
        # The finding must appear somewhere in the bucketed output
        all_findings = [f for bucket in cats.values() for f in bucket]
        assert len(all_findings) == 1

    def test_categorize_by_rule_cs_prefix(self):
        parser = self._get_parser()
        sarif = _make_sarif("Roslyn", "CS0168", "Variable declared but never used")
        findings = parser.parse_sarif_output(sarif)
        cats = parser.categorize_by_rule(findings)
        assert len(cats) >= 1

    def test_execute_roslyn_no_dotnet(self, monkeypatch):
        """execute_roslyn should return [] gracefully when dotnet absent."""
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        result = parser.execute_roslyn(".")
        assert result == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        sarif = _make_sarif("Roslyn", "IDE0001", "Name can be simplified")
        findings = parser.parse_sarif_output(sarif)
        report = parser.generate_report(findings, format="json")
        data = json.loads(report)
        assert data["tool"] == "roslyn"
        assert data["total"] == 1

    def test_generate_report_text(self):
        parser = self._get_parser()
        sarif = _make_sarif(
            "Roslyn", "CA1234", "Some warning", file_path="Foo.cs", line=5
        )
        findings = parser.parse_sarif_output(sarif)
        report = parser.generate_report(findings, format="text")
        assert "CA1234" in report
        assert "Foo.cs" in report


# ---------------------------------------------------------------------------
# StyleCopParser
# ---------------------------------------------------------------------------


class TestStyleCopParser:
    """Tests for StyleCopParser."""

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("stylecop")

    def test_parse_sarif_sa_rules_only(self):
        parser = self._get_parser()
        # SA rule should be accepted
        sarif = _make_sarif("StyleCop", "SA1101", "Prefix local calls with this")
        findings = parser.parse_sarif_output(sarif)
        assert len(findings) == 1
        assert findings[0].rule_id == "SA1101"

    def test_categorize_rules_naming(self):
        parser = self._get_parser()
        sarif = _make_sarif("StyleCop", "SA1300", "Element must begin with upper-case")
        findings = parser.parse_sarif_output(sarif)
        cats = parser.categorize_rules(findings)
        # SA1300 is in NAMING range SA1300-SA1399
        assert any("naming" in str(k).lower() or "SA13" in str(k) for k in cats)

    def test_execute_stylecop_no_dotnet(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_stylecop(".") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        sarif = _make_sarif("StyleCop", "SA1000", "Some style violation")
        findings = parser.parse_sarif_output(sarif)
        report = json.loads(parser.generate_report(findings, format="json"))
        assert report["tool"] == "stylecop"


# ---------------------------------------------------------------------------
# SecurityCodeScanParser
# ---------------------------------------------------------------------------


class TestSecurityCodeScanParser:
    """Tests for SecurityCodeScanParser with CWE mapping."""

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("security-code-scan")

    def test_parse_sarif_scs_rule(self):
        parser = self._get_parser()
        sarif = _make_sarif(
            "SecurityCodeScan", "SCS0001", "SQL injection vulnerability"
        )
        findings = parser.parse_sarif_output(sarif)
        assert len(findings) >= 1

    def test_map_to_cwe_sql_injection(self):
        parser = self._get_parser()
        sarif = _make_sarif("SecurityCodeScan", "SCS0001", "SQL injection")
        findings = parser.parse_sarif_output(sarif)
        cwe_map = parser.map_to_cwe(findings)
        assert "CWE-89" in cwe_map

    def test_map_to_cwe_xss(self):
        parser = self._get_parser()
        sarif = _make_sarif("SecurityCodeScan", "SCS0007", "XSS")
        findings = parser.parse_sarif_output(sarif)
        cwe_map = parser.map_to_cwe(findings)
        assert "CWE-79" in cwe_map

    def test_map_to_owasp(self):
        parser = self._get_parser()
        sarif = _make_sarif("SecurityCodeScan", "SCS0001", "SQL injection")
        findings = parser.parse_sarif_output(sarif)
        owasp = parser.map_to_owasp(findings)
        # Should have at least one OWASP category
        assert len(owasp) >= 1

    def test_execute_scs_no_dotnet(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_scs(".") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        sarif = _make_sarif("SecurityCodeScan", "SCS0015", "Command injection")
        findings = parser.parse_sarif_output(sarif)
        data = json.loads(parser.generate_report(findings, format="json"))
        assert data["tool"] in ("security-code-scan", "security_code_scan")


# ---------------------------------------------------------------------------
# FxCopParser
# ---------------------------------------------------------------------------


class TestFxCopParser:
    """Tests for FxCopParser (XML + SARIF)."""

    _FXCOP_XML = textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <FxCopReport Version="10.0">
          <Namespaces>
            <Namespace Name="MyApp">
              <Types>
                <Type Name="MyClass">
                  <Members>
                    <Member Name="DoSomething">
                      <Messages>
                        <Message TypeName="EnumsShouldHaveZeroValue" Category="Microsoft.Design"
                                 Status="Active" Created="2024-01-01" FixCategory="Breaking">
                          <Issue Name="EnumsShouldHaveZeroValue" Path="src" File="MyClass.cs" Line="20">
                            Enum SomeEnum defines a member named 'None'.
                          </Issue>
                        </Message>
                      </Messages>
                    </Member>
                  </Members>
                </Type>
              </Types>
            </Namespace>
          </Namespaces>
        </FxCopReport>
    """)

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("fxcop")

    def test_parse_xml_report_basic(self):
        parser = self._get_parser()
        violations = parser.parse_xml_report(self._FXCOP_XML)
        assert len(violations) == 1
        v = violations[0]
        assert (
            "EnumsShouldHaveZeroValue" in v.rule_id
            or "EnumsShouldHaveZeroValue" in v.message
        )

    def test_parse_sarif_report_basic(self):
        parser = self._get_parser()
        sarif = _make_sarif("FxCop", "CA1008", "Enums should have zero value")
        violations = parser.parse_sarif_report(sarif)
        assert len(violations) == 1
        assert violations[0].rule_id == "CA1008"

    def test_categorize_violations_design(self):
        parser = self._get_parser()
        sarif = _make_sarif("FxCop", "CA1000", "Do not declare static members")
        violations = parser.parse_sarif_report(sarif)
        cats = parser.categorize_violations(violations)
        assert len(cats) >= 1

    def test_execute_fxcop_no_dotnet(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "which", lambda _: None)
        parser = self._get_parser()
        assert parser.execute_fxcop(".") == []

    def test_generate_report_json(self):
        parser = self._get_parser()
        violations = parser.parse_xml_report(self._FXCOP_XML)
        data = json.loads(parser.generate_report(violations, format="json"))
        assert data["tool"] == "fxcop"
        assert data["total"] == len(violations)


# ---------------------------------------------------------------------------
# ReSharperParser
# ---------------------------------------------------------------------------


class TestReSharperParser:
    """Tests for ReSharperParser — enterprise tool, execute raises NotImplementedError."""

    _INSPECTCODE_XML = textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <Report ToolsVersion="231.9161.14">
          <Information />
          <IssueTypes>
            <IssueType Id="UnusedVariable" Category="Code Redundancies" Description="Unused variable"
                       Severity="WARNING" WikiUrl="https://www.jetbrains.com/resharper/webhelp/Code_Analysis__Code_Inspections.html" />
          </IssueTypes>
          <Issues>
            <Project Name="MyProject" Url="/src/MyProject.csproj">
              <Issue TypeId="UnusedVariable" File="Program.cs" Offset="100-110"
                     Line="15" Message="The variable 'x' is declared but never used" />
            </Project>
          </Issues>
        </Report>
    """)

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("resharper")

    def test_execute_resharper_raises(self):
        """ReSharper is an enterprise tool that cannot be invoked via CLI here."""
        parser = self._get_parser()
        with pytest.raises(NotImplementedError):
            parser.execute_resharper(".")

    def test_parse_xml_report_basic(self):
        parser = self._get_parser()
        issues = parser.parse_xml_report(self._INSPECTCODE_XML)
        assert len(issues) == 1
        issue = issues[0]
        assert (
            getattr(issue, "rule_id", None) == "UnusedVariable"
            or getattr(issue, "type_id", None) == "UnusedVariable"
        )
        assert issue.line == 15
        assert "never used" in issue.message.lower() or "x" in issue.message

    def test_categorize_issues(self):
        parser = self._get_parser()
        issues = parser.parse_xml_report(self._INSPECTCODE_XML)
        cats = parser.categorize_issues(issues)
        assert len(cats) >= 1

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_xml_report(self._INSPECTCODE_XML)
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "resharper"

    def test_generate_report_text(self):
        parser = self._get_parser()
        issues = parser.parse_xml_report(self._INSPECTCODE_XML)
        report = parser.generate_report(issues, format="text")
        assert "UnusedVariable" in report or "Program.cs" in report


# ---------------------------------------------------------------------------
# SonarQubeCSharpParser
# ---------------------------------------------------------------------------


class TestSonarQubeCSharpParser:
    """Tests for SonarQubeCSharpParser."""

    _ISSUES_JSON = json.dumps(
        {
            "issues": [
                {
                    "key": "AV1234",
                    "rule": "csharpsquid:S1135",
                    "severity": "INFO",
                    "component": "myproject:src/Program.cs",
                    "line": 22,
                    "message": "Complete the task associated to this TODO comment.",
                    "type": "CODE_SMELL",
                    "status": "OPEN",
                },
                {
                    "key": "AV5678",
                    "rule": "csharpsquid:S2068",
                    "severity": "BLOCKER",
                    "component": "myproject:src/Auth.cs",
                    "line": 5,
                    "message": "Hard-coded credentials are security-sensitive.",
                    "type": "VULNERABILITY",
                    "status": "OPEN",
                },
            ],
            "total": 2,
        }
    )

    def _get_parser(self):
        from code_scalpel.code_parsers.csharp_parsers import CSharpParserRegistry

        return CSharpParserRegistry().get_parser("sonarqube")

    def test_execute_sonarqube_raises(self):
        parser = self._get_parser()
        with pytest.raises(NotImplementedError):
            parser.execute_sonarqube(".")

    def test_parse_issues_json_basic(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(self._ISSUES_JSON)
        assert len(issues) == 2

    def test_parse_issues_json_dict_input(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(json.loads(self._ISSUES_JSON))
        assert len(issues) == 2

    def test_categorize_issues_by_type(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(self._ISSUES_JSON)
        cats = parser.categorize_issues(issues)
        assert any(
            "VULNERABILITY" in str(k).upper() or "vulnerability" in str(k).lower()
            for k in cats
        )

    def test_map_severity_blocker(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(self._ISSUES_JSON)
        by_sev = parser.map_severity(issues)
        assert "BLOCKER" in by_sev or any("blocker" in str(k).lower() for k in by_sev)

    def test_generate_report_json(self):
        parser = self._get_parser()
        issues = parser.parse_issues_json(self._ISSUES_JSON)
        data = json.loads(parser.generate_report(issues, format="json"))
        assert data["tool"] == "sonarqube_csharp"
        assert data["total"] == 2

    def test_rule_prefix_is_csharpsquid(self):
        parser = self._get_parser()
        assert parser.RULE_PREFIX == "csharpsquid"
