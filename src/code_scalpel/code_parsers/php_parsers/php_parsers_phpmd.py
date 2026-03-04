#!/usr/bin/env python3
"""PHPMD Parser — PHP Mess Detector (complexity & code quality).

[20260304_FEATURE] Phase 2: full implementation.

Reference: https://phpmd.org/
Command:   phpmd [path] xml [ruleset]
Output:    PMD-flavoured XML <pmd><file><violation rule=\"...\" priority=\"3\">...
"""

from __future__ import annotations

import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

_PHPMD_BINARY_CANDIDATES = [
    "phpmd",
    "./vendor/bin/phpmd",
    "vendor/bin/phpmd",
]

# CWE mapping for relevant PHPMD rules
_CWE_MAP: Dict[str, str] = {
    "CyclomaticComplexity": "CWE-1121",  # Excessive McCabe Cyclomatic Complexity
    "ExcessiveMethodLength": "CWE-1080",  # Source Code File with Excessive Number of Lines
    "ExcessiveClassLength": "CWE-1080",
    "ExcessiveParameterList": "CWE-1041",  # Use of Redundant Code
    "LongVariable": "CWE-1101",  # Reliance on Runtime Arithmetic
    "ShortVariable": "CWE-1101",
    "EvalExpression": "CWE-95",  # Code Injection
    "ErrorControlOperator": "CWE-20",
}


def _find_phpmd() -> Optional[str]:
    for candidate in _PHPMD_BINARY_CANDIDATES:
        if shutil.which(candidate):
            return candidate
    return None


