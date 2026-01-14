"""Matrix benchmark for Code Scalpel MCP tools.

[20260112_TEST] Measure latency + payload size across all 22 tools for
Community/Pro/Enterprise tiers using real JWT licenses.

This benchmark runs tool implementations in-process (no MCP framing, no HTTP).
Tier selection is controlled via CODE_SCALPEL_LICENSE_PATH with
CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY=1 for determinism.

Outputs:
- evidence/perf/matrix_benchmark_results.json
- PROOF_OF_PERFORMANCE_MATRIX.md
"""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable


PROJECT_ROOT = Path(__file__).resolve().parent
TARGET_FILE = PROJECT_ROOT / "src" / "code_scalpel" / "mcp" / "server.py"

EVIDENCE_DIR = PROJECT_ROOT / "evidence" / "perf"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Deterministic tier selection via explicit license paths.
LICENSE_PATHS: dict[str, str | None] = {
    "community": None,
    "pro": str(PROJECT_ROOT / "tests" / "licenses" / "code_scalpel_license_pro_20260101_190345.jwt"),
    "enterprise": str(PROJECT_ROOT / "tests" / "licenses" / "code_scalpel_license_enterprise_20260101_190754.jwt"),
}

TIERS = ["community", "pro", "enterprise"]


def _p95_nearest_rank(values: list[float]) -> float:
    if not values:
        return float("nan")
    v = sorted(values)
    # nearest-rank: ceil(0.95*n)
    idx = int((0.95 * len(v) - 1) // 1) + 1
    idx = max(1, min(len(v), idx))
    return v[idx - 1]


def _to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None

    # Pydantic v2
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            return obj.model_dump()
        except Exception:
            pass

    # Common patterns
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]

    # Last resort: stringify
    return str(obj)


def _payload_size_bytes(obj: Any) -> int:
    data = _to_jsonable(obj)
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return len(raw)


def _reset_tier_env(tier: str) -> None:
    # Clear tier-related env
    for key in (
        "CODE_SCALPEL_LICENSE_PATH",
        "CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY",
        "CODE_SCALPEL_TIER",
        "SCALPEL_TIER",
        "CODE_SCALPEL_TEST_FORCE_TIER",
        "CODE_SCALPEL_LICENSE_VERIFIER_URL",
    ):
        os.environ.pop(key, None)

    # Deterministic tier selection: disable discovery and set explicit license path.
    os.environ["CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY"] = "1"
    license_path = LICENSE_PATHS.get(tier)
    if license_path:
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = license_path


@dataclass
class ToolRunSummary:
    tool: str
    tier: str
    iterations: int
    latencies_ms: list[float]
    payload_sizes_bytes: list[int]
    ok_count: int
    error_count: int
    sample_error: str | None
    effective_tier: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "tier": self.tier,
            "iterations": self.iterations,
            "latencies_ms": self.latencies_ms,
            "payload_sizes_bytes": self.payload_sizes_bytes,
            "ok_count": self.ok_count,
            "error_count": self.error_count,
            "sample_error": self.sample_error,
            "effective_tier": self.effective_tier,
            "stats": {
                "min_ms": min(self.latencies_ms) if self.latencies_ms else None,
                "median_ms": statistics.median(self.latencies_ms) if self.latencies_ms else None,
                "p95_ms": _p95_nearest_rank(self.latencies_ms),
                "max_ms": max(self.latencies_ms) if self.latencies_ms else None,
                "median_payload_bytes": statistics.median(self.payload_sizes_bytes)
                if self.payload_sizes_bytes
                else None,
                "max_payload_bytes": max(self.payload_sizes_bytes)
                if self.payload_sizes_bytes
                else None,
            },
            "notes": self.notes,
        }


