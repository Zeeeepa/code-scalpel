"""Tier boundary enforcement tests (MCP stdio integration).

[20251228_TEST] Parametrized tests prove community/pro tiers enforce limits
from .code-scalpel/limits.toml at the MCP boundary.

These tests intentionally exercise the real MCP stdio transport, since that is
what customers run.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

pytestmark = [pytest.mark.asyncio]


def _repo_root() -> Path:
    # tests/mcp/* is two levels below repo root
    return Path(__file__).resolve().parents[2]


def _pythonpath_env(repo_root: Path) -> dict[str, str]:
    src_root = repo_root / "src"
    assert (src_root / "code_scalpel").exists()

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_root) + (":" + existing if existing else "")
    return env


def _tool_json(result) -> dict:
    assert result.isError is False
    assert result.content, "Tool returned empty content"
    first = result.content[0]
    assert hasattr(first, "text"), f"Unexpected content type: {type(first)!r}"
    text = first.text

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "Tool content is not valid JSON; first 200 chars: " + repr(text[:200])
        ) from exc


def _assert_envelope(payload: dict, *, tool_name: str) -> dict:
    assert isinstance(payload, dict)

    for key in (
        "tier",
        "tool_version",
        "tool_id",
        "request_id",
        "capabilities",
        "duration_ms",
        "error",
        "upgrade_hints",
        "data",
    ):
        assert key in payload, f"Missing envelope field: {key}"

    assert payload["tool_id"] == tool_name
    assert isinstance(payload["tier"], str) and payload["tier"]
    assert isinstance(payload["request_id"], str) and payload["request_id"]
    assert isinstance(payload["capabilities"], list)
    assert isinstance(payload["upgrade_hints"], list)
    assert isinstance(payload["duration_ms"], int) and payload["duration_ms"] >= 0

    err = payload.get("error")
    if err is not None:
        assert isinstance(err, dict)
        assert isinstance(err.get("error"), str) and err.get("error")
        assert isinstance(err.get("error_code"), str) and err.get("error_code")
        if err.get("error_details") is not None:
            assert isinstance(err.get("error_details"), dict)

    data = payload.get("data")
    assert isinstance(data, dict) or data is None
    return data  # type: ignore[return-value]


def _ensure_signed_policy_dir(policy_dir: Path, *, secret: str) -> None:
    """Create a minimal allow-all policy dir + signed manifest for tests."""

    from code_scalpel.policy_engine.crypto_verify import CryptographicPolicyVerifier

    policy_dir.mkdir(parents=True, exist_ok=True)

    (policy_dir / "policy.yaml").write_text(
        """# Code Scalpel Policy Configuration
version: \"1.0\"

policies:
  - name: allow-all
    severity: LOW
    action: ALLOW
    description: \"Allow all operations in tests\"
    rule: |
      package code_scalpel.test
      default allow = true
""",
        encoding="utf-8",
    )
    (policy_dir / "budget.yaml").write_text(
        """# Budget constraints for agent operations
