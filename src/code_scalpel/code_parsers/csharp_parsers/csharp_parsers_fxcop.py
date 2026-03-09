#!/usr/bin/env python3
"""FxCop .NET code analysis parser.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.

Provides comprehensive code analysis for .NET assemblies following Microsoft
design guidelines and best practices.

Output formats:
  - Legacy XML:  FxCop.exe /out:results.xml
  - SARIF:       dotnet build with Roslyn-based code analysis (/p:ErrorLog=...)
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from . import SarifFinding, _parse_sarif


class FxCopSeverity(Enum):
    """FxCop violation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


class RuleCategory(Enum):
    """FxCop rule categories."""

    DESIGN = "design"
    GLOBALIZATION = "globalization"
    INTEROPERABILITY = "interoperability"
    MAINTAINABILITY = "maintainability"
    NAMING = "naming"
    PERFORMANCE = "performance"
    PORTABILITY = "portability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    USAGE = "usage"
    OTHER = "other"


@dataclass
class FxCopViolation:
    """Represents an FxCop code analysis violation."""

    rule_id: str
    rule_name: str
    category: RuleCategory
    severity: FxCopSeverity
    message: str
    file_path: str
    line_number: int
    type_name: Optional[str] = None
    member_name: Optional[str] = None


@dataclass
class FxCopConfig:
    """FxCop configuration for analysis."""

    fxcop_version: str = "4.3.0"
    config_file: Optional[Path] = None
    rules_file: Optional[Path] = None
    suppression_file: Optional[Path] = None


# FxCop XML rule category string → enum
_CATEGORY_MAP: Dict[str, RuleCategory] = {
    cat.lower().replace(" ", ""): cat_enum
    for cat, cat_enum in {
        "design": RuleCategory.DESIGN,
        "globalization": RuleCategory.GLOBALIZATION,
        "interoperability": RuleCategory.INTEROPERABILITY,
        "maintainability": RuleCategory.MAINTAINABILITY,
        "naming": RuleCategory.NAMING,
        "performance": RuleCategory.PERFORMANCE,
        "portability": RuleCategory.PORTABILITY,
        "reliability": RuleCategory.RELIABILITY,
        "security": RuleCategory.SECURITY,
        "usage": RuleCategory.USAGE,
    }.items()
}


class FxCopParser:
    """Parser for FxCop .NET code analysis (XML and SARIF formats).

    [20260303_FEATURE] Phase 2 full implementation.

    Note: FxCop as a standalone executable is deprecated in favour of
    Roslyn-based code analysis (CA rules). This parser handles both the
    legacy XML format and modern SARIF format.
    """

    def __init__(self) -> None:
        """Initialize FxCop parser."""
        self.config = FxCopConfig()
        self.violations: List[FxCopViolation] = []

    def execute_fxcop(
        self,
        paths: Union[List[Path], Path],
        config: Optional[FxCopConfig] = None,
    ) -> List[FxCopViolation]:
        """Execute FxCop analysis.

        Note: Legacy FxCop.exe is deprecated and rarely installed.
        Modern equivalent uses ``dotnet build`` with CA rules.
        Returns ``[]`` when neither fxcop nor dotnet is available.
        """
        import shutil
        import subprocess

        if not shutil.which("dotnet"):
            return []

        target = (
            paths if isinstance(paths, Path) else (paths[0] if paths else Path("."))
        )
        sarif = Path("/tmp/fxcop.sarif")
        try:
            subprocess.run(
                ["dotnet", "build", str(target), f"/p:ErrorLog={sarif}"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        return self.parse_sarif_report(sarif) if sarif.exists() else []

    def parse_xml_report(self, report_path: Union[str, Path]) -> List[FxCopViolation]:
        """Parse legacy FxCop XML report.

        [20260303_FEATURE] Handles the legacy ``FxCopReport`` XML schema.
        Accepts a file path or an XML string directly (for testing).

        Args:
            report_path: Path to XML file or raw XML string produced by FxCop.exe.
        """
        try:
            source = str(report_path)
            if source.lstrip().startswith("<"):
                # Raw XML string provided
                root = ET.fromstring(source)
            else:
                tree = ET.parse(source)
                root = tree.getroot()
        except (ET.ParseError, OSError):
            return []
        violations: List[FxCopViolation] = []

        # FxCopReport XML schema: <Message TypeName="..." Category="..."><Issue .../>
        for message in root.iter("Message"):
            rule_id = message.get("TypeName", message.get("CheckId", ""))
            rule_name = rule_id
            category_raw = message.get("Category", "")
            # Normalize "Microsoft.Design" → "design"
            category_key = (
                category_raw.replace("Microsoft.", "").lower().replace(" ", "")
            )
            category = _CATEGORY_MAP.get(category_key, RuleCategory.OTHER)
            for issue in message.findall("Issue"):
                level_str = message.get("Level", issue.get("Level", "Warning")).lower()
                severity = (
                    FxCopSeverity.ERROR
                    if "error" in level_str
                    else (
                        FxCopSeverity.WARNING
                        if "warning" in level_str
                        else FxCopSeverity.INFORMATION
                    )
                )
                violations.append(
                    FxCopViolation(
                        rule_id=rule_id,
                        rule_name=rule_name,
                        category=category,
                        severity=severity,
                        message=(issue.text or "").strip(),
                        file_path=issue.get("Path", issue.get("File", "")),
                        line_number=int(issue.get("Line", 0)),
                        type_name=issue.get("TypeName"),
                        member_name=issue.get("MemberName"),
                    )
                )
        return violations

    def parse_sarif_report(
        self, sarif_source: Union[str, Path, dict]
    ) -> List[FxCopViolation]:
        """Parse SARIF 2.1 report (modern Roslyn-based FxCop / CA rules)."""
        findings = _parse_sarif(sarif_source)
        return [_sarif_to_violation(f) for f in findings if f.rule_id.startswith("CA")]

    def load_config(self, config_file: Path) -> FxCopConfig:
        """Load FxCop configuration."""
        return FxCopConfig(config_file=config_file)

    def categorize_violations(
        self, violations: List[FxCopViolation]
    ) -> Dict[RuleCategory, List[FxCopViolation]]:
        """Group violations by rule category."""
        result: Dict[RuleCategory, List[FxCopViolation]] = {}
        for v in violations:
            result.setdefault(v.category, []).append(v)
        return result

    def generate_report(
        self,
        violations: List[FxCopViolation],
        format: str = "json",
    ) -> str:
        """Return JSON or text report of FxCop violations."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "fxcop",
                    "total": len(violations),
                    "summary": {
                        cat.value: len(v)
                        for cat, v in self.categorize_violations(violations).items()
                    },
                    "issues": [
                        {
                            "rule_id": v.rule_id,
                            "rule_name": v.rule_name,
                            "category": v.category.value,
                            "severity": v.severity.value,
                            "message": v.message,
                            "file": v.file_path,
                            "line": v.line_number,
                        }
                        for v in violations
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{v.file_path}:{v.line_number}: {v.severity.value}: {v.rule_id} - {v.message}"
            for v in violations
        )


def _sarif_to_violation(f: SarifFinding) -> FxCopViolation:
    """Convert a SarifFinding (CA* rule) to an FxCopViolation."""
    # CA rules don't carry category in the rule_id — default to OTHER
    return FxCopViolation(
        rule_id=f.rule_id,
        rule_name=f.rule_id,
        category=RuleCategory.OTHER,
        severity=FxCopSeverity.WARNING if f.level == "warning" else FxCopSeverity.ERROR,
        message=f.message,
        file_path=f.uri,
        line_number=f.line,
    )
