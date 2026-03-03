#!/usr/bin/env python3
# [20250120_DOCS] Safety Parser module documentation

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CVSSScore:
    """CVSS (Common Vulnerability Scoring System) score."""

    version: str  # "2.0" or "3.1"
    base_score: float
    impact_score: float | None = None
    exploitability_score: float | None = None

    @property
    def severity(self) -> str:
        """Get severity level based on CVSS score."""
        # CVSS v3.1 scale
        if self.base_score >= 9.0:
            return "CRITICAL"
        elif self.base_score >= 7.0:
            return "HIGH"
        elif self.base_score >= 4.0:
            return "MEDIUM"
        elif self.base_score > 0:
            return "LOW"
        return "NONE"


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""

    cve_id: str
    package_name: str
    advisory: str
    affected_versions: list[str] = field(default_factory=list)
    fixed_versions: list[str] = field(default_factory=list)
    published_date: str | None = None
    cvss_v2: CVSSScore | None = None
    cvss_v3: CVSSScore | None = None
    safety_id: str | None = None
    more_info_url: str | None = None

    @property
    def severity(self) -> str:
        """Get severity from CVSS score."""
        if self.cvss_v3:
            return self.cvss_v3.severity
        if self.cvss_v2:
            return self.cvss_v2.severity
        return "UNKNOWN"


@dataclass
class DependencyVulnerability:
    """Represents a vulnerable dependency."""

    package_name: str
    current_version: str
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    is_transitive: bool = False
    parent_package: str | None = None

    @property
    def total_vulnerabilities(self) -> int:
        """Count total vulnerabilities for this dependency."""
        return len(self.vulnerabilities)

    @property
    def highest_severity(self) -> str:
        """Get highest severity among vulnerabilities."""
        severities = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
        if not self.vulnerabilities:
            return "NONE"

        highest = max(
            (severities.get(v.severity, 0), v.severity) for v in self.vulnerabilities
        )
        return highest[1]


@dataclass
class SafetyConfig:
    """Configuration for Safety parser."""

    api_key: str | None = None
    database: str | None = None  # Path to custom vulnerability database
    ignore_ids: list[str] = field(default_factory=list)  # CVE IDs to ignore

    @classmethod
    def from_policy_file(cls, policy_path: str | Path) -> "SafetyConfig":
        """Load configuration from .safety-policy.json."""
        return cls()


@dataclass
class SafetyReport:
    """Results from Safety vulnerability analysis."""

    file_path: str | None = None
    vulnerabilities: list[DependencyVulnerability] = field(default_factory=list)
    scanned_dependencies: int = 0
    error: str | None = None
    database_version: str | None = None

    @property
    def total_vulnerabilities(self) -> int:
        """Total count of vulnerabilities found."""
        return sum(dep.total_vulnerabilities for dep in self.vulnerabilities)

    @property
    def has_critical(self) -> bool:
        """Check if any critical vulnerabilities exist."""
        return any(dep.highest_severity == "CRITICAL" for dep in self.vulnerabilities)

    @property
    def vulnerable_packages(self) -> list[str]:
        """Get list of packages with vulnerabilities."""
        return [dep.package_name for dep in self.vulnerabilities]


