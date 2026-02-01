#!/usr/bin/env python3
"""
Automated Oracle Resilience Pilot Tests

Tests all 7 pilot tools by calling them directly via async functions.
Validates oracle resilience behavior without needing the MCP server.

Usage:
    python run_oracle_tests.py
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
    tool_name: str
    test_name: str
    test_input: Dict[str, Any]
    passed: bool = False
    error_code: Optional[str] = None
    has_suggestions: bool = False
    suggestion_count: int = 0
    top_suggestion: Optional[str] = None
    top_score: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None


class OracleTestClient:
    """Client for testing oracle resilience in MCP tools."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.tools_module = None

    async def initialize(self):
        """Initialize the MCP tools module."""
        try:
            # Import MCP tools directly
            from code_scalpel.mcp import tools as mcp_tools
            self.tools_module = mcp_tools
            print("✅ Initialized MCP tools module")
        except ImportError as e:
            print(f"❌ Failed to import MCP tools: {e}")
            raise

    def get_tool_function(self, tool_name: str):
        """Get a tool function by name."""
        if not self.tools_module:
            raise RuntimeError("Tools module not initialized")

        # Map tool names to module and function
        tool_map = {
            "extract_code": ("extraction", "extract_code"),
            "rename_symbol": ("extraction", "rename_symbol"),
            "update_symbol": ("extraction", "update_symbol"),
            "get_symbol_references": ("context", "get_symbol_references"),
            "get_call_graph": ("graph", "get_call_graph"),
            "get_graph_neighborhood": ("graph", "get_graph_neighborhood"),
            "get_cross_file_dependencies": ("graph", "get_cross_file_dependencies"),
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        module_name, func_name = tool_map[tool_name]

        # Get the module
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

        # Get the function
        func = getattr(module, func_name, None)
        if not func:
            raise ValueError(f"Tool function not found: {tool_name}.{func_name}")

        return func

    def validate_oracle_response(self, response: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that the response has oracle resilience structure.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check for error object
        if "error" not in response:
            errors.append("Missing 'error' field in response")
            return False, errors

        error = response.get("error")
        if not error:
            errors.append("'error' field is null (should be error object)")
            return False, errors

        if not isinstance(error, dict):
            errors.append(f"'error' should be dict, got {type(error).__name__}")
            return False, errors

        # Check for error_code
        error_code = error.get("error_code")
        if error_code != "correction_needed":
            errors.append(f"error_code is '{error_code}', expected 'correction_needed'")

        # Check for error_details
        if "error_details" not in error:
            errors.append("Missing 'error_details' in error object")
            return False, errors

        error_details = error.get("error_details", {})

        # Check for suggestions
        if "suggestions" not in error_details:
            errors.append("Missing 'suggestions' in error_details")
            return False, errors

        suggestions = error_details.get("suggestions", [])
        if not isinstance(suggestions, list):
            errors.append(f"'suggestions' should be list, got {type(suggestions).__name__}")
            return False, errors

        if len(suggestions) == 0:
            errors.append("'suggestions' list is empty")
            return False, errors

        # Validate each suggestion
        for i, suggestion in enumerate(suggestions):
            if not isinstance(suggestion, dict):
                errors.append(f"Suggestion {i} is not a dict")
                continue

            # Check for symbol or path
            if "symbol" not in suggestion and "path" not in suggestion:
                errors.append(f"Suggestion {i} missing 'symbol' or 'path'")

            # Check for score
            if "score" not in suggestion:
                errors.append(f"Suggestion {i} missing 'score'")
            else:
                score = suggestion.get("score")
                if not isinstance(score, (int, float)):
                    errors.append(f"Suggestion {i} score should be number, got {type(score).__name__}")
                elif not (0.0 <= score <= 1.0):
                    errors.append(f"Suggestion {i} score out of range: {score}")

            # Check for reason
            if "reason" not in suggestion:
                errors.append(f"Suggestion {i} missing 'reason'")

        return len(errors) == 0, errors

    async def run_test(
        self,
        test_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> TestResult:
        """Run a single test case."""
        result = TestResult(
            tool_name=tool_name,
            test_name=test_name,
            test_input=arguments
        )

        try:
            print(f"\n📝 Running: {test_name}")
            print(f"   Tool: {tool_name}")

            # Get tool function
            tool_func = self.get_tool_function(tool_name)

            # Call the tool
            response = await tool_func(**arguments)

            # Convert response to dict if it's an object
            if hasattr(response, "model_dump"):
                response_dict = response.model_dump()
            elif isinstance(response, dict):
                response_dict = response
            else:
                response_dict = response.__dict__ if hasattr(response, "__dict__") else {}

            result.raw_response = response_dict

            # Validate oracle structure
            is_valid, errors = self.validate_oracle_response(response_dict)
            result.errors = errors

            # Extract oracle information
            error = response_dict.get("error", {})
            result.error_code = error.get("error_code") if isinstance(error, dict) else None

            error_details = error.get("error_details", {}) if isinstance(error, dict) else {}
            suggestions = error_details.get("suggestions", [])

            result.has_suggestions = len(suggestions) > 0
            result.suggestion_count = len(suggestions)

            if suggestions:
                top = suggestions[0]
                result.top_suggestion = top.get("symbol") or top.get("path")
                result.top_score = top.get("score")

            result.passed = is_valid and len(errors) == 0

            if result.passed:
                print(f"   ✅ PASSED")
                print(f"      - error_code: {result.error_code}")
                print(f"      - suggestions: {result.suggestion_count}")
                print(f"      - top: {result.top_suggestion} (score: {result.top_score})")
            else:
                print(f"   ❌ FAILED")
                for error in errors:
                    print(f"      - {error}")

        except Exception as e:
            result.passed = False
            result.errors = [str(e)]
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        self.results.append(result)
        return result

    async def run_all_tests(self):
        """Run all 7 oracle resilience tests."""
        print("=" * 70)
        print("Oracle Resilience Pilot Tests - Automated Validation")
        print("=" * 70)

        # Define all 7 test cases
        tests = [
            {
                "name": "Test 1.1: extract_code - Symbol Typo",
                "tool": "extract_code",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "proces_data"
                }
            },
            {
                "name": "Test 2.1: rename_symbol - Missing Symbol",
                "tool": "rename_symbol",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "proces_data",
                    "new_name": "process_input"
                }
            },
            {
                "name": "Test 3.1: update_symbol - Missing Symbol",
                "tool": "update_symbol",
                "args": {
                    "file_path": "tests/mcp_tool_verification/mcp_inspector/test_code.py",
                    "target_type": "function",
                    "target_name": "proces_item",
                    "new_code": "def process_item(y):\n    return y + 2",
                    "operation": "replace"
                }
            },
            {
                "name": "Test 4.1: get_symbol_references - Missing Symbol",
                "tool": "get_symbol_references",
                "args": {
                    "symbol_name": "proces_data",
                    "project_root": "tests/mcp_tool_verification/mcp_inspector"
                }
            },
            {
                "name": "Test 5.1: get_call_graph - Entry Point Typo",
                "tool": "get_call_graph",
                "args": {
                    "project_root": "tests/mcp_tool_verification/mcp_inspector",
                    "entry_point": "proces_data",
                    "depth": 2
                }
            },
            {
                "name": "Test 6.1: get_graph_neighborhood - Node Typo",
                "tool": "get_graph_neighborhood",
                "args": {
                    "center_node_id": "python::test_code::function::proces_data",
                    "k": 2,
                    "direction": "both",
                    "project_root": "tests/mcp_tool_verification/mcp_inspector"
                }
            },
            {
                "name": "Test 7.1: get_cross_file_dependencies - Symbol Typo",
                "tool": "get_cross_file_dependencies",
                "args": {
                    "target_file": "test_code.py",
                    "target_symbol": "proces_data",
                    "project_root": "tests/mcp_tool_verification/mcp_inspector",
                    "max_depth": 2
                }
            },
        ]

        # Run each test
        for test_case in tests:
            await self.run_test(
                test_name=test_case["name"],
                tool_name=test_case["tool"],
                arguments=test_case["args"]
            )

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Pass Rate: {(passed/total*100):.1f}%")

        print("\nDetailed Results:")
        print("-" * 70)

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"\n{status} | {result.test_name}")
            print(f"       Tool: {result.tool_name}")
            print(f"       Error Code: {result.error_code}")
            print(f"       Suggestions: {result.suggestion_count}")
            if result.top_suggestion:
                print(f"       Top: {result.top_suggestion} (score: {result.top_score})")

            if result.errors:
                print(f"       Issues:")
                for error in result.errors:
                    print(f"         - {error}")

        print("\n" + "=" * 70)
        print("TEST REPORT")
        print("=" * 70)

        # Generate markdown report
        report = self.generate_markdown_report()

        # Save to file
        report_file = Path(__file__).parent / "ORACLE_PILOT_TEST_RESULTS_AUTOMATED.md"
        report_file.write_text(report)
        print(f"\n✅ Report saved to: {report_file}")

        # Print to console
        print("\n" + report)

    def generate_markdown_report(self) -> str:
        """Generate a markdown report of test results."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)

        lines = [
            "# Oracle Resilience Pilot Tests - Automated Results",
            "",
            f"**Date**: {__import__('datetime').datetime.now().isoformat()}",
            f"**Total Tests**: {total}",
            f"**Passed**: {passed}",
            f"**Failed**: {total - passed}",
            f"**Pass Rate**: {(passed/total*100):.1f}%",
            "",
            "---",
            "",
            "## Summary Table",
            "",
            "| Test | Tool | Status | Error Code | Suggestions | Top Suggestion |",
            "|------|------|--------|-----------|-------------|-----------------|",
        ]

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            top_sugg = f"{result.top_suggestion} ({result.top_score})" if result.top_suggestion else "N/A"

            lines.append(
                f"| {result.test_name} | {result.tool_name} | {status} | "
                f"{result.error_code or 'N/A'} | {result.suggestion_count} | {top_sugg} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Detailed Results",
            "",
        ])

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.extend([
                f"### {result.test_name}",
                "",
                f"**Status**: {status}",
                f"**Tool**: {result.tool_name}",
                f"**Error Code**: {result.error_code or 'N/A'}",
                f"**Suggestions Count**: {result.suggestion_count}",
            ])

            if result.top_suggestion:
                lines.extend([
                    f"**Top Suggestion**: {result.top_suggestion}",
                    f"**Score**: {result.top_score}",
                ])

            if result.errors:
                lines.append("**Issues**:")
                for error in result.errors:
                    lines.append(f"- {error}")

            if result.raw_response:
                lines.extend([
                    "",
                    "**Raw Response**:",
                    "```json",
                    json.dumps(result.raw_response, indent=2),
                    "```",
                ])

            lines.append("")

        return "\n".join(lines)


async def main():
    """Main entry point."""
    client = OracleTestClient()

    try:
        # Initialize tools
        await client.initialize()

        # Run all tests
        await client.run_all_tests()

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
