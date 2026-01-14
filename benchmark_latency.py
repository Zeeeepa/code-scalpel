"""[20260112_TEST] Latency benchmark for Code Scalpel security_scan.

Runs the MCP server's security_scan implementation directly (no HTTP/MCP stdio)
to measure per-file execution latency over a set of repository files.

Primary metric: p95 latency in seconds.
"""

from __future__ import annotations

import argparse
import math
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LatencyStats:
    n: int
    min_s: float
    max_s: float
    mean_s: float
    median_s: float
    p95_s: float


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _ensure_src_on_path(repo_root: Path) -> None:
    src_root = repo_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def _iter_python_files(repo_root: Path, *, include_tests: bool) -> list[Path]:
    paths: list[Path] = []
    for base in [repo_root / "src", repo_root / "tests"]:
        if base.name == "tests" and not include_tests:
            continue
        if not base.exists():
            continue
        paths.extend(sorted(base.rglob("*.py")))
    # Drop common noise directories
    filtered: list[Path] = []
    for p in paths:
        parts = set(p.parts)
        if "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        filtered.append(p)
    return filtered


def _p95(values_s: list[float]) -> float:
    """Nearest-rank p95 (ceil(0.95*n))."""
    if not values_s:
        raise ValueError("p95 requires at least one value")
    xs = sorted(values_s)
    idx = max(0, min(len(xs) - 1, math.ceil(0.95 * len(xs)) - 1))
    return xs[idx]


def _stats(values_s: list[float]) -> LatencyStats:
    return LatencyStats(
        n=len(values_s),
        min_s=min(values_s),
        max_s=max(values_s),
        mean_s=statistics.fmean(values_s),
        median_s=statistics.median(values_s),
        p95_s=_p95(values_s),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark security_scan latency")
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of files to benchmark (default: 100)",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include tests/ files in the benchmark input set",
    )
    parser.add_argument(
        "--tier",
        choices=["community", "pro", "enterprise"],
        default="enterprise",
        help="Tier to apply for capability/limit selection (default: enterprise)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=0,
        help="Warmup iterations (calls not timed; default: 0)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable unified cache for this process (sets SCALPEL_NO_CACHE=1)",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to write JSON results",
    )

    args = parser.parse_args(argv)

    repo_root = _repo_root()
    _ensure_src_on_path(repo_root)

    if args.no_cache:
        os.environ["SCALPEL_NO_CACHE"] = "1"

    # Import after env + sys.path adjustments.
    from code_scalpel.mcp import server as mcp_server

    # Precompute capabilities once to avoid repeatedly loading tier limits/config.
    # This better reflects a long-running MCP server process where tier limits
    # are loaded once and reused for many tool invocations.
    capabilities = mcp_server.get_tool_capabilities("security_scan", args.tier)

    files = _iter_python_files(repo_root, include_tests=args.include_tests)
    if not files:
        print("No Python files found under src/ (and tests/ if enabled).", file=sys.stderr)
        return 2

    selected = files[: args.count] if len(files) >= args.count else files
    if len(selected) < args.count:
        # Loop over available files to reach the requested count.
        reps = math.ceil(args.count / len(selected))
        selected = (selected * reps)[: args.count]

    # Optional warmup.
    for i in range(args.warmup):
        p = selected[i % len(selected)]
        _ = mcp_server._security_scan_sync(
            file_path=str(p), tier=args.tier, capabilities=capabilities
        )

    latencies_s: list[float] = []
    for p in selected:
        t0 = time.perf_counter_ns()
        _ = mcp_server._security_scan_sync(
            file_path=str(p), tier=args.tier, capabilities=capabilities
        )
        dt_s = (time.perf_counter_ns() - t0) / 1_000_000_000
        latencies_s.append(dt_s)

    st = _stats(latencies_s)
    print("security_scan latency (seconds)")
    print(f"  n      : {st.n}")
    print(f"  min    : {st.min_s:.6f}")
    print(f"  max    : {st.max_s:.6f}")
    print(f"  mean   : {st.mean_s:.6f}")
    print(f"  median : {st.median_s:.6f}")
    print(f"  p95    : {st.p95_s:.6f}")
    print(f"  target : p95 < 0.050000 => {st.p95_s < 0.05}")

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tool": "security_scan",
            "tier": args.tier,
            "no_cache": args.no_cache,
            "count": args.count,
            "include_tests": args.include_tests,
            "warmup": args.warmup,
            "stats": asdict(st),
            "samples_s": latencies_s,
        }
        out_path.write_text(
            __import__("json").dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
