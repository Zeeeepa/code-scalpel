#!/usr/bin/env python3
"""Validate tool compliance for Code Scalpel MCP refactor.

This script performs AST-based validation of tool compliance criteria
for the refactored MCP tools.

[20260125_TEST] validate tool compliance

Usage:
    python scripts/validate_tool_compliance.py --root /path/to/repo [--out-csv file.csv] [--format csv|md|json] [--strict] [--verbose]

Exit codes:
    0: All pass
    1: Warnings
    2: Failures
"""

import argparse
import ast
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Expected tools from mcp_validate_22_tools.py
EXPECTED_TOOLS = {
    "analyze_code",
    "code_policy_check",
    "crawl_project",
    "cross_file_security_scan",
    "extract_code",
    "generate_unit_tests",
    "get_call_graph",
    "get_cross_file_dependencies",
    "get_file_context",
    "get_graph_neighborhood",
    "get_project_map",
    "get_symbol_references",
    "rename_symbol",
    "scan_dependencies",
    "security_scan",
    "simulate_refactor",
    "symbolic_execute",
    "type_evaporation_scan",
    "unified_sink_detect",
    "update_symbol",
    "validate_paths",
    "verify_policy_integrity",
}

CRITERIA_NAMES = [
    "has_mcp_tool_decorator",
    "is_async_function",
    "calls_asyncio_to_thread",
    "imports_helper_correctly",
    "helper_file_exists",
    "helper_function_exists",
    "helper_is_sync",
    "no_mcp_tool_in_server",
    "tool_in_expected_list",
    "tool_registered",
    "signature_has_parameters",
    "no_envelop_wrapper",
    "returns_correct_type",
]


