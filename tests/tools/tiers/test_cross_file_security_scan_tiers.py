from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _make_python_deep_chain_project(root: Path, package_dir: str = "proj") -> Path:
    """Create a small Python package with a deep call chain to a SQL sink."""
    pkg = root / package_dir
    pkg.mkdir(parents=True, exist_ok=True)
    _write(pkg / "__init__.py", "# test package\n")

    # Source module: introduces tainted data via request.args.get.
    _write(
        pkg / "routes.py",
        """\
from flask import request
from .s1 import s1

def handler():
    q = request.args.get('q', '')
    return s1(q)
""",
    )

    # Deep chain: s1 -> s2 -> s3 -> s4 -> db.run_query
    _write(pkg / "s1.py", "from .s2 import s2\n\ndef s1(q):\n    return s2(q)\n")
    _write(pkg / "s2.py", "from .s3 import s3\n\ndef s2(q):\n    return s3(q)\n")
    _write(pkg / "s3.py", "from .s4 import s4\n\ndef s3(q):\n    return s4(q)\n")
    _write(
        pkg / "s4.py",
        "from .db import run_query\n\ndef s4(q):\n    return run_query(q)\n",
    )

    _write(
        pkg / "db.py",
        """\
import sqlite3

def run_query(user_supplied: str) -> str:
    sql = f\"SELECT * FROM users WHERE name = '{user_supplied}'\"
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()
    return sql
""",
    )

    return pkg


# ============================================================================
# [20260111_TEST] v1.0 validation - Output metadata field tests
# ============================================================================


class TestOutputMetadataFields:
    """Test that output metadata fields are present and correctly populated."""

    async def test_metadata_fields_exist_on_model(self):
        """CrossFileSecurityResult should define all metadata fields."""
        from code_scalpel.mcp.server import CrossFileSecurityResult

        fields = CrossFileSecurityResult.model_fields

        # Check all metadata fields exist
        assert "tier_applied" in fields
        assert "max_depth_applied" in fields
        assert "max_modules_applied" in fields
        assert "framework_aware_enabled" in fields
        assert "enterprise_features_enabled" in fields

    async def test_metadata_fields_have_defaults(self):
        """Metadata fields should have sensible defaults."""
        from code_scalpel.mcp.server import CrossFileSecurityResult

        result = CrossFileSecurityResult(success=True)

        # Verify defaults are applied
        assert result.tier_applied == "community"  # Default tier
        assert result.max_depth_applied is None  # No limit by default
        assert result.max_modules_applied is None  # No limit by default
        assert result.framework_aware_enabled is False  # Disabled by default
        assert result.enterprise_features_enabled is False  # Disabled by default

    async def test_community_tier_metadata(self, tmp_path: Path, monkeypatch):
        """Community tier should report correct metadata."""
        from code_scalpel.mcp import server

        monkeypatch.setattr(server, "_get_current_tier", lambda: "community")

        root = tmp_path / "repo"
        root.mkdir()
        _make_python_deep_chain_project(root)

        from code_scalpel.mcp.server import cross_file_security_scan

        r = await cross_file_security_scan(
            project_root=str(root),
            max_depth=50,
            max_modules=999,
        )

        assert r.success is True
        assert r.tier_applied == "community"
        assert r.max_depth_applied == 3
        assert r.max_modules_applied == 10
        assert r.framework_aware_enabled is False
        assert r.enterprise_features_enabled is False

    async def test_pro_tier_metadata(self, tmp_path: Path, monkeypatch):
        """Pro tier should report correct metadata."""
        from code_scalpel.mcp import server

        monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

        root = tmp_path / "repo"
        root.mkdir()
        _make_python_deep_chain_project(root)

        from code_scalpel.mcp.server import cross_file_security_scan

        r = await cross_file_security_scan(
            project_root=str(root),
            max_depth=50,
            max_modules=999,
        )

        assert r.success is True
        assert r.tier_applied == "pro"
        assert r.max_depth_applied == 10
        assert r.max_modules_applied == 100
        assert r.framework_aware_enabled is True
        assert r.enterprise_features_enabled is False

    async def test_enterprise_tier_metadata(self, tmp_path: Path, monkeypatch):
        """Enterprise tier should report correct metadata."""
        from code_scalpel.mcp import server

        monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")

        root = tmp_path / "repo"
        root.mkdir()
        _make_python_deep_chain_project(root)

        from code_scalpel.mcp.server import cross_file_security_scan

        r = await cross_file_security_scan(
            project_root=str(root),
            max_depth=50,
            max_modules=999,
        )

        assert r.success is True
        assert r.tier_applied == "enterprise"
        assert r.max_depth_applied is None  # Unlimited
        assert r.max_modules_applied is None  # Unlimited
        assert r.framework_aware_enabled is True
        assert r.enterprise_features_enabled is True


# ============================================================================
# Original tier enforcement tests
# ============================================================================


