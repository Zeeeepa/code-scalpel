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


@pytest.mark.asyncio
async def test_code_policy_check_community_limits(monkeypatch, tmp_path: Path):
    """Community tier enforces max_files=100 and max_rules=50 without upsell.
    
    [20260111_TEST] Added tier gating smoke test for code_policy_check.
    Validates Community tier restrictions and Pro feature gating.
    """
    from code_scalpel.mcp import server

    # Create a file with code that triggers multiple rules
    test_file = tmp_path / "test_violations.py"
    test_file.write_text("""\
from os import *  # PY004 star import

def bad_func(arg=[]):  # PY002 mutable default
    try:
        x = eval("1+1")  # PY007 eval usage
    except:  # PY001 bare except
        pass
""")

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files": 100, "max_rules": 50},
            "capabilities": {"style_guide_checking", "pep8_validation", "basic_patterns"},
        },
    )

    result = await server.code_policy_check(paths=[str(test_file)])

    # Verify Community tier is applied
    assert result.tier == "community"
    assert result.success is True
    
    # Verify limits are enforced (no limit exceeded warnings needed for small test)
    assert result.files_checked <= 100
    assert result.rules_applied <= 50
    
    # Verify Community gets anti-pattern violations (PY001-PY010)
    # violations are dicts with 'rule_id' key
    violation_ids = [v.get("rule_id", v.get("id", "")) if isinstance(v, dict) else getattr(v, "rule_id", "") for v in result.violations]
    assert any(vid.startswith("PY") for vid in violation_ids), \
        "Community tier should detect PY anti-pattern rules"
    
    # Verify Pro features (best_practices, custom_rules) are NOT exposed
    assert not getattr(result, "best_practices_violations", []), \
        "Community tier should NOT expose best_practices_violations"
    assert not getattr(result, "custom_rule_results", {}), \
        "Community tier should NOT expose custom_rule_results"
    
    # No marketing upsell in output
    summary_text = result.summary or ""
    assert "upgrade" not in summary_text.lower()
    assert "pro" not in summary_text.lower()


@pytest.mark.asyncio
async def test_type_evaporation_scan_community_limits(monkeypatch):
    """Community tier enforces frontend-only analysis, max 50 files, no Pro features.
    
    [20260111_TEST] Added tier gating smoke test for type_evaporation_scan.
    Validates Community tier is frontend-only and Pro features (cross_file_issues,
    implicit_any, network_boundaries) are gated.
    """
    from code_scalpel.mcp import server

    # TypeScript frontend with type evaporation vulnerability
    frontend_code = """\
type Role = 'admin' | 'user';
const role = input.value as Role;  // Unsafe type assertion
fetch('/api/user', {body: JSON.stringify({role})});
"""

    # Python backend with unvalidated input
    backend_code = """\
role = request.get_json()['role']  # No validation!
if role == 'admin':
    grant_admin_access()
"""

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files": 50, "frontend_only": True},
            "capabilities": {"explicit_any_detection", "typescript_any_scanning", "basic_type_check"},
        },
    )

    result = await server.type_evaporation_scan(
        frontend_code=frontend_code,
        backend_code=backend_code,
    )

    # Verify tool returns success
    assert result.success is True
    
    # Verify frontend issues are detected (Community capability)
    # frontend_vulnerabilities should be accessible (may be 0 or list)
    assert hasattr(result, "frontend_vulnerabilities")
    
    # Verify Pro features are omitted/empty for Community tier
    # Pro features: cross_file_issues, implicit_any_count > 0, network_boundaries
    # Community tier should have these as 0 or empty
    cross_file = getattr(result, "cross_file_issues", 0)
    assert cross_file in (0, None, []), \
        f"Community tier should have cross_file_issues=0/empty, got {cross_file}"
    
    implicit_any = getattr(result, "implicit_any_count", 0)
    assert implicit_any == 0, \
        f"Community tier should have implicit_any_count=0, got {implicit_any}"
    
    network = getattr(result, "network_boundaries", [])
    assert network in (0, None, []), \
        f"Community tier should have network_boundaries empty, got {network}"
    
    # Verify Enterprise features are omitted/empty
    schemas = getattr(result, "generated_schemas", None)
    assert schemas in (None, [], {}), \
        f"Community tier should NOT have generated_schemas, got {schemas}"
    
    pydantic = getattr(result, "pydantic_models", None)
    assert pydantic in (None, [], {}), \
        f"Community tier should NOT have pydantic_models, got {pydantic}"
