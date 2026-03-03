#!/usr/bin/env python3
"""
Roslyn Analyzers C# Parser - .NET Compiler Platform analysis integration.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.

Reference: https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
Command: dotnet build /p:RunAnalyzersDuringBuild=true (emits SARIF to ./analyzer-results/)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from . import SarifFinding, _parse_sarif


@dataclass
class RoslynDiagnostic:
    """A single Roslyn analyzer diagnostic.

    [20260303_FEATURE] Wraps SarifFinding with Roslyn-specific metadata.
    """

    rule_id: str
    level: str  # "error", "warning", "suggestion", "hidden"
    message: str
    file_path: str
    line: int
    column: int
    category: str = ""
    help_url: str = ""


# Known Roslyn category prefixes
_CATEGORY_PREFIXES: Dict[str, str] = {
    "CA": "code_analysis",
    "CS": "compiler",
    "IDE": "ide_style",
    "SA": "stylecop",
    "SCS": "security",
}


class RoslynAnalyzersParser:
    """Parser for .NET Roslyn Analyzers output via SARIF.

    [20260303_FEATURE] Phase 2 full implementation.

    Consumes SARIF 2.1 files produced by ``dotnet build`` (with analyzers
    enabled) or by ``dotnet format --verify-no-changes``.  Falls back to
    empty list when ``dotnet`` is not installed.
    """

    def execute_roslyn(
        self,
        paths: Union[List[Path], Path],
        output_dir: Optional[Path] = None,
    ) -> List[RoslynDiagnostic]:
        """Run ``dotnet build`` with analyzers and return diagnostics.

        Returns ``[]`` gracefully when ``dotnet`` is not on PATH.
        """
        if not shutil.which("dotnet"):
            return []

        target = paths if isinstance(paths, Path) else (paths[0] if paths else Path("."))
        out_dir = output_dir or Path("/tmp/roslyn_out")
        out_dir.mkdir(parents=True, exist_ok=True)
        sarif_path = out_dir / "roslyn.sarif"

        try:
            subprocess.run(
                [
                    "dotnet",
                    "build",
                    str(target),
                    "/p:RunAnalyzersDuringBuild=true",
                    f"/p:ErrorLog={sarif_path}",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        if sarif_path.exists():
            return self.parse_sarif_output(sarif_path)
        return []

    def parse_sarif_output(
        self,
        sarif_source: Union[str, Path, dict],
    ) -> List[RoslynDiagnostic]:
        """Parse SARIF 2.1 output and return Roslyn diagnostics.

        Args:
            sarif_source: Path, JSON string, or pre-parsed dict.
        """
        findings = _parse_sarif(sarif_source)
        return [_sarif_to_roslyn(f) for f in findings]

    def categorize_by_rule(
        self, diags: List[RoslynDiagnostic]
    ) -> Dict[str, List[RoslynDiagnostic]]:
        """Group diagnostics by rule category prefix (CA, CS, IDE, …).

        [20260303_FEATURE] Supports CA, CS, IDE, SA, SCS prefixes.
        """
        result: Dict[str, List[RoslynDiagnostic]] = {}
        for d in diags:
            cat = d.category or "other"
            result.setdefault(cat, []).append(d)
        return result

    def generate_report(
        self,
        diags: List[RoslynDiagnostic],
        format: str = "json",
    ) -> str:
        """Return a JSON or plain text report of diagnostics."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "roslyn",
                    "total": len(diags),
                    "issues": [
                        {
                            "rule_id": d.rule_id,
                            "level": d.level,
                            "message": d.message,
                            "file": d.file_path,
                            "line": d.line,
                            "column": d.column,
                            "category": d.category,
                        }
                        for d in diags
                    ],
                },
                indent=2,
            )
        # Plain text
        lines = []
        for d in diags:
            lines.append(f"{d.file_path}:{d.line}:{d.column}: {d.level}: {d.message} [{d.rule_id}]")
        return "\n".join(lines)


def _sarif_to_roslyn(f: SarifFinding) -> RoslynDiagnostic:
    """Convert a SarifFinding to a RoslynDiagnostic."""
    # Detect category from rule_id prefix
    category = "other"
    for prefix, cat in _CATEGORY_PREFIXES.items():
        if f.rule_id.startswith(prefix):
            category = cat
            break
    return RoslynDiagnostic(
        rule_id=f.rule_id,
        level=f.level,
        message=f.message,
        file_path=f.uri,
        line=f.line,
        column=f.column,
        category=category,
    )

