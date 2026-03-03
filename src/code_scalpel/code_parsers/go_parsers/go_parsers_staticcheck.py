#!/usr/bin/env python3
"""staticcheck Go Parser - Advanced Go static analysis.

[20260303_FEATURE] Phase 2: full implementation.

Reference: https://staticcheck.io/
Command: staticcheck -f json ./...
JSONL output: one JSON object per line.
{"code":"SA1006","severity":"error","location":{"file":"main.go","line":15,"column":3},"message":"..."}

Check categories:
  SA: staticcheck (bugs, performance)
  S:  simple (simplifications)
  ST: stylecheck (style issues)
  QF: quickfix (auto-fixable)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union


class CheckCategory(Enum):
    """Staticcheck check category prefixes."""

    STATICCHECK = "SA"
    SIMPLE = "S"
    STYLECHECK = "ST"
    QUICKFIX = "QF"
    UNKNOWN = ""


def _categorize_code(code: str) -> CheckCategory:
    """Return the CheckCategory for a check code like 'SA1006', 'S1000'."""
    for cat in CheckCategory:
        if cat.value and code.startswith(cat.value):
            return cat
    return CheckCategory.UNKNOWN


@dataclass
class StaticcheckLocation:
    """File location referenced in a staticcheck finding."""

    file: str = ""
    line: int = 0
    column: int = 0


@dataclass
class StaticcheckFinding:
    """A single staticcheck finding from JSONL output."""

    code: str
    severity: str
    message: str
    location: StaticcheckLocation
    category: CheckCategory = CheckCategory.UNKNOWN
    end_location: Optional[StaticcheckLocation] = None
    related: List[Dict] = field(default_factory=list)


class StaticcheckParser:
    """Parser for staticcheck analysis output.

    [20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
    Falls back to ``[]`` gracefully when staticcheck is not on PATH.
    """

    def __init__(self) -> None:
        """Initialize StaticcheckParser."""
        self.language = "go"

    def execute_staticcheck(
        self,
        paths: Union[List[Path], Path, str],
    ) -> List[StaticcheckFinding]:
        """Run ``staticcheck -f json ./...`` and return findings.

        Returns ``[]`` gracefully when ``staticcheck`` is not on PATH.
        """
        if not shutil.which("staticcheck"):
            return []
        target = str(paths) if not isinstance(paths, list) else " ".join(str(p) for p in paths)
        cmd = ["staticcheck", "-f", "json", target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return self.parse_jsonl_output(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def parse_jsonl_output(self, output: str) -> List[StaticcheckFinding]:
        """Parse JSONL output (one JSON object per line).

        [20260303_FEATURE] Handles the staticcheck -f json format.

        Args:
            output: JSONL string from staticcheck stdout.
        """
        findings: List[StaticcheckFinding] = []
        if not output:
            return findings
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            loc_data = obj.get("location", {})
            loc = StaticcheckLocation(
                file=loc_data.get("file", ""),
                line=loc_data.get("line", 0),
                column=loc_data.get("column", 0),
            )
            end_data = obj.get("end", {})
            end_loc = (
                StaticcheckLocation(
                    file=end_data.get("file", ""),
                    line=end_data.get("line", 0),
                    column=end_data.get("column", 0),
                )
                if end_data
                else None
            )
            code = obj.get("code", "")
            findings.append(
                StaticcheckFinding(
                    code=code,
                    severity=obj.get("severity", "error"),
                    message=obj.get("message", ""),
                    location=loc,
                    category=_categorize_code(code),
                    end_location=end_loc,
                    related=obj.get("related", []),
                )
            )
        return findings

    def parse_json(self, json_output: str) -> List[StaticcheckFinding]:
        """Parse staticcheck JSON/JSONL output (alias for parse_jsonl_output)."""
        return self.parse_jsonl_output(json_output)

    def parse_json_report(self, path: Union[str, Path]) -> List[StaticcheckFinding]:
        """Parse a pre-saved staticcheck JSONL report file."""
        try:
            content = Path(path).read_text(encoding="utf-8")
            return self.parse_jsonl_output(content)
        except OSError:
            return []

    def categorize_by_code(
        self, findings: List[StaticcheckFinding]
    ) -> Dict[CheckCategory, List[StaticcheckFinding]]:
        """Group findings by CheckCategory (SA/S/ST/QF)."""
        result: Dict[CheckCategory, List[StaticcheckFinding]] = {}
        for f in findings:
            result.setdefault(f.category, []).append(f)
        return result

    def filter_by_severity(
        self,
        findings: List[StaticcheckFinding],
        severity: str = "error",
    ) -> List[StaticcheckFinding]:
        """Filter findings to those with the given severity."""
        return [f for f in findings if f.severity.lower() == severity.lower()]

    def generate_report(
        self, findings: List[StaticcheckFinding], format: str = "json"
    ) -> str:
        """Return a JSON or text report of staticcheck findings."""
        by_cat = self.categorize_by_code(findings)
        if format == "json":
            return json.dumps(
                {
                    "tool": "staticcheck",
                    "total": len(findings),
                    "by_category": {k.value or "UNKNOWN": len(v) for k, v in by_cat.items()},
                    "findings": [
                        {
                            "code": f.code,
                            "category": f.category.value,
                            "severity": f.severity,
                            "message": f.message,
                            "file": f.location.file,
                            "line": f.location.line,
                            "column": f.location.column,
                        }
                        for f in findings
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{f.location.file}:{f.location.line}:{f.location.column}: [{f.code}] {f.message}"
            for f in findings
        )
