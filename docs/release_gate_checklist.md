<!-- [20251214_DOCS] Release gate checklist for v1.5.4 -->

# Release Gate Checklist (v1.5.4)

## Pre-flight Quality
- [ ] ruff clean and black clean on all touched files.
- [ ] pytest full suite green (record log path in `release_artifacts/v1.5.4/dynamic_import_tests.log`).
- <!-- [20251214_DOCS] Coverage ramp plan for v1.5.4 -->
- [ ] Coverage path: current overall 90.01% (coverage_20251214.xml); final gate ≥95% with report path and delta recorded.
- [ ] Mutation smoke (core AST/PDG/symbolic modules) executed; log results and surviving mutants.
- [ ] Parser/symbolic interpreter fuzz smoke executed; log corpus/seed and findings.

<!-- [20251214_DOCS] Marked SBOM and vulnerability scan as captured for v1.5.4 -->
## Security & Compliance
- [x] Dependency vulnerability scan (pip-audit) recorded with tool version, date, and findings in `v1.5.4_credibility_evidence.json` (residual: pdfminer-six GHSA-f83h-ghpp-7wcc; operational mitigation until upstream fix).  <!-- [20251214_DOCS] Updated after mcp/urllib3 bumps -->
- [x] SBOM generated (CycloneDX) and stored under `release_artifacts/v1.5.4/`; linked from evidence JSON with noted unpinned-version warnings.
- [ ] Artifact signing completed with Sigstore/Cosign; attach verification command outputs and signer identity in evidence JSON.
- [ ] LICENSE and third-party notices validated; license scan summary captured.

## Functionality & Performance
- [ ] Dynamic import acceptance criteria satisfied; evidence files updated.
- [ ] Benchmark run on ≥1000-file fixture (cold/warm) for import resolution, cross-file extraction, and crawl; thresholds met and logged in `performance_benchmark_log.json`.
- [ ] No regressions in static import resolution and existing v1.5.3 APIs/tests.

## Documentation & Evidence
- [ ] SECURITY.md updated if any policy changes.
- [ ] Release notes `docs/release_notes/RELEASE_NOTES_v1.5.4.md` updated with features, metrics, acceptance, known issues.
- [ ] Evidence bundle `v1.5.4_credibility_evidence.json` populated (coverage deltas, mutation/fuzz notes, signing, SBOM, vuln scan, interop validation, governance links).
- [ ] DX/interop playbook updated and referenced from roadmap.
- <!-- [20251214_DOCS] Agent-first MCP validation -->
- [ ] MCP agent contract validation (Copilot/Claude/ChatGPT/OpenAI clients) logged with tool/schema versions and evidence paths.

## Final Verification
- [ ] All checkboxes above are complete and referenced in evidence files.
- [ ] Tag and publish only after evidence artifacts are present and signed.
