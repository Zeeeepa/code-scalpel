#!/usr/bin/env python3
"""
SonarQube C++ Parser - Code quality and security analysis platform.

[20260303_FEATURE] Interfaces with SonarQube API to retrieve C++ analysis
results. SonarQube is server-based; execution raises NotImplementedError.
Parse results from the SonarQube Web API JSON responses.

Reference: https://docs.sonarsource.com/sonarqube/latest/
Scan:      sonar-scanner -Dsonar.projectKey=myproject -Dsonar.sources=src
API:       GET /api/issues/search?componentKeys={project_key}&languages=cpp
"""

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass
class SonarCppIssue:
    """Represents a SonarQube C++ issue."""

    key: str
    rule: str  # e.g. "cpp:S1135", "cppcheck:nullPointer"
    severity: str  # BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    component: str  # File path
    line: Optional[int]
    message: str
    effort: str  # Remediation effort e.g. "5min"
    debt: str  # Technical debt
    issue_type: str  # BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT
    tags: List[str] = field(default_factory=list)


@dataclass
class SonarCppMetrics:
    """SonarQube C++ project metrics."""

    bugs: int = 0
    vulnerabilities: int = 0
    code_smells: int = 0
    coverage: float = 0.0
    duplicated_lines_density: float = 0.0
    ncloc: int = 0
    sqale_rating: str = ""  # A-E
    reliability_rating: str = ""
    security_rating: str = ""


# --- Internal helpers ------------------------------------------------------- #

_SEVERITY_LEVELS = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
_ISSUE_TYPES = ["BUG", "VULNERABILITY", "CODE_SMELL", "SECURITY_HOTSPOT"]

# SonarQube rule to CWE mapping for common C++ rules
_RULE_CWE_MAP: Dict[str, str] = {
    "cpp:S2068": "CWE-798",  # Hardcoded credentials
    "cpp:S2278": "CWE-327",  # Weak cipher
    "cpp:S2755": "CWE-611",  # XXE
    "cpp:S4036": "CWE-78",  # OS command injection
    "cpp:S5766": "CWE-476",  # Null dereference
    "cppcheck:nullPointer": "CWE-476",
    "cppcheck:arrayIndexOutOfBounds": "CWE-125",
    "cppcheck:bufferAccessOutOfBounds": "CWE-119",
    "cppcheck:memLeak": "CWE-401",
}


def _rating_to_letter(value: str) -> str:
    """Convert SonarQube numeric rating to letter grade."""
    ratings = {"1.0": "A", "2.0": "B", "3.0": "C", "4.0": "D", "5.0": "E"}
    return ratings.get(value, value)


def _to_sarif_result(issue: SonarCppIssue) -> Dict[str, Any]:
    """Convert a SonarCppIssue to a SARIF 2.1 result dict."""
    level = (
        "error"
        if issue.severity in ("BLOCKER", "CRITICAL")
        else "warning" if issue.severity in ("MAJOR", "MINOR") else "note"
    )
    return {
        "ruleId": issue.rule,
        "level": level,
        "message": {"text": issue.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": issue.component},
                    "region": {"startLine": issue.line or 1},
                }
            }
        ],
    }


# ---------------------------------------------------------------------------- #


