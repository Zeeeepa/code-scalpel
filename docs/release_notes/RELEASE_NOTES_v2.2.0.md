# Code Scalpel v2.2.0 "Nexus" Release Notes

**Release Date:** December 16, 2025  
**Codename:** Nexus  
**Status:** Stable Release

---

## Executive Summary

Code Scalpel v2.2.0 "Nexus" introduces the **Unified Cross-Language Graph** - a major architectural advancement that enables AI agents to understand and trace dependencies across language boundaries. This release consolidates v2.0.2, v2.0.3, and v2.1.0 features into a single cohesive release with comprehensive adversarial validation.

### Key Highlights

- [LINK] **Cross-Language HTTP Link Detection** - Trace frontend fetch calls to backend endpoints
- [METRICS] **Confidence Scoring Engine** - All heuristic links scored 0.0-1.0, definite links = 1.0
- [SECURITY]️ **Contract Breach Detection** - Detect breaking changes between client/server
- [GEOMETRY] **Universal Node IDs** - `language::module::type::name` format for graph consistency
- [TARGET] **Zero Silent Hallucinations** - All uncertain connections flagged with evidence

---

## New Features

### P0: Universal Node ID Format

All graph nodes now follow a deterministic format:
```
language::module::type::name[:method]
```

**Examples:**
- `python::utils::function::calculate_tax`
- `java::com.example.api::controller::UserController:getUser`
- `typescript::src/api/client::function::fetchUsers`

This ensures consistent cross-language references and enables reliable dependency tracking.

### P0: Confidence Scoring Engine

Every edge in the dependency graph now carries a confidence score:

| Edge Type | Confidence | Description |
|-----------|------------|-------------|
| `direct_call` | 1.0 | Definite function call |
| `import_dependency` | 1.0 | Explicit import |
| `http_exact_match` | 0.95 | URL exactly matches endpoint |
| `http_pattern_match` | 0.8 | URL matches with path params |
| `http_dynamic_route` | 0.5 | String interpolation detected |
| `inferred_type` | 0.7 | Type inferred from usage |

**Threshold Enforcement:**
- Default threshold: 0.8
- Links below threshold return `requires_human_approval=True`
- All links include evidence strings explaining the confidence level

### P1: HTTP Link Detection

Detects and links frontend API calls to backend endpoints:

```python
# TypeScript client
# fetch('/api/users/${id}')  →  links to  →  Java @GetMapping("/api/users/{id}")
```

**Match Types:**
- `exact` - Confidence 0.95 - Direct URL match
- `pattern` - Confidence 0.8 - Path parameter matching
- `dynamic` - Confidence 0.5 - String interpolation detected

### P1: Contract Breach Detection

Detects breaking changes between client and server:

| Breach Type | Severity | Description |
|-------------|----------|-------------|
| `missing_field` | HIGH | Server field not in client model |
| `endpoint_path_changed` | CRITICAL | API route changed |
| `response_format_changed` | HIGH | Response structure changed |
| `type_mismatch` | MEDIUM | Field types don't match |

Each breach includes fix hints for remediation.

### P2: Resource Templates

New `code:///{language}/{module}/{symbol}` URI scheme for direct symbol access:

```
code:///python/utils/calculate_tax
code:///java/com.example.api/UserController:getUser
```

### P2: Workflow Prompts

Pre-defined prompts for common AI agent workflows:
- Security audit workflow
- Refactoring workflow
- Dependency analysis workflow

### P2: Structured Logging

Comprehensive MCP operation logging with:
- Request/response tracking
- Performance metrics
- Error correlation IDs

---

## Bug Fixes

### HTTP Detector: Dynamic Route Match Type

**Issue:** Dynamic routes (with string interpolation) returned `match_type="none"` instead of `match_type="dynamic"`.

**Fix:** Added `_has_structural_similarity()` method to properly identify dynamic routes and return confidence 0.5 with `match_type="dynamic"`.

**Impact:** Reduces false negatives in HTTP link detection.

