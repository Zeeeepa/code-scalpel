# Release Notes - v2.5.0 "Guardian"

**Release Date:** December 17, 2025  
**Codename:** Guardian  
**Theme:** Governance & Policy  

> [20251217_DOCS] Final release notes for v2.5.0 Guardian

---

## Executive Summary

Code Scalpel v2.5.0 "Guardian" introduces enterprise-grade governance and policy enforcement capabilities, enabling organizations to control AI agent behavior with unprecedented precision. This release marks a significant milestone in the project's mission: **"An agent must never modify code unless Code Scalpel can prove the change is safe, minimal, and intentional."**

**Key Highlights:**
- **Policy Engine**: OPA/Rego-based policy evaluation with fail-closed semantics
- **Semantic Blocking**: 100% block rate on OWASP Top 10 injection attacks
- **Change Budgeting**: Enforce limits on files, lines, and complexity per operation
- **Tamper Resistance**: HMAC-SHA256 signed policy files with TOTP override system
- **Compliance Reporting**: Generate audit-ready JSON/HTML reports
- **Confidence Decay Hardening**: Validates decay_factor, clamps >1.0, rejects invalid values

---

## Test Results

| Metric | Value |
|--------|-------|
| **Total Tests** | 3,354 |
| **Passed** | 3,342 |
| **Failed** | 0 |
| **Skipped** | 11 |
| **Pass Rate** | 100% |
| **Coverage** | 94% |

**Skipped Tests (Intentional):**
- 10 tests: OPA CLI not installed (optional dependency for Rego evaluation)
- 1 test: reportlab not installed (optional for PDF compliance reports)

---

## New Features

### 1. Policy Engine (P0)

OPA/Rego-based governance for AI agent operations with fail-closed semantics.

**Capabilities:**
- Load and parse `.scalpel/policy.yaml` configuration
- Validate Rego syntax at startup via OPA CLI
- Evaluate all operations against defined policies
- **Fail CLOSED** on any policy parsing or evaluation error
- Enforce file pattern rules, annotation rules, and semantic patterns

### 2. Semantic Blocking (P0)

Prevents SQL injection via string construction across all supported languages.

| Pattern | Languages | Status |
|---------|-----------|--------|
| String concatenation | Python, JS, TS, Java | [COMPLETE] Blocked |
| f-strings | Python | [COMPLETE] Blocked |
| format() strings | Python, Java | [COMPLETE] Blocked |
| Template literals | JavaScript, TypeScript | [COMPLETE] Blocked |
| StringBuilder | Java | [COMPLETE] Blocked |

### 3. Change Budgeting (P0)

Enforces limits on AI agent modifications: `max_files`, `max_lines_per_file`, `max_total_lines`, `max_complexity_increase`, `allowed_file_patterns`, `forbidden_paths`.

### 4. Tamper Resistance (P0)

- Policy files locked (0444 permissions)
- SHA-256 integrity verification on startup
- HMAC-signed policy manifest
- TOTP-based human override (single-use, 30-minute expiry)
- All modification attempts logged to audit trail

### 5. Compliance Reporting (P1)

- **JSON**: Machine-readable for CI/CD integration
- **HTML**: Browser-viewable dashboards
- **PDF**: Print-ready reports (requires `reportlab`)

### 6. Confidence Decay Hardening

- `calculate_confidence` validates decay_factor
- Clamps values >1.0 to prevent amplification
- Rejects negatives/NaN/inf to avoid hallucinated confidence

---

## OWASP Top 10 Coverage

| Category | Block Rate |
|----------|------------|
| A01: Broken Access Control | 100% |
| A02: Cryptographic Failures | 100% |
| A03: Injection | 100% |
| A05: Security Misconfiguration | 100% |
| A06: Vulnerable Components | 100% |
| A07: Auth Failures | 100% |
| A08: Integrity Failures | 100% |
| A10: SSRF | 100% |

**False Positive Rate:** <5%

---

## Evidence Files

All release evidence in `release_artifacts/v2.5.0/`:

- [v2.5.0_test_evidence.json](../../release_artifacts/v2.5.0/v2.5.0_test_evidence.json) - Test execution results
- [v2.5.0_owasp_coverage.json](../../release_artifacts/v2.5.0/v2.5.0_owasp_coverage.json) - OWASP Top 10 block rates
- [v2.5.0_policy_evidence.json](../../release_artifacts/v2.5.0/v2.5.0_policy_evidence.json) - Policy engine validation
- [v2.5.0_adversarial_test_evidence.json](../../release_artifacts/v2.5.0/v2.5.0_adversarial_test_evidence.json) - Adversarial test results
- [v2.5.0_mcp_tools_evidence.json](../../release_artifacts/v2.5.0/v2.5.0_mcp_tools_evidence.json) - MCP tools inventory

---

## Migration Notes

- **From v2.2.0**: No breaking changes. Fully backward compatible.
- **Enabling Governance**: Create `.scalpel/policy.yaml` and optionally install OPA CLI
- **PDF Reports**: `pip install reportlab` (optional)

---

## Known Issues / Limitations

- Coverage at 94% (target was 95%) - deferred to v3.0.0
- OPA CLI required for Rego evaluation (graceful skip without it)
- Symbolic execution: int/bool/string only; float/list/dict unsupported
- Multiprocessing fork deprecation warning on some CI runners (non-blocking)

---

## Release Checklist

- [x] Adversarial suite (ADV-2.5.x) passing
- [x] Full test suite passing (3,342 passed, 0 failed)
- [x] Coverage 94% (95% deferred to v3.0.0)
- [x] Evidence artifacts published and referenced
- [x] Release notes finalized

---

## What's Next: v3.0.0 "Autonomy"

- **Error-to-Diff**: Actionable fix hints from error messages
- **Speculative Execution**: Sandbox testing before apply
- **Loop Termination Guards**: Bounded fuel for infinite loop prevention
- **Coverage Target**: ≥95%

---

*"Trust Through Restraint"* - Code Scalpel v2.5.0 Guardian
