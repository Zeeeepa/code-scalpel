#!/usr/bin/env python3
"""
Pitest Java Parser - Mutation testing analysis tool.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: http://pitest.org/
Command: mvn org.pitest:pitest-maven:mutationCoverage
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MutationResult:
    """Result from a single PIT mutation test."""

    mutation_id: str
    status: str          # KILLED, SURVIVED, TIMED_OUT, NO_COVERAGE
    operator: str        # mutator class name (short form)
    source_file: str
    mutated_class: str
    mutated_method: str
    line_number: int
    detected: bool


def _short_mutator(full_name: str) -> str:
    """Extract the short mutator name from a fully-qualified class name."""
    if "." in full_name:
        return full_name.rsplit(".", 1)[-1]
    return full_name


class PitestParser:
    """Parser for Pitest mutation testing XML reports.

    [20260303_FEATURE] Implements parse_xml_report, get_mutation_score,
    get_survived_mutations, categorize_by_mutator, generate_report.
    """

    def __init__(self, report_path: Optional[Path] = None) -> None:
        """Initialize Pitest parser."""
        self.report_path = Path(report_path) if report_path else None

    def parse_xml_report(self, path: Optional[Path] = None) -> List[MutationResult]:
        """Parse a Pitest ``mutations.xml`` report.

        [20260303_FEATURE] Handles both ``<mutations>`` root and
        ``<mutation detected='true' status='KILLED'>`` children.
        """
        target = Path(path) if path else self.report_path
        if target is None:
            return []
        try:
            tree = ET.parse(str(target))
        except (ET.ParseError, OSError):
            return []
        root = tree.getroot()
        results: List[MutationResult] = []
        for mut in root.findall(".//mutation"):
            detected = mut.get("detected", "false").lower() == "true"
            status = mut.get("status", "UNKNOWN").upper()
            source_file = (mut.findtext("sourceFile") or "").strip()
            mutated_class = (mut.findtext("mutatedClass") or "").strip()
            mutated_method = (mut.findtext("mutatedMethod") or "").strip()
            try:
                line_number = int(mut.findtext("lineNumber") or 0)
            except ValueError:
                line_number = 0
            mutator = _short_mutator((mut.findtext("mutator") or "").strip())
            mutation_id = f"{mutated_class}:{mutated_method}:{line_number}:{mutator}"
            results.append(MutationResult(
                mutation_id=mutation_id,
                status=status,
                operator=mutator,
                source_file=source_file,
                mutated_class=mutated_class,
                mutated_method=mutated_method,
                line_number=line_number,
                detected=detected,
            ))
        return results

    def parse_xml_string(self, xml_content: str) -> List[MutationResult]:
        """Parse Pitest XML from a string (for testing without file I/O)."""
        if not xml_content or not xml_content.strip():
            return []
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return []
        results: List[MutationResult] = []
        for mut in root.findall(".//mutation") if root.tag != "mutation" else [root]:
            detected = mut.get("detected", "false").lower() == "true"
            status = mut.get("status", "UNKNOWN").upper()
            source_file = (mut.findtext("sourceFile") or "").strip()
            mutated_class = (mut.findtext("mutatedClass") or "").strip()
            mutated_method = (mut.findtext("mutatedMethod") or "").strip()
            try:
                line_number = int(mut.findtext("lineNumber") or 0)
            except ValueError:
                line_number = 0
            mutator = _short_mutator((mut.findtext("mutator") or "").strip())
            mutation_id = f"{mutated_class}:{mutated_method}:{line_number}:{mutator}"
            results.append(MutationResult(
                mutation_id=mutation_id,
                status=status,
                operator=mutator,
                source_file=source_file,
                mutated_class=mutated_class,
                mutated_method=mutated_method,
                line_number=line_number,
                detected=detected,
            ))
        return results

    def get_mutation_score(self, results: List[MutationResult]) -> float:
        """Calculate mutation score = killed / total (excluding NO_COVERAGE)."""
        eligible = [r for r in results if r.status != "NO_COVERAGE"]
        if not eligible:
            return 0.0
        killed = sum(1 for r in eligible if r.detected)
        return round(killed / len(eligible) * 100, 2)

    def get_survived_mutations(self, results: List[MutationResult]) -> List[MutationResult]:
        """Return only mutations that survived (were NOT killed)."""
        return [r for r in results if not r.detected and r.status != "NO_COVERAGE"]

    def categorize_by_mutator(
        self, results: List[MutationResult]
    ) -> Dict[str, List[MutationResult]]:
        """Group mutation results by operator/mutator name."""
        out: Dict[str, List[MutationResult]] = {}
        for r in results:
            out.setdefault(r.operator, []).append(r)
        return out

    def generate_report(
        self, results: List[MutationResult], format: str = "json"
    ) -> str:
        """Return a JSON or text report of mutation test results."""
        score = self.get_mutation_score(results)
        survived = self.get_survived_mutations(results)
        by_mutator = self.categorize_by_mutator(results)
        if format == "json":
            return json.dumps(
                {
                    "tool": "pitest",
                    "total": len(results),
                    "mutation_score": score,
                    "killed": sum(1 for r in results if r.detected),
                    "survived": len(survived),
                    "by_mutator": {k: len(v) for k, v in by_mutator.items()},
                    "survived_mutations": [
                        {
                            "class": r.mutated_class,
                            "method": r.mutated_method,
                            "line": r.line_number,
                            "operator": r.operator,
                        }
                        for r in survived
                    ],
                },
                indent=2,
            )
        return (
            f"Pitest: {len(results)} mutations | Score: {score}% | "
            f"Survived: {len(survived)}"
        )

    def parse(self) -> Dict:
        """Backward-compat: parse the report set in constructor."""
        results = self.parse_xml_report(self.report_path)
        return {
            "total": len(results),
            "mutation_score": self.get_mutation_score(results),
            "survived": len(self.get_survived_mutations(results)),
        }
