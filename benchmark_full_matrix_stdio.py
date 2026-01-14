"""Matrix benchmark for Code Scalpel MCP tools over MCP stdio.

[20260113_TEST] Measure end-to-end latency + payload size across MCP tools for
Community/Pro/Enterprise tiers using *real* JWT licenses, driving the server via
stdin/stdout JSON-RPC (MCP stdio transport).

Why this exists:
- The in-process benchmark in `benchmark_full_matrix.py` excludes transport overhead.
- MCP stdio is the dominant integration path for IDEs and desktop clients.

Outputs:
- evidence/perf/matrix_benchmark_results_stdio.json

Notes:
- This script intentionally starts the server via `python -m code_scalpel.mcp.server`
  (NOT `code-scalpel mcp`) to avoid CLI banners on stdout corrupting the stdio stream.
- Heavy tools can take minutes on a full repo; control runtime via env vars.
"""

from __future__ import annotations

import json
import os
import selectors
import statistics
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
TARGET_FILE = PROJECT_ROOT / "src" / "code_scalpel" / "mcp" / "server.py"

EVIDENCE_DIR = PROJECT_ROOT / "evidence" / "perf"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

LICENSE_PATHS: dict[str, str | None] = {
    "community": None,
    "pro": str(
        PROJECT_ROOT
        / "tests"
        / "licenses"
        / "code_scalpel_license_pro_20260101_190345.jwt"
    ),
    "enterprise": str(
        PROJECT_ROOT
        / "tests"
        / "licenses"
        / "code_scalpel_license_enterprise_20260101_190754.jwt"
    ),
}

TIERS = ["community", "pro", "enterprise"]

# Runtime controls.
# [20260113_TEST] Default to full-matrix coverage (including heavy tools) since
# this project is primarily used by AI agents who can interpret long runtimes.
# Use env vars to reduce scope during local/dev iterations.
DEFAULT_ITERS = int(os.environ.get("SCALPEL_STDIO_MATRIX_ITERS", "9"))
HEAVY_ITERS = int(os.environ.get("SCALPEL_STDIO_MATRIX_HEAVY_ITERS", "1"))
INCLUDE_HEAVY = os.environ.get("SCALPEL_STDIO_INCLUDE_HEAVY", "1") in {"1", "true", "True"}


def _p95_nearest_rank(values: list[float]) -> float:
    if not values:
        return float("nan")
    v = sorted(values)
    idx = int((0.95 * len(v) - 1) // 1) + 1
    idx = max(1, min(len(v), idx))
    return v[idx - 1]


def _to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]

    # Fall back to best-effort conversion.
    return str(obj)


