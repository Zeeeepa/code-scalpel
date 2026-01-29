#!/usr/bin/env python3
"""Analyze deprecated code patterns in Code Scalpel.

This script performs AST-based analysis to identify deprecated code patterns,
import usage, and provides recommendations for cleanup.

[20260125_TEST] analyze deprecated code

Usage:
    python scripts/analyze_deprecated_code.py --root /path/to/repo [--out-json file.json] [--min-import-threshold N]

Exit codes:
    0: Success
    1: Warnings (deprecated code found)
    2: Errors
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any


class DeprecatedCodeAnalyzer:
    """Analyzer for deprecated code patterns."""

    def __init__(self, repo_root: Path, min_import_threshold: int = 0):
        self.repo_root = repo_root
        self.min_import_threshold = min_import_threshold
        self.analyzed_files: Dict[str, Dict[str, Any]] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for deprecated patterns."""
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
            "has_deprecation_marker": False,
            "deprecation_markers": [],
            "import_count": 0,
            "imports": [],
            "legacy_functions": [],
            "has_datetime_now_without_tz": False,
            "datetime_now_locations": [],
            "has_migration_guidance": False,
            "migration_guidance": [],
            "caller_count": 0,
            "callers": [],
            "recommendations": [],
        }

        # Check for deprecation markers in comments
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(r"#\s*\[.*_DEPRECATED.*\]", line, re.IGNORECASE):
                result["has_deprecation_marker"] = True
                result["deprecation_markers"].append({"line": i, "text": line.strip()})

        # Analyze AST
        self._analyze_ast(tree, result)

        # Check for migration guidance
        for line in lines:
            if re.search(r"(TODO|migrate|migration|use.*instead)", line, re.IGNORECASE):
                result["has_migration_guidance"] = True
                result["migration_guidance"].append(line.strip())

        # Find callers (simplified: grep for function names)
        # if result["legacy_functions"]:
        #     self._find_callers(file_path, result)

        # Generate recommendations
        self._generate_recommendations(result)

        return result

    def _analyze_ast(self, tree: ast.Module, result: Dict[str, Any]):
        """Analyze AST for imports and patterns."""
        imports = []
        legacy_functions = []

        for node in ast.walk(tree):
            # Count imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                result["import_count"] += 1
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                else:
                    module = node.module or ""
                    imports.extend(f"{module}.{alias.name}" for alias in node.names)

            # Find legacy functions (no type hints)
            elif isinstance(node, ast.FunctionDef):
                if not node.returns and not any(arg.annotation for arg in node.args.args):
                    legacy_functions.append(node.name)

            # Check datetime.now() without timezone
            elif isinstance(node, ast.Call):
                if self._is_datetime_now_without_tz(node):
                    result["has_datetime_now_without_tz"] = True
                    result["datetime_now_locations"].append(node.lineno)

        result["imports"] = imports
        result["legacy_functions"] = legacy_functions

    def _is_datetime_now_without_tz(self, node: ast.Call) -> bool:
        """Check if call is datetime.datetime.now() without timezone."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "datetime"
                    and node.func.value.attr == "datetime"
                    and node.func.attr == "now"
                ):
                    # Check if no arguments (no timezone)
                    return len(node.args) == 0
        return False

    def _find_callers(self, file_path: Path, result: Dict[str, Any]):
        """Find files that call deprecated functions."""
        callers = []
        func_names = result["legacy_functions"]

        # Simple grep approach
        for py_file in self.repo_root.rglob("*.py"):
            if py_file == file_path:
                continue
            try:
                content = py_file.read_text()
                for func_name in func_names:
                    if re.search(rf"\b{func_name}\b", content):
                        callers.append(str(py_file.relative_to(self.repo_root)))
                        break
            except Exception:
                continue

        result["callers"] = list(set(callers))
        result["caller_count"] = len(callers)

    def _generate_recommendations(self, result: Dict[str, Any]):
        """Generate cleanup recommendations."""
        recs = []

        if result["has_deprecation_marker"]:
            recs.append("Remove deprecated functions marked with deprecation comments")

        if result["import_count"] > 10:
            recs.append("Consider consolidating imports or using import aliases")

        if result["legacy_functions"]:
            recs.append(f"Add type hints to {len(result['legacy_functions'])} functions")

        if result["has_datetime_now_without_tz"]:
            recs.append("Replace datetime.now() with timezone-aware alternatives")

        if result["caller_count"] > 0:
            recs.append(f"Update {result['caller_count']} caller files before removal")

        result["recommendations"] = recs

    def build_inventory(self) -> Dict[str, Any]:
        """Build complete inventory of deprecated code."""
        files = []

        for py_file in self.repo_root.rglob("*.py"):
            if py_file.is_file():
                analysis = self.analyze_file(py_file)
                if analysis and (
                    analysis["import_count"] >= self.min_import_threshold
                    or analysis["has_deprecation_marker"]
                    or analysis["legacy_functions"]
                ):
                    files.append(analysis)

        summary = {
            "total_files_analyzed": len(files),
            "files_with_deprecation": sum(1 for f in files if f["has_deprecation_marker"]),
            "files_with_legacy_functions": sum(1 for f in files if f["legacy_functions"]),
            "files_with_datetime_issues": sum(1 for f in files if f["has_datetime_now_without_tz"]),
            "total_imports": sum(f["import_count"] for f in files),
            "total_callers": sum(f["caller_count"] for f in files),
        }

        return {"files": files, "summary": summary}


def main():
    parser = argparse.ArgumentParser(description="Analyze deprecated code")
    parser.add_argument("--root", required=True, type=Path, help="Repository root")
    parser.add_argument("--out-json", type=Path, help="Output JSON file")
    parser.add_argument(
        "--min-import-threshold",
        type=int,
        default=0,
        help="Minimum import count to include file",
    )

    args = parser.parse_args()

    analyzer = DeprecatedCodeAnalyzer(args.root, args.min_import_threshold)
    inventory = analyzer.build_inventory()

    if args.out_json:
        with open(args.out_json, "w") as f:
            json.dump(inventory, f, indent=2)
        print(f"JSON output written to {args.out_json}")

    # Determine exit code based on findings
    has_issues = any(
        f["has_deprecation_marker"] or f["legacy_functions"] or f["has_datetime_now_without_tz"]
        for f in inventory["files"]
    )

    print(f"Analyzed {inventory['summary']['total_files_analyzed']} files")
    if has_issues:
        print("Found deprecated code patterns")
        sys.exit(1)
    else:
        print("No deprecated code patterns found")
        sys.exit(0)


if __name__ == "__main__":
    main()
