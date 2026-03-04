#!/usr/bin/env python3
"""Exakat Parser — comprehensive PHP code auditor (enterprise tool).

[20260304_FEATURE] Phase 2: parse_output implemented; execute_exakat raises
NotImplementedError by design (enterprise tool requiring manual install).

Reference: https://www.exakat.io/
Installation: https://exakat.readthedocs.io/en/latest/Installation.html
  (requires Docker or standalone Java + PHP)

To run Exakat:
    docker run -it exakat/exakat:latest exakat project -p myproject -R /path/to/src
    exakat report -p myproject -format JSON
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# CWE mapping for Exakat categories — specific entries before generic "Security"
_CWE_MAP: Dict[str, str] = {
    "SQL": "CWE-89",  # SQL Injection
    "XSS": "CWE-79",  # Cross-site Scripting
    "Command": "CWE-78",  # Command Injection
    "PHPInjection": "CWE-94",  # Code Injection
    "FileInclusion": "CWE-98",  # Remote File Include
    "Dead code": "CWE-561",
    "Compatibility": "CWE-1038",
    "Performance": "CWE-400",
    "Security": "CWE-693",  # catch-all — must be last
}


class ExakatCategory(Enum):
    """Exakat analysis categories."""

    SECURITY = "Security"
    PERFORMANCE = "Performance"
    DEAD_CODE = "Dead code"
    CODE_QUALITY = "Code Quality"
    COMPATIBILITY = "Compatibility"
    ARCHITECTURE = "Architecture"


@dataclass
class ExakatIssue:
    """Represents a single Exakat analysis issue.

    [20260304_FEATURE] Added cwe_id field.
    """

    category: str
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    severity: Optional[str] = None
    code: Optional[str] = None
    cwe_id: Optional[str] = None


def _infer_cwe(category: str, title: str) -> Optional[str]:
    for key, cwe in _CWE_MAP.items():
        if key.lower() in category.lower() or key.lower() in title.lower():
            return cwe
    return None


class ExakatParser:
    """Parser for Exakat comprehensive PHP analysis output.

    [20260304_FEATURE] parse_json_report and parse_csv_report fully implemented.
    execute_exakat raises NotImplementedError by design — Exakat requires
    a standalone Java + PHP environment or Docker. See module docstring.
    """

    def __init__(self) -> None:
        """Initialise ExakatParser."""
        self.issues: List[ExakatIssue] = []
        self.language = "php"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_json_report(self, json_data: str) -> List[ExakatIssue]:
        """Parse Exakat JSON report.

        [20260304_FEATURE] Handles Exakat's nested JSON output.

        Exakat JSON format (simplified):
            {"results": [{"analyzer": "Security/...", "file": "...",
                          "line": 5, "code": "..."}]}
        Or flat array:
            [{"analyzer": "...", "file": "...", "line": 5}]

        Args:
            json_data: JSON text from exakat stdout.
        Returns:
            List of ExakatIssue objects.
        """
        issues: List[ExakatIssue] = []
        if not json_data:
            return issues
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return issues

        # Normalise to list
        items: List[Dict[str, Any]] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("results", data.get("issues", []))

        for item in items:
            analyzer = item.get("analyzer", item.get("title", ""))
            # Exakat analyzer names: "Security/PHPInjection" → category="Security"
            category = analyzer.split("/")[0] if "/" in analyzer else "Code Quality"
            title = analyzer.split("/")[-1] if "/" in analyzer else analyzer
            issues.append(
                ExakatIssue(
                    category=category,
                    title=title,
                    description=item.get("description") or item.get("message", ""),
                    file_path=item.get("file") or item.get("file_path"),
                    line_number=item.get("line") or item.get("line_number"),
                    severity=item.get("severity", "warning"),
                    code=item.get("code"),
                    cwe_id=_infer_cwe(category, title),
                )
            )
        self.issues = issues
        return issues

    def parse_csv_report(self, csv_file: Path) -> List[ExakatIssue]:
        """Parse Exakat CSV report.

        [20260304_FEATURE] Full implementation.

        Exakat CSV columns: analyzer, file, namespace, class, function, line, code

        Args:
            csv_file: Path to Exakat CSV report.
        Returns:
            List of ExakatIssue objects.
        """
        issues: List[ExakatIssue] = []
        try:
            content = Path(csv_file).read_text(encoding="utf-8", errors="replace")
        except (OSError, FileNotFoundError):
            return issues
        return self.parse_csv_string(content)

    def parse_csv_string(self, csv_data: str) -> List[ExakatIssue]:
        """Parse Exakat CSV content from string (helper for tests)."""
        issues: List[ExakatIssue] = []
        if not csv_data:
            return issues
        reader = csv.DictReader(io.StringIO(csv_data))
        for row in reader:
            analyzer = row.get("analyzer", "")
            category = analyzer.split("/")[0] if "/" in analyzer else "Code Quality"
            title = analyzer.split("/")[-1] if "/" in analyzer else analyzer
            try:
                line_number: Optional[int] = int(row.get("line", 0)) or None
            except (ValueError, TypeError):
                line_number = None
            issues.append(
                ExakatIssue(
                    category=category,
                    title=title,
                    file_path=row.get("file"),
                    line_number=line_number,
                    code=row.get("code"),
                    cwe_id=_infer_cwe(category, title),
                )
            )
        self.issues = issues
        return issues

    def parse_output(self, output: str) -> List[ExakatIssue]:
        """Parse raw exakat output — tries JSON then CSV."""
        output = output.strip()
        if not output:
            return []
        # JSON?
        if output.lstrip().startswith(("{", "[")):
            result = self.parse_json_report(output)
            if result:
                return result
        # Try CSV
        return self.parse_csv_string(output)

    # ------------------------------------------------------------------
    # Execution (Enterprise tool — NotImplementedError by design)
    # ------------------------------------------------------------------

    def execute_exakat(self, project_path: Path) -> Dict[str, Any]:
        """Exakat requires Docker or a standalone installation.

        This method intentionally raises NotImplementedError.
        To run Exakat, install it manually and call ``parse_json_report``
        or ``parse_csv_report`` on its output:

            docker run exakat/exakat:latest exakat project -p myproject -R /path
            exakat report -p myproject -format JSON > report.json

        See: https://exakat.readthedocs.io/en/latest/Installation.html
        """
        raise NotImplementedError(
            "Exakat requires a standalone installation (Java + PHP) or Docker. "
            "Run exakat manually and pass the output to parse_json_report() "
            "or parse_csv_report(). "
            "See: https://exakat.readthedocs.io/en/latest/Installation.html"
        )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def categorize_by_category(
        self, issues: List[ExakatIssue]
    ) -> Dict[str, List[ExakatIssue]]:
        """Group issues by Exakat category."""
        result: Dict[str, List[ExakatIssue]] = {}
        for issue in issues:
            result.setdefault(issue.category, []).append(issue)
        return result

    def generate_report(
        self,
        issues: Optional[List[ExakatIssue]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text analysis report."""
        isss = issues if issues is not None else self.issues
        by_cat = self.categorize_by_category(isss)
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "exakat",
                    "total": len(isss),
                    "by_category": {k: len(v) for k, v in by_cat.items()},
                    "issues": [
                        {
                            "category": i.category,
                            "title": i.title,
                            "file": i.file_path,
                            "line": i.line_number,
                            "severity": i.severity,
                            "cwe": i.cwe_id,
                            "description": i.description,
                        }
                        for i in isss
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{i.file_path or '?'}:{i.line_number or '?'}: " f"[{i.category}] {i.title}"
            for i in isss
        )
