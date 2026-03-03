#!/usr/bin/env python3
"""gofmt Go Parser - Go code formatting verification.

[20260303_FEATURE] Phase 2: full implementation.

Reference: https://pkg.go.dev/cmd/gofmt
Commands:
  gofmt -l .  -> list unformatted files (one per line)
  gofmt -d .  -> show unified diff for unformatted files
  gofmt -w .  -> rewrite files in place
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class FormattingIssue:
    """A file that is not correctly formatted."""

    file_path: str
    diff: str = ""


class GofmtParser:
    """Parser for gofmt formatting output.

    [20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
    Falls back to ``[]`` gracefully when ``gofmt`` is not on PATH.
    """

    def __init__(self) -> None:
        """Initialize GofmtParser."""
        self.language = "go"

    def execute_gofmt(
        self,
        paths: Union[List[Path], Path, str, None] = None,
        include_diff: bool = True,
    ) -> List[FormattingIssue]:
        """Run ``gofmt -l`` on paths and return formatting issues.

        Returns ``[]`` gracefully when ``gofmt`` is not on PATH.
        """
        if not shutil.which("gofmt"):
            return []
        if isinstance(paths, list):
            results: List[FormattingIssue] = []
            for p in paths:
                results.extend(self.execute_gofmt(p, include_diff=include_diff))
            return results
        target = "." if paths is None else str(paths)
        try:
            list_result = subprocess.run(
                ["gofmt", "-l", target],
                capture_output=True, text=True, timeout=300,
            )
            issues: List[FormattingIssue] = []
            for fp in self.parse_file_list(list_result.stdout):
                diff = self.get_diff(fp) if include_diff else ""
                issues.append(FormattingIssue(file_path=fp, diff=diff))
            return issues
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def check_formatting(self, path: str) -> List[FormattingIssue]:
        """Check if a Go file or directory is properly formatted (alias)."""
        return self.execute_gofmt(paths=path, include_diff=True)

    def parse_file_list(self, output: str) -> List[str]:
        """Parse ``gofmt -l`` output to a list of file paths.

        [20260303_FEATURE] Returns paths of files that need reformatting.
        """
        return [line.strip() for line in output.splitlines() if line.strip()]

    def get_diff(self, file_path: Union[str, Path]) -> str:
        """Return the unified diff for a single file via ``gofmt -d``."""
        if not shutil.which("gofmt"):
            return ""
        try:
            result = subprocess.run(
                ["gofmt", "-d", str(file_path)],
                capture_output=True, text=True, timeout=60,
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""

    def check_files(
        self,
        paths: List[Union[str, Path]],
        include_diff: bool = True,
    ) -> List[FormattingIssue]:
        """Check a list of specific file paths for formatting issues."""
        if not shutil.which("gofmt"):
            return []
        issues: List[FormattingIssue] = []
        for p in paths:
            result = subprocess.run(
                ["gofmt", "-l", str(p)],
                capture_output=True, text=True, timeout=300,
            )
            for fp in self.parse_file_list(result.stdout):
                diff = self.get_diff(fp) if include_diff else ""
                issues.append(FormattingIssue(file_path=fp, diff=diff))
        return issues

    def generate_report(self, issues: List[FormattingIssue], format: str = "json") -> str:
        """Return a JSON or text report of formatting issues."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "gofmt",
                    "total_unformatted": len(issues),
                    "files": [{"file": i.file_path, "has_diff": bool(i.diff)} for i in issues],
                },
                indent=2,
            )
        return "\n".join(i.file_path for i in issues)