class SonarQubeCppParser:
    """
    Parser for SonarQube C++ code quality and security analysis.

    [20260303_FEATURE] SonarQube is server-based; this parser retrieves
    results via the Web API. Direct scanner execution raises NotImplementedError
    — run sonar-scanner externally and point this parser at the SonarQube API.

    Usage:
        parser = SonarQubeCppParser(server_url="http://sonar:9000", token="squ_...")
        issues = parser.get_issues("my-cpp-project")
        report = parser.generate_report(issues)
    """

    SEVERITY_LEVELS = _SEVERITY_LEVELS
    ISSUE_TYPES = _ISSUE_TYPES

    def __init__(
        self,
        server_url: str = "http://localhost:9000",
        token: Optional[str] = None,
    ) -> None:
        """
        Initialize SonarQube C++ parser.

        Args:
            server_url: SonarQube server URL.
            token: Authentication token (squ_... format).
        """
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.language = "cpp"

    # ------------------------------------------------------------------ #
    # Execution (server-based — raises NotImplementedError)               #
    # ------------------------------------------------------------------ #

    def execute_sonarqube(
        self,
        _paths: List[Path],
        _config: Any = None,
    ) -> List[SonarCppIssue]:
        """
        Not available — SonarQube requires a running server.

        To use this parser:
          1. Configure sonar-project.properties with sonar.language=cpp.
          2. Run: sonar-scanner (or cmake + build-wrapper + sonar-scanner).
          3. Once analysis is complete, call get_issues(project_key) to
             retrieve results via the SonarQube Web API.
        """
        raise NotImplementedError(
            "SonarQube requires a running SonarQube server and sonar-scanner. "
            "Run sonar-scanner externally, then use get_issues(project_key) or "
            "parse_issues_json() to retrieve results from the SonarQube Web API."
        )

    # ------------------------------------------------------------------ #
    # API retrieval                                                        #
    # ------------------------------------------------------------------ #

    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make an authenticated request to the SonarQube Web API."""
        parsed_base = urlparse(self.server_url)
        if parsed_base.scheme not in {"http", "https"} or not parsed_base.netloc:
            return None

        url = f"{self.server_url}/api/{endpoint}"
        try:
            request = Request(url)
            if self.token:
                credentials = base64.b64encode(f"{self.token}:".encode()).decode()
                request.add_header("Authorization", f"Basic {credentials}")
            with urlopen(request, timeout=30) as response:  # nosec B310
                return json.loads(response.read().decode())
        except (URLError, json.JSONDecodeError):
            return None

    def get_issues(self, project_key: str) -> List[SonarCppIssue]:
        """
        Retrieve all issues for a C++ project via the SonarQube Web API.

        Args:
            project_key: SonarQube project key.

        Returns:
            List of SonarCppIssue objects.
        """
        issues: List[SonarCppIssue] = []
        page = 1
        page_size = 100

        while True:
            endpoint = (
                f"issues/search?componentKeys={project_key}"
                f"&languages=cpp,c&ps={page_size}&p={page}"
            )
            data = self._make_request(endpoint)
            if not data or "issues" not in data:
                break

            for issue in data["issues"]:
                issues.append(
                    SonarCppIssue(
                        key=issue.get("key", ""),
                        rule=issue.get("rule", ""),
                        severity=issue.get("severity", "INFO"),
                        component=issue.get("component", ""),
                        line=issue.get("line"),
                        message=issue.get("message", ""),
                        effort=issue.get("effort", ""),
                        debt=issue.get("debt", ""),
                        issue_type=issue.get("type", "CODE_SMELL"),
                        tags=issue.get("tags", []),
                    )
                )

            total = data.get("total", 0)
            if page * page_size >= total:
                break
            page += 1

        return issues

    def get_metrics(self, project_key: str) -> SonarCppMetrics:
        """Retrieve project-level quality metrics."""
        metrics = SonarCppMetrics()
        metric_keys = (
            "bugs,vulnerabilities,code_smells,coverage,"
            "duplicated_lines_density,ncloc,sqale_rating,"
            "reliability_rating,security_rating"
        )
        endpoint = (
            f"measures/component?component={project_key}&metricKeys={metric_keys}"
        )
        data = self._make_request(endpoint)
        if not data or "component" not in data:
            return metrics

        for measure in data["component"].get("measures", []):
            metric = measure.get("metric", "")
            value = measure.get("value", "")
            if metric == "bugs":
                metrics.bugs = int(value)
            elif metric == "vulnerabilities":
                metrics.vulnerabilities = int(value)
            elif metric == "code_smells":
                metrics.code_smells = int(value)
            elif metric == "coverage":
                metrics.coverage = float(value)
            elif metric == "duplicated_lines_density":
                metrics.duplicated_lines_density = float(value)
            elif metric == "ncloc":
                metrics.ncloc = int(value)
            elif metric == "sqale_rating":
                metrics.sqale_rating = _rating_to_letter(value)
            elif metric == "reliability_rating":
                metrics.reliability_rating = _rating_to_letter(value)
            elif metric == "security_rating":
                metrics.security_rating = _rating_to_letter(value)

        return metrics

    # ------------------------------------------------------------------ #
    # Offline JSON parsing                                                 #
    # ------------------------------------------------------------------ #

    def parse_issues_json(self, json_str: str) -> List[SonarCppIssue]:
        """
        Parse a SonarQube API JSON response string.

        Useful for offline testing or when the API response has been cached.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return []

        issues = []
        for issue in data.get("issues", []):
            issues.append(
                SonarCppIssue(
                    key=issue.get("key", ""),
                    rule=issue.get("rule", ""),
                    severity=issue.get("severity", "INFO"),
                    component=issue.get("component", ""),
                    line=issue.get("line"),
                    message=issue.get("message", ""),
                    effort=issue.get("effort", ""),
                    debt=issue.get("debt", ""),
                    issue_type=issue.get("type", "CODE_SMELL"),
                    tags=issue.get("tags", []),
                )
            )
        return issues

    def parse_issues_from_file(self, json_path: Path) -> List[SonarCppIssue]:
        """Parse a saved SonarQube API JSON response file."""
        try:
            return self.parse_issues_json(json_path.read_text(encoding="utf-8"))
        except OSError:
            return []

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def get_vulnerabilities(self, issues: List[SonarCppIssue]) -> List[SonarCppIssue]:
        """Filter for security vulnerabilities."""
        return [i for i in issues if i.issue_type == "VULNERABILITY"]

    def get_bugs(self, issues: List[SonarCppIssue]) -> List[SonarCppIssue]:
        """Filter for bug issues."""
        return [i for i in issues if i.issue_type == "BUG"]

    def get_by_severity(
        self, issues: List[SonarCppIssue], severity: str
    ) -> List[SonarCppIssue]:
        """Filter issues by severity level."""
        return [i for i in issues if i.severity == severity.upper()]

    def map_to_cwe(self, issues: List[SonarCppIssue]) -> Dict[str, List[SonarCppIssue]]:
        """Map issues to CWE identifiers using known rule-to-CWE mappings."""
        result: Dict[str, List[SonarCppIssue]] = {}
        for issue in issues:
            cwe = _RULE_CWE_MAP.get(issue.rule)
            if cwe:
                result.setdefault(cwe, []).append(issue)
        return result

    def categorize_issues(
        self, issues: List[SonarCppIssue]
    ) -> Dict[str, List[SonarCppIssue]]:
        """Group issues by issue_type (BUG, VULNERABILITY, CODE_SMELL, etc.)."""
        result: Dict[str, List[SonarCppIssue]] = {}
        for issue in issues:
            result.setdefault(issue.issue_type, []).append(issue)
        return result

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(self, issues: List[SonarCppIssue], format: str = "json") -> str:
        """Generate a normalized report in JSON or SARIF 2.1 format."""
        if format == "sarif":
            sarif = {
                "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "SonarQube", "version": "10.x"}},
                        "results": [_to_sarif_result(i) for i in issues],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        by_severity: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1

        report = {
            "tool": "sonarqube",
            "language": "cpp",
            "issues": [
                {
                    "key": i.key,
                    "rule": i.rule,
                    "severity": i.severity,
                    "type": i.issue_type,
                    "message": i.message,
                    "component": i.component,
                    "line": i.line,
                    "effort": i.effort,
                    "tags": i.tags,
                }
                for i in issues
            ],
            "summary": {
                "total": len(issues),
                "by_severity": by_severity,
                "by_type": by_type,
            },
        }
        return json.dumps(report, indent=2)
