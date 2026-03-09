#!/usr/bin/env python3
"""
ReSharper C# Parser - JetBrains code analysis integration.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.

Reference: https://www.jetbrains.com/help/resharper/InspectCode.html
Command: inspectcode.exe Solution.sln -o=results.xml  (Enterprise — CLI not free)
Output: XML from InspectCode.

Enterprise tool: execute_resharper() raises NotImplementedError.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union


class IssueCategory(Enum):
    """ReSharper issue categories."""

    CODE_ISSUES = "code_issues"
    POTENTIAL_CODE_QUALITY_ISSUES = "potential_code_quality_issues"
    REDUNDANCIES_IN_CODE = "redundancies_in_code"
    REDUNDANCIES_IN_SYMBOL_DECLARATIONS = "redundancies_in_symbol_declarations"
    SPELLING_ISSUES = "spelling_issues"
    OTHER = "other"


@dataclass
class ReSharperIssue:
    """A single ReSharper InspectCode issue.

    [20260303_FEATURE] Populated by parse_xml_report().
    """

    type_id: str
    category: IssueCategory
    severity: str
    message: str
    file_path: str
    line: int
    offset: Optional[str] = None


@dataclass
class IssueType:
    """Metadata for a ReSharper issue type (from <IssueTypes> header)."""

    type_id: str
    category: str
    description: str
    severity: str = "WARNING"


# ReSharper category string → enum
_CATEGORY_MAP: Dict[str, IssueCategory] = {
    "code issues": IssueCategory.CODE_ISSUES,
    "potential code quality issues": IssueCategory.POTENTIAL_CODE_QUALITY_ISSUES,
    "redundancies in code": IssueCategory.REDUNDANCIES_IN_CODE,
    "redundancies in symbol declarations": IssueCategory.REDUNDANCIES_IN_SYMBOL_DECLARATIONS,
    "spelling issues": IssueCategory.SPELLING_ISSUES,
}


class ReSharperParser:
    """Parser for JetBrains ReSharper InspectCode XML output.

    [20260303_FEATURE] Phase 2 full implementation.

    Enterprise tool: inspectcode requires a ReSharper license.
    ``execute_resharper()`` raises ``NotImplementedError`` with instructions.
    All parsing methods work on pre-generated XML files.
    """

    def execute_resharper(
        self,
        solution_path: Union[str, Path],
        output_path: Optional[Path] = None,
    ) -> List[ReSharperIssue]:
        """Run ReSharper InspectCode.

        Raises:
            NotImplementedError: Always — ReSharper requires a licensed
                JetBrains installation.  Run ``inspectcode.exe Solution.sln
                --output=result.xml`` externally and pass the output file to
                ``parse_xml_report()``.
        """
        raise NotImplementedError(
            "ReSharper InspectCode requires a licensed JetBrains installation. "
            "Run 'inspectcode.exe YourSolution.sln --output=result.xml' externally "
            "and pass the result to parse_xml_report()."
        )

    def parse_xml_report(self, report_path: Union[str, Path]) -> List[ReSharperIssue]:
        """Parse an InspectCode XML report.

        [20260303_FEATURE] Handles the standard InspectCode XML schema.

        Args:
            report_path: Path to the XML file produced by inspectcode.

        Returns:
            List of ReSharperIssue objects; ``[]`` on parse error.
        """
        try:
            source = str(report_path)
            if source.lstrip().startswith("<"):
                root = ET.fromstring(source)
            else:
                tree = ET.parse(source)
                root = tree.getroot()
        except (ET.ParseError, OSError):
            return []

        # Build issue-type metadata index
        issue_types: Dict[str, IssueType] = {}
        for it in root.iter("IssueType"):
            tid = it.get("Id", "")
            issue_types[tid] = IssueType(
                type_id=tid,
                category=it.get("Category", ""),
                description=it.get("Description", ""),
                severity=it.get("Severity", "WARNING"),
            )

        issues: List[ReSharperIssue] = []
        for project in root.iter("Project"):
            for issue in project.iter("Issue"):
                tid = issue.get("TypeId", "")
                meta = issue_types.get(
                    tid, IssueType(type_id=tid, category="", description="")
                )
                cat_str = meta.category.lower()
                category = _CATEGORY_MAP.get(cat_str, IssueCategory.OTHER)
                try:
                    line = int(issue.get("Line", 0))
                except ValueError:
                    line = 0
                issues.append(
                    ReSharperIssue(
                        type_id=tid,
                        category=category,
                        severity=meta.severity,
                        message=issue.get("Message", ""),
                        file_path=issue.get("File", ""),
                        line=line,
                        offset=issue.get("Offset"),
                    )
                )
        return issues

    def categorize_issues(
        self, issues: List[ReSharperIssue]
    ) -> Dict[IssueCategory, List[ReSharperIssue]]:
        """Group issues by category."""
        result: Dict[IssueCategory, List[ReSharperIssue]] = {}
        for issue in issues:
            result.setdefault(issue.category, []).append(issue)
        return result

    def generate_report(
        self, issues: List[ReSharperIssue], format: str = "json"
    ) -> str:
        """Return JSON or text report of ReSharper issues."""
        if format == "json":
            return json.dumps(
                {
                    "tool": "resharper",
                    "total": len(issues),
                    "issues": [
                        {
                            "type_id": i.type_id,
                            "category": i.category.value,
                            "severity": i.severity,
                            "message": i.message,
                            "file": i.file_path,
                            "line": i.line,
                        }
                        for i in issues
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{i.file_path}:{i.line}: {i.severity}: {i.type_id} - {i.message}"
            for i in issues
        )