max_files_read: 100
max_tokens_per_session: 50000
max_api_calls_per_hour: 1000
""",
        encoding="utf-8",
    )

    manifest = CryptographicPolicyVerifier.create_manifest(
        policy_files=["policy.yaml", "budget.yaml"],
        secret_key=secret,
        signed_by="pytest",
        policy_dir=str(policy_dir),
    )
    CryptographicPolicyVerifier.save_manifest(manifest, policy_dir=str(policy_dir))


@asynccontextmanager
async def _stdio_session(
    *, project_root: Path, extra_env: dict[str, str] | None = None
):
    repo_root = _repo_root()
    env = _pythonpath_env(repo_root)

    # Ensure deterministic tier selection for tests.
    # The dev environment may have license-related env vars set, which would
    # otherwise cause the server to start in Pro/Enterprise unexpectedly.
    for key in (
        "CODE_SCALPEL_LICENSE_PATH",
        "CODE_SCALPEL_LICENSE_JWT",
        "CODE_SCALPEL_ALLOW_HS256",
        "CODE_SCALPEL_SECRET_KEY",
    ):
        env.pop(key, None)

    # Defensive: keep CRL vars empty unless test sets them.
    env.setdefault("CODE_SCALPEL_LICENSE_CRL_PATH", "")
    env.setdefault("CODE_SCALPEL_LICENSE_CRL_JWT", "")

    # Disable filesystem auto-discovery so a dev/test license in the repo does
    # not cause the server to start in Pro/Enterprise unexpectedly.
    # Pro/Enterprise tests still pass an explicit CODE_SCALPEL_LICENSE_PATH.
    env.setdefault("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")

    # Pro/Enterprise tiers require cryptographic policy verification and fail
    # closed if the signing secret is missing. Make tests deterministic by
    # provisioning a minimal policy dir under the test project root.
    policy_secret = env.setdefault("SCALPEL_MANIFEST_SECRET", "unit-test-secret")
    policy_dir = project_root / ".code-scalpel"
    env.setdefault("SCALPEL_POLICY_DIR", str(policy_dir))
    _ensure_signed_policy_dir(policy_dir, secret=policy_secret)

    if extra_env:
        env.update(extra_env)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "code_scalpel.mcp.server",
            "--transport",
            "stdio",
            "--root",
            str(project_root),
        ],
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def _write_fixture_project(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pkg").mkdir(parents=True, exist_ok=True)
    (root / "pkg" / "__init__.py").write_text("\n", encoding="utf-8")
    (root / "pkg" / "a.py").write_text(
        "def a():\n    return 'a'\n\n\n" "def b():\n    return a()\n",
        encoding="utf-8",
    )
    (root / "main.py").write_text(
        "from pkg.a import b\n\n\n" "def main():\n    return b()\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("requested_depth", [10, 999])
async def test_get_call_graph_depth_is_clamped_at_community_but_not_pro(
    tmp_path: Path,
    requested_depth: int,
    hs256_test_secret,
    write_hs256_license_jwt,
):
    project_root = tmp_path / "proj"
    _write_fixture_project(project_root)

    # Community: depth is clamped to 3 per limits.toml.
    async with _stdio_session(project_root=project_root) as session:
        payload = await session.call_tool(
            "get_call_graph",
            arguments={
                "project_root": str(project_root),
                "entry_point": None,
                "depth": requested_depth,
                "include_circular_import_check": False,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="get_call_graph")
        assert env_json["tier"] == "community"
        assert data is not None
        assert data.get("success") is True
        # CallGraphResultModel exposes depth_limit.
        assert data.get("depth_limit") == 3

    # Pro: depth should not be clamped for these values (pro max_depth=50 in limits.toml).
    license_path = write_hs256_license_jwt(
        jti=f"lic-{requested_depth}",
        base_dir=tmp_path,
        filename="license.jwt",
    )

    async with _stdio_session(
        project_root=project_root,
        extra_env={
            "CODE_SCALPEL_ALLOW_HS256": "1",
            "CODE_SCALPEL_SECRET_KEY": hs256_test_secret,
            "CODE_SCALPEL_LICENSE_PATH": str(license_path),
        },
    ) as session:
        payload = await session.call_tool(
            "get_call_graph",
            arguments={
                "project_root": str(project_root),
                "entry_point": None,
                "depth": requested_depth,
                "include_circular_import_check": False,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="get_call_graph")
        assert env_json["tier"] == "pro"
        assert data is not None
        assert data.get("success") is True
        # Pro is not clamped at 10; 999 is clamped to 50 in tool logic.
        expected = requested_depth if requested_depth <= 50 else 50
        assert data.get("depth_limit") == expected


async def test_get_call_graph_pro_resolves_js_imports_cross_file(
    tmp_path: Path,
    hs256_test_secret,
    write_hs256_license_jwt,
):
    project_root = tmp_path / "proj"
    project_root.mkdir(parents=True, exist_ok=True)

    (project_root / "util.js").write_text(
        """
