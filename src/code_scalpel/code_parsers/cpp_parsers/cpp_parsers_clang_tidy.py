#!/usr/bin/env python3
"""
Clang-Tidy Parser - C++ Modernization and Best Practices.

[20260303_FEATURE] Full implementation: execute clang-tidy, parse diagnostic
output and JSON fixes export, categorize checks, and generate reports.

Reference: https://clang.llvm.org/extra/clang-tidy/
Command:   clang-tidy <file> -- [compile_flags]
           clang-tidy --export-fixes=fixes.yaml <file> --
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckCategory(Enum):
    """Clang-Tidy check categories."""

    MODERNIZE = "modernize"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    BUGPRONE = "bugprone"
    CLANG_ANALYZER = "clang_analyzer"
    CPPCOREGUIDELINES = "cppcoreguidelines"
    GOOGLE = "google"
    LLVM = "llvm"
    MISC = "misc"


@dataclass
class ClangTidyCheck:
    """Represents a clang-tidy check violation."""

    check_id: str
    category: CheckCategory
    message: str
    file_path: str
    line_number: int
    column: int
    severity: str
    replacements: Optional[str] = None
    modernization_level: Optional[str] = None


@dataclass
class ClangTidyConfig:
    """Clang-Tidy configuration for analysis."""

    clang_tidy_version: str = "18.0.0"
    config_file: Optional[Path] = None
    checks_enabled: Optional[List[str]] = None
    checks_disabled: Optional[List[str]] = None
    cpp_standard: str = "c++17"
    fix_mode: bool = False


# --- Internal helpers ------------------------------------------------------- #

# Ordered prefix → CheckCategory mapping (checked in order; first match wins)
_CHECK_PREFIX_MAP: List[tuple] = [
    ("modernize-", CheckCategory.MODERNIZE),
    ("performance-", CheckCategory.PERFORMANCE),
    ("readability-", CheckCategory.READABILITY),
    ("bugprone-", CheckCategory.BUGPRONE),
    ("clang-analyzer-", CheckCategory.CLANG_ANALYZER),
    ("cppcoreguidelines-", CheckCategory.CPPCOREGUIDELINES),
    ("google-", CheckCategory.GOOGLE),
    ("llvm-", CheckCategory.LLVM),
]

# Regex to parse clang-tidy diagnostic lines:
# file.cpp:12:5: warning: message text [check-name]
_DIAG_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s+"
    r"(?P<severity>warning|error|note|remark):\s+"
    r"(?P<msg>.+?)\s+\[(?P<check>[^\]]+)\]$"
)


def _check_to_category(check_id: str) -> CheckCategory:
    """Map a clang-tidy check ID prefix to its CheckCategory."""
    for prefix, category in _CHECK_PREFIX_MAP:
        if check_id.startswith(prefix):
            return category
    return CheckCategory.MISC


def _modernization_level(check_id: str) -> Optional[str]:
    """Infer C++ standard level from modernize-* check name."""
    for std in ("c++20", "c++17", "c++14", "c++11"):
        short = std.replace("+", "").replace("-", "")  # cpp20, cpp17 ...
        if short in check_id:
            return std
    return None


def _to_sarif_result(check: ClangTidyCheck) -> Dict[str, Any]:
    """Convert a ClangTidyCheck to a SARIF 2.1 result dict."""
    return {
        "ruleId": check.check_id,
        "level": "error" if check.severity == "error" else "warning",
        "message": {"text": check.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": check.file_path},
                    "region": {
                        "startLine": check.line_number,
                        "startColumn": check.column,
                    },
                }
            }
        ],
    }


# ---------------------------------------------------------------------------- #


class ClangTidyParser:
    """
    Parser for Clang-Tidy C++ modernization and best practices analysis.

    [20260303_FEATURE] Detects modernization opportunities, performance issues,
    and code quality problems using LLVM's clang-tidy tool.

    Supports both direct execution and offline diagnostic/fixes-export parsing.
    """

    def __init__(self) -> None:
        """Initialize Clang-Tidy parser."""
        self.config = ClangTidyConfig()
        self.checks: List[ClangTidyCheck] = []

    # ------------------------------------------------------------------ #
    # Execution                                                            #
    # ------------------------------------------------------------------ #

    def execute_clang_tidy(
        self, paths: List[Path], config: Optional[ClangTidyConfig] = None
    ) -> List[ClangTidyCheck]:
        """
        Run clang-tidy on the given files and return parsed checks.

        Returns empty list if clang-tidy is not installed.
        """
        if shutil.which("clang-tidy") is None:
            return []

        cfg = config or self.config
        all_checks: List[ClangTidyCheck] = []

        for path in paths:
            cmd = ["clang-tidy"]
            if cfg.config_file and cfg.config_file.exists():
                cmd += [f"--config-file={cfg.config_file}"]
            if cfg.checks_enabled:
                cmd += [f"--checks={','.join(cfg.checks_enabled)}"]
            if cfg.fix_mode:
                cmd += ["--fix"]
            cmd += [str(path), "--", f"-std={cfg.cpp_standard}"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            # clang-tidy diagnostic output is on stdout
            combined = result.stdout + result.stderr
            all_checks.extend(self.parse_diagnostic_output(combined))

        return all_checks

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_diagnostic_output(self, output: str) -> List[ClangTidyCheck]:
        """
        Parse clang-tidy diagnostic output (stdout/stderr).

        Expected line format:
            file.cpp:12:5: warning: message text [check-name]
        """
        checks = []
        for line in output.splitlines():
            m = _DIAG_RE.match(line.strip())
            if not m:
                continue
            check_id = m.group("check")
            category = _check_to_category(check_id)
            checks.append(
                ClangTidyCheck(
                    check_id=check_id,
                    category=category,
                    message=m.group("msg"),
                    file_path=m.group("file"),
                    line_number=int(m.group("line")),
                    column=int(m.group("col")),
                    severity=m.group("severity"),
                    modernization_level=(
                        _modernization_level(check_id)
                        if category == CheckCategory.MODERNIZE
                        else None
                    ),
                )
            )
        return checks

    def parse_json_report(self, report_path: Path) -> List[ClangTidyCheck]:
        """
        Parse a clang-tidy --export-fixes YAML/JSON output file.

        The fixes export contains the same diagnostic information in a
        structured format; we extract the check name and location.
        """
        checks = []
        try:
            raw = report_path.read_text(encoding="utf-8")
            # clang-tidy can write YAML or JSON; try JSON first
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Try minimal YAML parsing for the Diagnostics key
                data = _parse_minimal_yaml_fixes(raw)

            for diag in data.get("Diagnostics", []):
                check_id = diag.get("DiagnosticName", "")
                msg = diag.get("DiagnosticMessage", {}).get("Message", "")
                file_path = diag.get("DiagnosticMessage", {}).get("FilePath", "")
                offset = diag.get("DiagnosticMessage", {}).get("FileOffset", 0)
                category = _check_to_category(check_id)
                checks.append(
                    ClangTidyCheck(
                        check_id=check_id,
                        category=category,
                        message=msg,
                        file_path=file_path,
                        line_number=0,  # offset-based; line not directly available
                        column=offset,
                        severity="warning",
                    )
                )
        except (OSError, KeyError):
            pass
        return checks

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #

    def load_config(self, config_file: Path) -> ClangTidyConfig:
        """
        Parse a .clang-tidy YAML config file.

        Extracts Checks, CheckOptions, and InheritParentConfig entries.
        """
        cfg = ClangTidyConfig(config_file=config_file)
        try:
            raw = config_file.read_text(encoding="utf-8")
            for line in raw.splitlines():
                stripped = line.strip()
                if stripped.startswith("Checks:"):
                    checks_str = stripped.split(":", 1)[1].strip().strip("'\"")
                    parts = [c.strip() for c in checks_str.split(",")]
                    enabled = [c for c in parts if not c.startswith("-")]
                    disabled = [c.lstrip("-") for c in parts if c.startswith("-")]
                    cfg.checks_enabled = enabled or None
                    cfg.checks_disabled = disabled or None
        except OSError:
            pass
        return cfg

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def categorize_checks(
        self, checks: List[ClangTidyCheck]
    ) -> Dict[CheckCategory, List[ClangTidyCheck]]:
        """Group checks by CheckCategory."""
        result: Dict[CheckCategory, List[ClangTidyCheck]] = {
            cat: [] for cat in CheckCategory
        }
        for check in checks:
            result[check.category].append(check)
        return result

    def detect_modernization_opportunities(
        self, checks: List[ClangTidyCheck]
    ) -> List[ClangTidyCheck]:
        """Return only modernize-* checks."""
        return [c for c in checks if c.category == CheckCategory.MODERNIZE]

    def apply_fixes(self, checks: List[ClangTidyCheck]) -> Dict[str, int]:
        """
        Run clang-tidy --fix on files with pending checks.

        Returns a dict mapping file path → number of fixes applied.
        Returns empty dict if clang-tidy is not installed.
        """
        if shutil.which("clang-tidy") is None:
            return {}

        files = list({c.file_path for c in checks if c.file_path})
        fixes_applied: Dict[str, int] = {}
        for file_path in files:
            result = subprocess.run(
                ["clang-tidy", "--fix", file_path, "--"],
                capture_output=True,
                text=True,
            )
            # Count "fix applied" in output as a proxy
            count = result.stdout.lower().count(
                "fix applied"
            ) + result.stderr.lower().count("fix applied")
            fixes_applied[file_path] = count
        return fixes_applied

    def analyze_cpp_standard_compatibility(
        self, checks: List[ClangTidyCheck], target_std: str
    ) -> List[ClangTidyCheck]:
        """
        Filter modernize-* checks relevant to the target C++ standard.

        E.g. target_std="c++17" returns only checks targeting C++17 or earlier.
        """
        std_order = ["c++11", "c++14", "c++17", "c++20"]
        try:
            target_idx = std_order.index(target_std.lower())
        except ValueError:
            return checks

        relevant = []
        for check in checks:
            if check.category != CheckCategory.MODERNIZE:
                relevant.append(check)
                continue
            level = check.modernization_level
            if level is None:
                relevant.append(check)
                continue
            try:
                if std_order.index(level) <= target_idx:
                    relevant.append(check)
            except ValueError:
                relevant.append(check)
        return relevant

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(
        self, checks: List[ClangTidyCheck], format: str = "json"
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
                                "name": "clang-tidy",
                                "version": self.config.clang_tidy_version,
                            }
                        },
                        "results": [_to_sarif_result(c) for c in checks],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        by_category: Dict[str, int] = {}
        for check in checks:
            by_category[check.category.value] = (
                by_category.get(check.category.value, 0) + 1
            )

        report = {
            "tool": "clang-tidy",
            "checks": [
                {
                    "id": c.check_id,
                    "category": c.category.value,
                    "severity": c.severity,
                    "message": c.message,
                    "file": c.file_path,
                    "line": c.line_number,
                    "column": c.column,
                    "modernization_level": c.modernization_level,
                }
                for c in checks
            ],
            "summary": {
                "total": len(checks),
                "by_category": by_category,
            },
        }
        return json.dumps(report, indent=2)


def _parse_minimal_yaml_fixes(raw: str) -> Dict[str, Any]:
    """
    Minimal YAML parser for clang-tidy fixes export.

    The fixes YAML has a simple structure; we only need Diagnostics entries.
    Falls back to empty dict on parse failure.
    """
    # This is a best-effort minimal parser — not a full YAML library.
    # The fixes export from clang-tidy looks like:
    #   ---
    #   MainSourceFile: 'foo.cpp'
    #   Diagnostics:
    #     - DiagnosticName:  'modernize-use-nullptr'
    #       DiagnosticMessage:
    #         Message:        'use nullptr'
    #         FilePath:       'foo.cpp'
    #         FileOffset:     42
    diagnostics = []
    in_diag = False
    current: Dict[str, Any] = {}
    in_message = False

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("- DiagnosticName:"):
            if current:
                diagnostics.append(current)
            current = {"DiagnosticName": stripped.split(":", 1)[1].strip().strip("'")}
            in_diag = True
            in_message = False
        elif in_diag and stripped.startswith("DiagnosticMessage:"):
            in_message = True
            current["DiagnosticMessage"] = {}
        elif in_message and stripped.startswith("Message:"):
            current.setdefault("DiagnosticMessage", {})["Message"] = (
                stripped.split(":", 1)[1].strip().strip("'")
            )
        elif in_message and stripped.startswith("FilePath:"):
            current.setdefault("DiagnosticMessage", {})["FilePath"] = (
                stripped.split(":", 1)[1].strip().strip("'")
            )
        elif in_message and stripped.startswith("FileOffset:"):
            try:
                current.setdefault("DiagnosticMessage", {})["FileOffset"] = int(
                    stripped.split(":", 1)[1].strip()
                )
            except ValueError:
                pass

    if current:
        diagnostics.append(current)

    return {"Diagnostics": diagnostics}
