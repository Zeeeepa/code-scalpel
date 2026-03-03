#!/usr/bin/env python3
"""
CppLint Parser - Google C++ Style Guide Enforcement.

[20260303_FEATURE] Full implementation: execute cpplint, parse stderr output,
categorize violations, calculate style score, and generate reports.

Reference: https://github.com/cpplint/cpplint
Command:   cpplint [--filter=...] <files>
Output:    stderr  file:line:  message  [category/check] [confidence 1-5]
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class StyleViolationType(Enum):
    """Style violation types from cpplint."""

    BUILD = "build"
    RUNTIME = "runtime"
    WHITESPACE = "whitespace"
    NAMING = "naming"
    COMMENTS = "comments"
    INCLUDES = "includes"
    FORMATTING = "formatting"


@dataclass
class CppLintViolation:
    """Represents a cpplint style violation."""

    violation_type: StyleViolationType
    message: str
    file_path: str
    line_number: int
    severity: str
    confidence: int = 0
    check_name: str = ""
    line_content: Optional[str] = None


@dataclass
class CppLintConfig:
    """CppLint configuration for style checking."""

    cpplint_version: str = "1.6.0"
    filter_rules: Optional[List[str]] = None
    max_line_length: int = 80
    root_dir: Optional[Path] = None
    extensions: List[str] = field(default_factory=lambda: ["cpp", "cc", "cxx", "h", "hpp"])


# --- Internal helpers ------------------------------------------------------- #

# cpplint output line:  path/file.cpp:42:  Missing space  [whitespace/braces] [4]
_LINE_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):\s+"
    r"(?P<msg>.+?)\s+"
    r"\[(?P<category>[^/\]]+)/(?P<check>[^\]]+)\]\s+"
    r"\[(?P<conf>\d)\]$"
)

# Map category prefix to StyleViolationType
_CAT_MAP: Dict[str, StyleViolationType] = {
    "build": StyleViolationType.BUILD,
    "runtime": StyleViolationType.RUNTIME,
    "whitespace": StyleViolationType.WHITESPACE,
    "naming": StyleViolationType.NAMING,
    "comments": StyleViolationType.COMMENTS,
    "include": StyleViolationType.INCLUDES,
    "includes": StyleViolationType.INCLUDES,
    "legal": StyleViolationType.COMMENTS,
    "readability": StyleViolationType.FORMATTING,
}

# Confidence weight for style score penalty (5 = most confident = bigger penalty)
_CONF_WEIGHT = {5: 2.0, 4: 1.5, 3: 1.0, 2: 0.5, 1: 0.25}


def _category_to_type(category: str) -> StyleViolationType:
    """Map a cpplint category string to StyleViolationType."""
    return _CAT_MAP.get(category.lower(), StyleViolationType.FORMATTING)


def _confidence_to_severity(confidence: int) -> str:
    """Map cpplint confidence (1-5) to a severity string."""
    if confidence >= 5:
        return "error"
    if confidence >= 3:
        return "warning"
    return "note"


def _to_sarif_result(v: CppLintViolation) -> Dict[str, Any]:
    """Convert a CppLintViolation to a SARIF 2.1 result dict."""
    return {
        "ruleId": f"cpplint/{v.check_name}",
        "level": "error" if v.confidence >= 5 else "warning",
        "message": {"text": v.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": v.file_path},
                    "region": {"startLine": v.line_number},
                }
            }
        ],
    }


# ---------------------------------------------------------------------------- #


class CppLintParser:
    """
    Parser for CppLint Google C++ style guide enforcement.

    [20260303_FEATURE] Enforces Google's C++ style guide with comprehensive
    checks for naming, formatting, and code organization.

    Supports direct execution (free tool) and offline output parsing.
    """

    def __init__(self) -> None:
        """Initialize CppLint parser."""
        self.config = CppLintConfig()
        self.violations: List[CppLintViolation] = []

    # ------------------------------------------------------------------ #
    # Execution                                                            #
    # ------------------------------------------------------------------ #

    def execute_cpplint(
        self, paths: List[Path], config: Optional[CppLintConfig] = None
    ) -> List[CppLintViolation]:
        """
        Run cpplint on the given files/directories.

        cpplint writes violations to stderr. Returns empty list if not installed.
        """
        if shutil.which("cpplint") is None:
            return []

        cfg = config or self.config
        cmd = ["cpplint"]
        if cfg.filter_rules:
            cmd.append(f"--filter={','.join(cfg.filter_rules)}")
        if cfg.max_line_length != 80:
            cmd.append(f"--linelength={cfg.max_line_length}")
        if cfg.root_dir:
            cmd.append(f"--root={cfg.root_dir}")

        # Expand directories to source files
        file_args: List[str] = []
        for path in paths:
            if path.is_dir():
                for ext in cfg.extensions:
                    file_args.extend(str(p) for p in path.rglob(f"*.{ext}"))
            else:
                file_args.append(str(path))

        if not file_args:
            return []

        cmd.extend(file_args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        # cpplint writes to stderr
        return self.parse_cpplint_output(result.stderr)

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_cpplint_output(self, output: str) -> List[CppLintViolation]:
        """
        Parse cpplint stderr output.

        Expected format per violation line:
            file.cpp:42:  message text  [category/check] [confidence]

        Lines not matching this format (e.g. "Done processing") are skipped.
        """
        violations = []
        for line in output.splitlines():
            m = _LINE_RE.match(line.strip())
            if not m:
                continue
            confidence = int(m.group("conf"))
            category = m.group("category")
            violations.append(
                CppLintViolation(
                    violation_type=_category_to_type(category),
                    message=m.group("msg").strip(),
                    file_path=m.group("file"),
                    line_number=int(m.group("line")),
                    severity=_confidence_to_severity(confidence),
                    confidence=confidence,
                    check_name=f"{category}/{m.group('check')}",
                )
            )
        return violations

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #

    def load_config(self, config_file: Path) -> CppLintConfig:
        """
        Parse a CPPLINT.cfg file.

        CPPLINT.cfg contains simple key=value pairs, e.g.:
            filter=-whitespace/tab,+build/include_order
            linelength=100
        """
        cfg = CppLintConfig()
        try:
            for line in config_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" in stripped:
                    key, _, value = stripped.partition("=")
                    key = key.strip().lower()
                    value = value.strip()
                    if key == "filter":
                        cfg.filter_rules = [r.strip() for r in value.split(",")]
                    elif key == "linelength":
                        try:
                            cfg.max_line_length = int(value)
                        except ValueError:
                            pass
                    elif key == "root":
                        cfg.root_dir = Path(value)
        except OSError:
            pass
        return cfg

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def categorize_violations(
        self, violations: List[CppLintViolation]
    ) -> Dict[StyleViolationType, List[CppLintViolation]]:
        """Group violations by StyleViolationType."""
        result: Dict[StyleViolationType, List[CppLintViolation]] = {
            vt: [] for vt in StyleViolationType
        }
        for v in violations:
            result[v.violation_type].append(v)
        return result

    def calculate_style_score(
        self, violations: List[CppLintViolation], total_lines: int
    ) -> float:
        """
        Calculate a style quality score (0–100).

        Penalty is weighted by confidence level:
            confidence 5 → 2.0 pts/violation
            confidence 4 → 1.5 pts/violation
            confidence 3 → 1.0 pts/violation
            confidence 1-2 → 0.5 pts/violation

        Score is normalized per 100 lines.
        """
        if total_lines == 0 or not violations:
            return 100.0

        total_penalty = sum(_CONF_WEIGHT.get(v.confidence, 1.0) for v in violations)
        penalty_per_100 = (total_penalty / total_lines) * 100.0
        return max(0.0, round(100.0 - penalty_per_100, 2))

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(
        self, violations: List[CppLintViolation], format: str = "json"
    ) -> str:
        """Generate a normalized report in JSON or SARIF 2.1 format."""
        if format == "sarif":
            sarif = {
                "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "cpplint",
                                "version": self.config.cpplint_version,
                            }
                        },
                        "results": [_to_sarif_result(v) for v in violations],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        by_type: Dict[str, int] = {}
        for v in violations:
            by_type[v.violation_type.value] = by_type.get(v.violation_type.value, 0) + 1

        report = {
            "tool": "cpplint",
            "violations": [
                {
                    "type": v.violation_type.value,
                    "check": v.check_name,
                    "message": v.message,
                    "file": v.file_path,
                    "line": v.line_number,
                    "severity": v.severity,
                    "confidence": v.confidence,
                }
                for v in violations
            ],
            "summary": {
                "total": len(violations),
                "by_type": by_type,
            },
        }
        return json.dumps(report, indent=2)
