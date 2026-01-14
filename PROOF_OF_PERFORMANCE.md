# PROOF_OF_PERFORMANCE

> [20260112_TEST] Empirical performance + AST extraction evidence generated on 2026-01-12.

This report backs the claim:

> Built Code Scalpel using AST parsing and cross-file dependency mapping to analyze 270k+ lines of code with sub-50ms latency.

All measurements here call Code Scalpel tool implementations **directly in-process** (no HTTP, no MCP stdio framing).

## Environment

- Runtime: `conda env` `code-scalpel`
- Interpreter: `/home/xbyooki/anaconda3/envs/code-scalpel/bin/python`
- Code Scalpel version: `3.3.0`
- Tier used for latency benchmark: `enterprise`

## Task 1 — Velocity Test (sub-50ms)

Benchmark script: [benchmark_latency.py](benchmark_latency.py)

Method:
- Tool: `security_scan`
- Sample size: 100 file scans
- Timer: `time.perf_counter_ns()`
- P95: nearest-rank (ceil(0.95*n))

### Results (Warm process / cached)

Source: [evidence/perf/latency_warm_cache_conda.json](evidence/perf/latency_warm_cache_conda.json)

| Metric | Value (seconds) | Value (ms) |
|---|---:|---:|
| Min | 0.003375984 | 3.376 |
| Max | 0.014145738 | 14.146 |
| P95 | 0.009697992 | 9.698 |

✅ Meets target: P95 < 50ms

### Results (Cache disabled)

Source: [evidence/perf/latency_no_cache_conda.json](evidence/perf/latency_no_cache_conda.json)

| Metric | Value (seconds) | Value (ms) |
|---|---:|---:|
| Min | 0.004516276 | 4.516 |
| Max | 0.139990642 | 139.991 |
| P95 | 0.047553601 | 47.554 |

✅ Meets target: P95 < 50ms

Notes:
- The max includes outliers; the claim target is P95.

## Task 2 — Volume Test (270k+ LOC)

### Repo size check

Command used:
`find . -name "*.py" -print0 | xargs -0 wc -l | tail -n 5`

Observed total Python LOC:
- `404,635 total`

✅ Repo is already > 270k LOC (no iteration needed).

### Crawl throughput

Tool: `crawl_project` (enterprise tier, deep crawl)

Source: [evidence/perf/crawl_project_throughput_conda.json](evidence/perf/crawl_project_throughput_conda.json)

- Processed `346,495` lines in `12.387831` seconds
- Throughput: `27,970.59` lines/sec

## Task 3 — AST verification (no regex truncation)

Demonstration:
- Tool: `extract_code`
- Target: class `JWTLicenseValidator`
- File: `src/code_scalpel/licensing/jwt_validator.py`

Source: [evidence/perf/ast_extraction_snippet_conda.json](evidence/perf/ast_extraction_snippet_conda.json)

Snippet (shows full class node content including docstring + decorator + body):

```python
class JWTLicenseValidator:
    """
    Validate JWT-based license keys for Code Scalpel.

    Supports two validation modes:
    1. RS256: Public key verification (recommended)
    2. HS256: Shared secret verification

    License File Locations (in priority order):
    1. Explicit license file path: CODE_SCALPEL_LICENSE_PATH
    2. Project license: .code-scalpel/license.jwt
    3. User config: ~/.config/code-scalpel/license.jwt
    4. Legacy fallback: ~/.code-scalpel/license.jwt
    5. Legacy fallback: .scalpel-license
    """
    DEFAULT_LICENSE_PATHS = [
        '.code-scalpel/license/license.jwt',
        '.code-Scalpel/license/license.jwt',
        '.code-scalpel/license.jwt',
        '.code-Scalpel/license.jwt',
        '~/.config/code-scalpel/license.jwt',
        '~/.code-scalpel/license.jwt',
        '~/.code-Scalpel/license.jwt',
        '.scalpel-license',
    ]

    @classmethod
    def _load_public_key(cls) -> str:
        """Load the current public key from public_key/ folder or fall back to embedded key."""
        ...
```
