"""Governance budget enforcement tests.

[20251231_TEST] Ensure change budgets are enforced at the MCP boundary for
write tools (update_symbol, rename_symbol) using tier-derived governance.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _write_budget_yaml(
    policy_dir: Path, *, max_total_lines: int = 1, max_files: int = 1
) -> None:
    (policy_dir / "budget.yaml").write_text(
        """budgets:
  default:
    max_files: {max_files}
    max_lines_per_file: 100
    max_total_lines: {max_total_lines}
    max_complexity_increase: 100
    allowed_file_patterns: ["*.py"]
    forbidden_paths: [".git/", "node_modules/", "__pycache__/"]
""".format(
            max_total_lines=max_total_lines, max_files=max_files
        ),
        encoding="utf-8",
    )


@pytest.mark.anyio
async def test_pro_block_mode_denies_update_symbol_when_budget_exceeded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    policy_dir = tmp_path / ".code-scalpel"
    policy_dir.mkdir(parents=True, exist_ok=True)
    _write_budget_yaml(policy_dir, max_total_lines=1)

    target_file = tmp_path / "app.py"
    target_file.write_text(
        """def f():
    return 1
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCALPEL_GOVERNANCE_ENFORCEMENT", "block")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_FEATURES", "budget")

    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [])

    tool = server.mcp._tool_manager.get_tool("update_symbol")
    result = await tool.run(
        {
            "file_path": str(target_file),
            "target_type": "function",
            "target_name": "f",
            "new_code": """def f():\n    x = 1\n    y = 2\n    return x + y\n""",
            "operation": "replace",
            "new_name": None,
            "create_backup": False,
        },
        context=None,
        convert_result=False,
    )

    assert result["tool_id"] == "update_symbol"
    assert result["error"] is not None
    assert result["error"]["error_code"] == "forbidden"

    # Ensure file was not modified.
    assert (
        target_file.read_text(encoding="utf-8")
        == """def f():
    return 1
"""
    )


@pytest.mark.anyio
async def test_pro_block_mode_emits_audit_event_on_budget_deny(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """[20251231_TEST] Budget blocks should produce an audit.jsonl entry."""
    monkeypatch.chdir(tmp_path)

    policy_dir = tmp_path / ".code-scalpel"
    policy_dir.mkdir(parents=True, exist_ok=True)
    _write_budget_yaml(policy_dir, max_total_lines=0)

    target_file = tmp_path / "app.py"
    target_file.write_text(
        """def f():
    return 1
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCALPEL_GOVERNANCE_ENFORCEMENT", "block")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_FEATURES", "budget")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_AUDIT", "1")

    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [])

    tool = server.mcp._tool_manager.get_tool("update_symbol")
    result = await tool.run(
        {
            "file_path": str(target_file),
            "target_type": "function",
            "target_name": "f",
            "new_code": """def f():\n    x = 1\n    return x\n""",
            "operation": "replace",
            "new_name": None,
            "create_backup": False,
        },
        context=None,
        convert_result=False,
    )

    assert result["tool_id"] == "update_symbol"
    assert result["error"] is not None
    assert result["error"]["error_code"] == "forbidden"

    audit_path = policy_dir / "audit.jsonl"
    assert audit_path.exists()

    lines = [
        ln for ln in audit_path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    assert lines
    last = json.loads(lines[-1])
    assert last["tool_id"] == "update_symbol"
    assert last["tier"] == "pro"
    assert last["check"] == "budget"
    assert last["decision"] == "deny"


@pytest.mark.anyio
async def test_pro_warn_mode_allows_update_symbol_with_break_glass_and_warning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    policy_dir = tmp_path / ".code-scalpel"
    policy_dir.mkdir(parents=True, exist_ok=True)
    _write_budget_yaml(policy_dir, max_total_lines=1)

    target_file = tmp_path / "app.py"
    target_file.write_text(
        """def f():
    return 1
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCALPEL_GOVERNANCE_ENFORCEMENT", "warn")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_BREAK_GLASS", "1")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_FEATURES", "budget")

    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [])

    tool = server.mcp._tool_manager.get_tool("update_symbol")
    result = await tool.run(
        {
            "file_path": str(target_file),
            "target_type": "function",
            "target_name": "f",
            "new_code": """def f():\n    x = 1\n    y = 2\n    return x + y\n""",
            "operation": "replace",
            "new_name": None,
            "create_backup": False,
        },
        context=None,
        convert_result=False,
    )

    assert result["tool_id"] == "update_symbol"
    assert result["error"] is None
    assert isinstance(result.get("warnings"), list)
    assert any("Governance WARN" in w for w in result["warnings"])

    # Ensure file was modified.
    assert "return x + y" in target_file.read_text(encoding="utf-8")


@pytest.mark.anyio
async def test_pro_block_mode_denies_rename_symbol_when_budget_exceeded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    policy_dir = tmp_path / ".code-scalpel"
    policy_dir.mkdir(parents=True, exist_ok=True)
    # Disallow any line changes.
    _write_budget_yaml(policy_dir, max_total_lines=0)

    target_file = tmp_path / "app.py"
    target_file.write_text(
        """def f():
    return 1
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCALPEL_GOVERNANCE_ENFORCEMENT", "block")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_FEATURES", "budget")

    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [])

    tool = server.mcp._tool_manager.get_tool("rename_symbol")
    result = await tool.run(
        {
            "file_path": str(target_file),
            "target_type": "function",
            "target_name": "f",
            "new_name": "g",
            "create_backup": False,
        },
        context=None,
        convert_result=False,
    )

    assert result["tool_id"] == "rename_symbol"
    assert result["error"] is not None
    assert result["error"]["error_code"] == "forbidden"

    # Ensure file was not modified.
    assert "def f" in target_file.read_text(encoding="utf-8")


@pytest.mark.anyio
async def test_pro_block_mode_denies_cross_file_rename_when_budget_max_files_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    policy_dir = tmp_path / ".code-scalpel"
    policy_dir.mkdir(parents=True, exist_ok=True)
    # Allow plenty of line changes but only one file per operation.
    _write_budget_yaml(policy_dir, max_total_lines=1000, max_files=1)

    a_py = tmp_path / "a.py"
    a_py.write_text(
        """def f():
    return 1
""",
        encoding="utf-8",
    )

    b_py = tmp_path / "b.py"
    b_py.write_text(
        """from a import f


def g():
    return f()
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("SCALPEL_GOVERNANCE_ENFORCEMENT", "block")
    monkeypatch.setenv("SCALPEL_GOVERNANCE_FEATURES", "budget")

    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [])

    tool = server.mcp._tool_manager.get_tool("rename_symbol")
    result = await tool.run(
        {
            "file_path": str(a_py),
            "target_type": "function",
            "target_name": "f",
            "new_name": "h",
            "create_backup": False,
        },
        context=None,
        convert_result=False,
    )

    assert result["tool_id"] == "rename_symbol"
    assert result["error"] is not None
    assert result["error"]["error_code"] == "forbidden"

    # Ensure neither file was modified.
    assert "def f" in a_py.read_text(encoding="utf-8")
    assert "from a import f" in b_py.read_text(encoding="utf-8")
