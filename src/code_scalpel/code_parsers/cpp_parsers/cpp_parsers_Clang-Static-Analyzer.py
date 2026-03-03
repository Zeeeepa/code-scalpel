#!/usr/bin/env python3
"""
Clang Static Analyzer Parser - Deep C/C++ Bug Detection.

[20260303_FEATURE] Full implementation: execute scan-build, parse plist/HTML
report output, extract bug paths, and generate normalized reports.

Reference: https://clang-analyzer.llvm.org/
Command:   scan-build -o /tmp/report make
           scan-build -o /tmp/report cmake --build .
"""

import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import base_parser


class BugType(Enum):
    """Clang Static Analyzer bug types."""

    MEMORY_LEAK = "memory_leak"
    USE_AFTER_FREE = "use_after_free"
    NULL_DEREFERENCE = "null_dereference"
    UNINITIALIZED_VALUE = "uninitialized_value"
    BUFFER_OVERFLOW = "buffer_overflow"
    RESOURCE_LEAK = "resource_leak"
    LOGIC_ERROR = "logic_error"
    SECURITY_ISSUE = "security_issue"


@dataclass
class AnalyzerFinding:
    """Represents a Clang Static Analyzer finding."""

    bug_type: BugType
    bug_category: str
    message: str
    file_path: str
    line_number: int
    column: int
    severity: str
    bug_path: Optional[List[Dict[str, Any]]] = None


@dataclass
class AnalyzerConfig:
    """Clang Static Analyzer configuration."""

    analyzer_version: str = "18.0.0"
    config_file: Optional[Path] = None
    checkers_enabled: Optional[List[str]] = None
    checkers_disabled: Optional[List[str]] = None


# --- Internal helpers ------------------------------------------------------- #

# Map scan-build check_name prefixes to BugType
_CHECK_BUG_MAP: List[tuple] = [
    ("core.NullDereference", BugType.NULL_DEREFERENCE),
    ("core.uninitialized", BugType.UNINITIALIZED_VALUE),
    ("cplusplus.NewDeleteLeaks", BugType.MEMORY_LEAK),
    ("cplusplus.Memory", BugType.MEMORY_LEAK),
    ("cplusplus.NewDelete", BugType.USE_AFTER_FREE),
    ("unix.Malloc", BugType.MEMORY_LEAK),
    ("unix.MismatchedDeallocator", BugType.USE_AFTER_FREE),
    ("alpha.security", BugType.SECURITY_ISSUE),
    ("alpha.cplusplus.STLAlgorithmModeling", BugType.LOGIC_ERROR),
    ("security", BugType.SECURITY_ISSUE),
    ("osx.cocoa.Memory", BugType.MEMORY_LEAK),
    ("alpha.unix.cstring", BugType.BUFFER_OVERFLOW),
]


def _check_to_bug_type(check_name: str) -> BugType:
    """Map a clang-sa check name to its BugType."""
    for prefix, bug_type in _CHECK_BUG_MAP:
        if check_name.startswith(prefix):
            return bug_type
    return BugType.LOGIC_ERROR


def _extract_file_list(plist_data: Dict[str, Any]) -> List[str]:
    """Extract the 'files' list from plist data (file indices → paths)."""
    return plist_data.get("files", [])