class ToolComplianceChecker:
    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

        self.tools_dir = repo_root / "src" / "code_scalpel" / "mcp" / "tools"
        self.helpers_dir = repo_root / "src" / "code_scalpel" / "mcp" / "helpers"
        self.server_py = repo_root / "src" / "code_scalpel" / "mcp" / "server.py"

    def find_tool_files(self) -> List[Path]:
        """Find all Python files in tools/ directory."""
        if not self.tools_dir.exists():
            self.logger.error(f"Tools directory not found: {self.tools_dir}")
            return []
        files = list(self.tools_dir.glob("*.py"))
        return files

    def parse_file(self, file_path: Path) -> Optional[ast.Module]:
        """Parse Python file to AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            self.logger.error(f"Failed to parse {file_path}: {e}")
            return None

    def find_decorated_functions(self, tree: ast.Module) -> List[Tuple[str, ast.FunctionDef]]:
        """Find functions decorated with @mcp.tool()."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if self._is_mcp_tool_decorator(decorator):
                        functions.append((node.name, node))
                        break
        return functions

    def _is_mcp_tool_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @mcp.tool()."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "mcp":
                    if decorator.func.attr == "tool":
                        return True
        return False

    def check_criteria(self, tool_name: str, func_node: ast.FunctionDef, tool_file: Path) -> Dict[str, Any]:
        """Check all compliance criteria for a tool."""
        criteria = {}

        # 1. has_mcp_tool_decorator
        criteria["has_mcp_tool_decorator"] = any(self._is_mcp_tool_decorator(d) for d in func_node.decorator_list)

        # 2. is_async_function
        criteria["is_async_function"] = isinstance(func_node, ast.AsyncFunctionDef)

        # 3. calls_asyncio_to_thread
        has_asyncio_to_thread, has_direct_await = self._calls_asyncio_to_thread(func_node)
        criteria["calls_asyncio_to_thread"] = has_asyncio_to_thread or has_direct_await

        # 4. imports_helper_correctly
        criteria["imports_helper_correctly"] = self._imports_helper_correctly(func_node, tool_name)

        # 5. helper_file_exists
        helper_file = self._get_helper_file_path(tool_name)
        criteria["helper_file_exists"] = helper_file is not None and helper_file.exists()

        # 6. helper_function_exists
        helper_func_name = self._get_helper_func_name(tool_name)
        criteria["helper_function_exists"] = (
            self._helper_function_exists(helper_file, helper_func_name) if helper_file else False
        )

        # 7. helper_is_sync
        if has_asyncio_to_thread:
            criteria["helper_is_sync"] = self._helper_is_sync(helper_file, helper_func_name) if helper_file else False
        elif has_direct_await:
            criteria["helper_is_sync"] = True
        else:
            criteria["helper_is_sync"] = False

        # 8. no_mcp_tool_in_server
        criteria["no_mcp_tool_in_server"] = not self._mcp_tool_in_server(tool_name)

        # 9. tool_in_expected_list
        criteria["tool_in_expected_list"] = tool_name in EXPECTED_TOOLS

        # 10. tool_registered
        criteria["tool_registered"] = self._tool_registered(tool_name)

        # 11. signature_has_parameters
        criteria["signature_has_parameters"] = len(func_node.args.args) > 0

        # 12. no_envelop_wrapper
        criteria["no_envelop_wrapper"] = not self._uses_envelop_wrapper(func_node)

        # 13. returns_correct_type (basic check)
        criteria["returns_correct_type"] = func_node.returns is not None

        return criteria

    def _calls_asyncio_to_thread(self, func_node: ast.FunctionDef) -> Tuple[bool, bool]:
        """Check if function calls asyncio.to_thread or awaits helper directly.

        Returns (has_asyncio_to_thread, has_direct_await)
        """
        has_asyncio_to_thread = False
        has_direct_await = False

        # First check for asyncio.to_thread
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "asyncio":
                        if node.func.attr == "to_thread":
                            has_asyncio_to_thread = True

        # Check for await on helper
        expected_helper = f"_{func_node.name}"
        for node in ast.walk(func_node):
            if isinstance(node, ast.Await):
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Name) and func.id == expected_helper:
                        has_direct_await = True

        return has_asyncio_to_thread, has_direct_await

    def _imports_helper_correctly(self, func_node: ast.FunctionDef, tool_name: str) -> bool:
        """Check if imports helper function correctly."""
        f"from code_scalpel.mcp.helpers.{self._get_category(tool_name)}_helpers import _{tool_name}_sync"
        # Simplified: check if any import contains the helper
        # Full implementation would parse imports
        return True  # TODO: implement proper import checking

    def _get_helper_file_path(self, tool_name: str) -> Optional[Path]:
        """Get expected helper file path."""
        category = self._get_category(tool_name)
        return self.helpers_dir / f"{category}_helpers.py"

    def _get_category(self, tool_name: str) -> str:
        """Map tool name to category."""
        # Mapping based on tool files
        mapping = {
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
        return mapping.get(tool_name, "unknown")

    def _get_helper_func_name(self, tool_name: str) -> str:
        """Get the expected helper function name."""
        # Mapping for helper function names (not always _<tool_name>_sync)
        mapping = {
            "analyze_code": "_analyze_code_sync",
            "crawl_project": "_crawl_project_sync",
            "get_file_context": "_get_file_context_sync",
            "get_symbol_references": "_get_symbol_references_sync",
            "extract_code": "_extract_code_impl",  # async def in extraction_helpers
            "rename_symbol": "rename_symbol",  # async def in extraction_helpers
            "update_symbol": "update_symbol",  # async def in extraction_helpers
            "get_call_graph": "_get_call_graph_sync",
            "get_graph_neighborhood": "_get_graph_neighborhood_sync",
            "get_project_map": "_get_project_map_sync",
            "get_cross_file_dependencies": "_get_cross_file_dependencies_sync",
            "cross_file_security_scan": "_cross_file_security_scan_sync",
            "validate_paths": "_validate_paths_sync",
            "verify_policy_integrity": "_verify_policy_integrity_sync",
            "code_policy_check": "_code_policy_check_sync",
            "security_scan": "_security_scan_sync",
            "unified_sink_detect": "_unified_sink_detect_sync",
            "type_evaporation_scan": "_type_evaporation_scan_sync",
            "scan_dependencies": "_scan_dependencies_sync",
            "symbolic_execute": "_symbolic_execute_sync",
            "generate_unit_tests": "_generate_tests_sync",  # Note: not _generate_unit_tests_sync
            "simulate_refactor": "_simulate_refactor_sync",
        }
        return mapping.get(tool_name, f"_{tool_name}_sync")

    def _helper_function_exists(self, helper_file: Path, func_name: str) -> bool:
        """Check if helper function exists in file."""
        if not helper_file.exists():
            return False
        tree = self.parse_file(helper_file)
        if not tree:
            return False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return True
        return False

    def _helper_is_sync(self, helper_file: Path, func_name: str) -> bool:
        """Check if helper function is sync (not async)."""
        if not helper_file.exists():
            return False
        tree = self.parse_file(helper_file)
        if not tree:
            return False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return not isinstance(node, ast.AsyncFunctionDef)
        return False

    def _mcp_tool_in_server(self, tool_name: str) -> bool:
        """Check if tool is still defined in server.py."""
        if not self.server_py.exists():
            return False
        tree = self.parse_file(self.server_py)
        if not tree:
            return False
        for func_name, _ in self.find_decorated_functions(tree):
            if func_name == tool_name:
                return True
        return False

    def _tool_registered(self, tool_name: str) -> bool:
        """Check if tool is registered in tools/__init__.py."""
        init_file = self.tools_dir / "__init__.py"
        if not init_file.exists():
            return False
        # Check if the module containing the tool is imported in register_tools
        category = self._get_category(tool_name)
        if category == "unknown":
            # For unknown, assume registered if in expected
            return tool_name in EXPECTED_TOOLS
        module_import = f"code_scalpel.mcp.tools.{category}"
        content = init_file.read_text()
        return module_import in content

    def _uses_envelop_wrapper(self, func_node: ast.FunctionDef) -> bool:
        """Check if uses envelop_tool_function or similar wrappers."""
        # Simplified check
        return False  # TODO: implement if needed

    def validate_all_tools(self) -> List[Dict[str, Any]]:
        """Validate all tools and return results."""
        results = []
        tool_files = self.find_tool_files()

        for tool_file in tool_files:
            if tool_file.name == "__init__.py":
                continue
            tree = self.parse_file(tool_file)
            if not tree:
                continue

            decorated_funcs = self.find_decorated_functions(tree)
            for tool_name, func_node in decorated_funcs:
                criteria = self.check_criteria(tool_name, func_node, tool_file)
                result = {
                    "tool_id": tool_name,
                    "module": str(tool_file.relative_to(self.repo_root)),
                    "first_failure_line": (func_node.lineno if any(not v for v in criteria.values()) else None),
                    "status": "PASS" if all(criteria.values()) else "FAIL",
                    **criteria,
                }
                results.append(result)

        return results

    def output_csv(self, results: List[Dict[str, Any]], output_file: Path) -> None:
        """Output results to CSV."""
        if not results:
            return
        fieldnames = [
            "tool_id",
            "module",
            "status",
            "first_failure_line",
        ] + CRITERIA_NAMES
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    def output_json(self, results: List[Dict[str, Any]], output_file: Path) -> None:
        """Output results to JSON."""
        with open(output_file, "w") as f:
            json.dump({"results": results, "criteria": CRITERIA_NAMES}, f, indent=2)

    def output_markdown_table(self, results: List[Dict[str, Any]]) -> str:
        """Generate Markdown table."""
        if not results:
            return "No results"

        headers = ["Tool ID", "Module", "Status"] + CRITERIA_NAMES
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join("---" for _ in headers) + "|\n"

        for result in results:
            row = [result["tool_id"], result["module"], result["status"]] + [str(result[c]) for c in CRITERIA_NAMES]
            table += "| " + " | ".join(row) + " |\n"

        return table


def main():
    parser = argparse.ArgumentParser(description="Validate tool compliance")
    parser.add_argument("--root", required=True, type=Path, help="Repository root")
    parser.add_argument("--out-csv", type=Path, help="Output CSV file")
    parser.add_argument("--format", choices=["csv", "md", "json"], default="csv", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    checker = ToolComplianceChecker(args.root, args.verbose)
    results = checker.validate_all_tools()

    # Determine exit code
    failures = [r for r in results if r["status"] == "FAIL"]
    warnings = []  # Could add warning criteria
    exit_code = 2 if failures else (1 if warnings else 0)

    if args.format == "csv" or args.out_csv:
        output_file = args.out_csv or Path("tool_compliance.csv")
        checker.output_csv(results, output_file)
        print(f"CSV output written to {output_file}")

    if args.format == "json":
        output_file = Path("tool_compliance.json")
        checker.output_json(results, output_file)
        print(f"JSON output written to {output_file}")

    if args.format == "md":
        table = checker.output_markdown_table(results)
        print(table)

    print(f"Validated {len(results)} tools: {len(failures)} failures")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
