#!/usr/bin/env python3
"""Psalm Parser — Vimeo's PHP static analyser with taint analysis.

[20260304_FEATURE] Phase 2: full implementation.

Reference: https://psalm.dev/
Command:   vendor/bin/psalm --output-format=json [paths...]
Output:    [{"severity":"error","line_from":5,"message":"...","file_name":"src/Foo.php",...}]
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

_PSALM_BINARY_CANDIDATES = [
    "psalm",
    "./vendor/bin/psalm",
    "vendor/bin/psalm",
]

# CWE mapping for Psalm issue types
_CWE_MAP: Dict[str, str] = {
    "ExecutionOfCode": "CWE-78",  # Command Injection
    "PossiblyNullReference": "CWE-476",
    "NullReference": "CWE-476",
    "UndefinedVariable": "CWE-824",
    "UndefinedFunction": "CWE-824",
    "PossiblyFalseReference": "CWE-476",
    "TypeDoesNotContainType": "CWE-704",
    "InvalidArgument": "CWE-20",
    "Taint": "CWE-89",  # Default taint → SQL injection
    "EscapeString": "CWE-79",  # XSS
    "ShellExec": "CWE-78",
    "FileInclusion": "CWE-98",
    "UnresolvableInclude": "CWE-98",
}


def _find_psalm() -> Optional[str]:
    for candidate in _PSALM_BINARY_CANDIDATES:
        if shutil.which(candidate):
            return candidate
    return None


class PsalmSeverity(Enum):
    """Psalm error severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PsalmErrorType(Enum):
    """Psalm error type categories."""

    TYPE_ERROR = "type_error"
    TAINT = "taint"
    DEAD_CODE = "dead_code"
    UNDEFINED = "undefined"
    SECURITY = "security"
    LOGIC = "logic"
    UNKNOWN = "unknown"


@dataclass
class PsalmError:
    """Represents a single Psalm analysis error.

    [20260304_FEATURE] Added cwe_id, psalm_type fields.
    """

    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    severity: Optional[str] = None
    error_type: Optional[str] = None
    psalm_type: Optional[str] = None
    snippet: Optional[str] = None
    cwe_id: Optional[str] = None


@dataclass
class PsalmConfig:
    """Psalm configuration settings."""

    config_file: Optional[Path] = None
    level: int = 1
    analysis_type: str = "normal"
    paths: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(default_factory=list)
    plugins: List[str] = field(default_factory=list)


def _infer_error_type(psalm_type: str) -> str:
    """Infer our PsalmErrorType from Psalm's issue type string."""
    t = psalm_type.lower()
    if "taint" in t or "escape" in t or "shell" in t or "inclusion" in t:
        return PsalmErrorType.TAINT.value
    if "undefined" in t or "unresolvable" in t:
        return PsalmErrorType.UNDEFINED.value
    if "dead" in t or "unreachable" in t:
        return PsalmErrorType.DEAD_CODE.value
    if "type" in t or "argument" in t or "return" in t:
        return PsalmErrorType.TYPE_ERROR.value
    if "security" in t or "injection" in t:
        return PsalmErrorType.SECURITY.value
    return PsalmErrorType.UNKNOWN.value


def _infer_cwe(psalm_type: str) -> Optional[str]:
    for key, cwe in _CWE_MAP.items():
        if key.lower() in psalm_type.lower():
            return cwe
    return None


