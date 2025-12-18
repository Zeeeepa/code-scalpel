# Code Scalpel v2.0.1 Release Notes - "Java Complete"

**Release Date:** December 16, 2025  
**Version:** 2.0.1  
**Codename:** Java Complete  
**Maintainer:** 3D Tech Solutions LLC

---

## Executive Summary

v2.0.1 is a **stability and documentation release** that locks in 95% code coverage, confirms Java support stability, and integrates the Revolution Roadmap (v2.2.0 → v3.0.0) into official documentation. No new MCP tools ship in this release; changes focus on test hardening, coverage enforcement, and roadmap alignment.

> **North Star Mission:** "An agent must never modify code unless Code Scalpel can prove the change is safe, minimal, and intentional."

### Key Highlights

- **95% Coverage Lock:** Enforced via CI gate with documented exclusions
- **Java Stability Confirmed:** All Java generics, Spring Security, and JPA/ORM tests passing
- **Revolution Roadmap Integration:** v2.2.0 "Nexus", v2.5.0 "Guardian", v3.0.0 "Autonomy" documented
- **Zero Regressions:** All 2,698 tests pass (1 expected xfail for symbolic edge case)
- **Determinism Verified:** Re-running analysis yields identical results

---

## What's New

<!-- [20251216_DOCS] v2.0.1 release documentation -->

### 1. Coverage and Quality Lock

**Test Results:**
- **Total Tests:** 2,698 passing, 1 xfailed (expected)
- **Coverage:** 95% overall (post-omit)
- **Pass Rate:** 100%

**Module Coverage Breakdown:**
| Module | Coverage |
|--------|----------|
| pdg_tools | 99% |
| surgical_extractor | 97% |
| surgical_patcher | 96% |
| security_analysis | 95% |
| symbolic_execution_tools | 92% |
| cli | 90% |

### 2. Coverage Exclusions (Documented)

The following paths are excluded from coverage requirements with justification:

- `src/code_scalpel/agents/*`, `src/code_scalpel/integrations/*`: Require live MCP/client plumbing
- IR normalizers: `src/code_scalpel/ir/normalizers/*` – Language-specific CST handling
- Path resolution: `src/code_scalpel/path_resolver.py`, `src/code_scalpel/import_resolver.py` – Environment-specific
- PDG visualization: `src/code_scalpel/pdg_tools/transformer.py`, `visualizer.py` – Graph rendering backends
- Project crawling: `src/code_scalpel/project_crawler.py`, `polyglot_extractor.py` – Filesystem-heavy
- Cross-file security: `src/code_scalpel/security/cross_file_security_analyzer.py` – Integration-heavy

### 3. Java Stability Verification

All Java regression baseline tests pass:

- [COMPLETE] **Java Generics:** `Repository<User>` vs `Repository<Order>` correctly distinguished
- [COMPLETE] **Spring Security:** `LdapTemplate` and `OAuth2TokenProvider` sinks detected
- [COMPLETE] **JPA/ORM:** Entity relationships and query sinks tracked
- [COMPLETE] **Determinism:** Identical node IDs on re-analysis
- [COMPLETE] **Performance:** < 200ms parsing for standard files

### 4. Revolution Roadmap Integration

This release officially documents the path to v3.0.0 "Autonomy":

| Version | Codename | Theme | Timeline |
|---------|----------|-------|----------|
| v2.2.0 | Nexus | Unified Graph with Confidence Scoring | Q1 2026 |
| v2.5.0 | Guardian | Governance & Policy Engine | Q1 2026 |
| v3.0.0 | Autonomy | Self-Correction Loop | Q2 2026 |

**Key Documents Updated:**
- [DEVELOPMENT_ROADMAP.md](../../DEVELOPMENT_ROADMAP.md) - Revolution Edition v3.1
- [release_gate_checklist.md](../release_gate_checklist.md) - Phase-specific gates with adversarial criteria
- [Revolution-CodeScalpelExecutionRoadmap.md](../Revolution-CodeScalpelExecutionRoadmap.md) - Weekly execution plan
- [Revolution-CodeScalpelAversarialChecklist.md](../Revolution-CodeScalpelAversarialChecklist.md) - Stop-ship criteria

---

## MCP Tools (Unchanged from v2.0.0)

18 MCP tools remain stable with identical schemas:

| Tool | Description | Languages |
|------|-------------|-----------|
| `analyze_code` | Parse and extract code structure | Python, JS, TS, Java |
| `extract_code` | Surgical extraction by symbol name | Python, JS, TS, Java |
| `security_scan` | Taint-based vulnerability detection | Python, JS, TS, Java |
| `cross_file_security_scan` | Cross-module taint tracking | Python, JS, TS, Java |
| `generate_unit_tests` | Symbolic execution test generation | Python |
| `simulate_refactor` | Verify refactor preserves behavior | Python |
| `crawl_project` | Project-wide analysis | All |
| `get_call_graph` | Function relationship mapping | Python |
| `get_file_context` | Surrounding context extraction | All |
| `get_symbol_references` | Find all symbol usages | Python |
| `get_cross_file_dependencies` | Cross-file dependency chains | Python |
| `scan_dependencies` | Vulnerable dependency detection (OSV) | Python, JS |
| `validate_paths` | Path accessibility validation | All |

---

## Performance Metrics (Unchanged from v2.0.0)

| Metric | Value | Status |
|--------|-------|--------|
| Analysis Throughput | 20,000+ LOC/sec | [COMPLETE] Maintained |
| Token Efficiency | 99% reduction vs full-file | [COMPLETE] Maintained |
| Security Detection F1 | 1.0 (100% precision/recall) | [COMPLETE] Maintained |
| Java Parse Time | < 200ms (standard files) | [COMPLETE] Maintained |

---

## Breaking Changes

**None.** v2.0.1 is fully backward compatible with v2.0.0.

---

## Migration Guide

No migration required. Upgrade by updating your dependency:

```bash
pip install code-scalpel==2.0.1
```

Or with Docker:
```bash
docker pull 3dtechsolutions/code-scalpel:2.0.1
```

---

## Known Issues

1. **JavaScript CST Warnings:** Some advanced JavaScript patterns (`super`, `spread_element`) emit warnings but do not affect functionality
2. **Symbolic Execution xfail:** One symbolic execution edge case remains xfailed (complex constraint solving)
3. **Coverage Exclusions:** Certain integration-heavy paths excluded from coverage metrics

---

## Evidence Files

All evidence stored in `release_artifacts/v2.0.1/`:

| File | Description |
|------|-------------|
| `coverage.xml` | Coverage report (95% overall) |
| `pytest_full.log` | Full test execution log |
| `ruff_black.log` | Linter verification |
| `v2.0.1_test_evidence.json` | Test summary and metrics |
| `v2.0.1_performance_evidence.json` | Performance benchmarks |
| `v2.0.1_security_evidence.json` | Security scan results |
| `v2.0.1_dependency_evidence.json` | Dependency audit |

---

## Contributors

- 3D Tech Solutions LLC (Maintainer)
- Code Scalpel Development Team

---

## What's Next: v2.2.0 "Nexus"

The next release introduces the **Unified Graph** with cross-language confidence scoring:

- Universal Node IDs across Python/JS/TS/Java
- Confidence Engine (0.0-1.0 scores for heuristic links)
- Cross-Boundary Taint tracking
- Contract Breach Detection

See [DEVELOPMENT_ROADMAP.md](../../DEVELOPMENT_ROADMAP.md) for the full Revolution Roadmap.