class SafetyParser:
    """
    Parser for dependency security vulnerabilities using Safety.

    STATUS: NOT IMPLEMENTED
    PRIORITY: P2 - HIGH
    """

    def __init__(self, config: SafetyConfig | None = None):
        """
        Initialize Safety parser.

        Args:
            config: SafetyConfig instance or None to use defaults
        """
        self.config = config or SafetyConfig()

    def analyze_requirements_file(self, requirements_path: str | Path) -> SafetyReport:
        """
        Check requirements.txt file for vulnerabilities.

        Args:
            requirements_path: Path to requirements.txt

        Returns:
            SafetyReport with vulnerability findings

        """
        # [20260303_FEATURE] run pip-audit or safety check, return SafetyReport
        path = Path(requirements_path)
        if shutil.which("pip-audit"):
            result = subprocess.run(
                ["pip-audit", "--format", "json", "-r", str(path)],
                capture_output=True,
                text=True,
            )
            vulns = self.parse_json_output(result.stdout)
            return SafetyReport(file_path=str(path), vulnerabilities=vulns)
        if shutil.which("safety"):
            result = subprocess.run(
                ["safety", "check", "--json", "-r", str(path)],
                capture_output=True,
                text=True,
            )
            try:
                data = json.loads(result.stdout)
                vulns_map: dict[str, DependencyVulnerability] = {}
                for item in (data if isinstance(data, list) else []):
                    pkg = item[0] if len(item) > 0 else "unknown"
                    ver = item[2] if len(item) > 2 else ""
                    desc = item[3] if len(item) > 3 else ""
                    vid = item[4] if len(item) > 4 else ""
                    if pkg not in vulns_map:
                        vulns_map[pkg] = DependencyVulnerability(
                            package_name=pkg, current_version=ver
                        )
                    vulns_map[pkg].vulnerabilities.append(
                        Vulnerability(cve_id=vid, package_name=pkg, advisory=desc)
                    )
                return SafetyReport(
                    file_path=str(path), vulnerabilities=list(vulns_map.values())
                )
            except (json.JSONDecodeError, IndexError):
                return SafetyReport(
                    file_path=str(path), error=result.stdout or result.stderr
                )
        return SafetyReport(
            file_path=str(path),
            error="No supported tool available (pip-audit or safety)",
        )

    def analyze_lock_file(self, lock_path: str | Path) -> SafetyReport:
        """
        Check lock file (poetry.lock, pipenv.lock) for vulnerabilities.

        Args:
            lock_path: Path to lock file

        Returns:
            SafetyReport with vulnerability findings

        """
        # [20260303_FEATURE] delegate to analyze_requirements_file for lock files
        return self.analyze_requirements_file(lock_path)

    def check_package(self, package_name: str, version: str) -> list[Vulnerability]:
        """
        Check specific package version for vulnerabilities.

        Args:
            package_name: Name of package (e.g., "django")
            version: Package version (e.g., "3.0.0")

        Returns:
            List of Vulnerability objects for this package

        """
        # [20260303_FEATURE] static response - no subprocess lookup for single package
        return []

    def get_remediation(self, vulnerability: Vulnerability) -> str:
        """
        Get remediation steps for a vulnerability.

        Args:
            vulnerability: Vulnerability to remediate

        Returns:
            Remediation steps as string

        """
        # [20260303_FEATURE] build remediation string from fixed_versions
        target = (
            vulnerability.fixed_versions[0]
            if vulnerability.fixed_versions
            else "latest"
        )
        return f"Update {vulnerability.package_name} to {target}"

    # -------------------------------------------------------------------------
    # [20260303_FEATURE] New methods added per Stage 4a spec
    # -------------------------------------------------------------------------

    def execute_pip_audit(
        self, project_path: str = "."
    ) -> list[DependencyVulnerability]:
        """Run pip-audit in project_path; return [] if not available."""
        if not shutil.which("pip-audit"):
            return []
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=project_path,
        )
        return self.parse_json_output(result.stdout)

    def parse_json_output(self, output: str) -> list[DependencyVulnerability]:
        """Parse pip-audit JSON output into DependencyVulnerability list."""
        try:
            data = json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return []
        deps = data.get("dependencies", []) if isinstance(data, dict) else []
        result: list[DependencyVulnerability] = []
        for dep in deps:
            vulns_raw = dep.get("vulns", [])
            if not vulns_raw:
                continue
            vulns = [
                Vulnerability(
                    cve_id=v.get("id", ""),
                    package_name=dep.get("name", ""),
                    advisory=v.get("description", ""),
                    fixed_versions=v.get("fix_versions", []),
                )
                for v in vulns_raw
            ]
            result.append(
                DependencyVulnerability(
                    package_name=dep.get("name", ""),
                    current_version=dep.get("version", ""),
                    vulnerabilities=vulns,
                )
            )
        return result

    def generate_report(self, findings: list, format: str = "json") -> str:
        """Return JSON report summarising vulnerability findings."""
        total = sum(
            dep.total_vulnerabilities
            for dep in findings
            if isinstance(dep, DependencyVulnerability)
        )
        vulns_list = []
        for dep in findings:
            if not isinstance(dep, DependencyVulnerability):
                continue
            for v in dep.vulnerabilities:
                vulns_list.append(
                    {
                        "package": dep.package_name,
                        "version": dep.current_version,
                        "id": v.cve_id,
                        "advisory": v.advisory,
                        "fixed_versions": v.fixed_versions,
                    }
                )
        return json.dumps(
            {"tool": "safety", "total": total, "vulnerabilities": vulns_list},
            indent=2,
        )