async def test_cross_file_security_scan_community_enforces_depth_cap(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CODE_SCALPEL_TIER", "community")

    root = tmp_path / "repo"
    root.mkdir()
    _make_python_deep_chain_project(root)

    # Capture the effective limits passed into the underlying tracker.
    from code_scalpel.security.analyzers.cross_file_taint import CrossFileTaintTracker

    state: dict[str, object] = {}
    orig_init = CrossFileTaintTracker.__init__
    orig_analyze = CrossFileTaintTracker.analyze

    def _init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        state["tracker"] = self

    def _analyze(self, *args, **kwargs):
        state["effective_max_depth"] = kwargs.get("max_depth")
        state["effective_max_modules"] = kwargs.get("max_modules")
        return orig_analyze(self, *args, **kwargs)

    monkeypatch.setattr(CrossFileTaintTracker, "__init__", _init)
    monkeypatch.setattr(CrossFileTaintTracker, "analyze", _analyze)

    from code_scalpel.mcp.server import cross_file_security_scan

    r = await cross_file_security_scan(
        project_root=str(root),
        entry_points=["proj/routes.py"],
        max_depth=50,
        include_diagram=False,
        timeout_seconds=10.0,
        max_modules=999,
    )

    assert r.success is True
    assert state["effective_max_depth"] == 3
    assert state["effective_max_modules"] == 10


async def test_cross_file_security_scan_pro_finds_deep_chain_vuln(tmp_path: Path, monkeypatch):
    # [20250108_BUGFIX] Mock _get_current_tier directly since env var only allows downgrade
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

    root = tmp_path / "repo"
    root.mkdir()
    _make_python_deep_chain_project(root)

    from code_scalpel.mcp.server import cross_file_security_scan

    r = await cross_file_security_scan(
        project_root=str(root),
        entry_points=["proj/routes.py"],
        max_depth=50,
        include_diagram=False,
        timeout_seconds=10.0,
        max_modules=999,
    )

    assert r.success is True
    assert r.has_vulnerabilities is True
    assert r.vulnerability_count >= 1
    assert any(v.cwe == "CWE-89" for v in r.vulnerabilities)


async def test_cross_file_security_scan_pro_clamps_limits(tmp_path: Path, monkeypatch):
    # [20250108_BUGFIX] Mock _get_current_tier directly since env var only allows downgrade
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

    root = tmp_path / "repo"
    root.mkdir()
    _make_python_deep_chain_project(root)

    from code_scalpel.security.analyzers.cross_file_taint import CrossFileTaintTracker

    state: dict[str, object] = {}
    orig_analyze = CrossFileTaintTracker.analyze

    def _analyze(self, *args, **kwargs):
        state["effective_max_depth"] = kwargs.get("max_depth")
        state["effective_max_modules"] = kwargs.get("max_modules")
        return orig_analyze(self, *args, **kwargs)

    monkeypatch.setattr(CrossFileTaintTracker, "analyze", _analyze)

    from code_scalpel.mcp.server import cross_file_security_scan

    r = await cross_file_security_scan(
        project_root=str(root),
        entry_points=["proj/routes.py"],
        max_depth=50,
        include_diagram=False,
        timeout_seconds=10.0,
        max_modules=999,
    )

    assert r.success is True
    assert state["effective_max_depth"] == 10
    assert state["effective_max_modules"] == 100


async def test_cross_file_security_scan_enterprise_returns_extra_fields(
    tmp_path: Path, monkeypatch
):
    # [20250108_BUGFIX] Mock _get_current_tier directly since env var only allows downgrade
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")

    root = tmp_path / "repo"
    root.mkdir()

    # Put the package under a directory named 'frontend' to exercise global flow heuristics.
    pkg_root = root / "frontend"
    pkg_root.mkdir()
    _make_python_deep_chain_project(pkg_root, package_dir="proj")

    # Add a TSX file containing useContext to trigger framework context scanning.
    _write(
        pkg_root / "ui.tsx",
        "import { useContext } from 'react';\nexport const x = () => useContext(null);\n",
    )

    from code_scalpel.mcp.server import cross_file_security_scan

    r = await cross_file_security_scan(
        project_root=str(root),
        entry_points=["frontend/proj/routes.py"],
        max_depth=50,
        include_diagram=False,
        timeout_seconds=10.0,
        max_modules=999,
    )

    assert r.success is True
    assert r.has_vulnerabilities is True

    # Enterprise should populate at least some tier-gated extras when heuristics match.
    assert r.framework_contexts is not None
    assert any(ctx.get("framework") == "react" for ctx in r.framework_contexts)

    assert r.dependency_chains is not None
    assert r.confidence_scores is not None

    # Global flow hints are best-effort; ensure the field exists and is list-or-None.
    assert r.global_flows is None or isinstance(r.global_flows, list)
    assert r.microservice_boundaries is None or isinstance(r.microservice_boundaries, list)
    assert r.distributed_trace is None or isinstance(r.distributed_trace, dict)