def _parse_plist_diagnostic(diag: Dict[str, Any], files: List[str]) -> AnalyzerFinding:
    """Convert a single plist diagnostic dict to an AnalyzerFinding."""
    check_name = diag.get("check_name", "")
    bug_type = _check_to_bug_type(check_name)
    description = diag.get("description", diag.get("message", ""))
    category = diag.get("category", check_name)

    # Location
    loc = diag.get("location", {})
    file_idx = loc.get("file", 0)
    file_path = files[file_idx] if file_idx < len(files) else ""
    line = loc.get("line", 0)
    col = loc.get("col", 0)

    # Bug path steps
    raw_path = diag.get("path", [])
    bug_path_steps = []
    for step in raw_path:
        if step.get("kind") not in ("event", "control"):
            continue
        step_loc = step.get("location", {})
        step_file_idx = step_loc.get("file", 0)
        bug_path_steps.append(
            {
                "kind": step.get("kind", "event"),
                "message": step.get("message", step.get("extended_message", "")),
                "file": files[step_file_idx] if step_file_idx < len(files) else "",
                "line": step_loc.get("line", 0),
                "col": step_loc.get("col", 0),
            }
        )

    return AnalyzerFinding(
        bug_type=bug_type,
        bug_category=category,
        message=description,
        file_path=file_path,
        line_number=line,
        column=col,
        severity="warning",
        bug_path=bug_path_steps or None,
    )


def _to_sarif_result(finding: AnalyzerFinding) -> Dict[str, Any]:
    """Convert an AnalyzerFinding to a SARIF 2.1 result dict."""
    return {
        "ruleId": finding.bug_type.value,
        "level": "warning",
        "message": {"text": finding.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.file_path},
                    "region": {
                        "startLine": finding.line_number,
                        "startColumn": finding.column,
                    },
                }
            }
        ],
    }


# ---------------------------------------------------------------------------- #


