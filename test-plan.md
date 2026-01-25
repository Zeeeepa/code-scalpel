Test Plan: MCP stdio tools validation

Purpose
- Validate the 22 stdio JSON-RPC tools and 6 templates exposed by the Code Scalpel MCP stdio server.
- Produce an automated harness, per-tool specs, CI integration example, and a living tracking document updated during execution.

Scope
- Discovery + validation for each tool/template (happy path, edge cases, invalid inputs, concurrency, protocol conformance).
- Use JSON-RPC 2.0 over stdio.

Approach
- Discovery: attempt JSON-RPC discovery (`rpc.listMethods`, `rpc.discover`, `system.listMethods`), fallback to `docs/roadmap/*.md` for canonical list.
- Spec generation: auto-generate test specs from roadmap docs.
- Harness: Python runner that spawns MCP server (stdio), sends JSON-RPC requests, captures responses and stderr, normalizes nondeterministic fields, validates basic assertions, and records logs/metrics.
- Tracking: `testing/TRACKING.md` is a living file updated after each run.

Artifacts
- `testing/TRACKING.md` — status table and triage notes.
- `test-harness/` — runner, discovery, specs, logs.
- `results/results.json` and `results/summary.txt` — machine and human summaries.

Execution
- The harness will be executed from repo root and uses `PYTHONPATH=src` so the local source is used.

Next steps
1. Run discovery and generate per-tool specs from `docs/roadmap/`.
2. Spawn the MCP stdio server and run discovery + a smoke set of tests.
3. Expand to full suite and update `testing/TRACKING.md` with results and triage.

---
Generated on: 2026-01-24