### Resource Templates: Uppercase Function Names

**Issue:** React component names (uppercase functions like `Button`) failed to resolve via resource templates.

**Fix:** Added fallback strategy: try class first, then function if class not found.

**Impact:** Full support for React/JSX component extraction.

---

## Test Suite

| Metric | Value |
|--------|-------|
| Total Tests | 2,963 |
| Passed | 2,963 |
| Failed | 0 |
| xfailed | 1 |
| Pass Rate | **100%** |

### Key Test Coverage

- `test_graph_engine_http_detector.py` - 26 tests
- `test_graph_engine_confidence.py` - 23 tests
- `test_graph_engine_graph.py` - 40 tests
- `test_graph_engine_node_id.py` - 17 tests
- `test_contract_breach_detector.py` - 19 tests
- `test_resource_templates.py` - 14 tests
- `test_workflow_prompts.py` - 17 tests
- `test_mcp_logging.py` - 18 tests

---

## Adversarial Validation

### Regression Baseline [COMPLETE]

| Check | Status |
|-------|--------|
| Java generics parsing | PASS |
| Spring Security annotations | PASS |
| Determinism (5 runs identical) | PASS |
| Performance (< 10s for 100 files) | PASS |

### Explicit Uncertainty [COMPLETE]

| Check | Status |
|-------|--------|
| Confidence scores on heuristic links | PASS |
| Threshold enforcement | PASS |
| Evidence strings populated | PASS |

### Cross-Boundary Linking [COMPLETE]

| Check | Status |
|-------|--------|
| HTTP links verified | PASS |
| Type syncing verified | PASS |
| Zero silent hallucinations | PASS |

---

## Breaking Changes

None. This release is fully backward compatible with v2.0.1.

---

## Migration Guide

### From v2.0.1

No migration required. All existing code continues to work.

### New Capabilities to Enable

1. **Confidence Threshold Configuration:**
   ```python
   graph.get_dependencies(symbol, confidence_threshold=0.9)
   ```

2. **HTTP Link Detection:**
   ```python
   from code_scalpel.graph_engine import HTTPLinkDetector
   detector = HTTPLinkDetector()
   links = detector.detect_links(frontend_ast, backend_ast)
   ```

3. **Contract Breach Detection:**
   ```python
   from code_scalpel.polyglot import ContractBreachDetector
   detector = ContractBreachDetector()
   breaches = detector.detect_breaches(server_schema, client_schema)
   ```

---

## Performance

| Operation | v2.0.1 | v2.2.0 | Change |
|-----------|--------|--------|--------|
| Crawl 100 files | 7.5s | 7.2s | -4% |
| Graph build | 2.1s | 2.0s | -5% |
| Confidence scoring | N/A | 0.1s | New |
| HTTP detection | N/A | 0.3s | New |

---

## Known Issues

1. **TSX Generic Components:** Complex TypeScript generics with multiple type parameters may not fully resolve.
2. **Kotlin Data Classes:** Limited support for Kotlin-specific patterns.

Both are scheduled for v2.5.0.

---

## Contributors

- Junior Team - Initial v2.2.0 implementation
- Lead Architect - Bug fixes, adversarial validation, release coordination

---

## Release Artifacts

- **Release Notes:** `docs/release_notes/RELEASE_NOTES_v2.2.0.md`
- **MCP Tools Evidence:** `release_artifacts/v2.2.0/v2.2.0_mcp_tools_evidence.json`
- **Graph Evidence:** `release_artifacts/v2.2.0/v2.2.0_graph_evidence.json`
- **Adversarial Evidence:** `release_artifacts/v2.2.0/v2.2.0_adversarial_evidence.json`

---

## What's Next

**v2.5.0 "Deep Intelligence"** (Target: Q2 2025)
- Full Kotlin support with coroutine tracking
- Enhanced TSX generic resolution
- OpenTelemetry distributed tracing

---

*Code Scalpel v2.2.0 - Surgical Precision Across Language Boundaries*
