"""Tier gating smoke tests for selected MCP tools.

These tests intentionally validate only behavior that is actually implemented and
stable (limits + non-marketing messaging).

[20251230_TEST] Replace oversized, speculative tier tests with small smoke tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_get_symbol_references_community_limits(monkeypatch, tmp_path: Path):
    """Community tier applies max_files_searched/max_references without upsell."""
    from code_scalpel.mcp import server

    # Create multiple files that reference the same symbol.
    for idx in range(10):
        (tmp_path / f"m{idx}.py").write_text(
            """\
def target():
    return 1

x = target()
"""
        )

    monkeypatch.setattr(server, "get_current_tier_from_license", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files_searched": 2, "max_references": 3},
            "capabilities": [],
        },
    )

    result = await server.get_symbol_references("target", str(tmp_path))

    assert result.success is True
    assert result.files_truncated is True
    assert result.files_scanned == 2
    assert result.references_truncated is True
    assert len(result.references) == 3
    assert "upgrade" not in (result.truncation_warning or "").lower()
    assert "upgrade" not in (result.file_truncation_warning or "").lower()


@pytest.mark.asyncio
async def test_symbolic_execute_community_truncates_paths(monkeypatch):
    """Community tier enforces max_paths and never suggests upgrading."""
    from code_scalpel.mcp import server

    def _fake_sync(
        code: str,
        max_paths=None,
        max_depth=None,
        constraint_types=None,
        tier=None,
        capabilities=None,
    ):
        return server.SymbolicResult(
            success=True,
            total_paths=10,
            feasible_count=10,
            infeasible_count=0,
            error=None,
            paths_explored=max_paths or 10,
            truncated=(max_paths is not None and max_paths < 10),
            truncation_warning=(
                "Results truncated: output reached the configured maximum path limit."
                if (max_paths is not None and max_paths < 10)
                else None
            ),
            paths=[],
            constraints=[],
        )

    monkeypatch.setattr(server, "_symbolic_execute_sync", _fake_sync)
    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_name, tier: {
            "limits": {"max_paths": 3, "max_depth": 5, "constraint_types": ["int"]},
            "capabilities": {},
        },
    )

    result = await server.symbolic_execute(code="def f(x: int): return x")

    assert result.success is True
    assert result.total_paths == 10
    assert result.paths_explored == 3
    assert result.truncated is True
    assert result.truncation_warning
    assert "upgrade" not in result.truncation_warning.lower()


@pytest.mark.asyncio
async def test_update_symbol_community_forces_backup(monkeypatch, tmp_path: Path):
    """Community tier forces backups when configured as required."""
    import code_scalpel.mcp.server as server

    # Allow operating on tmp_path for this unit test.
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [tmp_path.resolve()], raising=False)

    test_file = tmp_path / "mod.py"
    test_file.write_text(
        """\
def target():
    return 1
"""
    )

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {
                "backup_enabled": True,
                "backup_required": True,
                "validation_level": "syntax",
            },
            "capabilities": {"basic_replacement"},
        },
        raising=False,
    )

    result = await server.update_symbol(
        file_path=str(test_file),
        target_type="function",
        target_name="target",
        new_code="""def target():
    return 2
""",
        create_backup=False,
    )

    assert result.success is True
    assert (tmp_path / "mod.py.bak").exists()
    assert result.backup_path is not None
    assert "upgrade" not in " ".join(result.warnings).lower()