def _payload_size_bytes(obj: Any) -> int:
    raw = json.dumps(_to_jsonable(obj), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return len(raw)


def _env_for_tier(tier: str) -> dict[str, str]:
    env = dict(os.environ)

    # Clear tier-related env keys that could leak across runs.
    for key in (
        "CODE_SCALPEL_LICENSE_PATH",
        "CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY",
        "CODE_SCALPEL_TIER",
        "SCALPEL_TIER",
        "CODE_SCALPEL_TEST_FORCE_TIER",
        "CODE_SCALPEL_LICENSE_VERIFIER_URL",
    ):
        env.pop(key, None)

    # Deterministic tier selection: disable discovery and set explicit license path.
    env["CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY"] = "1"
    license_path = LICENSE_PATHS.get(tier)
    if license_path:
        env["CODE_SCALPEL_LICENSE_PATH"] = license_path

    return env


class MCPStdioClient:
    """Very small MCP stdio JSON-RPC client.

    The installed `mcp.server.stdio` transport uses newline-delimited JSON:
    one JSON-RPC message per line.
    """

    def __init__(self, proc: subprocess.Popen[bytes]):
        self._proc = proc
        self._next_id = 1
        self._sel = selectors.DefaultSelector()
        assert proc.stdout is not None
        self._sel.register(proc.stdout, selectors.EVENT_READ)

    def close(self) -> None:
        try:
            self._sel.close()
        except Exception:
            pass

    def _write(self, payload: dict[str, Any]) -> None:
        assert self._proc.stdin is not None
        line = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

    def _read_message(self, timeout_s: float) -> dict[str, Any]:
        assert self._proc.stdout is not None
        deadline = time.time() + timeout_s

        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError("Timed out waiting for message line")

            events = self._sel.select(timeout=remaining)
            if not events:
                continue

            raw_line = self._proc.stdout.readline()
            if not raw_line:
                raise EOFError("stdout closed")

            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            return json.loads(line)

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._write(payload)

    def request(self, method: str, params: dict[str, Any] | None = None, timeout_s: float = 60.0) -> Any:
        req_id = self._next_id
        self._next_id += 1

        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._write(payload)

        deadline = time.time() + timeout_s
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"Timed out waiting for response to {method}")
            msg = self._read_message(timeout_s=remaining)
            if msg.get("id") != req_id:
                # Ignore notifications / other responses (we run sequentially).
                continue
            if "error" in msg:
                raise RuntimeError(json.dumps(msg["error"], ensure_ascii=False))
            return msg.get("result")


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
    server_reported_tier: str | None
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
            "server_reported_tier": self.server_reported_tier,
            "stats": {
                "min_ms": min(self.latencies_ms) if self.latencies_ms else None,
                "median_ms": statistics.median(self.latencies_ms) if self.latencies_ms else None,
                "p95_ms": _p95_nearest_rank(self.latencies_ms),
                "max_ms": max(self.latencies_ms) if self.latencies_ms else None,
                "median_payload_bytes": (
                    statistics.median(self.payload_sizes_bytes)
                    if self.payload_sizes_bytes
                    else None
                ),
                "max_payload_bytes": (
                    max(self.payload_sizes_bytes) if self.payload_sizes_bytes else None
                ),
            },
            "notes": self.notes,
        }


def _spawn_server(tier: str) -> tuple[subprocess.Popen[bytes], list[str]]:
    env = _env_for_tier(tier)

    cmd = [
        os.environ.get("PYTHON", "python"),
        "-m",
        "code_scalpel.mcp.server",
        "--transport",
        "stdio",
        "--root",
        str(PROJECT_ROOT),
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )

    stderr_lines: list[str] = []

    def _drain_stderr() -> None:
        assert proc.stderr is not None
        for raw in iter(proc.stderr.readline, b""):
            try:
                stderr_lines.append(raw.decode("utf-8", errors="replace").rstrip("\n"))
            except Exception:
                stderr_lines.append(repr(raw))

    t = threading.Thread(target=_drain_stderr, daemon=True)
    t.start()
    return proc, stderr_lines


