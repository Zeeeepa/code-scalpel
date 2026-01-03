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


async def test_cross_file_security_scan_community_enforces_depth_cap(
    tmp_path: Path, monkeypatch
):
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


async def test_cross_file_security_scan_pro_finds_deep_chain_vuln(
    tmp_path: Path, monkeypatch
):
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
    assert r.microservice_boundaries is None or isinstance(
        r.microservice_boundaries, list
    )
    assert r.distributed_trace is None or isinstance(r.distributed_trace, dict)
