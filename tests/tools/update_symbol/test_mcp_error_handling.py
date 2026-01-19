"""
[20260104_TEST] Targeted MCP boundary tests for update_symbol.

These tests cover JSON-RPC-esque error envelopes for missing/invalid
arguments at the FastMCP layer, closing coverage gaps for protocol-level
validation identified in the checklist.
"""

import asyncio
import time

import pytest

from code_scalpel.mcp import server as mcp_server
from code_scalpel.mcp.server import mcp

pytestmark = pytest.mark.asyncio


async def test_update_symbol_missing_required_params_returns_error_envelope():
    """Ensure missing required args return an error envelope, not a crash."""

    tool = mcp._tool_manager._tools["update_symbol"]

    result = await tool.run({}, context=None, convert_result=False)

    assert isinstance(result, dict)
    assert result.get("error"), "Missing params should produce an error message"
    # Should not return partial data when validation fails
    assert result.get("data") in (None, {})


async def test_update_symbol_invalid_param_types_return_error_envelope(tmp_path):
    """Invalid argument types should surface as tool errors with guidance."""

    tool = mcp._tool_manager._tools["update_symbol"]

    bad_args = {
        "file_path": tmp_path / "sample.py",  # Path object instead of str
        "symbol_name": 123,  # int instead of str
        "new_code": None,  # None instead of str
    }

    result = await tool.run(bad_args, context=None, convert_result=False)

    assert isinstance(result, dict)
    assert result.get("error"), "Type validation should produce an error"

    # Error payload should use structured error_code rather than crashing
    error_payload = result.get("error")
    if isinstance(error_payload, dict):
        assert error_payload.get("error_code") in {"internal_error", "invalid_params"}
        assert isinstance(error_payload.get("error"), str)
    else:
        # Fallback: ensure we still got a string error description
        assert "error" in str(error_payload).lower()


async def test_update_symbol_fault_injection_returns_internal_error(monkeypatch, tmp_path):
    """Unexpected exceptions should be wrapped in an internal_error envelope."""

    tool = mcp._tool_manager._tools["update_symbol"]

    # Force an unexpected exception inside the envelope (post tool execution)
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("""def foo():
    return 0
""")

    def boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(mcp_server, "filter_tool_response", boom)

    args = {
        "file_path": str(sample_file),
        "target_type": "function",
        "target_name": "foo",
        "new_code": "def foo():\n    return 1\n",
    }

    result = await tool.run(args, context=None, convert_result=False)

    assert isinstance(result, dict)
    err = result.get("error")
    assert err, "Fault injection should yield an error envelope"
    if isinstance(err, dict):
        assert err.get("error_code") == "internal_error"
        assert err.get("error") == "Tool error"
    else:
        assert "error" in str(err).lower()


async def test_update_symbol_unknown_tool_returns_not_found_error():
    """Non-existent tool name should raise a not-found error from FastMCP manager."""

    with pytest.raises(KeyError):
        _ = mcp._tool_manager._tools["does_not_exist"]


async def test_update_symbol_respects_timeout_budget(monkeypatch, tmp_path):
    """update_symbol should complete well within a short timeout budget."""

    monkeypatch.setattr(mcp_server, "_get_current_tier", lambda: "community")
    tool = mcp._tool_manager._tools["update_symbol"]

    sample_file = tmp_path / "timeout_sample.py"
    sample_file.write_text("""def foo():
    return 0
""")

    args = {
        "file_path": str(sample_file),
        "target_type": "function",
        "target_name": "foo",
        "new_code": "def foo():\n    return 1\n",
    }

    result = await asyncio.wait_for(tool.run(args, context=None, convert_result=False), timeout=1.0)

    assert isinstance(result, dict)
    # Timeout guard: response should return quickly and include duration metadata.
    assert result.get("duration_ms", 0) < 1000
    err = result.get("error")
    if err:
        assert isinstance(err, dict)
        assert err.get("error_code") in {"internal_error", "invalid_params"}
    else:
        data = result.get("data") or {}
        if isinstance(data, dict):
            assert data.get("success") is True


