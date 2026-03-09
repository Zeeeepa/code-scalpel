#!/usr/bin/env python3
"""SonarQube C# Parser - SonarQube/SonarCloud analysis integration.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
Adapted from java_parsers_SonarQube.py — rule key prefix is ``csharpsquid:``.

Reference: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/
           scanners/sonarscanner-for-dotnet/
Command: dotnet sonarscanner begin /k:"project-key" && dotnet build && dotnet sonarscanner end

Enterprise / server-based tool: execute_sonarqube() raises NotImplementedError.
Use parse_issues_json() with a pre-fetched SonarQube API response.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass
class SonarIssue:
    """Represents a SonarQube issue for C#."""

    key: str
    rule: str
    severity: str  # BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    component: str  # file path
    line: Optional[int]
    message: str
    effort: str
    debt: str
    issue_type: str  # BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT
    tags: List[str] = field(default_factory=list)


@dataclass
class SonarMetrics:
    """SonarQube project metrics."""

    bugs: int = 0
    vulnerabilities: int = 0
    code_smells: int = 0
    coverage: float = 0.0
    duplicated_lines_density: float = 0.0
    ncloc: int = 0
    sqale_rating: str = ""
    reliability_rating: str = ""
    security_rating: str = ""


class SonarQubeCSharpParser:
    """Parser for SonarQube C# analysis results.

    [20260303_FEATURE] Phase 2 full implementation (adapted from Java version).

    Server-based enterprise tool.  Use ``execute_sonarqube()`` only if you
    have a running SonarQube instance; it will raise ``NotImplementedError``
    if called without a live server.  All static parsing helpers work offline.
    """

    SEVERITY_LEVELS = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
    ISSUE_TYPES = ["BUG", "VULNERABILITY", "CODE_SMELL", "SECURITY_HOTSPOT"]
    RULE_PREFIX = "csharpsquid"

    def __init__(
        self,
        server_url: str = "http://localhost:9000",
        token: Optional[str] = None,
    ) -> None:
        """Initialise SonarQube C# parser.

        Args:
            server_url: SonarQube server URL (default localhost:9000).
            token: SonarQube authentication token.
        """
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.language = "csharp"

    def execute_sonarqube(self, paths: object = None) -> List[SonarIssue]:
        """Execute SonarQube analysis.

        Raises:
            NotImplementedError: Always — SonarQube is a server-based tool.
                Run ``dotnet sonarscanner`` externally and use
                ``parse_issues_json()`` with the API response.
        """
        raise NotImplementedError(
            "SonarQube is a server-based tool and cannot be executed locally. "
            "Configure and run 'dotnet sonarscanner begin/end' externally, "
            "then fetch results via the SonarQube Web API and pass them to "
            "parse_issues_json()."
        )

    def parse_issues_json(self, json_data: str) -> List[SonarIssue]:
        """Parse a SonarQube Web API JSON response (issues/search endpoint).

        [20260303_FEATURE] Accepts the raw JSON string from
        ``/api/issues/search?componentKeys=...``.

        Args:
            json_data: JSON string or dict from SonarQube API.

        Returns:
            List of SonarIssue; ``[]`` on error.
        """
        if isinstance(json_data, dict):
            data = json_data
        else:
            try:
                data = json.loads(json_data)
            except (json.JSONDecodeError, TypeError):
                return []

        issues: List[SonarIssue] = []
        for issue in data.get("issues", []):
            issues.append(
                SonarIssue(
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

    def parse_metrics_json(self, json_data: str) -> SonarMetrics:
        """Parse SonarQube metrics from a measures/component API response."""
        if isinstance(json_data, dict):
            data = json_data
        else:
            try:
                data = json.loads(json_data)
            except (json.JSONDecodeError, TypeError):
                return SonarMetrics()

        metrics = SonarMetrics()
        for measure in data.get("component", {}).get("measures", []):
            metric = measure.get("metric", "")
            value = measure.get("value", "")
            try:
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
                    metrics.sqale_rating = self._rating_to_letter(value)
                elif metric == "reliability_rating":
                    metrics.reliability_rating = self._rating_to_letter(value)
                elif metric == "security_rating":
                    metrics.security_rating = self._rating_to_letter(value)
            except (ValueError, TypeError):
                pass
        return metrics

    def _make_request(self, endpoint: str) -> Optional[dict]:
        """Make authenticated request to SonarQube API."""
        parsed_base = urlparse(self.server_url)
        if parsed_base.scheme not in {"http", "https"} or not parsed_base.netloc:
            return None
        url = f"{self.server_url}/api/{endpoint}"
        try:
            req = Request(url)
            if self.token:
                creds = base64.b64encode(f"{self.token}:".encode()).decode()
                req.add_header("Authorization", f"Basic {creds}")
            with urlopen(req, timeout=30) as response:  # nosec B310
                return json.loads(response.read().decode())
        except (URLError, json.JSONDecodeError):
            return None

    def get_issues(self, project_key: str) -> List[SonarIssue]:
        """Fetch issues from a live SonarQube server."""
        issues: List[SonarIssue] = []
        page, page_size = 1, 100
        while True:
            data = self._make_request(
                f"issues/search?componentKeys={project_key}&ps={page_size}&p={page}"
            )
            if not data or "issues" not in data:
                break
            issues.extend(self.parse_issues_json(data))
            if page * page_size >= data.get("total", 0):
                break
            page += 1
        return issues

    def categorize_issues(
        self, issues: List[SonarIssue]
    ) -> Dict[str, List[SonarIssue]]:
        """Group issues by issue_type (BUG, VULNERABILITY, CODE_SMELL, …)."""
        result: Dict[str, List[SonarIssue]] = {}
        for issue in issues:
            result.setdefault(issue.issue_type, []).append(issue)
        return result

    def map_severity(self, issues: List[SonarIssue]) -> Dict[str, List[SonarIssue]]:
        """Group issues by severity."""
        result: Dict[str, List[SonarIssue]] = {}
        for issue in issues:
            result.setdefault(issue.severity, []).append(issue)
        return result

    def generate_report(self, issues: List[SonarIssue], format: str = "json") -> str:
        """Return JSON report of SonarQube C# issues."""
        by_type = self.categorize_issues(issues)
        if format == "json":
            return json.dumps(
                {
                    "tool": "sonarqube_csharp",
                    "rule_prefix": self.RULE_PREFIX,
                    "total": len(issues),
                    "summary": {k: len(v) for k, v in by_type.items()},
                    "issues": [
                        {
                            "key": i.key,
                            "rule": i.rule,
                            "severity": i.severity,
                            "type": i.issue_type,
                            "component": i.component,
                            "line": i.line,
                            "message": i.message,
                        }
                        for i in issues
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{i.component}:{i.line}: {i.severity}: {i.rule} - {i.message}"
            for i in issues
        )

    @staticmethod
    def _rating_to_letter(value: str) -> str:
        """Convert SonarQube numeric rating to letter grade."""
        return {"1.0": "A", "2.0": "B", "3.0": "C", "4.0": "D", "5.0": "E"}.get(
            value, value
        )
