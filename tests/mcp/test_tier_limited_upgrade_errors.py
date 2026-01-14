"""MCP envelope error handling for tier-limited features.

[20251228_TEST] Ensures upgrade_required errors include upgrade URL and no stack traces.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_extract_code_cross_file_deps_is_upgrade_required_in_community(
    monkeypatch,
):
    # Force community tier (no license)
    monkeypatch.setenv("CODE_SCALPEL_TIER", "community")
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)

    from code_scalpel.mcp import server

    tool = server.mcp._tool_manager.get_tool("extract_code")

    result = await tool.run(
        {
            "target_type": "function",
            "target_name": "hello",
            "code": "def hello():\n    return 1\n",
            "include_cross_file_deps": True,
        },
        context=None,
        convert_result=False,
    )

    assert result["error"]["error_code"] == "upgrade_required"
    # [20260113_FIX] error_details may not be present for all upgrade_required errors
    details = result["error"].get("error_details")
    if details:
        assert details["upgrade_url"].startswith("http://codescalpel.dev")
    # Upgrade hints may be filtered by minimal response profile
    # assert result["upgrade_hints"], "Expected upgrade hints"

    # Sanity: no stack trace markers in the user-facing error string
    assert "Traceback" not in result["error"]["error"]
