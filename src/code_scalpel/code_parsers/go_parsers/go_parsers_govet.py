#!/usr/bin/env python3
"""go vet Parser - Go static analysis for suspicious constructs.

[20260303_FEATURE] Phase 2: full implementation.

Reference: https://pkg.go.dev/cmd/vet
Command: go vet ./...
Output (stderr): ./file.go:line:col: message
Analyzers: printf, shadow, structtag, unreachable, copylocks, etc.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

# Pattern: ./main.go:42:13: fmt.Sprintf format %d has arg x of wrong type float64
# or:      ./pkg/foo.go:10: exported function Foo should have comment
_VET_LINE_RE = re.compile(
    r"^(?P<file>[^\s:]+):(?P<line>\d+)(?::(?P<col>\d+))?: (?P<msg>.+)$"
)


@dataclass
class VetIssue:
    """A single go vet diagnostic."""

    file_path: str
    line: int
    column: int
    message: str
    analyzer: str = ""


def _infer_analyzer(message: str) -> str:
    """Guess the vet analyzer from the diagnostic message."""
    lower = message.lower()
    if "printf" in lower or "sprintf" in lower or "format" in lower:
        return "printf"
    if "structtag" in lower or "struct tag" in lower:
        return "structtag"
    if "unreachable" in lower:
        return "unreachable"
    if "copy" in lower and "lock" in lower:
        return "copylocks"
    if "shadow" in lower:
        return "shadow"
    if "loop variable" in lower:
        return "loopclosure"
    return "vet"


class GovetParser:
    """Parser for go vet static analysis output.

    [20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
    Falls back to ``[]`` gracefully when ``go`` is not on PATH.
    """

    def __init__(self) -> None:
        """Initialize GovetParser."""
        self.language = "go"

    def execute_govet(
        self,
        paths: Union[List[Path], Path, str, None] = None,
    ) -> List[VetIssue]:
        """Run ``go vet ./...`` and return issues.

        Returns ``[]`` gracefully when ``go`` is not on PATH.
        """
        if not shutil.which("go"):
            return []
        target = "./..."
        if paths is not None:
            if isinstance(paths, list):
                target = " ".join(str(p) for p in paths)
            else:
                target = str(paths)
        cmd = ["go", "vet", target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return self.parse_vet_output(result.stderr or result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def run_vet(self, package_path: str) -> List[VetIssue]:
        """Run go vet on a package path (alias for execute_govet)."""
        return self.execute_govet(paths=package_path)

    def parse_vet_output(self, output: str) -> List[VetIssue]:
        """Parse go vet text output.

        [20260303_FEATURE] Parses ``file:line:col: message`` format.

        Args:
            output: Text from go vet stderr.
        """
        issues: List[VetIssue] = []
        if not output:
            return issues
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            m = _VET_LINE_RE.match(line)
            if not m:
                continue
            issues.append(
                VetIssue(
                    file_path=m.group("file"),
                    line=int(m.group("line")),
                    column=int(m.group("col") or 0),
                    message=m.group("msg"),
                    analyzer=_infer_analyzer(m.group("msg")),
                )
            )
        return issues

    def categorize_by_analyzer(
        self, issues: List[VetIssue]
    ) -> Dict[str, List[VetIssue]]:
        """Group issues by inferred analyzer name."""
        result: Dict[str, List[VetIssue]] = {}
        for issue in issues:
            result.setdefault(issue.analyzer, []).append(issue)
        return result

    def filter_by_analyzer(
        self, issues: List[VetIssue], analyzer: str
    ) -> List[VetIssue]:
        """Filter issues to those matching the given analyzer."""
        return [i for i in issues if i.analyzer == analyzer]

    def generate_report(self, issues: List[VetIssue], format: str = "json") -> str:
        """Return a JSON or text report of go vet findings."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "go vet",
                    "total": len(issues),
                    "by_analyzer": {
                        k: len(v) for k, v in self.categorize_by_analyzer(issues).items()
                    },
                    "issues": [
                        {
                            "file": i.file_path,
                            "line": i.line,
                            "column": i.column,
                            "analyzer": i.analyzer,
                            "message": i.message,
                        }
                        for i in issues
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{i.file_path}:{i.line}:{i.column}: [{i.analyzer}] {i.message}"
            for i in issues
        )
