#!/usr/bin/env python3
"""Jetpack Compose linter / compiler analysis parser.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
"""

import json
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ComposeIssueType(Enum):
    STABILITY = "stability"
    RECOMPOSITION = "recomposition"
    SIDE_EFFECT = "side-effect"
    PREVIEW = "preview"
    INTEROP = "interop"
    PERFORMANCE = "performance"
    MISSING_CONTENT_DESCRIPTION = "missing-content-description"
    OTHER = "other"


class ComposeSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"
    HINT = "hint"


@dataclass
class ComposeIssue:
    issue_type: str
    severity: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ComposeMetrics:
    total_composables: int = 0
    restartable_composables: int = 0
    skippable_composables: int = 0
    stable_classes: int = 0
    unstable_classes: int = 0
    recomposition_count: int = 0
    skipped_count: int = 0
    avg_recompositions: float = 0.0


class ComposeLinterParser:
    """Parser for Jetpack Compose compiler output and lint reports."""

    def __init__(self) -> None:
        self.issues: List[ComposeIssue] = []
        self.metrics: Optional[ComposeMetrics] = None

    def parse_compiler_output(self, output: str) -> List[ComposeIssue]:
        """Parse Compose compiler output or Android Lint SARIF / plain text."""
        if not output or not output.strip():
            return []
        issues: List[ComposeIssue] = []
        # Try SARIF JSON
        try:
            sarif = json.loads(output)
            for run in sarif.get("runs", []):
                for result in run.get("results", []):
                    loc = result.get("locations", [{}])[0]
                    physical = loc.get("physicalLocation", {})
                    region = physical.get("region", {})
                    file_path = physical.get("artifactLocation", {}).get("uri", "")
                    sev_map = {
                        "error": ComposeSeverity.ERROR.value,
                        "warning": ComposeSeverity.WARNING.value,
                        "note": ComposeSeverity.INFORMATION.value,
                    }
                    level = result.get("level", "warning")
                    issues.append(
                        ComposeIssue(
                            issue_type=ComposeIssueType.OTHER.value,
                            severity=sev_map.get(level, level),
                            message=result.get("message", {}).get("text", ""),
                            file_path=file_path,
                            line_number=region.get("startLine"),
                            column=region.get("startColumn"),
                            rule_id=result.get("ruleId"),
                        )
                    )
            self.issues = issues
            return issues
        except (json.JSONDecodeError, KeyError):
            pass
        # Plain-text fallback: "file.kt:12: error: …"
        import re

        pattern = re.compile(r"^(.+):(\d+):\s+(error|warning|info):\s+(.+)$")
        for line in output.splitlines():
            m = pattern.match(line.strip())
            if m:
                issues.append(
                    ComposeIssue(
                        issue_type=ComposeIssueType.OTHER.value,
                        severity=m.group(3),
                        message=m.group(4),
                        file_path=m.group(1),
                        line_number=int(m.group(2)),
                    )
                )
        self.issues = issues
        return issues

    def parse_stability_analysis(
        self, report_data: Dict[str, Any]
    ) -> List[ComposeIssue]:
        """Parse Compose stability analysis report dict."""
        issues: List[ComposeIssue] = []
        for cls in report_data.get("unstableClasses", []):
            issues.append(
                ComposeIssue(
                    issue_type=ComposeIssueType.STABILITY.value,
                    severity=ComposeSeverity.WARNING.value,
                    message=f"Unstable class: {cls.get('name', cls)} — {cls.get('reason', '')}",
                    file_path=cls.get("file"),
                    line_number=cls.get("line"),
                )
            )
        return issues

    def analyze_recompositions(self, trace_data: Dict[str, Any]) -> ComposeMetrics:
        """Analyse recomposition trace data."""
        composables = trace_data.get("composables", [])
        total = len(composables)
        restartable = sum(1 for c in composables if c.get("restartable", False))
        skippable = sum(1 for c in composables if c.get("skippable", False))
        recomp_counts = [c.get("recompositions", 0) for c in composables]
        skips = [c.get("skips", 0) for c in composables]
        metrics = ComposeMetrics(
            total_composables=total,
            restartable_composables=restartable,
            skippable_composables=skippable,
            stable_classes=trace_data.get("stableClasses", 0),
            unstable_classes=trace_data.get("unstableClasses", 0),
            recomposition_count=sum(recomp_counts),
            skipped_count=sum(skips),
            avg_recompositions=sum(recomp_counts) / total if total else 0.0,
        )
        self.metrics = metrics
        return metrics

    def generate_performance_report(
        self,
        issues: Optional[List[ComposeIssue]] = None,
        metrics: Optional[ComposeMetrics] = None,
        format: str = "json",
    ) -> str:
        vs = issues if issues is not None else self.issues
        m = metrics if metrics is not None else self.metrics
        metrics_dict = {}
        if m:
            metrics_dict = {
                "total_composables": m.total_composables,
                "restartable": m.restartable_composables,
                "skippable": m.skippable_composables,
                "stable_classes": m.stable_classes,
                "unstable_classes": m.unstable_classes,
                "avg_recompositions": m.avg_recompositions,
            }
        if format == "json":
            return json.dumps(
                {
                    "tool": "compose-compiler",
                    "total_issues": len(vs),
                    "issues": [
                        {
                            "type": i.issue_type,
                            "severity": i.severity,
                            "message": i.message,
                            "file": i.file_path,
                            "line": i.line_number,
                        }
                        for i in vs
                    ],
                    "metrics": metrics_dict,
                },
                indent=2,
            )
        lines = [f"Compose Analysis: {len(vs)} issue(s)"]
        for i in vs:
            lines.append(
                f"  [{i.severity}] {i.file_path}:{i.line_number} — {i.message}"
            )
        if metrics_dict:
            lines.append(f"  Metrics: {metrics_dict}")
        return "\n".join(lines)

    def execute_compiler_analysis(self, project_path: Path) -> Dict[str, Any]:
        """Run ./gradlew lint; return issues list."""
        gradlew = Path(project_path) / "gradlew"
        if not gradlew.exists() and not shutil.which("gradle"):
            return {"issues": [], "error": "gradle not found"}
        cmd = [str(gradlew), "lint"] if gradlew.exists() else ["gradle", "lint"]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180, cwd=str(project_path)
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return {"issues": [], "error": str(exc)}
        issues = self.parse_compiler_output(result.stdout + result.stderr)
        return {"issues": issues, "error": None}
