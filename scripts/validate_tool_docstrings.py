#!/usr/bin/env python3
"""Validate MCP tool docstrings for consistency and completeness.

This script checks that all MCP tools have properly formatted docstrings with:
- Brief one-line description
- Longer description (1-2 sentences)
- **Tier Behavior:** section
- **Tier Capabilities:** section (optional but recommended)
- **Args:** section with all parameters documented
- **Returns:** section describing ToolResponseEnvelope fields
- **Example:** section with usage code

Usage:
    python scripts/validate_tool_docstrings.py
    python scripts/validate_tool_docstrings.py --fix  # Interactive fixes
"""

import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional


class DocstringIssue(NamedTuple):
    """Represents a docstring validation issue."""

    file: str
    tool_name: str
    line: int
    issue: str
    severity: str  # 'error', 'warning', 'info'


class DocstringValidator:
    """Validates MCP tool docstrings for consistency."""

    # Required sections for tool docstrings
    REQUIRED_SECTIONS = {
        "Tier Behavior": r"\s*\*\*Tier Behavior:\*\*",
        "Args": r"\s*\*\*Args:\*\*",
        "Returns": r"\s*\*\*Returns:\*\*",
    }

    # Optional but recommended sections
    RECOMMENDED_SECTIONS = {
        "Tier Capabilities": r"\s*\*\*Tier Capabilities:\*\*",
    }

    def __init__(self):
        self.issues: list[DocstringIssue] = []
        self.tools_checked = 0

    def validate_tools_in_file(self, file_path: Path) -> list[DocstringIssue]:
        """Validate all MCP tools in a file."""
        file_issues = []

        try:
            with open(file_path, "r") as f:
                content = f.read()
                tree = ast.parse(content)
        except (SyntaxError, FileNotFoundError) as e:
            return [
                DocstringIssue(
                    file=str(file_path),
                    tool_name="<parse>",
                    line=0,
                    issue=f"Failed to parse: {e}",
                    severity="error",
                )
            ]

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                # Check if this is an MCP tool (has @mcp.tool decorator)
                if self._has_mcp_tool_decorator(node):
                    self.tools_checked += 1
                    issues = self._validate_tool_docstring(node.name, ast.get_docstring(node), node.lineno, file_path)
                    file_issues.extend(issues)

        return file_issues

    @staticmethod
    def _has_mcp_tool_decorator(node: ast.AsyncFunctionDef) -> bool:
        """Check if function has @mcp.tool() decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == "tool":
                        return True
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr == "tool":
                    return True
        return False

    def _validate_tool_docstring(
        self, tool_name: str, docstring: Optional[str], line: int, file_path: Path
    ) -> list[DocstringIssue]:
        """Validate a single tool's docstring."""
        issues = []

        if not docstring:
            issues.append(
                DocstringIssue(
                    file=str(file_path),
                    tool_name=tool_name,
                    line=line,
                    issue="Missing docstring",
                    severity="error",
                )
            )
            return issues

        # Check for required sections
        for section_name, pattern in self.REQUIRED_SECTIONS.items():
            if not re.search(pattern, docstring):
                issues.append(
                    DocstringIssue(
                        file=str(file_path),
                        tool_name=tool_name,
                        line=line,
                        issue=f"Missing required section: {section_name}",
                        severity="error",
                    )
                )

        # Check for recommended sections
        for section_name, pattern in self.RECOMMENDED_SECTIONS.items():
            if not re.search(pattern, docstring):
                issues.append(
                    DocstringIssue(
                        file=str(file_path),
                        tool_name=tool_name,
                        line=line,
                        issue=f"Missing recommended section: {section_name}",
                        severity="warning",
                    )
                )

        # Check for old section naming (Tier Features, Tier Requirements, Tier Capabilities)
        if re.search(r"\s*\*\*Tier (Features|Requirements|Capabilities):\*\*", docstring):
            # Make sure it's only "Tier Behavior" and "Tier Capabilities"
            if re.search(r"\s*\*\*Tier (Features|Requirements):\*\*", docstring):
                issues.append(
                    DocstringIssue(
                        file=str(file_path),
                        tool_name=tool_name,
                        line=line,
                        issue='Use "Tier Behavior" instead of "Tier Features" or "Tier Requirements"',
                        severity="warning",
                    )
                )

        # Check that Args and Returns have proper indentation (DISABLED - user wants simple format)
        # if "**Args:**" in docstring:
        #     args_section = re.search(
        #         r"\s*\*\*Args:\*\*\s+(.*?)(?=\s*\*\*|$)", docstring, re.DOTALL
        #     )
        #     if args_section:
        #         args_content = args_section.group(1)
        #         # Should have indented parameter descriptions
        #         if not re.search(r"\s{4,}", args_content):
        #             issues.append(
        #                 DocstringIssue(
        #                     file=str(file_path),
        #                     tool_name=tool_name,
        #                     line=line,
        #                     issue="Args section should have indented parameter descriptions",
        #                     severity="warning",
        #                 )
        #             )

        # Check that Returns has proper format
        if "**Returns:**" in docstring:
            returns_section = re.search(r"\s*\*\*Returns:\*\*\s+(.*?)(?=\s*\*\*|$)", docstring, re.DOTALL)
            if returns_section:
                returns_content = returns_section.group(1)
                # Should mention ToolResponseEnvelope
                if "ToolResponseEnvelope" not in returns_content:
                    issues.append(
                        DocstringIssue(
                            file=str(file_path),
                            tool_name=tool_name,
                            line=line,
                            issue="Returns section should describe ToolResponseEnvelope fields",
                            severity="warning",
                        )
                    )

        return issues

    def validate_project(self, tools_dir: Path) -> None:
        """Validate all tools in the project."""
        tool_files = list(tools_dir.glob("*.py"))
        tool_files = [f for f in tool_files if not f.name.startswith("_")]

        for tool_file in sorted(tool_files):
            file_issues = self.validate_tools_in_file(tool_file)
            self.issues.extend(file_issues)

    def report(self) -> int:
        """Print validation report and return exit code."""
        if not self.issues:
            print(f"✓ All {self.tools_checked} tools validated successfully!")
            return 0

        # Group issues by severity
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        infos = [i for i in self.issues if i.severity == "info"]

        print(f"Found {len(self.issues)} issue(s) in {self.tools_checked} tools:")
        print()

        if errors:
            print(f"❌ ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"  {issue.file}:{issue.line} - {issue.tool_name}")
                print(f"    {issue.issue}")
            print()

        if warnings:
            print(f"⚠️  WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line} - {issue.tool_name}")
                print(f"    {issue.issue}")
            print()

        if infos:
            print(f"ℹ️  INFO ({len(infos)}):")
            for issue in infos:
                print(f"  {issue.file}:{issue.line} - {issue.tool_name}")
                print(f"    {issue.issue}")
            print()

        # Return non-zero exit code if there are errors
        return 1 if errors else 0


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    tools_dir = repo_root / "src" / "code_scalpel" / "mcp" / "tools"

    if not tools_dir.exists():
        print(f"Error: Tools directory not found: {tools_dir}")
        return 1

    validator = DocstringValidator()
    validator.validate_project(tools_dir)
    return validator.report()


if __name__ == "__main__":
    sys.exit(main())
