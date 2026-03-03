#!/usr/bin/env python3
# [20260303_FEATURE] Complete implementation of npm audit parser (was stub)
"""
NPM Audit JavaScript Parser - Vulnerability scanning for npm dependencies.

Reference: https://docs.npmjs.com/cli/v10/commands/npm-audit
Command: npm audit --json

Supports npm audit report v2 JSON format (npm >= 7).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NpmAuditFinding:
    """Parsed finding from npm audit --json output."""

    # [20260303_FEATURE] Dataclass matching Stage 4b specification
    package_name: str
    severity: str
    vulnerable_range: str
    cwe_ids: list[str] = field(default_factory=list)
    advisory_url: str = ""
    source_id: int = 0


class NpmAuditParser:
    """Parser for npm audit --json vulnerability reports.

    Supports npm audit v2 report format (npm >= 7).
    """

    # [20260303_FEATURE] Complete parser implementation

    def __init__(self) -> None:
        """Initialize the NpmAuditParser."""
        pass

    def execute_npm_audit(self, project_path: str = ".") -> list[NpmAuditFinding]:
        """Run ``npm audit --json`` in *project_path* and parse the output.

        Returns [] if npm is not installed or the project has no package-lock.json.

        Args:
            project_path: Directory containing package.json / package-lock.json.

        Returns:
            List of NpmAuditFinding objects.
        """
        if shutil.which("npm") is None:
            return []
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout or ""
            if not output.strip():
                return []
            return self.parse_v2_json(output)
        except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
            return []

    def parse_v2_json(self, output: str) -> list[NpmAuditFinding]:
        """Parse npm audit v2 JSON output (vulnerabilities dict format).

        Args:
            output: Raw JSON string from ``npm audit --json``.

        Returns:
            List of NpmAuditFinding objects, one per vulnerable package.
        """
        try:
            data: dict[str, Any] = json.loads(output)
        except json.JSONDecodeError:
            return []

        vulnerabilities: dict[str, Any] = data.get("vulnerabilities", {})
        findings: list[NpmAuditFinding] = []

        for pkg_name, vuln in vulnerabilities.items():
            severity = str(vuln.get("severity", "unknown")).lower()
            vulnerable_range = str(vuln.get("range", ""))

            # Collect CWEs and advisory URL from nested ``via`` list
            cwe_ids: list[str] = []
            advisory_url = ""
            source_id = 0

            for via_entry in vuln.get("via", []):
                if not isinstance(via_entry, dict):
                    continue
                for cwe in via_entry.get("cwe", []):
                    cwe_str = str(cwe)
                    if cwe_str not in cwe_ids:
                        cwe_ids.append(cwe_str)
                if not advisory_url:
                    advisory_url = str(via_entry.get("url", ""))
                if not source_id:
                    source_id = int(via_entry.get("source", 0) or 0)

            findings.append(
                NpmAuditFinding(
                    package_name=pkg_name,
                    severity=severity,
                    vulnerable_range=vulnerable_range,
                    cwe_ids=cwe_ids,
                    advisory_url=advisory_url,
                    source_id=source_id,
                )
            )

        return findings

    def map_to_cwe(
        self, findings: list[NpmAuditFinding]
    ) -> dict[str, list[NpmAuditFinding]]:
        """Group findings by CWE ID.

        Args:
            findings: List of NpmAuditFinding objects.

        Returns:
            Dict mapping CWE ID -> list of findings that include that CWE.
        """
        result: dict[str, list[NpmAuditFinding]] = {}
        for finding in findings:
            for cwe in finding.cwe_ids:
                result.setdefault(cwe, []).append(finding)
        return result

    def get_severity_summary(self, findings: list[NpmAuditFinding]) -> dict[str, int]:
        """Return count of findings per severity level.

        Args:
            findings: List of NpmAuditFinding objects.

        Returns:
            Dict with keys ``critical``, ``high``, ``moderate``, ``low``,
            ``info``, ``unknown``.
        """
        summary: dict[str, int] = {
            "critical": 0,
            "high": 0,
            "moderate": 0,
            "low": 0,
            "info": 0,
            "unknown": 0,
        }
        for finding in findings:
            key = finding.severity if finding.severity in summary else "unknown"
            summary[key] += 1
        return summary

    def generate_report(
        self, findings: list[NpmAuditFinding], format: str = "json"
    ) -> str:
        """Generate a structured report for the given findings.

        Args:
            findings: List of NpmAuditFinding objects.
            format: Output format (currently only "json" is supported).

        Returns:
            JSON string with tool name, total count, and findings list.
        """
        report = {
            "tool": "npm-audit",
            "total": len(findings),
            "severity_summary": self.get_severity_summary(findings),
            "findings": [
                {
                    "package_name": f.package_name,
                    "severity": f.severity,
                    "vulnerable_range": f.vulnerable_range,
                    "cwe_ids": f.cwe_ids,
                    "advisory_url": f.advisory_url,
                    "source_id": f.source_id,
                }
                for f in findings
            ],
        }
        return json.dumps(report, indent=2)
