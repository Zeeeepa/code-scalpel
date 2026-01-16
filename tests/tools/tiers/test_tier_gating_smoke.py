"""Tier gating smoke tests for selected MCP tools.

These tests intentionally validate only behavior that is actually implemented and
stable (limits + non-marketing messaging).

[20251230_TEST] Replace oversized, speculative tier tests with small smoke tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import code_scalpel.licensing.tier_detector
import code_scalpel.licensing.features
import code_scalpel.mcp.path_resolver
import code_scalpel.mcp.helpers.symbolic_helpers
from code_scalpel.mcp.tools import referencing
from code_scalpel.mcp.tools import execution
from code_scalpel.mcp.tools import extraction
from code_scalpel.mcp.tools import security
from code_scalpel.mcp.models.execution import SymbolicResult


@pytest.mark.asyncio
async def test_get_symbol_references_community_limits(monkeypatch, tmp_path: Path):
    """Community tier applies max_files_searched/max_references without upsell."""

    # Create multiple files that reference the same symbol.
    for idx in range(10):
        (tmp_path / f"m{idx}.py").write_text(
            """def target():
    return 1

x = target()
"""
        )

    monkeypatch.setattr(code_scalpel.licensing.tier_detector, "get_current_tier", lambda: "community")
    monkeypatch.setattr(
        code_scalpel.licensing.features,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files_searched": 2, "max_references": 3},
            "capabilities": [],
        },
    )

    result = await referencing.get_symbol_references("target", str(tmp_path))

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

    def _fake_sync(
        code: str,
        max_paths=None,
        max_depth=None,
        constraint_types=None,
        tier=None,
        capabilities=None,
    ):
        return SymbolicResult(
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

    monkeypatch.setattr(code_scalpel.mcp.helpers.symbolic_helpers, "_symbolic_execute_sync", _fake_sync)
    monkeypatch.setattr(code_scalpel.licensing.tier_detector, "get_current_tier", lambda: "community")
    monkeypatch.setattr(
        code_scalpel.licensing.features,
        "get_tool_capabilities",
        lambda tool_name, tier: {
            "limits": {"max_paths": 3, "max_depth": 5, "constraint_types": ["int"]},
            "capabilities": {},
        },
    )

    result = await execution.symbolic_execute(code="def f(x: int): return x")

    assert result.success is True
    assert result.total_paths == 10
    assert result.paths_explored == 3
    assert result.truncated is True
    assert result.truncation_warning


@pytest.mark.asyncio
async def test_update_symbol_community_forces_backup(monkeypatch, tmp_path: Path):
    """Community tier forces backups when configured as required."""

    # Allow operating on tmp_path for this unit test.
    monkeypatch.setattr(code_scalpel.mcp.path_resolver, "ALLOWED_ROOTS", [tmp_path.resolve()], raising=False)

    test_file = tmp_path / "mod.py"
    test_file.write_text(
        """def target():
    return 1
"""
    )

    monkeypatch.setattr(code_scalpel.licensing.tier_detector, "get_current_tier", lambda: "community")
    monkeypatch.setattr(
        code_scalpel.licensing.features,
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

    result = await extraction.update_symbol(
        file_path=str(test_file),
        target_type="function",
        target_name="target",
        new_code="""def target():
    return 2
""",
        create_backup=False,
    )

    assert result.success is True
    # Verification that backup created
    assert (tmp_path / "mod.py.bak").exists()


@pytest.mark.asyncio
async def test_type_evaporation_scan_community_limits(monkeypatch):
    """Community tier enforces frontend-only analysis, max 50 files, no Pro features.

    [20260111_TEST] Added tier gating smoke test for type_evaporation_scan.
    Validates Community tier is frontend-only and Pro features (cross_file_issues,
    implicit_any, network_boundaries) are gated.
    """

    # TypeScript frontend with type evaporation vulnerability
    frontend_code = """type Role = 'admin' | 'user';
const role = input.value as Role;  // Unsafe type assertion
fetch('/api/user', {body: JSON.stringify({role})});
"""

    # Python backend with unvalidated input
    backend_code = """role = request.get_json()['role']  # No validation!
if role == 'admin':
    grant_admin_access()
"""

    monkeypatch.setattr(code_scalpel.licensing.tier_detector, "get_current_tier", lambda: "community")
    monkeypatch.setattr(
        code_scalpel.licensing.features,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files": 50, "frontend_only": True},
            "capabilities": {
                "explicit_any_detection",
                "typescript_any_scanning",
                "basic_type_check",
            },
        },
    )

    result = await security.type_evaporation_scan(
        frontend_code=frontend_code,
        backend_code=backend_code,
    )

    # Verify tool returns success
    assert result.success is True
    # Community should only find frontend vulnerability
    assert result.frontend_vulnerabilities == 1
    # Backend analysis should be skipped/limited
    assert result.backend_vulnerabilities == 0
    # Cross-file should be disabled
    assert result.cross_file_issues == 0