class PHPMDPriority(Enum):
    """PHPMD violation priority levels (1=critical, 5=minor)."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINOR = 5


class PHPMDRuleType(Enum):
    """PHPMD rule type categories."""

    CODE_SMELL = "code_smell"
    UNUSED = "unused"
    COMPLEXITY = "complexity"
    NAMING = "naming"
    CONTROVERSIAL = "controversial"
    DESIGN = "design"


@dataclass
class PHPMDViolation:
    """Represents a single PHPMD code violation.

    [20260304_FEATURE] Added cwe_id field.
    """

    message: str
    rule: str
    rule_set: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    priority: Optional[int] = None
    cwe_id: Optional[str] = None


@dataclass
class PHPMDConfig:
    """PHPMD configuration settings."""

    ruleset: str = "cleancode,codesize,controversial,design,naming,unusedcode"
    config_file: Optional[Path] = None
    custom_rules: List[str] = field(default_factory=list)


_RULESET_CATEGORY_MAP: Dict[str, str] = {
    "Clean Code Rules": PHPMDRuleType.CODE_SMELL.value,
    "Code Size Rules": PHPMDRuleType.COMPLEXITY.value,
    "Controversial Rules": PHPMDRuleType.CONTROVERSIAL.value,
    "Design Rules": PHPMDRuleType.DESIGN.value,
    "Naming Rules": PHPMDRuleType.NAMING.value,
    "Unused Code Rules": PHPMDRuleType.UNUSED.value,
}


def _infer_cwe(rule: str) -> Optional[str]:
    for key, cwe in _CWE_MAP.items():
        if key.lower() in rule.lower():
            return cwe
    return None


class PHPMDParser:
    """Parser for PHP Mess Detector violations.

    [20260304_FEATURE] Full implementation — execute, parse XML/JSON, report.

    Falls back gracefully (returns []) when phpmd is not on PATH.
    """

    def __init__(self) -> None:
        """Initialise PHPMDParser."""
        self.violations: List[PHPMDViolation] = []
        self.config: Optional[PHPMDConfig] = None
        self.language = "php"

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_phpmd(
        self,
        target_path: Union[Path, str, None] = None,
        ruleset: str = "cleancode,codesize,controversial,design,naming,unusedcode",
        report_format: str = "xml",
    ) -> List[PHPMDViolation]:
        """Run phpmd and return violations.

        Returns ``[]`` gracefully when phpmd is not on PATH.
        """
        binary = _find_phpmd()
        if binary is None:
            return []
        path_str = str(target_path) if target_path else "."
        cmd = [binary, path_str, report_format, ruleset]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if report_format == "xml":
                self.violations = self._parse_xml_string(result.stdout)
            elif report_format == "json":
                self.violations = self.parse_json_report(result.stdout)
            return self.violations
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_xml_report(self, xml_file: Path) -> List[PHPMDViolation]:
        """Parse PHPMD XML report file.

        Args:
            xml_file: Path to PHPMD XML report.
        Returns:
            List of PHPMDViolation objects.
        """
        try:
            content = Path(xml_file).read_text(encoding="utf-8", errors="replace")
            return self._parse_xml_string(content)
        except (FileNotFoundError, OSError):
            return []

    def _parse_xml_string(self, xml_data: str) -> List[PHPMDViolation]:
        """Parse PHPMD XML output from string."""
        if not xml_data:
            return []
        # Strip default namespace declarations so plain findall("file") works
        import re as _re

        xml_clean = _re.sub(r' xmlns(?::\w+)?=["\'][^"\']*["\']', "", xml_data)
        try:
            root = ET.fromstring(xml_clean)
            return self._parse_xml_root(root)
        except ET.ParseError:
            return []

    def _parse_xml_root(self, root: ET.Element) -> List[PHPMDViolation]:
        violations: List[PHPMDViolation] = []
        for file_elem in root.findall("file"):
            file_path = file_elem.get("name", "")
            for v in file_elem.findall("violation"):
                rule = v.get("rule", "")
                rule_set = v.get("ruleset", "")
                violations.append(
                    PHPMDViolation(
                        message=(v.text or "").strip(),
                        rule=rule,
                        rule_set=rule_set,
                        file_path=file_path,
                        line_number=int(v.get("beginline", 0)) or None,
                        priority=int(v.get("priority", 0)) or None,
                        cwe_id=_infer_cwe(rule),
                    )
                )
        return violations

    def parse_json_report(self, json_data: str) -> List[PHPMDViolation]:
        """Parse PHPMD JSON report.

        [20260304_FEATURE] Handles PHPMD's experimental JSON format.

        Args:
            json_data: JSON text from phpmd stdout.
        Returns:
            List of PHPMDViolation objects.
        """
        violations: List[PHPMDViolation] = []
        if not json_data:
            return violations
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return violations
        for file_obj in data.get("files", []):
            file_path = file_obj.get("file", "")
            for v in file_obj.get("violations", []):
                rule = v.get("rule", "")
                violations.append(
                    PHPMDViolation(
                        message=v.get("description", ""),
                        rule=rule,
                        rule_set=v.get("ruleSet", ""),
                        file_path=file_path,
                        line_number=v.get("beginLine"),
                        priority=v.get("priority"),
                        cwe_id=_infer_cwe(rule),
                    )
                )
        return violations

    def parse_output(self, output: str) -> List[PHPMDViolation]:
        """Parse raw phpmd output — tries XML then JSON."""
        output = output.strip()
        if not output:
            return []
        if output.startswith("<?xml") or output.startswith("<pmd"):
            return self._parse_xml_string(output)
        return self.parse_json_report(output)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def categorize_by_ruleset(
        self, violations: List[PHPMDViolation]
    ) -> Dict[str, List[PHPMDViolation]]:
        """Group violations by rule_set (maps to PHPMDRuleType)."""
        result: Dict[str, List[PHPMDViolation]] = {}
        for v in violations:
            category = _RULESET_CATEGORY_MAP.get(v.rule_set, "unknown")
            result.setdefault(category, []).append(v)
        return result

    def generate_report(
        self,
        violations: Optional[List[PHPMDViolation]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text summary report."""
        viols = violations if violations is not None else self.violations
        by_ruleset = self.categorize_by_ruleset(viols)
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "phpmd",
                    "total": len(viols),
                    "by_category": {k: len(v) for k, v in by_ruleset.items()},
                    "violations": [
                        {
                            "file": v.file_path,
                            "line": v.line_number,
                            "priority": v.priority,
                            "rule": v.rule,
                            "ruleset": v.rule_set,
                            "cwe": v.cwe_id,
                            "message": v.message,
                        }
                        for v in viols
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{v.file_path or '?'}:{v.line_number or '?'}: "
            f"[P{v.priority}] {v.rule} — {v.message}"
            for v in viols
        )
