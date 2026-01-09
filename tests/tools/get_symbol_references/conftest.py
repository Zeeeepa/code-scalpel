import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Callable

import pytest


@pytest.fixture(autouse=True)
def _reset_tier_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """[20260104_TEST] Ensure tests control tier via env/monkeypatch.

    We disable license discovery so tier forcing works reliably in tests.
    """
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
    monkeypatch.delenv("CODE_SCALPEL_TIER", raising=False)
    monkeypatch.delenv("SCALPEL_TIER", raising=False)
    monkeypatch.setenv("CODE_SCALPEL_TEST_FORCE_TIER", "1")


@pytest.fixture
def make_project(tmp_path: Path) -> Callable[[dict[str, str]], Path]:
    """[20260104_TEST] Create a synthetic project tree with given files.

    Args:
        files: mapping of relative path -> file content.

    Returns:
        Path to the project root.
    """

    def _factory(files: dict[str, str]) -> Path:
        for rel, content in files.items():
            path = tmp_path / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return tmp_path

    return _factory


@pytest.fixture
def patch_tier(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    """[20260104_TEST] Force a specific tier for the current test."""

    def _set(tier: str) -> None:
        monkeypatch.setenv("CODE_SCALPEL_TIER", tier)

    return _set


@pytest.fixture
def patch_capabilities(monkeypatch: pytest.MonkeyPatch) -> Callable[[dict[str, Any]], None]:
    """[20260104_TEST] Override tool capabilities for deterministic tests."""

    def _set(mapping: dict[str, Any]) -> None:
        import code_scalpel.mcp.server as server

        def _caps(tool: str, tier: str) -> dict[str, Any]:
            return mapping

        monkeypatch.setattr(server, "get_tool_capabilities", _caps)

    return _set


@pytest.fixture
def patch_license_validator(monkeypatch: pytest.MonkeyPatch) -> Callable[[Any], None]:
    """[20260104_TEST] Stub JWTLicenseValidator.validate() for license scenarios."""

    def _set(fake_result: Any) -> None:
        import code_scalpel.mcp.server as server

        class _FakeValidator:
            def validate(self) -> Any:  # type: ignore[override]
                return fake_result

        monkeypatch.setattr(server, "JWTLicenseValidator", _FakeValidator)

    return _set
