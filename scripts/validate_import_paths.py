#!/usr/bin/env python3
"""Validate import paths for Code Scalpel post-refactor.

This script checks for deprecated import patterns and provides migration
suggestions for updated module locations.

[20260125_TEST] validate import paths

Usage:
    python scripts/validate_import_paths.py --root /path/to/repo [--whitelist file.txt] [--out-json file.json]

Exit codes:
    0: No issues
    1: Warnings (deprecated imports found)
    2: Critical issues (deprecated imports in source code)
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class ImportPathValidator:
    """Validator for import path correctness."""

    # Known deprecated import patterns and their replacements
    DEPRECATED_PATTERNS = {
        r"from code_scalpel\.server import": "from code_scalpel.mcp.tools.{category} import",
        r"import code_scalpel\.server": "from code_scalpel.mcp.tools.{category} import",
        r"from code_scalpel\.helpers import": "from code_scalpel.mcp.helpers.{category}_helpers import",
        r"import code_scalpel\.helpers": "from code_scalpel.mcp.helpers.{category}_helpers import",
        r"from code_scalpel\.governance import": "from code_scalpel.mcp.governance import",
        r"from code_scalpel\.contract import": "from code_scalpel.mcp.contract import",
        r"from code_scalpel\.models import": "from code_scalpel.mcp.models import",
    }

    def __init__(self, repo_root: Path, whitelist: Optional[List[str]] = None):
        self.repo_root = repo_root
        self.whitelist = set(whitelist or [])

    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate import paths in a single file."""
        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return {}

        tree = ast.parse(content, filename=str(file_path))

        result = {
            "file": str(file_path.relative_to(self.repo_root)),
            "category": self._categorize_file(file_path),
            "deprecated_imports": [],
            "fix_suggestions": [],
            "relative_imports": [],
        }

        # Analyze imports
        self._analyze_imports(tree, content, result)

        return result

    def _analyze_imports(self, tree: ast.Module, content: str, result: Dict[str, Any]):
        """Analyze import statements for deprecated patterns."""
        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
                import_line = lines[node.lineno - 1].strip()

                # Check for deprecated patterns
                for pattern, replacement_template in self.DEPRECATED_PATTERNS.items():
                    if re.search(pattern, import_line):
                        if not self._is_whitelisted(import_line):
                            result["deprecated_imports"].append(
                                {
                                    "line": node.lineno,
                                    "text": import_line,
                                    "pattern": pattern,
                                }
                            )

                            # Generate fix suggestion
                            suggestion = self._generate_fix(
                                import_line, replacement_template, result["category"]
                            )
                            if suggestion:
                                result["fix_suggestions"].append(suggestion)

                # Check for problematic relative imports
                if isinstance(node, ast.ImportFrom) and node.level > 0:
                    if self._is_problematic_relative(node, import_line):
                        result["relative_imports"].append(
                            {"line": node.lineno, "text": import_line}
                        )

    def _is_whitelisted(self, import_line: str) -> bool:
        """Check if import line is whitelisted."""
        for allowed in self.whitelist:
            if allowed in import_line:
                return True
        return False

    def _generate_fix(
        self, original: str, template: str, category: str
    ) -> Optional[Dict[str, str]]:
        """Generate a fix suggestion."""
        # For tool imports, try to infer category from tool name
        if "{category}" in template:
            # Extract tool name from import
            tool_match = re.search(r"import (\w+)", original)
            if tool_match:
                tool_name = tool_match.group(1)
                inferred_category = self._infer_tool_category(tool_name)
                template = template.format(category=inferred_category)
            else:
                return None

        return {"original": original, "suggested": template}

    def _infer_tool_category(self, tool_name: str) -> str:
        """Infer category from tool name."""
        # Simple mapping - could be enhanced
        tool_categories = {
            "analyze_code": "analyze",
            "security_scan": "security",
            "unified_sink_detect": "security",
            "type_evaporation_scan": "security",
            "scan_dependencies": "security",
            "extract_code": "extraction",
            "rename_symbol": "extraction",
            "update_symbol": "extraction",
            "symbolic_execute": "symbolic",
            "generate_unit_tests": "symbolic",
            "simulate_refactor": "symbolic",
            "crawl_project": "context",
            "get_file_context": "context",
            "get_symbol_references": "context",
            "get_call_graph": "graph",
            "get_graph_neighborhood": "graph",
            "get_project_map": "graph",
            "get_cross_file_dependencies": "graph",
            "cross_file_security_scan": "graph",
            "validate_paths": "policy",
            "verify_policy_integrity": "policy",
            "code_policy_check": "policy",
        }
        return tool_categories.get(tool_name, "unknown")

    def _is_problematic_relative(self, node: ast.ImportFrom, import_line: str) -> bool:
        """Check if relative import is problematic."""
        # Flag relative imports that might be from old structure
        if node.level > 1:
            return True
        # Or imports from modules that have been reorganized
        if node.module and any(old in node.module for old in ["server", "helpers"]):
            return True
        return False

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file by type."""
        path_str = str(file_path)

        if "src/code_scalpel" in path_str:
            return "source"
        elif "tests" in path_str:
            return "test"
        elif "docs" in path_str or "examples" in path_str:
            return "doc"
        else:
            return "other"

    def build_inventory(self) -> Dict[str, Any]:
        """Build complete inventory of import issues."""
        files = []

        for py_file in self.repo_root.rglob("*.py"):
            if py_file.is_file():
                validation = self.validate_file(py_file)
                if validation and (
                    validation["deprecated_imports"] or validation["relative_imports"]
                ):
                    files.append(validation)

        # Identify critical findings (deprecated imports in source code)
        critical_findings = [
            f for f in files if f["category"] == "source" and f["deprecated_imports"]
        ]

        summary = {
            "total_files_checked": len(
                [f for f in self.repo_root.rglob("*.py") if f.is_file()]
            ),
            "files_with_issues": len(files),
            "critical_findings": len(critical_findings),
            "total_deprecated_imports": sum(
                len(f["deprecated_imports"]) for f in files
            ),
            "total_fix_suggestions": sum(len(f["fix_suggestions"]) for f in files),
        }

        return {
            "files": files,
            "critical_findings": critical_findings,
            "summary": summary,
        }


def main():
    parser = argparse.ArgumentParser(description="Validate import paths")
    parser.add_argument("--root", required=True, type=Path, help="Repository root")
    parser.add_argument(
        "--whitelist", type=Path, help="Whitelist file with allowed deprecated imports"
    )
    parser.add_argument("--out-json", type=Path, help="Output JSON file")

    args = parser.parse_args()

    # Load whitelist if provided
    whitelist = None
    if args.whitelist and args.whitelist.exists():
        whitelist = [
            line.strip()
            for line in args.whitelist.read_text().split("\n")
            if line.strip()
        ]

    validator = ImportPathValidator(args.root, whitelist)
    inventory = validator.build_inventory()

    if args.out_json:
        with open(args.out_json, "w") as f:
            json.dump(inventory, f, indent=2)
        print(f"JSON output written to {args.out_json}")

    # Determine exit code
    has_critical = len(inventory["critical_findings"]) > 0
    has_warnings = len(inventory["files"]) > 0

    print(f"Checked {inventory['summary']['total_files_checked']} files")
    print(f"Found {inventory['summary']['files_with_issues']} files with import issues")
    print(
        f"Critical issues in source code: {inventory['summary']['critical_findings']}"
    )

    if has_critical:
        print("CRITICAL: Deprecated imports found in source code")
        sys.exit(2)
    elif has_warnings:
        print("WARNING: Deprecated imports found (in tests/docs)")
        sys.exit(1)
    else:
        print("No deprecated import issues found")
        sys.exit(0)


if __name__ == "__main__":
    main()