export function foo() {
  return 1;
}
""",
        encoding="utf-8",
    )
    (project_root / "index.js").write_text(
        """
import { foo } from './util.js';

function main() {
  foo();
}

main();
""",
        encoding="utf-8",
    )

    # Community: does not guarantee cross-file resolution.
    async with _stdio_session(project_root=project_root) as session:
        payload = await session.call_tool(
            "get_call_graph",
            arguments={
                "project_root": str(project_root),
                "entry_point": None,
                "depth": 10,
                "include_circular_import_check": False,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="get_call_graph")
        assert env_json["tier"] == "community"
        assert data is not None

    # Pro: should resolve foo() -> util.js:foo when named-imported.
    license_path = write_hs256_license_jwt(
        jti="lic-js-call-graph",
        base_dir=tmp_path,
        filename="license.jwt",
    )

    async with _stdio_session(
        project_root=project_root,
        extra_env={
            "CODE_SCALPEL_ALLOW_HS256": "1",
            "CODE_SCALPEL_SECRET_KEY": hs256_test_secret,
            "CODE_SCALPEL_LICENSE_PATH": str(license_path),
        },
    ) as session:
        payload = await session.call_tool(
            "get_call_graph",
            arguments={
                "project_root": str(project_root),
                "entry_point": None,
                "depth": 10,
                "include_circular_import_check": False,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="get_call_graph")
        assert env_json["tier"] == "pro"
        assert data is not None
        edges = data.get("edges") or []
        # Expect at least one resolved edge to util.js:foo
        assert any(
            (e.get("callee") == "util.js:foo") for e in edges if isinstance(e, dict)
        )


@pytest.mark.parametrize("requested_sinks", [60, 120])
async def test_unified_sink_detect_max_sinks_differs_by_tier(
    tmp_path: Path,
    requested_sinks: int,
    hs256_test_secret,
    write_hs256_license_jwt,
):
    project_root = tmp_path / "proj"
    _write_fixture_project(project_root)

    code = "\n".join(["eval(user_input)"] * requested_sinks) + "\n"

    # Community: max_sinks=50
    async with _stdio_session(project_root=project_root) as session:
        payload = await session.call_tool(
            "unified_sink_detect",
            arguments={
                "code": code,
                "language": "python",
                "min_confidence": 0.0,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="unified_sink_detect")
        assert env_json["tier"] == "community"
        assert data is not None
        assert data.get("success") is True
        assert data.get("sink_count") == 50
        assert isinstance(data.get("sinks"), list)
        assert len(data.get("sinks")) == 50

    # Pro: no max_sinks limit; should return all detected sinks.
    license_path = write_hs256_license_jwt(
        jti=f"lic-sinks-{requested_sinks}",
        base_dir=tmp_path,
        filename="license.jwt",
    )

    async with _stdio_session(
        project_root=project_root,
        extra_env={
            "CODE_SCALPEL_ALLOW_HS256": "1",
            "CODE_SCALPEL_SECRET_KEY": hs256_test_secret,
            "CODE_SCALPEL_LICENSE_PATH": str(license_path),
        },
    ) as session:
        payload = await session.call_tool(
            "unified_sink_detect",
            arguments={
                "code": code,
                "language": "python",
                "min_confidence": 0.0,
            },
            read_timeout_seconds=timedelta(seconds=20),
        )
        env_json = _tool_json(payload)
        data = _assert_envelope(env_json, tool_name="unified_sink_detect")
        assert env_json["tier"] == "pro"
        assert data is not None
        assert data.get("success") is True
        assert data.get("sink_count") == requested_sinks
        assert isinstance(data.get("sinks"), list)
        assert len(data.get("sinks")) == requested_sinks
