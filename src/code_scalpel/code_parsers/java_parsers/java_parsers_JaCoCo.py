#!/usr/bin/env python3
"""
JaCoCo Java Parser - Code coverage analysis tool.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: https://www.jacoco.org/
Command: java -javaagent:jacocoagent.jar=destfile=coverage.exec App
         mvn jacoco:report
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CoverageMetrics:
    """Code coverage metrics from JaCoCo."""

    method_covered: int = 0
    method_missed: int = 0
    line_covered: int = 0
    line_missed: int = 0
    branch_covered: int = 0
    branch_missed: int = 0
    complexity_covered: int = 0
    complexity_missed: int = 0

    @property
    def method_coverage(self) -> float:
        total = self.method_covered + self.method_missed
        return self.method_covered / total * 100 if total else 0.0

    @property
    def line_coverage(self) -> float:
        total = self.line_covered + self.line_missed
        return self.line_covered / total * 100 if total else 0.0

    @property
    def branch_coverage(self) -> float:
        total = self.branch_covered + self.branch_missed
        return self.branch_covered / total * 100 if total else 0.0


@dataclass
class ClassCoverage:
    """Coverage data for a single class."""

    class_name: str
    source_file: str
    metrics: CoverageMetrics = field(default_factory=CoverageMetrics)
    methods: List[Dict[str, Any]] = field(default_factory=list)


def _parse_counters(elem: ET.Element) -> CoverageMetrics:
    """Extract coverage counters from a JaCoCo XML element."""
    m = CoverageMetrics()
    for counter in elem.findall("counter"):
        typ = counter.get("type", "").upper()
        covered = int(counter.get("covered", 0))
        missed = int(counter.get("missed", 0))
        if typ == "METHOD":
            m.method_covered, m.method_missed = covered, missed
        elif typ == "LINE":
            m.line_covered, m.line_missed = covered, missed
        elif typ == "BRANCH":
            m.branch_covered, m.branch_missed = covered, missed
        elif typ == "COMPLEXITY":
            m.complexity_covered, m.complexity_missed = covered, missed
    return m


class JaCoCoParser:
    """Parser for JaCoCo code coverage XML reports.

    [20260303_FEATURE] Implements parse_xml_report, get_class_coverage,
    get_method_coverage, get_line_coverage, calculate_summary, generate_report.
    """

    def __init__(self, report_path: Optional[Path] = None) -> None:
        """Initialize JaCoCo parser."""
        self.report_path = Path(report_path) if report_path else None
        self._classes: List[ClassCoverage] = []

    def parse_xml_report(self, path: Optional[Path] = None) -> List[ClassCoverage]:
        """Parse a JaCoCo XML report file.

        Args:
            path: Path to JaCoCo XML. Falls back to ``self.report_path``.
        """
        target = Path(path) if path else self.report_path
        if target is None:
            return []
        try:
            tree = ET.parse(str(target))
        except (ET.ParseError, OSError):
            return []
        root = tree.getroot()
        classes: List[ClassCoverage] = []
        for pkg in root.findall(".//package"):
            for cls in pkg.findall("class"):
                class_name = cls.get("name", "").replace("/", ".")
                source_file = cls.get("sourcefilename", "")
                metrics = _parse_counters(cls)
                methods: List[Dict[str, Any]] = []
                for method in cls.findall("method"):
                    m_metrics = _parse_counters(method)
                    methods.append({
                        "name": method.get("name", ""),
                        "desc": method.get("desc", ""),
                        "line": int(method.get("line", 0)),
                        "line_coverage": m_metrics.line_coverage,
                    })
                classes.append(ClassCoverage(
                    class_name=class_name,
                    source_file=source_file,
                    metrics=metrics,
                    methods=methods,
                ))
        self._classes = classes
        return classes

    def get_class_coverage(self) -> List[Dict[str, Any]]:
        """Return per-class coverage percentages from last parse."""
        return [
            {
                "class": c.class_name,
                "line_coverage": round(c.metrics.line_coverage, 2),
                "branch_coverage": round(c.metrics.branch_coverage, 2),
                "method_coverage": round(c.metrics.method_coverage, 2),
            }
            for c in self._classes
        ]

    def get_method_coverage(self) -> List[Dict[str, Any]]:
        """Return per-method coverage data from last parse."""
        result: List[Dict[str, Any]] = []
        for cls in self._classes:
            for m in cls.methods:
                result.append({"class": cls.class_name, **m})
        return result

    def get_line_coverage(self) -> Dict[str, float]:
        """Return {class_name: line_coverage_pct} mapping."""
        return {c.class_name: round(c.metrics.line_coverage, 2) for c in self._classes}

    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate aggregate coverage summary across all classes."""
        if not self._classes:
            return {"line_coverage": 0.0, "branch_coverage": 0.0, "method_coverage": 0.0, "classes": 0}
        totals = CoverageMetrics()
        for c in self._classes:
            totals.line_covered += c.metrics.line_covered
            totals.line_missed += c.metrics.line_missed
            totals.branch_covered += c.metrics.branch_covered
            totals.branch_missed += c.metrics.branch_missed
            totals.method_covered += c.metrics.method_covered
            totals.method_missed += c.metrics.method_missed
        return {
            "classes": len(self._classes),
            "line_coverage": round(totals.line_coverage, 2),
            "branch_coverage": round(totals.branch_coverage, 2),
            "method_coverage": round(totals.method_coverage, 2),
        }

    def generate_report(
        self, classes: Optional[List[ClassCoverage]] = None, format: str = "json"
    ) -> str:
        """Return a JSON or text coverage report."""
        if classes is not None:
            self._classes = classes
        summary = self.calculate_summary()
        if format == "json":
            return json.dumps(
                {
                    "tool": "jacoco",
                    "summary": summary,
                    "classes": self.get_class_coverage(),
                },
                indent=2,
            )
        return (
            f"JaCoCo: {summary['classes']} classes | "
            f"Line: {summary['line_coverage']}% | "
            f"Branch: {summary['branch_coverage']}% | "
            f"Method: {summary['method_coverage']}%"
        )

    def parse(self) -> Dict[str, Any]:
        """Backward-compat: parse the XML report set in constructor."""
        self.parse_xml_report(self.report_path)
        return self.calculate_summary()
