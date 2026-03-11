#!/usr/bin/env python3
"""
Dependency-Check Java Parser - CVE and vulnerability scanning.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: https://owasp.org/www-project-dependency-check/
Command: dependency-check.sh --project myapp --scan . --format JSON
         dependency-check.sh --project myapp --scan . --format XML
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CVEFinding:
    """CVE finding from OWASP Dependency-Check."""

    component: str
    version: str
    cve_id: str
    cvss_score: float
    severity: str
    description: str = ""


def _cvss_to_severity(score: float) -> str:
    """Map a CVSS score to a severity label."""
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    return "LOW"


class DependencyCheckParser:
    """Parser for OWASP Dependency-Check JSON and XML reports.

    [20260303_FEATURE] Implements parse_json_report, parse_xml_report,
    map_to_cve, map_to_cvss, get_vulnerable_dependencies, generate_report.
    """

    def __init__(self, report_path: Optional[Path] = None) -> None:
        """Initialize Dependency-Check parser."""
        self.report_path = Path(report_path) if report_path else None

    def parse_json_report(self, path: Optional[Path] = None) -> List[CVEFinding]:
        """Parse a Dependency-Check JSON report file.

        Args:
            path: Path to the JSON report. Falls back to ``self.report_path``.
        """
        target = Path(path) if path else self.report_path
        if target is None:
            return []
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return self._parse_json_data(data)

    def parse_json_output(self, output: str) -> List[CVEFinding]:
        """Parse Dependency-Check JSON from a string."""
        if not output or not output.strip():
            return []
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []
        return self._parse_json_data(data)

    def _parse_json_data(self, data: dict) -> List[CVEFinding]:
        findings: List[CVEFinding] = []
        for dep in data.get("dependencies", []):
            component = dep.get("fileName", "")
            version = dep.get("version", "")
            for vuln in dep.get("vulnerabilities", []):
                name = vuln.get("name", "")
                cvss_scores = (
                    vuln.get("cvssv3", {}).get("baseScore")
                    or vuln.get("cvssv2", {}).get("score")
                    or 0.0
                )
                try:
                    score = float(cvss_scores)
                except (TypeError, ValueError):
                    score = 0.0
                severity = vuln.get("severity", _cvss_to_severity(score)).upper()
                findings.append(
                    CVEFinding(
                        component=component,
                        version=version,
                        cve_id=name,
                        cvss_score=score,
                        severity=severity,
                        description=vuln.get("description", ""),
                    )
                )
        return findings

    def parse_xml_report(self, path: Optional[Path] = None) -> List[CVEFinding]:
        """Parse a Dependency-Check XML report file."""
        target = Path(path) if path else self.report_path
        if target is None:
            return []
        try:
            tree = ET.parse(str(target))
        except (ET.ParseError, OSError):
            return []
        root = tree.getroot()
        # Handle namespace-prefixed tags
        ns = ""
        if "}" in root.tag:
            ns = root.tag.split("}")[0] + "}"

        findings: List[CVEFinding] = []
        for dep in root.findall(f".//{ns}dependency"):
            fname = dep.findtext(f"{ns}fileName") or ""
            ver = dep.findtext(f"{ns}version") or ""
            for vuln in dep.findall(f"{ns}vulnerabilities/{ns}vulnerability"):
                name = vuln.findtext(f"{ns}name") or ""
                try:
                    score = float(vuln.findtext(f"{ns}cvssScore") or 0)
                except ValueError:
                    score = 0.0
                severity = (
                    vuln.findtext(f"{ns}severity") or _cvss_to_severity(score)
                ).upper()
                findings.append(
                    CVEFinding(
                        component=fname,
                        version=ver,
                        cve_id=name,
                        cvss_score=score,
                        severity=severity,
                        description=vuln.findtext(f"{ns}description") or "",
                    )
                )
        return findings

    def map_to_cve(self, findings: List[CVEFinding]) -> Dict[str, List[CVEFinding]]:
        """Group findings by CVE ID."""
        result: Dict[str, List[CVEFinding]] = {}
        for f in findings:
            result.setdefault(f.cve_id, []).append(f)
        return result

    def map_to_cvss(self, findings: List[CVEFinding]) -> Dict[str, List[CVEFinding]]:
        """Group findings by severity label (CRITICAL/HIGH/MEDIUM/LOW)."""
        result: Dict[str, List[CVEFinding]] = {}
        for f in findings:
            result.setdefault(f.severity, []).append(f)
        return result

    def get_vulnerable_dependencies(self, findings: List[CVEFinding]) -> List[str]:
        """Return unique component names that have at least one CVE finding."""
        seen: set = set()
        out: List[str] = []
        for f in findings:
            if f.component not in seen:
                seen.add(f.component)
                out.append(f.component)
        return out

    def generate_report(self, findings: List[CVEFinding], format: str = "json") -> str:
        """Return a JSON or text report of CVE findings."""
        by_sev = self.map_to_cvss(findings)
        if format == "json":
            return json.dumps(
                {
                    "tool": "dependency-check",
                    "total": len(findings),
                    "by_severity": {k: len(v) for k, v in by_sev.items()},
                    "findings": [
                        {
                            "component": f.component,
                            "version": f.version,
                            "cve": f.cve_id,
                            "cvss": f.cvss_score,
                            "severity": f.severity,
                        }
                        for f in findings
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{f.component}:{f.version} [{f.cve_id}] {f.severity} CVSS={f.cvss_score}"
            for f in findings
        )

    def parse(self) -> List[CVEFinding]:
        """Backward-compat: parse the report set in constructor."""
        if self.report_path is None:
            return []
        path = self.report_path
        if path.suffix.lower() == ".json":
            return self.parse_json_report(path)
        return self.parse_xml_report(path)
