#!/usr/bin/env python3
"""Kotlin test report parser (JUnit, Kotest, JaCoCo coverage).

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
"""

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    IGNORED = "ignored"


class TestFramework(Enum):
    JUNIT = "junit"
    JUNIT5 = "junit5"
    KOTEST = "kotest"
    SPEK = "spek"
    MOCKK = "mockk"
    UNKNOWN = "unknown"


@dataclass
class TestCase:
    name: str
    class_name: Optional[str] = None
    status: str = TestStatus.PASSED.value
    duration_ms: float = 0.0
    failure_message: Optional[str] = None
    failure_type: Optional[str] = None
    framework: str = TestFramework.UNKNOWN.value
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    name: str
    test_count: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_ms: float = 0.0
    tests: List[TestCase] = field(default_factory=list)
    framework: str = TestFramework.UNKNOWN.value


@dataclass
class CoverageMetrics:
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    method_coverage: float = 0.0
    class_coverage: float = 0.0
    instruction_coverage: float = 0.0
    covered_lines: int = 0
    missed_lines: int = 0
    total_lines: int = 0


class KotlinTestParser:
    """Parser for Kotlin test results (JUnit XML, Kotest JSON, JaCoCo XML)."""

    def __init__(self) -> None:
        self.suites: List[TestSuite] = []
        self.coverage: Optional[CoverageMetrics] = None

    # ── JUnit XML ────────────────────────────────────────────────────────────
    def parse_junit_report(self, xml_source: Union[str, Path]) -> List[TestSuite]:
        """Parse JUnit XML — accepts file path OR raw XML string."""
        if isinstance(xml_source, Path) or (
            isinstance(xml_source, str) and not xml_source.strip().startswith("<")
        ):
            try:
                text = Path(xml_source).read_text(encoding="utf-8")
            except OSError:
                return []
        else:
            text = xml_source
        try:
            root = ET.fromstring(text)
        except ET.ParseError:
            return []
        suites: List[TestSuite] = []
        # Handle both <testsuites> wrapper and bare <testsuite>
        suite_elements = (
            root.findall("testsuite") if root.tag == "testsuites" else [root]
        )
        for suite_el in suite_elements:
            suite = TestSuite(
                name=suite_el.get("name", ""),
                test_count=int(suite_el.get("tests", 0)),
                failed=int(suite_el.get("failures", 0))
                + int(suite_el.get("errors", 0)),
                skipped=int(suite_el.get("skipped", 0)),
                duration_ms=float(suite_el.get("time", 0)) * 1000,
                framework=TestFramework.JUNIT.value,
            )
            for tc_el in suite_el.findall("testcase"):
                tc = TestCase(
                    name=tc_el.get("name", ""),
                    class_name=tc_el.get("classname"),
                    duration_ms=float(tc_el.get("time", 0)) * 1000,
                    framework=TestFramework.JUNIT.value,
                )
                failure = tc_el.find("failure")
                error = tc_el.find("error")
                skipped = tc_el.find("skipped")
                if failure is not None:
                    tc.status = TestStatus.FAILED.value
                    tc.failure_message = failure.get("message", failure.text or "")
                    tc.failure_type = failure.get("type")
                elif error is not None:
                    tc.status = TestStatus.ERROR.value
                    tc.failure_message = error.get("message", error.text or "")
                elif skipped is not None:
                    tc.status = TestStatus.SKIPPED.value
                else:
                    tc.status = TestStatus.PASSED.value
                suite.tests.append(tc)
            suite.passed = sum(
                1 for t in suite.tests if t.status == TestStatus.PASSED.value
            )
            suites.append(suite)
        self.suites = suites
        return suites

    # ── Kotest JSON ─────────────────────────────────────────────────────────
    def parse_kotest_results(self, report_data: Dict[str, Any]) -> List[TestSuite]:
        suites: List[TestSuite] = []
        for spec in report_data.get("specs", report_data.get("testSuites", [])):
            suite = TestSuite(
                name=spec.get("name", ""), framework=TestFramework.KOTEST.value
            )
            for tc in spec.get("tests", spec.get("testCases", [])):
                status_raw = tc.get("status", "passed").lower()
                status = (
                    status_raw
                    if status_raw in {e.value for e in TestStatus}
                    else (
                        TestStatus.UNKNOWN.value
                        if hasattr(TestStatus, "UNKNOWN")
                        else TestStatus.PASSED.value
                    )
                )
                suite.tests.append(
                    TestCase(
                        name=tc.get("name", ""),
                        status=status,
                        duration_ms=float(tc.get("duration", tc.get("durationMs", 0))),
                        failure_message=tc.get("error", tc.get("failureMessage")),
                        framework=TestFramework.KOTEST.value,
                    )
                )
            suite.test_count = len(suite.tests)
            suite.passed = sum(
                1 for t in suite.tests if t.status == TestStatus.PASSED.value
            )
            suite.failed = sum(
                1
                for t in suite.tests
                if t.status in {TestStatus.FAILED.value, TestStatus.ERROR.value}
            )
            suite.skipped = sum(
                1 for t in suite.tests if t.status == TestStatus.SKIPPED.value
            )
            suites.append(suite)
        self.suites = (self.suites or []) + suites
        return suites

    # ── JaCoCo Coverage XML ──────────────────────────────────────────────────
    def parse_coverage_report(self, coverage_file: Union[str, Path]) -> CoverageMetrics:
        """Parse JaCoCo XML coverage report."""
        try:
            root = ET.parse(str(coverage_file)).getroot()
        except (ET.ParseError, OSError):
            return CoverageMetrics()

        def _ratio(el: Optional[Any], kind: str) -> float:
            if el is None:
                return 0.0
            for ctr in el.findall("counter"):
                if ctr.get("type") == kind:
                    covered = int(ctr.get("covered", 0))
                    missed = int(ctr.get("missed", 0))
                    total = covered + missed
                    return (covered / total * 100) if total else 0.0
            return 0.0

        report = root if root.tag == "report" else root.find("report") or root
        line_ctr = next(
            (c for c in report.iter("counter") if c.get("type") == "LINE"), None
        )
        covered_lines = int(line_ctr.get("covered", 0)) if line_ctr is not None else 0
        missed_lines = int(line_ctr.get("missed", 0)) if line_ctr is not None else 0
        metrics = CoverageMetrics(
            line_coverage=_ratio(report, "LINE"),
            branch_coverage=_ratio(report, "BRANCH"),
            method_coverage=_ratio(report, "METHOD"),
            class_coverage=_ratio(report, "CLASS"),
            instruction_coverage=_ratio(report, "INSTRUCTION"),
            covered_lines=covered_lines,
            missed_lines=missed_lines,
            total_lines=covered_lines + missed_lines,
        )
        self.coverage = metrics
        return metrics

    # ── Analytics ────────────────────────────────────────────────────────────
    def analyze_test_quality(self) -> Dict[str, Any]:
        all_tests = [t for s in self.suites for t in s.tests]
        total = len(all_tests)
        if not total:
            return {"total": 0}
        passed = sum(1 for t in all_tests if t.status == TestStatus.PASSED.value)
        return {
            "total": total,
            "passed": passed,
            "failed": sum(1 for t in all_tests if t.status == TestStatus.FAILED.value),
            "skipped": sum(
                1 for t in all_tests if t.status == TestStatus.SKIPPED.value
            ),
            "pass_rate": round(passed / total * 100, 2),
            "avg_duration_ms": round(sum(t.duration_ms for t in all_tests) / total, 2),
        }

    def detect_flaky_tests(
        self, historical_data: List[Dict[str, Any]]
    ) -> List[TestCase]:
        """Return tests with high failure rate from historical run data."""
        FLAKY_THRESHOLD = 0.3
        counts: Dict[str, Dict[str, int]] = {}
        for run in historical_data:
            for t in run.get("tests", []):
                key = f"{t.get('class', '')}.{t.get('name', '')}"
                entry = counts.setdefault(key, {"total": 0, "failed": 0})
                entry["total"] += 1
                if t.get("status", "passed") != "passed":
                    entry["failed"] += 1
        flaky: List[TestCase] = []
        for key, stats in counts.items():
            if stats["total"] and stats["failed"] / stats["total"] >= FLAKY_THRESHOLD:
                parts = key.rsplit(".", 1)
                flaky.append(
                    TestCase(
                        name=parts[-1],
                        class_name=parts[0] if len(parts) > 1 else None,
                        status=TestStatus.FAILED.value,
                        metadata={
                            "fail_rate": round(stats["failed"] / stats["total"], 2),
                            "total_runs": stats["total"],
                        },
                    )
                )
        return flaky

    def generate_test_report(
        self,
        suites: Optional[List[TestSuite]] = None,
        format: str = "json",
    ) -> str:
        vs = suites if suites is not None else self.suites
        quality = self.analyze_test_quality()
        if format == "json":
            return json.dumps(
                {
                    "tool": "kotlin-test",
                    "quality": quality,
                    "coverage": (
                        {
                            "line": (
                                self.coverage.line_coverage if self.coverage else None
                            ),
                            "branch": (
                                self.coverage.branch_coverage if self.coverage else None
                            ),
                        }
                        if self.coverage
                        else {}
                    ),
                    "suites": [
                        {
                            "name": s.name,
                            "tests": s.test_count,
                            "passed": s.passed,
                            "failed": s.failed,
                        }
                        for s in vs
                    ],
                },
                indent=2,
            )
        lines = [
            f"Kotlin Tests: {quality.get('total', 0)} tests, "
            f"pass rate {quality.get('pass_rate', 0):.1f}%"
        ]
        for s in vs:
            lines.append(f"  {s.name}: {s.passed}/{s.test_count} passed")
        return "\n".join(lines)