class ClangStaticAnalyzerParser(base_parser.BaseParser):
    """
    Parser for Clang Static Analyzer deep bug detection.

    [20260303_FEATURE] Detects memory leaks, use-after-free, null dereferences,
    and other bugs using deep symbolic execution via scan-build.

    Supports both direct execution (scan-build) and offline plist parsing.
    """

    def __init__(self, file_path: Optional[str] = None) -> None:
        """Initialize Clang Static Analyzer parser."""
        super().__init__()
        self.file_path = file_path
        self.language = "cpp"
        self.config = AnalyzerConfig()
        self.findings: List[AnalyzerFinding] = []

    # [20260120_BUGFIX] Implemented abstract method to satisfy BaseParser interface
    def parse_code(self, code: str, preprocess: bool = True, config: Any = None) -> None:  # noqa: ARG002
        """Stub implementation to satisfy BaseParser ABC."""
        _ = code, preprocess, config

    def parse(self) -> None:
        """Legacy single-file parse using clang-check AST dump."""
        if not self.file_path:
            return
        if shutil.which("clang-check") is None:
            return
        try:
            clang_output = subprocess.check_output(
                ["clang-check", "-ast-dump=full", self.file_path],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output}")
            return
        self.parse_clang_output(clang_output)

    def parse_clang_output(self, clang_output: str) -> None:
        """Parse legacy clang-check AST dump output."""
        for line in clang_output.split("\n"):
            if line.strip().startswith("###"):
                self.handle_section_header(line.strip())
            elif line.strip().startswith("##"):
                self.handle_entity_header(line.strip())
            elif line.strip():
                self.handle_entity_line(line.strip())

    def handle_section_header(self, line: str) -> None:
        _ = line

    def handle_entity_header(self, line: str) -> None:
        _ = line

    def handle_entity_line(self, line: str) -> None:
        _ = line

    # ------------------------------------------------------------------ #
    # Execution                                                            #
    # ------------------------------------------------------------------ #

    def execute_scan_build(
        self, paths: List[Path], config: Optional[AnalyzerConfig] = None
    ) -> List[AnalyzerFinding]:
        """
        Run scan-build on a project directory.

        scan-build wraps a build command and captures analyzer findings.
        The analyzer output is saved as plist files in a temporary directory.

        Returns empty list if scan-build is not installed.
        """
        if shutil.which("scan-build") is None:
            return []

        cfg = config or self.config
        findings: List[AnalyzerFinding] = []

        with tempfile.TemporaryDirectory() as report_dir:
            cmd = ["scan-build", "-o", report_dir]
            if cfg.checkers_enabled:
                for checker in cfg.checkers_enabled:
                    cmd += ["-enable-checker", checker]
            if cfg.checkers_disabled:
                for checker in cfg.checkers_disabled:
                    cmd += ["-disable-checker", checker]

            # Try common build systems in the first path directory
            build_dir = str(paths[0]) if paths else "."
            if (Path(build_dir) / "Makefile").exists():
                cmd += ["make", "-C", build_dir]
            elif (Path(build_dir) / "CMakeLists.txt").exists():
                cmd += ["cmake", "--build", build_dir]
            else:
                cmd += ["make"]

            subprocess.run(cmd, capture_output=True, cwd=build_dir)

            # Parse all .plist files generated in report_dir
            for plist_file in Path(report_dir).rglob("*.plist"):
                findings.extend(self.parse_plist_report(plist_file))

        return findings

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_plist_report(self, report_path: Path) -> List[AnalyzerFinding]:
        """
        Parse a scan-build .plist output file.

        The plist contains a 'clang_diagnostics' (or 'diagnostics') array
        with one entry per bug found.
        """
        try:
            with open(report_path, "rb") as f:
                data = plistlib.load(f)
        except (OSError, plistlib.InvalidFileException, Exception):
            return []

        files = _extract_file_list(data)
        # scan-build uses 'clang_diagnostics'; some versions use 'diagnostics'
        diagnostics = data.get("clang_diagnostics", data.get("diagnostics", []))

        return [_parse_plist_diagnostic(diag, files) for diag in diagnostics]

    def parse_html_report_dir(self, report_dir: Path) -> List[AnalyzerFinding]:
        """
        Alternative: find and parse all .plist files in a scan-build report dir.

        scan-build produces both HTML and plist files; we parse the plists.
        """
        findings = []
        for plist_file in report_dir.rglob("*.plist"):
            findings.extend(self.parse_plist_report(plist_file))
        return findings

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def extract_bug_paths(
        self, findings: List[AnalyzerFinding]
    ) -> List[Dict[str, Any]]:
        """
        Extract execution path steps from all findings.

        Returns a list of path step dicts with keys:
            kind, message, file, line, col
        """
        all_paths = []
        for finding in findings:
            if finding.bug_path:
                all_paths.extend(finding.bug_path)
        return all_paths

    def filter_memory_bugs(
        self, findings: List[AnalyzerFinding]
    ) -> List[AnalyzerFinding]:
        """Return only memory-related findings."""
        memory_types = {
            BugType.MEMORY_LEAK,
            BugType.USE_AFTER_FREE,
            BugType.RESOURCE_LEAK,
        }
        return [f for f in findings if f.bug_type in memory_types]

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(
        self, findings: List[AnalyzerFinding], format: str = "json"
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
                                "name": "clang-static-analyzer",
                                "version": self.config.analyzer_version,
                            }
                        },
                        "results": [_to_sarif_result(f) for f in findings],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        by_type: Dict[str, int] = {}
        for finding in findings:
            by_type[finding.bug_type.value] = by_type.get(finding.bug_type.value, 0) + 1

        report = {
            "tool": "clang-static-analyzer",
            "findings": [
                {
                    "bug_type": f.bug_type.value,
                    "category": f.bug_category,
                    "message": f.message,
                    "file": f.file_path,
                    "line": f.line_number,
                    "column": f.column,
                    "severity": f.severity,
                    "path_steps": len(f.bug_path) if f.bug_path else 0,
                }
                for f in findings
            ],
            "summary": {
                "total": len(findings),
                "by_bug_type": by_type,
            },
        }
        return json.dumps(report, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_path>")
        sys.exit(1)
    _file_path = sys.argv[1]
    if not os.path.isfile(_file_path):
        print(f"Error: {_file_path} is not a valid file path")
        sys.exit(1)

    parser = ClangStaticAnalyzerParser(_file_path)
    parser.parse()
