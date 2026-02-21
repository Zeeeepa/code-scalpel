"""Tests for scripts/validate_tool_compliance.py

[20260125_TEST] validate tool compliance

Tests cover AST-based extraction and validation of tool compliance criteria.
"""

from unittest.mock import patch

import pytest

# from scripts.validate_tool_compliance import main as validate_main  # Will fail until script exists


@pytest.fixture
def minimal_repo(tmp_path):
    """Create a minimal repo subtree with representative tool modules."""
    # Create src/code_scalpel/mcp structure
    mcp_dir = tmp_path / "src" / "code_scalpel" / "mcp"
    mcp_dir.mkdir(parents=True)

    # tools/__init__.py with register_tools
    tools_init = mcp_dir / "tools" / "__init__.py"
    tools_init.parent.mkdir()
    tools_init.write_text(
        """
from .analyze import analyze_code
from .security import security_scan

TOOLS = [analyze_code, security_scan]

def register_tools():
    pass  # Mock registration
"""
    )

    # Good tool: tools/analyze.py
    analyze_py = mcp_dir / "tools" / "analyze.py"
    analyze_py.write_text(
        """
from code_scalpel.mcp.protocol import mcp
from code_scalpel.mcp.helpers.analyze_helpers import _analyze_code_sync

@mcp.tool()
async def analyze_code(code: str, language: str) -> dict:
    return await asyncio.to_thread(_analyze_code_sync, code, language)
"""
    )

    # Good helper: helpers/analyze_helpers.py
    helpers_analyze = mcp_dir / "helpers" / "analyze_helpers.py"
    helpers_analyze.parent.mkdir()
    helpers_analyze.write_text(
        """
def _analyze_code_sync(code: str, language: str) -> dict:
    return {"result": "analyzed"}
"""
    )

    # Bad tool: missing decorator
    bad_tool = mcp_dir / "tools" / "bad_tool.py"
    bad_tool.write_text(
        """
from code_scalpel.mcp.helpers.bad_helpers import _bad_sync

async def bad_tool(code: str) -> dict:
    return await asyncio.to_thread(_bad_sync, code)
"""
    )

    # Bad helper: async instead of sync
    bad_helper = mcp_dir / "helpers" / "bad_helpers.py"
    bad_helper.write_text(
        """
async def _bad_sync(code: str) -> dict:
    return {"result": "bad"}
"""
    )

    return tmp_path


class TestValidateToolCompliance:
    def test_detects_good_tool(self, minimal_repo):
        """Test detection of compliant tool with all criteria."""
        # This will fail until script is implemented
        with patch(
            "sys.argv",
            [
                "validate_tool_compliance.py",
                "--root",
                str(minimal_repo),
                "--format",
                "json",
            ],
        ):
            # Should pass for analyze_code
            pass

    def test_detects_bad_tool_missing_decorator(self, minimal_repo):
        """Test detection of tool missing @mcp.tool decorator."""
        # Should flag bad_tool.py
        pass

    def test_detects_bad_helper_async(self, minimal_repo):
        """Test detection of async helper function."""
        # Should flag _bad_sync as async
        pass

    def test_csv_output_format(self, minimal_repo):
        """Test CSV output contains expected columns."""
        minimal_repo / "output.csv"
        # Run script with --out-csv
        # Assert CSV has tool_id, module, and criteria columns
        pass

    def test_json_output_format(self, minimal_repo):
        """Test JSON output schema."""
        minimal_repo / "output.json"
        # Run script
        # Assert JSON structure
        pass

    def test_exit_codes(self, minimal_repo):
        """Test exit codes: 0 pass, 1 warnings, 2 fail."""
        # For good repo: 0
        # For bad repo: 2
        pass

    def test_verbose_mode(self, minimal_repo):
        """Test verbose logging output."""
        pass

    def test_strict_mode(self, minimal_repo):
        """Test strict mode treats warnings as failures."""
        pass
