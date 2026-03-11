#!/usr/bin/env python3
"""PHPCS Parser — PHP Code Sniffer (style & coding standards).

[20260304_FEATURE] Phase 2: full implementation.

Reference: https://github.com/squizlabs/PHP_CodeSniffer
Command:   phpcs --report=json [--standard=PSR12] [paths...]
Output:    {"totals":{...},"files":{"path":{"errors":N,"warnings":N,"messages":[...]}}}
"""

from __future__ import annotations

import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

_PHPCS_BINARY_CANDIDATES = [
    "phpcs",
    "./vendor/bin/phpcs",
    "vendor/bin/phpcs",
]


def _find_phpcs() -> Optional[str]:
    for candidate in _PHPCS_BINARY_CANDIDATES:
        if shutil.which(candidate):
            return candidate
    return None


class PHPCSSeverity(Enum):
    """PHPCS violation severity levels."""

    ERROR = "error"
    WARNING = "warning"


class PHPCSStandard(Enum):
    """Popular PHPCS coding standards."""

    PSR1 = "PSR1"
    PSR2 = "PSR2"
    PSR12 = "PSR12"
    WORDPRESS = "WordPress"
    SYMFONY = "Symfony"
    ZEND = "Zend"
    CUSTOM = "Custom"


@dataclass
class PHPCSViolation:
    """Represents a single PHPCS code standard violation."""

    sniff_id: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    severity: Optional[str] = None
    is_fixable: bool = False


@dataclass
class PHPCSConfig:
    """PHPCS configuration settings."""

    standard: str = "PSR12"
    config_file: Optional[Path] = None
    ignore_patterns: List[str] = field(default_factory=list)
    show_warnings: bool = True
    report_format: str = "json"


class PHPCSParser:
    """Parser for PHP Code Sniffer violations.

    [20260304_FEATURE] Full implementation — execute, parse JSON/XML, report.

    Falls back gracefully (returns []) when phpcs is not on PATH.
    """

    def __init__(self) -> None:
        """Initialise PHPCSParser."""
        self.violations: List[PHPCSViolation] = []
        self.config: Optional[PHPCSConfig] = None
        self.fixed_count: int = 0
        self.language = "php"

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_phpcs(
        self,
        target_path: Union[Path, str, None] = None,
        standard: str = "PSR12",
        report_format: str = "json",
    ) -> List[PHPCSViolation]:
        """Run phpcs and return violations.

        Returns ``[]`` gracefully when phpcs is not on PATH.
        """
        binary = _find_phpcs()
        if binary is None:
            return []
        path_str = str(target_path) if target_path else "."
        cmd = [
            binary,
            f"--standard={standard}",
            f"--report={report_format}",
            "--no-cache",
            path_str,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.violations = self.parse_json_report(result.stdout)
            return self.violations
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def auto_fix(
        self,
        target_path: Union[Path, str, None] = None,
        standard: str = "PSR12",
    ) -> dict[str, Any]:
        """Run phpcbf auto-fixer; returns count of fixed files."""
        phpcbf = shutil.which("phpcbf") or shutil.which("./vendor/bin/phpcbf")
        if phpcbf is None:
            return {"fixed": 0, "error": "phpcbf not found"}
        path_str = str(target_path) if target_path else "."
        cmd = [phpcbf, f"--standard={standard}", path_str]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            # phpcbf exits 1 if files were fixed, 0 if nothing to fix
            fixed = result.returncode in (0, 1)
            return {"fixed": fixed, "stdout": result.stdout}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"fixed": False, "error": "phpcbf execution failed"}

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_json_report(self, json_data: str) -> List[PHPCSViolation]:
        """Parse PHPCS --report=json output.

        [20260304_FEATURE] Parses per-file messages array.

        Args:
            json_data: JSON from phpcs stdout.
        Returns:
            List of PHPCSViolation objects.
        """
        violations: List[PHPCSViolation] = []
        if not json_data:
            return violations
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return violations
        for file_path, file_data in data.get("files", {}).items():
            for msg in file_data.get("messages", []):
                violations.append(
                    PHPCSViolation(
                        sniff_id=msg.get("source", ""),
                        message=msg.get("message", ""),
                        file_path=file_path,
                        line_number=msg.get("line"),
                        column=msg.get("column"),
                        severity=msg.get("type", "").lower(),
                        is_fixable=bool(msg.get("fixable", False)),
                    )
                )
        return violations

    def parse_xml_report(self, xml_file: Path) -> List[PHPCSViolation]:
        """Parse PHPCS --report=checkstyle XML output.

        Args:
            xml_file: Path to checkstyle XML report.
        """
        violations: List[PHPCSViolation] = []
        try:
            tree = ET.parse(xml_file)
        except (ET.ParseError, FileNotFoundError, OSError):
            return violations
        for file_elem in tree.getroot().findall("file"):
            file_path = file_elem.get("name", "")
            for error_elem in file_elem.findall("error"):
                violations.append(
                    PHPCSViolation(
                        sniff_id=error_elem.get("source", ""),
                        message=error_elem.get("message", ""),
                        file_path=file_path,
                        line_number=int(error_elem.get("line", 0)) or None,
                        column=int(error_elem.get("column", 0)) or None,
                        severity=error_elem.get("severity", "error").lower(),
                    )
                )
        return violations

    def parse_output(self, output: str) -> List[PHPCSViolation]:
        """Parse raw phpcs output (JSON format)."""
        return self.parse_json_report(output)

    def load_config(self, config_path: Path) -> PHPCSConfig:
        """Load phpcs.xml / .phpcs.xml config (best-effort)."""
        config = PHPCSConfig(config_file=config_path)
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            # <rule ref="PSR12"/>
            for rule in root.findall(".//rule"):
                ref = rule.get("ref", "")
                if ref:
                    config.standard = ref
                    break
        except (ET.ParseError, FileNotFoundError, OSError):
            pass
        return config

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def categorize_by_severity(
        self, violations: List[PHPCSViolation]
    ) -> Dict[str, List[PHPCSViolation]]:
        """Group violations by severity."""
        result: Dict[str, List[PHPCSViolation]] = {}
        for v in violations:
            key = v.severity or "unknown"
            result.setdefault(key, []).append(v)
        return result

    def generate_report(
        self,
        violations: Optional[List[PHPCSViolation]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text summary report."""
        viols = violations if violations is not None else self.violations
        by_sev = self.categorize_by_severity(viols)
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "phpcs",
                    "total": len(viols),
                    "by_severity": {k: len(v) for k, v in by_sev.items()},
                    "violations": [
                        {
                            "file": v.file_path,
                            "line": v.line_number,
                            "column": v.column,
                            "severity": v.severity,
                            "sniff": v.sniff_id,
                            "fixable": v.is_fixable,
                            "message": v.message,
                        }
                        for v in viols
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{v.file_path or '?'}:{v.line_number or '?'}: "
            f"[{v.severity}] {v.message} ({v.sniff_id})"
            for v in viols
        )
