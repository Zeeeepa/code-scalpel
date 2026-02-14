"""MCP envelope error handling for tier-limited features.

[20251228_TEST] Ensures upgrade_required errors include upgrade URL and no stack traces.
[20260212_TEST] Community max_depth=1 but include_cross_file_deps remains gated to Pro+.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_extract_code_cross_file_deps_is_upgrade_required_in_community(
    monkeypatch,
):
    """Community tier blocks cross_file_deps (gated separately from max_depth).

    [20260212_TEST] include_cross_file_deps=false in community limits.toml,
    so requesting cross-file deps should still return an upgrade error.
    """
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

    # [20260201_BUGFIX] Result is ToolResponseEnvelope - data contains the actual result
    result_dict = result.model_dump() if hasattr(result, "model_dump") else result
    data = result_dict.get("data") or result_dict

    assert (
        data.get("success") is False
    ), f"Community should block cross_file_deps. Got: {data}"

    # Check for error message about cross_file_deps requiring Pro
    error_msg = data.get("error")
    assert error_msg is not None, f"Expected error message. Got data: {data}"
    assert "cross_file_deps" in error_msg or "PRO" in error_msg
    # Sanity: no stack trace markers in the user-facing error string
    assert "Traceback" not in error_msg
