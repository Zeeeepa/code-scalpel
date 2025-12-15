# Code Scalpel v1.5.5 Release Notes

**Release Date:** December 14, 2025
**Version:** 1.5.5
**Status:** RELEASED
**Tag:** v1.5.5

## Themes
- **ScaleUp Performance:** Caching + parallel parsing + incremental analysis to hit <10s on 1000-file projects.
- **CI/CD Reliability:** Deflake, stabilize pipelines, add smoke gate, and publish troubleshooting guide.

---

## Features Implemented

### P0: Performance Optimization (COMPLETE)

| Feature | Status | Evidence |
|---------|--------|----------|
| AnalysisCache (memory+disk) | ✅ Complete | cache_effectiveness_evidence.json |
| ParallelParser (batched) | ✅ Complete | parallel_execution_results.json |
| IncrementalAnalyzer | ✅ Complete | incremental_analysis_results.json |
| <10s target on 1000+ files | ✅ PASS (3.1s) | v1.5.5_performance_benchmarks.json |

**Key Metrics:**
- Cold run: **3.1s** for 1201 files with 4190 imports (target was <10s)
- Batching optimization: **74.6% improvement** over per-file tasking
- Cache hit rate tracking: Memory, disk, and combined rates exposed via `CacheStats`

### P1: Observability & CI Reliability (COMPLETE)

| Feature | Status | Evidence |
|---------|--------|----------|
| CacheStats counters | ✅ Complete | 4 new tests |
| Memory-mapped file hashing | ✅ Complete | 2 new tests |
| CI troubleshooting guide | ✅ Complete | docs/ci_cd/troubleshooting.md |
| CI smoke gate | ✅ Complete | .github/workflows/ci.yml |
| Pip caching in CI | ✅ Complete | All jobs use setup-python cache |
| Windows spawn fix | ✅ Mitigated | test_parallel_parser_handles_unpicklable_callable |
| CI reliability log | ✅ Complete | ci_cd_reliability_log.json |

---

## New APIs

### CacheStats (src/code_scalpel/cache/analysis_cache.py)
```python
from code_scalpel.cache import CacheStats

# Access via cache.stats
stats = cache.stats.to_dict()
# Returns: {memory_hits, disk_hits, misses, stores, invalidations, hit_rate, ...}
```

### Memory-Mapped File Hashing
Large files (>1MB) are automatically hashed using `mmap` for better memory efficiency.

---

## Testing & Verification

| Category | Count | Status |
|----------|-------|--------|
| Total tests | 2545+ | ✅ Passing |
| Cache module tests | 10 | ✅ Passing |
| Test suite time | ~116s | Stable |

---

## Evidence Files (release_artifacts/v1.5.5/)

- **v1.5.5_performance_benchmarks.json** - Before/after timing, 74.6% improvement
- **cache_effectiveness_evidence.json** - Hit rates, cold vs warm analysis
- **parallel_execution_results.json** - Batching strategy, ProcessPoolExecutor config
- **incremental_analysis_results.json** - <1ms single-file operations
- **ci_cd_reliability_log.json** - CI issues tracked, Windows fix documented
- **accuracy_regression_tests.log** - 13/13 tests passing, no regressions

---

## Known Limitations

- Warm run (disk cache) is slower than cold run due to serial `get_cached()` I/O before parallelization. Disk cache is optimized for incremental single-file updates, not bulk re-analysis.
- CI rerun detector deferred until flaky failures surface in production.

---

## Security Updates

### Dependencies Upgraded (6 CVEs Fixed)

| Package | From | To | CVEs Fixed |
|---------|------|-----|------------|
| **mcp** | 1.16.0 | 1.24.0 | CVE-2025-66416 (DNS rebinding) |
| **pip** | 25.2 | 25.3 | CVE-2025-8869 (tarfile overwrite) |
| **urllib3** | 2.3.0 | 2.6.2 | CVE-2025-50182, CVE-2025-50181, CVE-2025-66418, CVE-2025-66471 |

### Known Vulnerability: pdfminer-six (GHSA-f83h-ghpp-7wcc)

**Status:** No fix available upstream  
**Severity:** HIGH (CVSS 7.8)  
**Type:** Insecure deserialization via pickle in CMap loading

**Impact on Code Scalpel:**
- pdfminer-six is a **transitive dependency** (via pdfplumber)
- Code Scalpel does **not** directly invoke the vulnerable CMap loading code
- Risk is limited to environments where `CMAP_PATH` environment variable points to untrusted/world-writable directories

**Mitigation:**
1. Do not set `CMAP_PATH` to untrusted directories
2. Avoid processing untrusted CMap files with pdfminer
3. Monitor [pdfminer.six security advisories](https://github.com/pdfminer/pdfminer.six/security/advisories) for upstream fix

**Tracking:** This issue is documented in `release_artifacts/v1.5.5/vuln_scan_report.json` and will be remediated when upstream releases a fix.

### Dependency Conflict: crewai

The crewai optional integration has dependency conflicts with `mcp>=1.23.0`. CrewAI currently pins `mcp~=1.16.0` which is incompatible with the security-upgraded MCP version. 

**Workaround:** Use alternative agent integrations (LangChain, Autogen, Claude) until crewai releases a Python 3.13 compatible version with updated MCP support.

---

## No Breaking Changes

All v1.5.4 APIs remain stable. No migration required.

---

## Evidence Artifacts

All release evidence is stored in `release_artifacts/v1.5.5/`:

| File | Contents |
|------|----------|
| `v1.5.5_credibility_evidence.json` | Governance, quality gates, security posture, benchmarks |
| `test_evidence.json` | 2547 tests breakdown by component |
| `coverage.xml` | 93% line coverage report |
| `sbom.json` | CycloneDX SBOM (215 dependencies) |
| `vuln_scan_report.json` | pip-audit vulnerability scan |
| `v1.5.5_performance_benchmarks.json` | Performance metrics |
| `cache_effectiveness_evidence.json` | Cache hit rates |
| `parallel_execution_results.json` | Batching optimization results |
| `incremental_analysis_results.json` | Incremental update metrics |
| `ci_cd_reliability_log.json` | CI/CD improvements |
| `accuracy_regression_tests.log` | Regression test results |
