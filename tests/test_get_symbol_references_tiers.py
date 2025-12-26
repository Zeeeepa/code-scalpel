"""Tier behavior tests for get_symbol_references.

[20251225_TEST] Validate capability-driven limits and Pro/Enterprise metadata.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_get_symbol_references_community_applies_limits(monkeypatch, tmp_path: Path):
    from code_scalpel.mcp import server

    # Create many files so a community max_files_searched limit will truncate.
    for idx in range(20):
        (tmp_path / f"f{idx}.py").write_text(
            """

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
            "limits": {"max_files_searched": 5, "max_references": 5},
            "capabilities": [],
        },
    )

    result = await server.get_symbol_references("target", str(tmp_path))

    assert result.success is True
    assert result.files_truncated is True
    assert result.files_scanned == 5
    assert result.references_truncated is True
    assert len(result.references) == 5

    # No marketing / upgrade hints in tool fields.
    assert (result.truncation_warning or "").lower().find("upgrade") == -1
    assert (result.file_truncation_warning or "").lower().find("upgrade") == -1


@pytest.mark.asyncio
async def test_get_symbol_references_pro_adds_categorization(monkeypatch, tmp_path: Path):
    from code_scalpel.mcp import server

    (tmp_path / "a.py").write_text(
        """

def target():
    return 1

y = target()
"""
    )

    monkeypatch.setattr(server, "get_current_tier_from_license", lambda: "pro")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files_searched": None, "max_references": None},
            "capabilities": [
                "usage_categorization",
                "read_write_classification",
                "import_classification",
                "scope_filtering",
                "test_file_filtering",
            ],
        },
    )

    result = await server.get_symbol_references(
        "target", str(tmp_path), scope_prefix=None, include_tests=True
    )

    assert result.success is True
    assert result.category_counts is not None
    assert any(r.reference_type in {"definition", "call", "read", "write", "import", "reference"} for r in result.references)


@pytest.mark.asyncio
async def test_get_symbol_references_enterprise_codeowners(monkeypatch, tmp_path: Path):
    from code_scalpel.mcp import server

    (tmp_path / "CODEOWNERS").write_text("* @core\n")

    (tmp_path / "mod.py").write_text(
        """

def target():
    return 1

z = target()
"""
    )

    monkeypatch.setattr(server, "get_current_tier_from_license", lambda: "enterprise")
    monkeypatch.setattr(
        server,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files_searched": None, "max_references": None},
            "capabilities": [
                "usage_categorization",
                "codeowners_integration",
                "ownership_attribution",
                "impact_analysis",
                "change_risk_assessment",
            ],
        },
    )

    result = await server.get_symbol_references("target", str(tmp_path))

    assert result.success is True
    assert result.owner_counts is not None
    assert result.owner_counts.get("@core", 0) >= 1
    assert result.change_risk in {"low", "medium", "high"}
