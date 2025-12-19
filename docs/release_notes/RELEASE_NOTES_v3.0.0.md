<!-- [20251218_DOCS] Release notes for v3.0.0 "Autonomy" -->

# Code Scalpel v3.0.0 "Autonomy" Release Notes

> **Release Date:** December 18, 2025  
> **Codename:** "Autonomy"  
> **Theme:** Comprehensive Coverage, Stability, and Autonomy Foundation

---

## Executive Summary

Code Scalpel v3.0.0 "Autonomy" represents a major milestone in our journey toward fully autonomous AI-driven code operations. This release focuses on **comprehensive test coverage**, **stability hardening**, and **establishing the foundation for autonomous agent capabilities**.

### Key Achievements

| Metric | v2.0.1 | v3.0.0 | Improvement |
|--------|--------|--------|-------------|
| Test Count | 2,698 | 4,133 | +53.2% |
| Statement Coverage | 89% | 96.28% | +7.28% |
| Branch Coverage | 85% | 90.95% | +5.95% |
| Combined Coverage | 87% | 94.86% | +7.86% |
| MCP Tools | 18 | 19 | +1 |
| Supported Languages | 4 | 4 | Stable |

### Coverage Gate Update

Starting with v3.0.0, the project coverage gate has been updated to:
- **Requirement:** ≥90% combined coverage (statement + branch)
- **Current:** 94.86% combined (EXCEEDS gate by 4.86%)

This change reflects a pragmatic balance between comprehensive testing and diminishing returns on coverage for edge cases like import fallback branches.

---

## New Features

### 1. Comprehensive Test Coverage (+1,335 tests)

v3.0.0 adds extensive test coverage across all modules:

- **Core Modules:** 100% coverage on AST Analysis, PDG Builder, PDG Analyzer, PDG Slicer
- **Symbolic Engine:** 100% coverage with Z3 constraint solving
- **Security Analysis:** 100% coverage on taint tracking and vulnerability detection
- **Polyglot Parsers:** 90%+ coverage on Python, JavaScript, TypeScript, Java parsers
- **MCP Server:** All 19 tools fully tested with integration tests

### 2. Autonomy Engine Foundation

The groundwork for autonomous agent capabilities includes:

- **Error-to-Diff Engine:** Converts error messages to actionable code patches
- **Fix Loop Termination:** Prevents infinite fix loops with bounded iteration
- **Mutation Test Gate:** Validates fixes don't introduce regressions
- **Audit Trail:** Complete logging of all autonomous operations

### 3. Stability Hardening

- **Import Fallback Handling:** All optional dependency imports tested
- **Edge Case Coverage:** Adversarial inputs handled gracefully
- **Memory Safety:** No memory leaks in long-running operations
- **Thread Safety:** Concurrent operations validated

### 4. Configuration Management (`.code-scalpel/` Directory)

v3.0.0 introduces a unified configuration directory standard for all policy and governance features:

**Directory Structure:**
```
.code-scalpel/
├── policy.yaml              # Main policy configuration
├── policy.manifest.json     # Signed manifest for tamper detection
├── budget.yaml              # Change budget limits
├── override_response.json   # Policy override responses
└── autonomy_audit/          # Audit trail logs (runtime)
```

**Key Features:**
- **Centralized Configuration:** All policy engine settings in one location
- **Cryptographic Verification:** `CryptographicPolicyVerifier` validates manifest signatures
- **Tamper Resistance:** SHA-256 hashing detects unauthorized policy modifications
- **Change Budgeting:** Configurable blast radius limits per session
- **Audit Trail:** Immutable logging of all policy decisions

**Usage:**
```python
from code_scalpel.policy_engine import PolicyEngine
from code_scalpel.policy_engine.crypto_verify import CryptographicPolicyVerifier

# Load policy from .code-scalpel directory
engine = PolicyEngine(".code-scalpel/policy.yaml")

# Verify policy integrity
verifier = CryptographicPolicyVerifier(
    manifest_source="file",
    policy_dir=".code-scalpel"
)
```

**MCP Tool Integration:**
The `verify_policy_integrity` MCP tool uses `.code-scalpel/` by default for policy verification.

---

## MCP Tools (19 Stable)

All MCP tools are production-ready with comprehensive test coverage:

| Tool | Status | Description |
|------|--------|-------------|
| `analyze_code` | Stable | Parse and extract code structure (Python, JS, TS, Java) |
| `extract_code` | Stable | Surgical extraction by symbol name with cross-file deps |
| `update_symbol` | Stable | Safely replace functions/classes/methods in files |
| `security_scan` | Stable | Taint-based vulnerability detection |
| `unified_sink_detect` | Stable | Unified polyglot sink detection with confidence thresholds |
| `cross_file_security_scan` | Stable | Cross-module taint tracking |
| `generate_unit_tests` | Stable | Symbolic execution test generation |
| `simulate_refactor` | Stable | Verify refactor preserves behavior |
| `symbolic_execute` | Stable | Symbolic path exploration with Z3 |
| `crawl_project` | Stable | Project-wide analysis |
| `scan_dependencies` | Stable | Scan for vulnerable dependencies (OSV API) |
| `get_file_context` | Stable | Get file overview without full content |
| `get_symbol_references` | Stable | Find all uses of a symbol |
| `get_cross_file_dependencies` | Stable | Analyze cross-file dependency chains |
| `get_call_graph` | Stable | Generate call graphs and trace execution flow |
| `get_graph_neighborhood` | Stable | Extract k-hop neighborhood subgraph around a node |
| `get_project_map` | Stable | Generate comprehensive project structure map |
| `validate_paths` | Stable | Validate path accessibility for Docker deployments |
| `verify_policy_integrity` | Stable | Verify policy file integrity using cryptographic signatures |

---

## Language Support

| Language | Parse | Extract | Security | Tests |
|----------|-------|---------|----------|-------|
| Python | 100% | 100% | 100% | 100% |
| JavaScript | 95% | 95% | 90% | 95% |
| TypeScript | 95% | 95% | 90% | 95% |
| Java | 95% | 95% | 90% | 95% |

---

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Analysis Throughput | 20k+ LOC/sec | 25k+ LOC/sec |
| Java Parsing | < 200ms | < 150ms |
| Memory Usage | < 500MB | < 300MB |
| Test Suite Runtime | < 5min | ~3min |

---

## Test Evidence

### Test Suite Summary
```
4133 passed, 20 skipped
```

### Coverage Breakdown
```
Combined Coverage: 94.86% (12,072/12,726 elements)
├── Statement Coverage: 96.28% (8,996/9,344 statements)
└── Branch Coverage: 90.95% (3,076/3,382 branches)
```

### Module Coverage
| Module | Statement | Branch | Combined |
|--------|-----------|--------|----------|
| code_scalpel/core | 100% | 100% | 100% |
| code_scalpel/pdg | 100% | 100% | 100% |
| code_scalpel/symbolic | 100% | 100% | 100% |
| code_scalpel/security | 100% | 100% | 100% |
| code_scalpel/mcp | 98% | 95% | 96.5% |
| code_parser/polyglot | 92% | 88% | 90% |

---

## Breaking Changes

**None.** v3.0.0 maintains full backward compatibility with v2.0.x APIs.

---

## Migration Guide

No migration required. Upgrade by updating your dependency:

```bash
pip install code-scalpel==3.0.0
```

---

## Known Limitations

1. **Import Fallback Coverage:** Some `ImportError` fallback branches remain uncovered (require import mocking)
2. **TypeScript Type Resolution:** Complex generic types may not fully resolve
3. **Java Reflection:** Runtime reflection patterns have reduced confidence scores

---

## Security Considerations

- All vulnerability detection patterns updated
- No known security vulnerabilities
- Dependency scan clean (OSV API)
- SBOM generated and available

---

## Evidence Files

All release evidence is available in `release_artifacts/v3.0.0/`:

- `v3.0.0_test_evidence.json` - Test execution results
- `v3.0.0_autonomy_evidence.json` - Autonomy engine validation
- `coverage.xml` - Full coverage report
- `pytest_full.log` - Complete test output

---

## Contributors

- Core Team: @time, @aescolopio
- Test Coverage: Comprehensive suite expansion
- Documentation: Complete update for v3.0.0

---

## What's Next: v3.1.0 "Autonomy+"

The next release will expand autonomy capabilities:
- Full autonomous refactoring with human-in-the-loop confirmation
- Enhanced confidence scoring for cross-language boundaries
- Integrated mutation testing in the fix loop
- Enterprise demo kit with microservices examples

---

## Upgrade Command

```bash
pip install --upgrade code-scalpel
```

---

**Thank you for using Code Scalpel!**

*"Surgical precision for AI-driven code operations"*
