#!/usr/bin/env python3
"""
[20251215_PERF] Java normalizer micro-benchmark for v2.0.1
- Measures parse/normalize throughput on sample Java service
- Useful for validating 50%+ speedup acceptance criteria
"""
import time
from pathlib import Path

from code_scalpel.ir.normalizers import JavaNormalizer

SAMPLE_PATH = Path(__file__).parent / "sample_java_service.java"
RUNS = 20


def load_source() -> str:
    return SAMPLE_PATH.read_text(encoding="utf-8")


def bench_java_normalizer() -> None:
    src = load_source()
    normalizer = JavaNormalizer()

    # Warmup
    normalizer.normalize(src)

    start = time.perf_counter()
    for _ in range(RUNS):
        normalizer.normalize(src)
    duration = time.perf_counter() - start

    avg_ms = (duration / RUNS) * 1000
    loc = len(src.splitlines())
    throughput = loc / (duration / RUNS) if duration > 0 else float("inf")

    print(f"Runs: {RUNS}")
    print(f"Lines: {loc}")
    print(f"Avg per run: {avg_ms:.3f} ms")
    print(f"Throughput: {throughput:.1f} LOC/s")


if __name__ == "__main__":
    bench_java_normalizer()