async def _run_tool_many(
    tool: str,
    tier: str,
    iterations: int,
    invoke: Callable[[], Awaitable[Any]],
    get_effective_tier: Callable[[], str],
) -> ToolRunSummary:
    lat_ms: list[float] = []
    sizes: list[int] = []
    ok = 0
    err = 0
    sample_error: str | None = None
    notes: list[str] = []

    # Prime one call (warming caches / imports) but do not count.
    try:
        _ = await invoke()
    except Exception as e:
        notes.append(f"Warmup error: {type(e).__name__}: {e}")

    for _ in range(iterations):
        start = time.perf_counter_ns()
        try:
            result = await invoke()
            end = time.perf_counter_ns()
            lat_ms.append((end - start) / 1e6)
            sizes.append(_payload_size_bytes(result))
            ok += 1
        except Exception as e:
            end = time.perf_counter_ns()
            lat_ms.append((end - start) / 1e6)
            sizes.append(_payload_size_bytes({"error": str(e), "type": type(e).__name__}))
            err += 1
            if sample_error is None:
                sample_error = f"{type(e).__name__}: {e}"

    return ToolRunSummary(
        tool=tool,
        tier=tier,
        iterations=iterations,
        latencies_ms=lat_ms,
        payload_sizes_bytes=sizes,
        ok_count=ok,
        error_count=err,
        sample_error=sample_error,
        effective_tier=get_effective_tier(),
        notes=notes,
    )


def _format_outcome(summary: ToolRunSummary, p95_ms: float) -> str:
    if summary.error_count == 0:
        return "✅ Success"
    # Partial failures
    if summary.ok_count > 0:
        return f"⚠️ Partial ({summary.ok_count}/{summary.iterations} ok)"
    # Total failure
    short = summary.sample_error or "error"
    if len(short) > 120:
        short = short[:117] + "..."
    return f"❌ Error ({short})"


