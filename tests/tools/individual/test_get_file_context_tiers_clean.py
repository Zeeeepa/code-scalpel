"""Tier gating smoke tests for get_file_context async wrapper."""

import textwrap

import pytest

from code_scalpel.mcp.contract import ToolResponseEnvelope
from code_scalpel.mcp.models.core import FileContextResult
from code_scalpel.mcp.tools.context import get_file_context

# [20251225_TEST] Ensure async wrapper respects tier capabilities


def _caps(max_lines, capabilities):
    return {"limits": {"max_context_lines": max_lines}, "capabilities": capabilities}


@pytest.mark.asyncio
async def test_async_get_file_context_pro(monkeypatch, tmp_path):
    helper = tmp_path / "helper.py"
    helper.write_text("CONST = 1\n")

    target = tmp_path / "target.py"
    target.write_text(
        textwrap.dedent(
            """
            import helper

            def calc(x):
                return helper.CONST + x
            """
        )
    )

    # [20260220_BUGFIX] Patch module-level tier functions directly (both context tool and helpers)
    from code_scalpel.mcp.tools import context as context_module
    from code_scalpel.mcp.helpers import context_helpers

    monkeypatch.setattr(context_module, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(context_helpers, "get_current_tier", lambda: "pro")

    result = await get_file_context(str(target))

    # [20260218_BUGFIX] get_file_context now returns ToolResponseEnvelope; accept both
    assert isinstance(result, (FileContextResult, ToolResponseEnvelope))
    assert result.semantic_summary
    assert result.related_imports
    assert result.expanded_context


@pytest.mark.asyncio
async def test_async_get_file_context_enterprise_redaction(monkeypatch, tmp_path):
    secret = tmp_path / "secret.py"
    secret.write_text("token='AKIA1234567890123456'\nemail='x@y.com'\n")

    # [20260220_BUGFIX] Patch module-level tier functions directly (both context tool and helpers)
    from code_scalpel.mcp.tools import context as context_module
    from code_scalpel.mcp.helpers import context_helpers

    monkeypatch.setattr(context_module, "_get_current_tier", lambda: "enterprise")
    monkeypatch.setattr(context_helpers, "get_current_tier", lambda: "enterprise")

    result = await get_file_context(str(secret))

    # [20260218_BUGFIX] get_file_context now returns ToolResponseEnvelope; accept both
    assert isinstance(result, (FileContextResult, ToolResponseEnvelope))
    assert result.pii_redacted is True
    assert result.secrets_masked is True
    assert result.access_controlled is True
    assert result.redaction_summary
