#!/usr/bin/env python3
"""golint Go Parser - Go style linter (deprecated, use staticcheck).

[20260303_FEATURE] Phase 2: full implementation.

Reference: https://github.com/golang/lint (archived/deprecated)
Command: golint ./...
Output: main.go:12:1: exported function Hello should have comment or be unexported

DEPRECATION NOTICE: golint is archived and no longer maintained.
Prefer staticcheck (SA and ST checks) for new projects.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

_LINT_LINE_RE = re.compile(
    r"^(?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+): (?P<msg>.+)$"
)

_RULE_KEYWORDS: dict = {
    "comment": "comment",
    "exported": "exported",
    "package": "package",
    "error": "error_type",
    "receiver": "receiver",
    "underscore": "naming",
    "name": "naming",
    "should": "style",
}


@dataclass
class LintSuggestion:
    """A single golint style suggestion."""

    file_path: str
    line: int
    column: int
    message: str
    rule_hint: str = "style"


def _infer_rule(message: str) -> str:
    lower = message.lower()
    for keyword, rule in _RULE_KEYWORDS.items():
        if keyword in lower:
            return rule
    return "style"


class GolintParser:
    """Parser for golint output (deprecated linter).

    [20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.

    .. deprecated::
        golint is archived. Use staticcheck or revive for new projects.

    Falls back to ``[]`` gracefully when ``golint`` is not on PATH.
    """

    DEPRECATION_WARNING = (
        "golint is archived and no longer maintained. "
        "Consider using staticcheck or revive instead."
    )

    def __init__(self) -> None:
        """Initialize GolintParser."""
        self.language = "go"

    def execute_golint(
        self,
        paths: Union[List[Path], Path, str, None] = None,
    ) -> List[LintSuggestion]:
        """Run ``golint ./...`` and return suggestions.

        Returns ``[]`` gracefully when ``golint`` is not on PATH.
        """
        if not shutil.which("golint"):
            return []
        target = "./..."
        if paths is not None:
            if isinstance(paths, list):
                target = " ".join(str(p) for p in paths)
            else:
                target = str(paths)
        cmd = ["golint", target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return self.parse_lint_output(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def parse_lint_output(self, output: str) -> List[LintSuggestion]:
        """Parse golint text output.

        [20260303_FEATURE] Parses ``file:line:col: message`` format.

        Args:
            output: Text from golint stdout.
        """
        suggestions: List[LintSuggestion] = []
        if not output:
            return suggestions
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            m = _LINT_LINE_RE.match(line)
            if not m:
                continue
            msg = m.group("msg")
            suggestions.append(
                LintSuggestion(
                    file_path=m.group("file"),
                    line=int(m.group("line")),
                    column=int(m.group("col")),
                    message=msg,
                    rule_hint=_infer_rule(msg),
                )
            )
        return suggestions

    def parse_output(self, output: str) -> List[LintSuggestion]:
        """Parse golint output (alias for parse_lint_output)."""
        return self.parse_lint_output(output)

    def categorize_by_rule(
        self, suggestions: List[LintSuggestion]
    ) -> Dict[str, List[LintSuggestion]]:
        """Group suggestions by inferred rule category."""
        result: Dict[str, List[LintSuggestion]] = {}
        for s in suggestions:
            result.setdefault(s.rule_hint, []).append(s)
        return result

    def generate_report(
        self, suggestions: List[LintSuggestion], format: str = "json"
    ) -> str:
        """Return a JSON or text report of golint suggestions."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "golint",
                    "deprecated": True,
                    "deprecation_notice": self.DEPRECATION_WARNING,
                    "total": len(suggestions),
                    "by_rule": {
                        k: len(v)
                        for k, v in self.categorize_by_rule(suggestions).items()
                    },
                    "suggestions": [
                        {
                            "file": s.file_path,
                            "line": s.line,
                            "column": s.column,
                            "rule": s.rule_hint,
                            "message": s.message,
                        }
                        for s in suggestions
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{s.file_path}:{s.line}:{s.column}: {s.message}"
            for s in suggestions
        )
