#!/usr/bin/env python3
"""
Semgrep Java Parser - Custom pattern matching and static analysis.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: https://semgrep.dev/
Command: semgrep --json --config=rules.yaml src/ > results.json
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class SemgrepFinding:
    """Finding from Semgrep analysis."""

    rule_id: str
    message: str
    file: str
    line: int
    severity: str
    cwe_ids: List[str] = field(default_factory=list)
    end_line: int = 0


class SemgrepParser:
    """Parser for Semgrep ``--json`` output.

    [20260303_FEATURE] Implements execute_semgrep, parse_json_output,
    map_to_cwe, categorize_by_severity, generate_report.
    Falls back to ``[]`` gracefully when ``semgrep`` is not on PATH.
    """

    def __init__(self, report_path: Optional[Path] = None) -> None:
        """Initialize Semgrep parser."""
        self.report_path = Path(report_path) if report_path else None

    def execute_semgrep(
        self,
        paths: Union[List[Path], Path, str],
        ruleset: Optional[str] = None,
    ) -> List[SemgrepFinding]:
        """Run ``semgrep --json`` and return findings.

        Returns ``[]`` gracefully when ``semgrep`` is not on PATH.
        """
        if not shutil.which("semgrep"):
            return []
        target = (
            str(paths)
            if not isinstance(paths, list)
            else " ".join(str(p) for p in paths)
        )
        config = ruleset or "auto"
        cmd = ["semgrep", "--json", f"--config={config}", target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return self.parse_json_output(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def parse_json_output(self, output: str) -> List[SemgrepFinding]:
        """Parse ``semgrep --json`` stdout.

        [20260303_FEATURE] Handles {"results": [...]} format.
        """
        if not output or not output.strip():
            return []
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        findings: List[SemgrepFinding] = []
        for item in data.get("results", []):
            extra = item.get("extra", {})
            metadata = extra.get("metadata", {})
            cwe_list = metadata.get("cwe", [])
            if isinstance(cwe_list, str):
                cwe_list = [cwe_list]
            start = item.get("start", {})
            end = item.get("end", {})
            findings.append(
                SemgrepFinding(
                    rule_id=item.get("check_id", ""),
                    message=extra.get("message", ""),
                    file=item.get("path", ""),
                    line=start.get("line", 0),
                    end_line=end.get("line", 0),
                    severity=extra.get("severity", "WARNING").upper(),
                    cwe_ids=cwe_list,
                )
            )
        return findings

    def parse_json_report(self, path: Optional[Path] = None) -> List[SemgrepFinding]:
        """Parse a pre-saved Semgrep JSON report file."""
        target = Path(path) if path else self.report_path
        if target is None:
            return []
        try:
            return self.parse_json_output(target.read_text(encoding="utf-8"))
        except OSError:
            return []

    def map_to_cwe(
        self, findings: List[SemgrepFinding]
    ) -> Dict[str, List[SemgrepFinding]]:
        """Group findings by CWE ID."""
        result: Dict[str, List[SemgrepFinding]] = {}
        for f in findings:
            if f.cwe_ids:
                for cwe in f.cwe_ids:
                    result.setdefault(cwe, []).append(f)
            else:
                result.setdefault("UNKNOWN", []).append(f)
        return result

    def categorize_by_severity(
        self, findings: List[SemgrepFinding]
    ) -> Dict[str, List[SemgrepFinding]]:
        """Group findings by severity (ERROR/WARNING/INFO)."""
        result: Dict[str, List[SemgrepFinding]] = {}
        for f in findings:
            result.setdefault(f.severity, []).append(f)
        return result

    def generate_report(
        self, findings: List[SemgrepFinding], format: str = "json"
    ) -> str:
        """Return a JSON or text report."""
        by_sev = self.categorize_by_severity(findings)
        if format == "json":
            return json.dumps(
                {
                    "tool": "semgrep",
                    "total": len(findings),
                    "by_severity": {k: len(v) for k, v in by_sev.items()},
                    "findings": [
                        {
                            "rule": f.rule_id,
                            "severity": f.severity,
                            "message": f.message,
                            "file": f.file,
                            "line": f.line,
                            "cwe": f.cwe_ids,
                        }
                        for f in findings
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{f.file}:{f.line}: [{f.rule_id}] {f.severity} - {f.message}"
            for f in findings
        )

    def parse(self) -> List[SemgrepFinding]:
        """Backward-compat: parse the report set in constructor."""
        return self.parse_json_report(self.report_path)
