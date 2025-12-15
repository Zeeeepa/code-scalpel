<!-- [20251215_DOCS] Release gate checklist for v2.0.0 -->

# Release Gate Checklist (v2.0.0)

## Pre-flight Quality
- [x] ruff clean and black clean on all touched files (record command outputs path in `release_artifacts/v2.0.0/ruff_black.log`).
- [x] pytest full suite green; store log in `release_artifacts/v2.0.0/pytest_full.log` (2,668 passed, 1 xfailed expected).
<!-- [20251215_DOCS] Coverage gate alignment for v2.0.0 -->
- [x] Coverage report stored as `release_artifacts/v2.0.0/coverage.xml` (89% overall; TypeScript parser stubs account for gap).
- [ ] Mutation smoke (core AST/PDG/symbolic) executed; log surviving mutants and seeds.
- [ ] Parser/symbolic interpreter fuzz smoke executed; log corpus/seed and findings.

## Security & Compliance
- [ ] Dependency vulnerability scan (pip-audit or osv-scanner) recorded with tool version/date in `v2.0.0_vuln_scan_evidence.json`.
- [ ] SBOM generated (CycloneDX) and stored under `release_artifacts/v2.0.0/`; referenced from evidence JSON.
- [ ] Artifact signing completed with Sigstore/Cosign; attach verification outputs and signer identity in evidence JSON.
- [ ] LICENSE and third-party notices validated; license scan summary captured.

## Functionality & Performance
- [x] Multi-language acceptance criteria satisfied (Python/TS/JS/Java) per [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md) and evidence in `v2.0.0_mcp_tools_evidence.json`.
- [x] Adversarial edge cases hardened (88 tests) with evidence: `v2.0.0_adversarial_test_evidence.json`, `v2.0.0_edge_case_evidence.json`.
- [x] Best-in-class validation: `v2.0.0_best_in_class_evidence.json` (F1=1.0, token reduction 99%, throughput 20k+ LOC/sec).
- [x] Performance benchmarks captured in `v2.0.0_performance_evidence.json`.
- [x] Regression guard: `v2.0.0_regression_evidence.json` confirms no v1.5.x API breakage.
- [x] Python 3.13 compatibility: All ast.Str/Num/Bytes deprecations resolved.

## Documentation & Evidence
- [x] Release notes `docs/release_notes/RELEASE_NOTES_v2.0.0.md` updated with MCP protocol, polyglot features, adversarial coverage, metrics, and known limitations.
- [x] Evidence bundle populated: `v2.0.0_mcp_tools_evidence.json`, `v2.0.0_test_evidence.json`, `v2.0.0_language_support_evidence.json`, `v2.0.0_performance_evidence.json`, `v2.0.0_best_in_class_evidence.json`, `v2.0.0_regression_evidence.json`, `v2.0.0_adversarial_test_evidence.json`, `v2.0.0_edge_case_evidence.json`.
- [ ] SECURITY.md updated if policy changes required.
- [ ] DX/interop playbook updated and referenced from roadmap for MCP clients.
- [ ] MCP agent contract validation (Copilot/Claude/ChatGPT/OpenAI) logged with tool/schema versions and evidence paths.

## Final Verification
- [ ] All checkboxes above are complete and referenced in evidence files.
- [ ] Tag and publish only after evidence artifacts are present and signed.
