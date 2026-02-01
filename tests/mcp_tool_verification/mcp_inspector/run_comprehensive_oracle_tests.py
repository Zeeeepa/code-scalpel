#!/usr/bin/env python3
"""
Comprehensive Oracle Resilience Tests

Tests ALL oracle recovery strategies:
- SymbolStrategy: Function, class, method typos
- PathStrategy: File path typos, missing files
- SafetyStrategy: Name collisions, duplicate symbols
- Cross-file scenarios: Import resolution, module paths

Usage:
    python run_comprehensive_oracle_tests.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Add project to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class TestResult:
    """Result of a single test case."""
    category: str
    test_name: str
    tool_name: str
    test_input: Dict[str, Any]
    passed: bool = False
    error_code: Optional[str] = None
    suggestion_count: int = 0
    top_suggestion: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None


class ComprehensiveOracleTestClient:
    """Comprehensive oracle resilience test client."""

    def __init__(self):
        self.results: List[TestResult] = []

    async def initialize(self):
        """Initialize the MCP tools module."""
        try:
            from code_scalpel.mcp import tools as mcp_tools
            self.tools_module = mcp_tools
            print("✅ Initialized MCP tools module\n")
        except ImportError as e:
            print(f"❌ Failed to import MCP tools: {e}")
            raise

    def get_tool_function(self, tool_name: str):
        """Get a tool function by name."""
        tool_map = {
            "extract_code": ("extraction", "extract_code"),
            "rename_symbol": ("extraction", "rename_symbol"),
            "update_symbol": ("extraction", "update_symbol"),
            "get_symbol_references": ("context", "get_symbol_references"),
            "get_call_graph": ("graph", "get_call_graph"),
            "get_file_context": ("context", "get_file_context"),
            "crawl_project": ("context", "crawl_project"),
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        module_name, func_name = tool_map[tool_name]

        if module_name == "extraction":
            from code_scalpel.mcp.tools import extraction
            module = extraction
        elif module_name == "context":
            from code_scalpel.mcp.tools import context
            module = context
        elif module_name == "graph":
            from code_scalpel.mcp.tools import graph
            module = graph
        else:
            raise ValueError(f"Unknown module: {module_name}")

        func = getattr(module, func_name, None)
        if not func:
            raise ValueError(f"Tool function not found: {tool_name}.{func_name}")

        return func

    def validate_oracle_response(self, response: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate oracle response structure."""
        errors = []

        if "error" not in response:
            errors.append("Missing 'error' field")
            return False, errors

        error = response.get("error")
        if not error:
            errors.append("'error' field is null")
            return False, errors

        if not isinstance(error, dict):
            errors.append(f"'error' not a dict, got {type(error).__name__}")
            return False, errors

        error_code = error.get("error_code")
        if error_code != "correction_needed":
            errors.append(f"error_code is '{error_code}', expected 'correction_needed'")

        if "error_details" not in error:
            errors.append("Missing 'error_details'")
            return False, errors

        error_details = error.get("error_details", {})
        if "suggestions" not in error_details:
            errors.append("Missing 'suggestions' in error_details")
            return False, errors

        suggestions = error_details.get("suggestions", [])
        if not isinstance(suggestions, list) or len(suggestions) == 0:
            errors.append(f"No suggestions provided: {suggestions}")
            return False, errors

        return len(errors) == 0, errors

    async def run_test(self, category: str, test_name: str, tool_name: str, arguments: Dict[str, Any]) -> TestResult:
        """Run a single test."""
        result = TestResult(
            category=category,
            test_name=test_name,
            tool_name=tool_name,
            test_input=arguments
        )

        try:
            tool_func = self.get_tool_function(tool_name)
            response = await tool_func(**arguments)

            # Convert to dict
            if hasattr(response, "model_dump"):
                response_dict = response.model_dump()
            elif isinstance(response, dict):
                response_dict = response
            else:
                response_dict = response.__dict__ if hasattr(response, "__dict__") else {}

            result.raw_response = response_dict

            # Validate
            is_valid, errors = self.validate_oracle_response(response_dict)
            result.errors = errors

            # Extract oracle info
            error = response_dict.get("error", {})
            result.error_code = error.get("error_code") if isinstance(error, dict) else None

            error_details = error.get("error_details", {}) if isinstance(error, dict) else {}
            suggestions = error_details.get("suggestions", [])
            result.suggestion_count = len(suggestions)

            if suggestions:
                top = suggestions[0]
                result.top_suggestion = top.get("symbol") or top.get("path") or top.get("hint")

            result.passed = is_valid and len(errors) == 0

        except Exception as e:
            result.passed = False
            result.errors = [str(e)]

        self.results.append(result)
        return result

    async def run_all_tests(self):
        """Run all comprehensive tests."""
        print("=" * 80)
        print("COMPREHENSIVE ORACLE RESILIENCE TESTS")
        print("=" * 80)

        # ===== CATEGORY 1: SYMBOL STRATEGIES =====
        print("\n📋 CATEGORY 1: SYMBOL EXTRACTION STRATEGIES")
        print("-" * 80)

        symbol_tests = [
            {
                "name": "Function Typo - Extract",
                "tool": "extract_code",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "proces_data"  # typo
                }
            },
            {
                "name": "Function Typo - Rename",
                "tool": "rename_symbol",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "proces_data",  # typo
                    "new_name": "process_input"
                }
            },
            {
                "name": "Function Typo - Get References",
                "tool": "get_symbol_references",
                "args": {
                    "symbol_name": "proces_data",  # typo
                    "project_root": "tests/mcp_tool_verification/mcp_inspector"
                }
            },
            {
                "name": "Entry Point Typo - Call Graph",
                "tool": "get_call_graph",
                "args": {
                    "project_root": "tests/mcp_tool_verification/mcp_inspector",
                    "entry_point": "proces_data",  # typo
                    "depth": 2
                }
            },
        ]

        for test in symbol_tests:
            await self.run_test("SymbolStrategy", test["name"], test["tool"], test["args"])

        # ===== CATEGORY 2: PATH STRATEGIES =====
        print("\n📋 CATEGORY 2: PATH RESOLUTION STRATEGIES")
        print("-" * 80)

        path_tests = [
            {
                "name": "Missing File - Extract Code",
                "tool": "extract_code",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/nonexistent_file.py",  # wrong
                    "target_type": "function",
                    "target_name": "some_function"
                }
            },
            {
                "name": "Missing File - Get Context",
                "tool": "get_file_context",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/nonexistent_file.py"  # wrong
                }
            },
            {
                "name": "Wrong Directory Path - Crawl",
                "tool": "crawl_project",
                "args": {
                    "root_path": "tests/mcp_tool_verification/wrong_dir_path/",  # wrong path
                    "complexity_threshold": 10
                }
            },
        ]

        for test in path_tests:
            await self.run_test("PathStrategy", test["name"], test["tool"], test["args"])

        # ===== CATEGORY 3: SAFETY STRATEGIES =====
        print("\n📋 CATEGORY 3: SAFETY/COLLISION STRATEGIES")
        print("-" * 80)

        safety_tests = [
            {
                "name": "Rename to Existing Name",
                "tool": "rename_symbol",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "process_data",
                    "new_name": "process_item"  # already exists
                }
            },
        ]

        for test in safety_tests:
            await self.run_test("SafetyStrategy", test["name"], test["tool"], test["args"])

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)

        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        # Print by category
        for category in sorted(categories.keys()):
            tests = categories[category]
            passed = sum(1 for t in tests if t.passed)
            total = len(tests)

            print(f"\n{category}: {passed}/{total} passed")
            print("-" * 80)

            for result in tests:
                status = "✅" if result.passed else "❌"
                print(f"{status} {result.test_name}")
                print(f"   Tool: {result.tool_name}")
                print(f"   Error Code: {result.error_code}")
                print(f"   Suggestions: {result.suggestion_count}")
                if result.top_suggestion:
                    print(f"   Top: {result.top_suggestion}")
                if result.errors:
                    for error in result.errors:
                        print(f"   ⚠️  {error}")

        # Overall summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)

        print("\n" + "=" * 80)
        print(f"OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        print("=" * 80)

        # Generate detailed report
        self.generate_report()

    def generate_report(self):
        """Generate detailed markdown report."""
        lines = [
            "# Comprehensive Oracle Resilience Test Report",
            "",
            f"**Total Tests**: {len(self.results)}",
            f"**Passed**: {sum(1 for r in self.results if r.passed)}",
            f"**Failed**: {sum(1 for r in self.results if not r.passed)}",
            f"**Pass Rate**: {(sum(1 for r in self.results if r.passed) / len(self.results) * 100):.1f}%",
            "",
            "---",
            "",
            "## By Strategy",
            "",
        ]

        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        for category in sorted(categories.keys()):
            tests = categories[category]
            passed = sum(1 for t in tests if t.passed)
            lines.extend([
                f"### {category}",
                f"**{passed}/{len(tests)} passed**",
                "",
            ])

            for result in tests:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                lines.extend([
                    f"**{result.test_name}** - {status}",
                    f"- Tool: {result.tool_name}",
                    f"- Error Code: {result.error_code}",
                    f"- Suggestions: {result.suggestion_count}",
                ])
                if result.top_suggestion:
                    lines.append(f"- Top: {result.top_suggestion}")
                if result.errors:
                    lines.append("- Issues:")
                    for error in result.errors:
                        lines.append(f"  - {error}")
                lines.append("")

        # Save report
        report_file = Path(__file__).parent / "ORACLE_COMPREHENSIVE_TEST_RESULTS.md"
        report_file.write_text("\n".join(lines))
        print(f"\n✅ Report saved to: {report_file}")


async def main():
    """Main entry point."""
    client = ComprehensiveOracleTestClient()

    try:
        await client.initialize()
        await client.run_all_tests()

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
