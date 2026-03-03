#!/usr/bin/env python3
"""
Cppcheck Parser - Static Analysis for C/C++ Code.

[20260303_FEATURE] Full implementation: execute cppcheck, parse XML v2 output,
categorize issues, map to CWE, and generate normalized reports.

Reference: https://cppcheck.sourceforge.io/
Command:   cppcheck --xml-version=2 --enable=all <paths> 2>&1
"""

import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CppcheckSeverity(Enum):
    """Cppcheck issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    STYLE = "style"
    PERFORMANCE = "performance"
    PORTABILITY = "portability"
    INFORMATION = "information"


class IssueCategory(Enum):
    """Cppcheck issue categories."""

    MEMORY = "memory"
    LOGIC = "logic"
    PERFORMANCE = "performance"
    STYLE = "style"
    SECURITY = "security"
    PORTABILITY = "portability"


@dataclass
class CppcheckIssue:
    """Represents a Cppcheck analysis issue."""

    issue_id: str
    category: IssueCategory
    severity: CppcheckSeverity
    message: str
    detailed_message: str
    file_path: str
    line_number: int
    column: int
    cwe_id: Optional[str] = None
    verbose_message: Optional[str] = None


@dataclass
class CppcheckConfig:
    """Cppcheck configuration for analysis."""

    cppcheck_version: str = "2.13"
    enable_checks: Optional[List[str]] = None
    suppress_file: Optional[Path] = None
    standard: str = "c++17"
    jobs: int = 4


# --- Internal helpers ------------------------------------------------------- #

# Map cppcheck error IDs to IssueCategory
_MEMORY_ID_PREFIXES = (
    "memLeak",
    "resourceLeak",
    "deallocDealloc",
    "doubleFree",
    "autovarInvalidDealloc",
    "mismatchAllocDealloc",
    "leakNoVarFunctionCall",
    "returnAddressOfAutoVariable",
    "danglingLifetime",
    "danglingTempReference",
)
_SECURITY_ID_PREFIXES = (
    "bufferAccess",
    "outOfBounds",
    "arrayIndexOutOfBounds",
    "negativeIndex",
    "useClosedFile",
    "writeReadOnlyFile",
    "invalidContainer",
)
_PERFORMANCE_ID_PREFIXES = (
    "stlFind",
    "redundantCopy",
    "inefficient",
    "postfixOperator",
    "passedByValue",
    "useStlAlgorithm",
)
_PORTABILITY_ID_PREFIXES = (
    "shiftTooManyBits",
    "integerOverflow",
    "truncLongCastAssignment",
    "invalidPointerCast",
)


def _infer_category(issue_id: str, severity: CppcheckSeverity) -> IssueCategory:
    """Infer IssueCategory from error id and severity."""
    for prefix in _MEMORY_ID_PREFIXES:
        if issue_id.startswith(prefix):
            return IssueCategory.MEMORY
    for prefix in _SECURITY_ID_PREFIXES:
        if issue_id.startswith(prefix):
            return IssueCategory.SECURITY
    for prefix in _PERFORMANCE_ID_PREFIXES:
        if issue_id.startswith(prefix):
            return IssueCategory.PERFORMANCE
    for prefix in _PORTABILITY_ID_PREFIXES:
        if issue_id.startswith(prefix):
            return IssueCategory.PORTABILITY
    # Fall back to severity-based mapping
    if severity == CppcheckSeverity.PERFORMANCE:
        return IssueCategory.PERFORMANCE
    if severity == CppcheckSeverity.PORTABILITY:
        return IssueCategory.PORTABILITY
    if severity == CppcheckSeverity.STYLE or severity == CppcheckSeverity.INFORMATION:
        return IssueCategory.STYLE
    # error/warning without a specific prefix → logic
    return IssueCategory.LOGIC


def _parse_error_element(error_elem: ET.Element) -> Optional[CppcheckIssue]:
    """Parse a single <error> XML element into a CppcheckIssue."""
    issue_id = error_elem.get("id", "")
    severity_str = error_elem.get("severity", "warning")
    msg = error_elem.get("msg", "")
    verbose = error_elem.get("verbose", "")
    cwe_raw = error_elem.get("cwe")
    cwe_id = f"CWE-{cwe_raw}" if cwe_raw else None

    try:
        severity = CppcheckSeverity(severity_str)
    except ValueError:
        severity = CppcheckSeverity.WARNING

    category = _infer_category(issue_id, severity)

    # Location may be in child <location> elements; use the first one
    loc = error_elem.find("location")
    if loc is not None:
        file_path = loc.get("file", "")
        try:
            line_number = int(loc.get("line", "0"))
        except ValueError:
            line_number = 0
        try:
            column = int(loc.get("column", "0"))
        except ValueError:
            column = 0
    else:
        file_path = error_elem.get("file0", "")
        line_number = 0
        column = 0

    return CppcheckIssue(
        issue_id=issue_id,
        category=category,
        severity=severity,
        message=msg,
        detailed_message=msg,
        file_path=file_path,
        line_number=line_number,
        column=column,
        cwe_id=cwe_id,
        verbose_message=verbose or None,
    )


def _to_sarif_result(issue: CppcheckIssue) -> Dict[str, Any]:
    """Convert a CppcheckIssue to a SARIF 2.1 result dict."""
    result: Dict[str, Any] = {
        "ruleId": issue.issue_id,
        "level": "error" if issue.severity == CppcheckSeverity.ERROR else "warning",
        "message": {"text": issue.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": issue.file_path},
                    "region": {
                        "startLine": issue.line_number,
                        "startColumn": issue.column,
                    },
                }
            }
        ],
    }
    if issue.cwe_id:
        result["taxa"] = [{"id": issue.cwe_id, "toolComponent": {"name": "CWE"}}]
    return result


# ---------------------------------------------------------------------------- #


class CppcheckParser:
    """
    Parser for Cppcheck static analysis of C/C++ code.

    [20260303_FEATURE] Detects bugs, memory issues, and code quality problems
    using comprehensive static analysis via Cppcheck's XML v2 output.

    Supports both direct execution (free tool) and offline XML report parsing.
    """

    def __init__(self) -> None:
        """Initialize Cppcheck parser."""
        self.config = CppcheckConfig()
        self.issues: List[CppcheckIssue] = []

    # ------------------------------------------------------------------ #
    # Execution                                                            #
    # ------------------------------------------------------------------ #

    def execute_cppcheck(
        self, paths: List[Path], config: Optional[CppcheckConfig] = None
    ) -> List[CppcheckIssue]:
        """
        Run cppcheck on the given paths and return parsed issues.

        Cppcheck outputs XML to stderr when --xml-version=2 is used.
        Returns empty list if cppcheck is not installed.
        """
        if shutil.which("cppcheck") is None:
            return []

        cfg = config or self.config
        cmd = [
            "cppcheck",
            "--xml-version=2",
            f"--std={cfg.standard}",
            f"-j{cfg.jobs}",
        ]
        if cfg.enable_checks:
            cmd.append(f"--enable={','.join(cfg.enable_checks)}")
        else:
            cmd.append("--enable=all")
        if cfg.suppress_file and cfg.suppress_file.exists():
            cmd.append(f"--suppressions-list={cfg.suppress_file}")
        cmd.extend(str(p) for p in paths)

        result = subprocess.run(cmd, capture_output=True, text=True)
        # cppcheck writes XML to stderr
        xml_output = result.stderr or result.stdout
        if not xml_output.strip():
            return []
        return self.parse_xml_string(xml_output)

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_xml_string(self, xml_str: str) -> List[CppcheckIssue]:
        """Parse Cppcheck XML v2 output from a string (typically stderr)."""
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError:
            return []

        errors_elem = root.find("errors")
        if errors_elem is None:
            return []

        issues = []
        for error_elem in errors_elem.findall("error"):
            issue = _parse_error_element(error_elem)
            if issue is not None:
                issues.append(issue)
        return issues

    def parse_xml_report(self, report_path: Path) -> List[CppcheckIssue]:
        """Parse a Cppcheck XML report file saved from a previous run."""
        try:
            return self.parse_xml_string(report_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return []

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #

    def load_config(self, config_file: Path) -> CppcheckConfig:
        """Parse a .cppcheck project XML file into a CppcheckConfig."""
        cfg = CppcheckConfig()
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
            # <builddir> version="2" ...
            version_elem = root.find(".//platform")
            if version_elem is not None:
                cfg.standard = version_elem.get("type", cfg.standard)
            jobs_elem = root.find(".//analyze/maxCtuDepth")
            if jobs_elem is not None:
                try:
                    cfg.jobs = int(jobs_elem.text or cfg.jobs)
                except ValueError:
                    pass
        except (ET.ParseError, OSError):
            pass
        return cfg

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def categorize_issues(
        self, issues: List[CppcheckIssue]
    ) -> Dict[IssueCategory, List[CppcheckIssue]]:
        """Group issues by IssueCategory."""
        result: Dict[IssueCategory, List[CppcheckIssue]] = {
            cat: [] for cat in IssueCategory
        }
        for issue in issues:
            result[issue.category].append(issue)
        return result

    def detect_memory_issues(self, issues: List[CppcheckIssue]) -> List[CppcheckIssue]:
        """Return only memory-related issues."""
        return [i for i in issues if i.category == IssueCategory.MEMORY]

    def map_to_cwe(
        self, issues: List[CppcheckIssue]
    ) -> Dict[str, List[CppcheckIssue]]:
        """Group issues by their CWE identifier (e.g. 'CWE-476')."""
        result: Dict[str, List[CppcheckIssue]] = {}
        for issue in issues:
            if issue.cwe_id:
                result.setdefault(issue.cwe_id, []).append(issue)
        return result

    def calculate_quality_metrics(
        self, issues: List[CppcheckIssue]
    ) -> Dict[str, Any]:
        """Return a summary metrics dict."""
        by_severity: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        cwe_ids: set = set()

        for issue in issues:
            by_severity[issue.severity.value] = (
                by_severity.get(issue.severity.value, 0) + 1
            )
            by_category[issue.category.value] = (
                by_category.get(issue.category.value, 0) + 1
            )
            if issue.cwe_id:
                cwe_ids.add(issue.cwe_id)

        return {
            "total": len(issues),
            "by_severity": by_severity,
            "by_category": by_category,
            "cwe_coverage": sorted(cwe_ids),
        }

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(
        self, issues: List[CppcheckIssue], format: str = "json"
    ) -> str:
        """
        Generate a normalized report.

        Args:
            issues: List of CppcheckIssue objects.
            format: "json" (default) or "sarif".

        Returns:
            JSON string.
        """
        if format == "sarif":
            sarif = {
                "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "Cppcheck",
                                "version": self.config.cppcheck_version,
                            }
                        },
                        "results": [_to_sarif_result(i) for i in issues],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        # Default: normalized JSON
        report = {
            "tool": "cppcheck",
            "issues": [
                {
                    "id": i.issue_id,
                    "severity": i.severity.value,
                    "category": i.category.value,
                    "message": i.message,
                    "file": i.file_path,
                    "line": i.line_number,
                    "column": i.column,
                    "cwe": i.cwe_id,
                }
                for i in issues
            ],
            "summary": self.calculate_quality_metrics(issues),
        }
        return json.dumps(report, indent=2)