def _write_markdown(results: list[ToolRunSummary], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# PROOF_OF_PERFORMANCE_MATRIX\n")
    lines.append("> [20260112_TEST] Empirical matrix benchmark across all MCP tools and tiers.\n")
    lines.append("This report summarizes P95 latency and outcome per tool/tier.\n")

    lines.append("## Method\n")
    lines.append("- Execution: in-process tool calls (no MCP stdio framing, no HTTP)\n")
    lines.append(f"- Standard target file: `{TARGET_FILE}`\n")
    lines.append("- Tier selection: real JWT licenses via `CODE_SCALPEL_LICENSE_PATH` with `CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY=1`\n")

    lines.append("## Results\n")
    lines.append("| Tool | Tier | Latency (P95) | Payload (median) | Outcome |\n")
    lines.append("|------|------|---------------:|----------------:|---------|\n")

    # Stable ordering
    for s in sorted(results, key=lambda x: (x.tool, x.tier)):
        p95_ms = _p95_nearest_rank(s.latencies_ms)
        outcome = _format_outcome(s, p95_ms)
        med_payload = (
            int(statistics.median(s.payload_sizes_bytes))
            if s.payload_sizes_bytes
            else 0
        )
        lines.append(
            f"| `{s.tool}` | {s.tier.title()} | {p95_ms:.1f}ms | {med_payload} bytes | {outcome} |\n"
        )

    lines.append("\n## Notes\n")
    lines.append("- `scan_dependencies` may contact OSV depending on configuration; this run uses its built-in `timeout` parameter to prevent hangs.\n")
    lines.append("- `verify_policy_integrity` requires `SCALPEL_MANIFEST_SECRET` for signature validation at Pro/Enterprise; failures are recorded as such if unset.\n")

    out_path.write_text("".join(lines), encoding="utf-8")


async def main() -> int:
    if not TARGET_FILE.exists():
        raise SystemExit(f"Target file not found: {TARGET_FILE}")

    # Import tool entrypoints once.
    from code_scalpel.mcp import server as mcp_server

    # Prepare a safe patch target file under repo root.
    bench_dir = PROJECT_ROOT / ".bench_tmp"
    bench_dir.mkdir(parents=True, exist_ok=True)
    patch_target = bench_dir / "matrix_patch_target.py"
    base_code = TARGET_FILE.read_text(encoding="utf-8")

    dummy_fn_name = "__matrix_bench_dummy_fn"
    dummy_fn_v2_name = "__matrix_bench_dummy_fn_v2"
    dummy_src = f"\n\ndef {dummy_fn_name}(x: int) -> int:\n    return x + 1\n"

    server_code = base_code

    # Iterations: keep runtime reasonable while still providing a P95.
    DEFAULT_ITERS = int(os.environ.get("SCALPEL_MATRIX_ITERS", "11"))
    HEAVY_ITERS = int(os.environ.get("SCALPEL_MATRIX_HEAVY_ITERS", "5"))

    # Tool definitions (name -> invocation)
    def tool_invocations() -> dict[str, Callable[[], Awaitable[Any]]]:
        return {
            "analyze_code": lambda: mcp_server.analyze_code(
                code=server_code, language="python", file_path=str(TARGET_FILE)
            ),
            "unified_sink_detect": lambda: mcp_server.unified_sink_detect(
                code="eval(user_input)", language="python", min_confidence=0.7
            ),
            "type_evaporation_scan": lambda: mcp_server.type_evaporation_scan(
                frontend_code=(
                    "type Role = 'admin' | 'user';\n"
                    "const role = (document.getElementById('r') as HTMLInputElement).value as Role;\n"
                    "fetch('/api/role', {method: 'POST', body: JSON.stringify({role})});\n"
                ),
                backend_code=(
                    "from flask import Flask, request\n"
                    "app = Flask(__name__)\n"
                    "@app.route('/api/role', methods=['POST'])\n"
                    "def role():\n"
                    "    data = request.get_json()\n"
                    "    role = data.get('role')\n"
                    "    return {'role': role}\n"
                ),
                frontend_file="frontend.ts",
                backend_file="backend.py",
            ),
            "scan_dependencies": lambda: mcp_server.scan_dependencies(
                project_root=str(PROJECT_ROOT),
                scan_vulnerabilities=True,
                include_dev=True,
                timeout=5.0,
            ),
            "security_scan": lambda: mcp_server.security_scan(file_path=str(TARGET_FILE)),
            "symbolic_execute": lambda: mcp_server.symbolic_execute(
                code=(
                    "def classify(age: int) -> str:\n"
                    "    if age < 0:\n"
                    "        return 'invalid'\n"
                    "    if age < 18:\n"
                    "        return 'minor'\n"
                    "    return 'adult'\n"
                ),
                max_paths=25,
                max_depth=8,
            ),
            "generate_unit_tests": lambda: mcp_server.generate_unit_tests(
                code=(
                    "def validate_age(age):\n"
                    "    if age < 0:\n"
                    "        return 'invalid'\n"
                    "    elif age < 18:\n"
                    "        return 'minor'\n"
                    "    else:\n"
                    "        return 'adult'\n"
                ),
                framework="pytest",
                data_driven=True,
            ),
            "simulate_refactor": lambda: mcp_server.simulate_refactor(
                original_code="def add(a, b):\n    return a + b\n",
                new_code="def add(a, b):\n    return eval(str(a)) + b\n",
                strict_mode=False,
            ),
            "extract_code": lambda: mcp_server.extract_code(
                target_type="function",
                target_name="resolve_file_path",
                file_path=str(TARGET_FILE),
                include_context=False,
                include_cross_file_deps=False,
            ),
            "rename_symbol": lambda: mcp_server.rename_symbol(
                file_path=str(patch_target),
                target_type="function",
                target_name=dummy_fn_name,
                new_name=dummy_fn_v2_name,
                create_backup=True,
            ),
            "update_symbol": lambda: mcp_server.update_symbol(
                file_path=str(patch_target),
                target_type="function",
                target_name=dummy_fn_v2_name,
                new_code=(
                    f"def {dummy_fn_v2_name}(x: int) -> int:\n"
                    "    return x + 2\n"
                ),
                create_backup=True,
            ),
            "crawl_project": lambda: mcp_server.crawl_project(
                root_path=str(PROJECT_ROOT),
                include_report=False,
                complexity_threshold=10,
            ),
            "get_file_context": lambda: mcp_server.get_file_context(
                file_path=str(TARGET_FILE)
            ),
            "get_symbol_references": lambda: mcp_server.get_symbol_references(
                symbol_name="security_scan",
                project_root=str(PROJECT_ROOT),
                include_tests=True,
            ),
            "get_call_graph": lambda: mcp_server.get_call_graph(
                project_root=str(PROJECT_ROOT),
                depth=3,
                include_circular_import_check=False,
            ),
            # get_graph_neighborhood is filled per-tier after discovering a valid center_node_id
            "get_project_map": lambda: mcp_server.get_project_map(
                project_root=str(PROJECT_ROOT),
                include_complexity=True,
                include_circular_check=False,
                detect_service_boundaries=False,
            ),
            "get_cross_file_dependencies": lambda: mcp_server.get_cross_file_dependencies(
                target_file=str(Path("src/code_scalpel/mcp/server.py")),
                target_symbol="_get_current_tier",
                project_root=str(PROJECT_ROOT),
                max_depth=5,
                include_code=True,
                include_diagram=False,
                timeout_seconds=30.0,
            ),
            "cross_file_security_scan": lambda: mcp_server.cross_file_security_scan(
                project_root=str(PROJECT_ROOT),
                max_depth=4,
                include_diagram=False,
                timeout_seconds=20.0,
                max_modules=250,
            ),
            "validate_paths": lambda: mcp_server.validate_paths(
                paths=[str(TARGET_FILE), str(PROJECT_ROOT / "does-not-exist.txt")],
                project_root=str(PROJECT_ROOT),
            ),
            "verify_policy_integrity": lambda: mcp_server.verify_policy_integrity(
                policy_dir=str(PROJECT_ROOT / ".code-scalpel"),
                manifest_source="file",
            ),
            "code_policy_check": lambda: mcp_server.code_policy_check(
                paths=[str(TARGET_FILE)],
                rules=None,
                compliance_standards=None,
                generate_report=False,
            ),
        }

    results: list[ToolRunSummary] = []

    for tier in TIERS:
        _reset_tier_env(tier)

        # Reset server module caches that can carry tier state across runs.
        try:
            mcp_server._LAST_VALID_LICENSE_TIER = None  # type: ignore[attr-defined]
            mcp_server._LAST_VALID_LICENSE_AT = None  # type: ignore[attr-defined]
            mcp_server._SESSION_UPDATE_COUNTS.clear()  # type: ignore[attr-defined]
        except Exception:
            pass

        # Ensure patch target exists and contains the current dummy function.
        patch_target.write_text(base_code + dummy_src, encoding="utf-8")

        effective = mcp_server._get_current_tier()  # type: ignore[attr-defined]
        if effective != tier:
            # Community can be clamped if a license leaks in; record it in output.
            pass

        inv = tool_invocations()

        # Discover a stable center node id for graph neighborhood.
        center_node_id = "python::code_scalpel.mcp.server::function::security_scan"
        inv["get_graph_neighborhood"] = lambda: mcp_server.get_graph_neighborhood(
            center_node_id=center_node_id,
            k=3,  # should clamp to k=1 at Community if limits are configured
            max_nodes=50,
            direction="both",
            min_confidence=0.0,
            project_root=str(PROJECT_ROOT),
        )

        for tool_name, invoke in inv.items():
            iters = DEFAULT_ITERS
            if tool_name in {"scan_dependencies", "symbolic_execute", "crawl_project", "cross_file_security_scan", "get_project_map", "get_call_graph", "get_symbol_references", "get_cross_file_dependencies"}:
                iters = HEAVY_ITERS

            summary = await _run_tool_many(
                tool=tool_name,
                tier=tier,
                iterations=iters,
                invoke=invoke,
                get_effective_tier=lambda: mcp_server._get_current_tier(),  # type: ignore[attr-defined]
            )
            results.append(summary)

    evidence_path = EVIDENCE_DIR / "matrix_benchmark_results.json"
    evidence = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "project_root": str(PROJECT_ROOT),
        "target_file": str(TARGET_FILE),
        "license_paths": LICENSE_PATHS,
        "tiers": TIERS,
        "results": [r.to_dict() for r in results],
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    md_path = PROJECT_ROOT / "PROOF_OF_PERFORMANCE_MATRIX.md"
    _write_markdown(results, md_path)

    print(f"Wrote JSON: {evidence_path}")
    print(f"Wrote report: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