def _extract_reported_tier(stderr_lines: list[str]) -> str | None:
    # The server prints "Tier: X" to stderr for stdio transport.
    for line in stderr_lines:
        if line.startswith("Tier:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def _tool_args(patch_target: Path, dummy_fn_name: str, dummy_fn_v2_name: str) -> dict[str, dict[str, Any]]:
    # Mirror the arguments used in the in-process benchmark.
    return {
        "analyze_code": {
            "code": TARGET_FILE.read_text(encoding="utf-8"),
            "language": "python",
            "file_path": str(TARGET_FILE),
        },
        "unified_sink_detect": {
            "code": "eval(user_input)",
            "language": "python",
            "min_confidence": 0.7,
        },
        "type_evaporation_scan": {
            "frontend_code": (
                "type Role = 'admin' | 'user';\n"
                "const role = (document.getElementById('r') as HTMLInputElement).value as Role;\n"
                "fetch('/api/role', {method: 'POST', body: JSON.stringify({role})});\n"
            ),
            "backend_code": (
                "from flask import Flask, request\n"
                "app = Flask(__name__)\n"
                "@app.route('/api/role', methods=['POST'])\n"
                "def role():\n"
                "    data = request.get_json()\n"
                "    role = data.get('role')\n"
                "    return {'role': role}\n"
            ),
            "frontend_file": "frontend.ts",
            "backend_file": "backend.py",
        },
        "scan_dependencies": {
            "project_root": str(PROJECT_ROOT),
            "scan_vulnerabilities": True,
            "include_dev": True,
            "timeout": 5.0,
        },
        "security_scan": {"file_path": str(TARGET_FILE)},
        "symbolic_execute": {
            "code": (
                "def classify(age: int) -> str:\n"
                "    if age < 0:\n"
                "        return 'invalid'\n"
                "    if age < 18:\n"
                "        return 'minor'\n"
                "    return 'adult'\n"
            ),
            "max_paths": 25,
            "max_depth": 8,
        },
        "generate_unit_tests": {
            "code": (
                "def validate_age(age):\n"
                "    if age < 0:\n"
                "        return 'invalid'\n"
                "    elif age < 18:\n"
                "        return 'minor'\n"
                "    else:\n"
                "        return 'adult'\n"
            ),
            "framework": "pytest",
            "data_driven": True,
        },
        "simulate_refactor": {
            "original_code": "def add(a, b):\n    return a + b\n",
            "new_code": "def add(a, b):\n    return eval(str(a)) + b\n",
            "strict_mode": False,
        },
        "extract_code": {
            "target_type": "function",
            "target_name": "resolve_file_path",
            "file_path": str(TARGET_FILE),
            "include_context": False,
            "include_cross_file_deps": False,
        },
        "rename_symbol": {
            "file_path": str(patch_target),
            "target_type": "function",
            "target_name": dummy_fn_name,
            "new_name": dummy_fn_v2_name,
            "create_backup": True,
        },
        "update_symbol": {
            "file_path": str(patch_target),
            "target_type": "function",
            "target_name": dummy_fn_v2_name,
            "new_code": f"def {dummy_fn_v2_name}(x: int) -> int:\n    return x + 2\n",
            "create_backup": True,
        },
        "crawl_project": {
            "root_path": str(PROJECT_ROOT),
            "include_report": False,
            "complexity_threshold": 10,
        },
        "get_file_context": {"file_path": str(TARGET_FILE)},
        "get_symbol_references": {
            "symbol_name": "security_scan",
            "project_root": str(PROJECT_ROOT),
            "include_tests": True,
        },
        "get_call_graph": {
            "project_root": str(PROJECT_ROOT),
            "depth": 3,
            "include_circular_import_check": False,
        },
        "get_graph_neighborhood": {
            "center_node_id": "python::code_scalpel.mcp.server::function::security_scan",
            "k": 3,
            "max_nodes": 50,
            "direction": "both",
            "min_confidence": 0.0,
            "project_root": str(PROJECT_ROOT),
        },
        "get_project_map": {
            "project_root": str(PROJECT_ROOT),
            "include_complexity": True,
            "include_circular_check": False,
            "detect_service_boundaries": False,
        },
        "get_cross_file_dependencies": {
            "target_file": str(Path("src/code_scalpel/mcp/server.py")),
            "target_symbol": "_get_current_tier",
            "project_root": str(PROJECT_ROOT),
            "max_depth": 5,
            "include_code": True,
            "include_diagram": False,
            "timeout_seconds": 30.0,
        },
        "cross_file_security_scan": {
            "project_root": str(PROJECT_ROOT),
            "max_depth": 4,
            "include_diagram": False,
            "timeout_seconds": 20.0,
            "max_modules": 250,
        },
        "validate_paths": {
            "paths": [str(TARGET_FILE), str(PROJECT_ROOT / "does-not-exist.txt")],
            "project_root": str(PROJECT_ROOT),
        },
        "verify_policy_integrity": {
            "policy_dir": str(PROJECT_ROOT / ".code-scalpel"),
            "manifest_source": "file",
        },
        "code_policy_check": {
            "paths": [str(TARGET_FILE)],
            "rules": None,
            "compliance_standards": None,
            "generate_report": False,
        },
    }


def main() -> int:
    if not TARGET_FILE.exists():
        raise SystemExit(f"Target file not found: {TARGET_FILE}")

    bench_dir = PROJECT_ROOT / ".bench_tmp"
    bench_dir.mkdir(parents=True, exist_ok=True)

    patch_target = bench_dir / "matrix_stdio_patch_target.py"
    base_code = TARGET_FILE.read_text(encoding="utf-8")

    dummy_fn_name = "__matrix_stdio_bench_dummy_fn"
    dummy_fn_v2_name = "__matrix_stdio_bench_dummy_fn_v2"
    dummy_src = f"\n\ndef {dummy_fn_name}(x: int) -> int:\n    return x + 1\n"

    # Tools in stable order.
    tool_order = [
        "analyze_code",
        "get_file_context",
        "get_graph_neighborhood",
        "unified_sink_detect",
        "security_scan",
        "simulate_refactor",
        "symbolic_execute",
        "generate_unit_tests",
        "extract_code",
        "validate_paths",
        "verify_policy_integrity",
        "code_policy_check",
        "type_evaporation_scan",
        "rename_symbol",
        "update_symbol",
    ]

    heavy_tools = {
        "scan_dependencies",
        "crawl_project",
        "get_symbol_references",
        "get_call_graph",
        "get_project_map",
        "get_cross_file_dependencies",
        "cross_file_security_scan",
    }

    if INCLUDE_HEAVY:
        tool_order.extend(sorted(heavy_tools))

    results: list[ToolRunSummary] = []

    for tier in TIERS:
        # Ensure patch target exists with dummy function for rename/update.
        patch_target.write_text(base_code + dummy_src, encoding="utf-8")

        proc, stderr_lines = _spawn_server(tier)
        try:
            client = MCPStdioClient(proc)

            # Initialize session (warmup; do not include in per-tool latencies).
            init_result = client.request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "code-scalpel-bench", "version": "20260113"},
                },
                timeout_s=60.0,
            )
            try:
                client.notify("notifications/initialized", {})
            except Exception:
                pass

            # tools/list warmup
            _ = client.request("tools/list", {}, timeout_s=60.0)

            # Allow server stderr banner to land.
            time.sleep(0.25)
            reported_tier = _extract_reported_tier(stderr_lines)

            args_by_tool = _tool_args(
                patch_target=patch_target,
                dummy_fn_name=dummy_fn_name,
                dummy_fn_v2_name=dummy_fn_v2_name,
            )

            for tool in tool_order:
                args = args_by_tool.get(tool)
                if args is None:
                    continue

                iters = DEFAULT_ITERS
                if tool in heavy_tools:
                    iters = HEAVY_ITERS

                lat_ms: list[float] = []
                sizes: list[int] = []
                ok = 0
                err = 0
                sample_error: str | None = None
                notes: list[str] = []

                # Prime one call.
                try:
                    _ = client.request(
                        "tools/call",
                        {"name": tool, "arguments": args},
                        timeout_s=180.0,
                    )
                except Exception as e:
                    notes.append(f"Warmup error: {type(e).__name__}: {e}")

                for _i in range(iters):
                    start = time.perf_counter_ns()
                    try:
                        result = client.request(
                            "tools/call",
                            {"name": tool, "arguments": args},
                            timeout_s=180.0,
                        )
                        end = time.perf_counter_ns()
                        lat_ms.append((end - start) / 1e6)
                        sizes.append(_payload_size_bytes(result))
                        ok += 1
                    except Exception as e:
                        end = time.perf_counter_ns()
                        lat_ms.append((end - start) / 1e6)
                        sizes.append(
                            _payload_size_bytes(
                                {"error": str(e), "type": type(e).__name__}
                            )
                        )
                        err += 1
                        if sample_error is None:
                            sample_error = f"{type(e).__name__}: {e}"

                results.append(
                    ToolRunSummary(
                        tool=tool,
                        tier=tier,
                        iterations=iters,
                        latencies_ms=lat_ms,
                        payload_sizes_bytes=sizes,
                        ok_count=ok,
                        error_count=err,
                        sample_error=sample_error,
                        server_reported_tier=reported_tier,
                        notes=notes,
                    )
                )

        finally:
            try:
                client.close()
            except Exception:
                pass

            # Terminate server.
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=10)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    evidence_path = EVIDENCE_DIR / "matrix_benchmark_results_stdio.json"
    evidence = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "project_root": str(PROJECT_ROOT),
        "target_file": str(TARGET_FILE),
        "license_paths": LICENSE_PATHS,
        "tiers": TIERS,
        "stdio": {
            "default_iters": DEFAULT_ITERS,
            "heavy_iters": HEAVY_ITERS,
            "include_heavy": INCLUDE_HEAVY,
        },
        "results": [r.to_dict() for r in results],
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote JSON: {evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