class PsalmParser:
    """Parser for Psalm static analysis results.

    [20260304_FEATURE] Full implementation — execute, parse, taint, report.

    Falls back gracefully (returns []) when psalm is not on PATH.
    """

    def __init__(self) -> None:
        """Initialise PsalmParser."""
        self.errors: List[PsalmError] = []
        self.config: Optional[PsalmConfig] = None
        self.language = "php"

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_psalm(
        self,
        paths: Union[List[str], str, None] = None,
        output_format: str = "json",
        taint_analysis: bool = False,
    ) -> List[PsalmError]:
        """Run psalm and return parsed errors.

        Returns ``[]`` gracefully when psalm is not on PATH.
        """
        binary = _find_psalm()
        if binary is None:
            return []
        target_paths: List[str] = (
            ["."]
            if paths is None
            else [paths] if isinstance(paths, str) else list(paths)
        )
        cmd = [binary, f"--output-format={output_format}", "--no-cache"]
        if taint_analysis:
            cmd.append("--taint-analysis")
        cmd += target_paths
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.errors = self.parse_json_report(result.stdout)
            return self.errors
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_json_report(self, json_data: str) -> List[PsalmError]:
        """Parse Psalm --output-format=json output.

        [20260304_FEATURE] Psalm emits a JSON array of issue objects.

        Args:
            json_data: JSON array text from psalm stdout.
        Returns:
            List of PsalmError objects.
        """
        errors: List[PsalmError] = []
        if not json_data:
            return errors
        try:
            items = json.loads(json_data)
        except json.JSONDecodeError:
            return errors
        if not isinstance(items, list):
            # Psalm may emit {"errors":[...]} wrapper
            items = items.get("errors", []) if isinstance(items, dict) else []
        for item in items:
            psalm_type = item.get("type", "") or item.get("error_type", "")
            message = item.get("message", "")
            errors.append(
                PsalmError(
                    message=message,
                    file_path=item.get("file_name") or item.get("file"),
                    line_number=item.get("line_from") or item.get("line"),
                    column=item.get("column_from") or item.get("column"),
                    severity=item.get("severity", "").lower() or "error",
                    error_type=_infer_error_type(psalm_type),
                    psalm_type=psalm_type,
                    snippet=item.get("snippet"),
                    cwe_id=_infer_cwe(psalm_type),
                )
            )
        return errors

    def parse_json_pretty(self, json_data: str) -> List[PsalmError]:
        """Alias for parse_json_report (same format, just pretty-printed)."""
        return self.parse_json_report(json_data)

    def parse_output(self, output: str) -> List[PsalmError]:
        """Parse raw psalm output."""
        return self.parse_json_report(output)

    def load_config(self, config_path: Path) -> PsalmConfig:
        """Load psalm.xml config (best-effort)."""
        import xml.etree.ElementTree as ET

        config = PsalmConfig(config_file=config_path)
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            level = root.get("errorLevel")
            if level:
                try:
                    config.level = int(level)
                except ValueError:
                    pass
            for proj in root.findall(".//projectFiles/directory"):
                name = proj.get("name")
                if name:
                    config.paths.append(name)
        except Exception:  # noqa: BLE001
            pass
        return config

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    def analyze_taint(
        self, errors: Optional[List[PsalmError]] = None
    ) -> List[Dict[str, Any]]:
        """Return taint-related errors with CWE IDs.

        Args:
            errors: Errors to filter; defaults to ``self.errors``.
        Returns:
            List of dicts with taint issue details.
        """
        errs = errors if errors is not None else self.errors
        return [
            {
                "file": e.file_path,
                "line": e.line_number,
                "psalm_type": e.psalm_type,
                "cwe": e.cwe_id,
                "message": e.message,
            }
            for e in errs
            if e.error_type == PsalmErrorType.TAINT.value or e.cwe_id is not None
        ]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def categorize_by_type(
        self, errors: List[PsalmError]
    ) -> Dict[str, List[PsalmError]]:
        """Group errors by error_type."""
        result: Dict[str, List[PsalmError]] = {}
        for e in errors:
            key = e.error_type or PsalmErrorType.UNKNOWN.value
            result.setdefault(key, []).append(e)
        return result

    def generate_report(
        self,
        errors: Optional[List[PsalmError]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text summary report."""
        errs = errors if errors is not None else self.errors
        by_type = self.categorize_by_type(errs)
        taint_count = sum(1 for e in errs if e.error_type == PsalmErrorType.TAINT.value)
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "psalm",
                    "total_errors": len(errs),
                    "taint_issues": taint_count,
                    "by_type": {k: len(v) for k, v in by_type.items()},
                    "errors": [
                        {
                            "file": e.file_path,
                            "line": e.line_number,
                            "severity": e.severity,
                            "type": e.psalm_type,
                            "cwe": e.cwe_id,
                            "message": e.message,
                        }
                        for e in errs
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{e.file_path or '?'}:{e.line_number or '?'}: [{e.severity}] {e.message}"
            for e in errs
        )