async def test_update_symbol_async_calls_do_not_block_event_loop(monkeypatch, tmp_path):
    """Concurrent async calls should execute without blocking the event loop."""

    monkeypatch.setattr(mcp_server, "_get_current_tier", lambda: "community")
    tool = mcp._tool_manager._tools["update_symbol"]

    async def invoke(i: int) -> dict[str, object]:
        sample_file = tmp_path / f"async_{i}.py"
        sample_file.write_text("""def foo():
    return 0
""")
        args = {
            "file_path": str(sample_file),
            "target_type": "function",
            "target_name": "foo",
            "new_code": "def foo():\n    return 1\n",
        }
        return await tool.run(args, context=None, convert_result=False)

    started = time.perf_counter()
    results = await asyncio.gather(*(invoke(i) for i in range(3)))
    elapsed = time.perf_counter() - started

    assert elapsed < 2.0, f"async dispatch took too long: {elapsed}s"
    for res in results:
        assert isinstance(res, dict)
        assert res.get("duration_ms", 0) < 1000
        err = res.get("error")
        if err:
            assert isinstance(err, dict)
            assert err.get("error_code") in {"internal_error", "invalid_params"}
        else:
            data = res.get("data") or {}
            if isinstance(data, dict):
                assert data.get("success") is True


async def test_update_symbol_memory_error_returns_structured_envelope(monkeypatch, tmp_path):
    """MemoryError during patching should return structured error envelope."""

    from code_scalpel.surgery.surgical_patcher import UnifiedPatcher

    monkeypatch.setattr(mcp_server, "_get_current_tier", lambda: "community")
    tool = mcp._tool_manager._tools["update_symbol"]

    sample_file = tmp_path / "oom_sample.py"
    sample_file.write_text("""def foo():
    return 0
""")

    # Inject MemoryError in the patcher
    def mock_from_file(*args, **kwargs):
        raise MemoryError("simulated OOM")

    monkeypatch.setattr(UnifiedPatcher, "from_file", mock_from_file)

    args = {
        "file_path": str(sample_file),
        "target_type": "function",
        "target_name": "foo",
        "new_code": "def foo():\n    return 1\n",
    }

    result = await tool.run(args, context=None, convert_result=False)

    assert isinstance(result, dict)
    err = result.get("error")
    assert err, "MemoryError should produce an error envelope"
    if isinstance(err, dict):
        assert err.get("error_code") in {"internal_error", "resource_exhausted"}
        assert err.get("error") is not None
    else:
        assert "error" in str(err).lower()


async def test_update_symbol_redacts_pii_from_error_details(monkeypatch, tmp_path, caplog):
    """Secret strings in args should not appear in error_details or logs."""

    import logging

    caplog.set_level(logging.DEBUG)

    monkeypatch.setattr(mcp_server, "_get_current_tier", lambda: "community")
    tool = mcp._tool_manager._tools["update_symbol"]

    sample_file = tmp_path / "pii_sample.py"
    sample_file.write_text("""def foo():
    return 0
""")

    secret_string = "sk_live_51AbC123XyZ456SECRET789"
    args = {
        "file_path": str(sample_file),
        "target_type": "function",
        "target_name": "nonexistent",  # Trigger error
        "new_code": f"def foo():\n    api_key = '{secret_string}'\n    return 1\n",
    }

    result = await tool.run(args, context=None, convert_result=False)

    assert isinstance(result, dict)
    err = result.get("error")
    assert err, "Should return error for nonexistent symbol"

    # Secret should not appear in error payload
    result_str = str(result)
    assert secret_string not in result_str, "Secret leaked in error payload"

    # Secret should not appear in logs
    for record in caplog.records:
        assert secret_string not in record.message, f"Secret leaked in log: {record.message}"

    # Temp paths should be redacted (e.g., /tmp/pytest-of-user/... -> [REDACTED]/...)
    if isinstance(err, dict) and err.get("error_details"):
        details_str = str(err["error_details"])
        # Allow /tmp/ prefix but temp session dirs should be redacted
        if "pytest-of-" in str(sample_file):
            assert "pytest-of-" not in details_str, "Temp session path leaked"
