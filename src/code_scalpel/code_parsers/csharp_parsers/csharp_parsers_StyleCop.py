#!/usr/bin/env python3
"""
StyleCop C# Parser - C# coding style enforcement.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.

Reference: https://github.com/DotNetAnalyzers/StyleCopAnalyzers
Rules: SA0001-SA1649 — documentation, spacing, ordering, naming conventions.
Output: SARIF 2.1 from MSBuild / dotnet build.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union
from pathlib import Path

from . import SarifFinding, _parse_sarif


class StyleCopCategory(Enum):
    """StyleCop rule categories based on SA1xxx rule ranges."""

    DOCUMENTATION = "documentation"  # SA1600–SA1655
    SPACING = "spacing"  # SA1000–SA1028
    READABILITY = "readability"  # SA1100–SA1124
    ORDERING = "ordering"  # SA1200–SA1217
    NAMING = "naming"  # SA1300–SA1314
    MAINTAINABILITY = "maintainability"  # SA1400–SA1412
    LAYOUT = "layout"  # SA1500–SA1519
    OTHER = "other"


# SA rule number → category
_SA_RANGES = [
    (1000, 1099, StyleCopCategory.SPACING),
    (1100, 1199, StyleCopCategory.READABILITY),
    (1200, 1299, StyleCopCategory.ORDERING),
    (1300, 1399, StyleCopCategory.NAMING),
    (1400, 1499, StyleCopCategory.MAINTAINABILITY),
    (1500, 1599, StyleCopCategory.LAYOUT),
    (1600, 1699, StyleCopCategory.DOCUMENTATION),
]


@dataclass
class StyleCopViolation:
    """A single StyleCop rule violation.

    [20260303_FEATURE] Wraps SarifFinding with StyleCop category metadata.
    """

    rule_id: str
    category: StyleCopCategory
    level: str
    message: str
    file_path: str
    line: int
    column: int


class StyleCopParser:
    """Parser for StyleCop Analyzers output (SARIF 2.1 via MSBuild).

    [20260303_FEATURE] Phase 2 full implementation.
    Falls back to ``[]`` when ``dotnet`` is absent.
    """

    def execute_stylecop(
        self,
        path: Union[str, Path],
        output_sarif: Optional[Path] = None,
    ) -> List[StyleCopViolation]:
        """Run dotnet build with StyleCop and return violations.

        Returns ``[]`` gracefully when ``dotnet`` is not on PATH.
        """
        if not shutil.which("dotnet"):
            return []

        import subprocess

        out = output_sarif or Path("/tmp/stylecop.sarif")
        try:
            subprocess.run(
                ["dotnet", "build", str(path), f"/p:ErrorLog={out}"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        return self.parse_sarif_output(out) if out.exists() else []

    def parse_sarif_output(
        self,
        sarif_source: Union[str, Path, dict],
    ) -> List[StyleCopViolation]:
        """Parse SARIF 2.1 output and return StyleCop violations."""
        findings = _parse_sarif(sarif_source)
        return [_sarif_to_violation(f) for f in findings if f.rule_id.startswith("SA")]

    def categorize_rules(
        self, violations: List[StyleCopViolation]
    ) -> Dict[StyleCopCategory, List[StyleCopViolation]]:
        """Group violations by StyleCop category."""
        result: Dict[StyleCopCategory, List[StyleCopViolation]] = {}
        for v in violations:
            result.setdefault(v.category, []).append(v)
        return result

    def generate_report(
        self, violations: List[StyleCopViolation], format: str = "json"
    ) -> str:
        """Return JSON or text report."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "stylecop",
                    "total": len(violations),
                    "issues": [
                        {
                            "rule_id": v.rule_id,
                            "category": v.category.value,
                            "level": v.level,
                            "message": v.message,
                            "file": v.file_path,
                            "line": v.line,
                        }
                        for v in violations
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{v.file_path}:{v.line}: {v.rule_id} {v.message}" for v in violations
        )


def _sa_category(rule_id: str) -> StyleCopCategory:
    """Determine StyleCop category from rule_id like 'SA1200'."""
    try:
        num = int(rule_id[2:6])
        for lo, hi, cat in _SA_RANGES:
            if lo <= num <= hi:
                return cat
    except (ValueError, IndexError):
        pass
    return StyleCopCategory.OTHER


def _sarif_to_violation(f: SarifFinding) -> StyleCopViolation:
    return StyleCopViolation(
        rule_id=f.rule_id,
        category=_sa_category(f.rule_id),
        level=f.level,
        message=f.message,
        file_path=f.uri,
        line=f.line,
        column=f.column,
    )
