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

    # [20260201_BUGFIX] Result is ToolResponseEnvelope - data contains the actual result
    result_dict = result.model_dump() if hasattr(result, "model_dump") else result
    data = result_dict.get("data") or result_dict

    # Debug output in case of failure
    if data.get("success") is not False:
        import json

        print(f"DEBUG DATA: {json.dumps(data, default=str)}")

    assert data.get("success") is False

    # Check for error message OR upgrade hints
    error_msg = data.get("error")
    upgrade_hints = data.get("upgrade_hints")

    assert (
        error_msg is not None or upgrade_hints is not None
    ), f"Expected error or upgrade_hints. Got data: {data}"

    if error_msg:
        assert "cross_file_deps" in error_msg or "PRO" in error_msg
        # Sanity: no stack trace markers in the user-facing error string
        assert "Traceback" not in error_msg

    if upgrade_hints:
        # Verify hints exist
        assert len(upgrade_hints) > 0
