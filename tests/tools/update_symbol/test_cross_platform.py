# [20260104_TEST] Cross-platform smoke tests for update_symbol
"""
Cross-platform compatibility tests:
- Tool registry loads on different platforms
- Minimal update_symbol call returns envelope on all platforms
- Python version compatibility assertions
"""

import pytest
import sys


@pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
class TestCrossPlatformSmoke:
    """Smoke tests across different platforms."""
    
    async def test_tool_registry_loads_on_platform(self, platform):
        """Tool registry loads successfully on each platform."""
        if sys.platform != platform:
            pytest.skip(f"Skipping {platform} test on {sys.platform}")
        
        from code_scalpel.mcp.server import mcp
        
        # Tool registry should load
        assert "update_symbol" in mcp._tool_manager._tools
        tool = mcp._tool_manager._tools["update_symbol"]
        assert tool is not None
    
    async def test_minimal_update_returns_envelope_on_platform(self, platform, tmp_path):
        """Minimal update_symbol call returns MCP envelope on each platform."""
        if sys.platform != platform:
            pytest.skip(f"Skipping {platform} test on {sys.platform}")
        
        from code_scalpel.mcp.server import mcp
        
        tool = mcp._tool_manager._tools["update_symbol"]
        
        sample_file = tmp_path / "platform_test.py"
        sample_file.write_text("""def foo():
    return 0
""")
        
        args = {
            "file_path": str(sample_file),
            "target_type": "function",
            "target_name": "foo",
            "new_code": "def foo():\n    return 1\n",
        }
        
        result = await tool.run(args, context=None, convert_result=False)
        
        # Should return MCP envelope structure
        assert isinstance(result, dict)
        assert "capabilities" in result
        assert "envelope-v1" in result.get("capabilities", [])
        assert "duration_ms" in result
        # May succeed or error depending on platform path handling
        assert result.get("error") is not None or result.get("data") is not None


@pytest.mark.parametrize("python_version", ["3.10", "3.11", "3.12"])
class TestPythonVersionCompatibility:
    """Tests across different Python versions."""
    
    async def test_tool_loads_on_python_version(self, python_version):
        """Tool loads on different Python minor versions."""
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version != python_version:
            pytest.skip(f"Skipping Python {python_version} test on {current_version}")
        
        from code_scalpel.mcp.server import mcp
        
        # Tool should load on supported Python versions
        assert "update_symbol" in mcp._tool_manager._tools
    
    async def test_envelope_structure_consistent_across_versions(self, python_version, tmp_path):
        """MCP envelope structure is consistent across Python versions."""
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version != python_version:
            pytest.skip(f"Skipping Python {python_version} test on {current_version}")
        
        from code_scalpel.mcp.server import mcp
        
        tool = mcp._tool_manager._tools["update_symbol"]
        
        sample_file = tmp_path / "version_test.py"
        sample_file.write_text("""def foo():
    return 0
""")
        
        args = {
            "file_path": str(sample_file),
            "target_type": "function",
            "target_name": "foo",
            "new_code": "def foo():\n    return 1\n",
        }
        
        result = await tool.run(args, context=None, convert_result=False)
        
        # Envelope structure should be consistent
        assert isinstance(result, dict)
        assert "tier" in result
        assert "tool_version" in result
        assert "tool_id" in result
        assert result["tool_id"] == "update_symbol"
        assert "request_id" in result
        assert "capabilities" in result
        assert "duration_ms" in result
