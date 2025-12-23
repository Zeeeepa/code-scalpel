# Pre-Fork Architecture Analysis Checklist (V1.0 Production)

This checklist defines the analysis required before forking the repository to create the V1.0 Production version (Community/Pro/Enterprise split). The goal is to identify coupling, define the public contract, and ensure a clean architectural separation for the tiered distribution model.

## 1. Public Contract Inventory ("Don't Break This")
- [ ] **Tool Registry Truth:** Enumerate all currently registered MCP tools (`tools/list`) with their exact argument and return schemas.
- [ ] **Behavioral Contract:** For each tool, document:
    - Required vs. optional arguments and defaults.
    - Error shapes and specific error conditions.
    - Side effects (read-only vs. write-capable).
- [ ] **Transport Contract:** Verify stdio vs. HTTP behavior differences (logging, health checks, auth assumptions).
- [ ] **CLI Contract:** List supported CLI commands and flags used in documentation/scripts.

## 2. Tier Boundary Feasibility (Coupling Analysis)
- [ ] **Dependency Graph by Tool:** Map imports for each MCP tool entrypoint. Identify heavy/optional dependencies (e.g., `z3-solver`, tree-sitter).
- [ ] **Coupling Hotspots:** Identify internal modules shared between "Community" and "Pro" tools. Determine if refactoring/extraction is needed.
- [ ] **Cross-File Compute Boundary:** Identify tools that implicitly perform project-wide analysis (`crawl_project`, `get_call_graph`, etc.).
- [ ] **Write-Safety Boundary:** Ensure Community write tools (`update_symbol`) do not depend on Pro-only components for basic safety.

## 3. Security Architecture (Production Hardening)
- [ ] **File Access Model:** Verify root restrictions and path validation are applied to *every* file-accessing tool.
- [ ] **Code Execution Guarantees:** Confirm tools parse/analyze but *never execute* user code (no `eval`, dynamic imports, subprocesses on repo code).
- [ ] **HTTP Posture:** Review default bind address, DNS rebinding protection, and auth assumptions.
- [ ] **Logging Policy:** Ensure no code content or secrets are logged; define safe audit event structure.

## 4. Packaging & Distribution Architecture
- [ ] **Current Packaging:** Analyze `pyproject.toml` and `MANIFEST.in` to see what is currently shipped.
- [ ] **Pro Package Design:** Define how `code-scalpel-pro` will extend the tool registry (plugin vs. import).
- [ ] **Version Compatibility:** Define policy for Pro package versioning relative to Community.
- [ ] **Docker Strategy:** Define entrypoints and env vars for Community vs. Pro/Enterprise images.

## 5. Operational Architecture (Enterprise Readiness)
- [ ] **Config Layering:** Document how configuration is discovered, validated, and overridden.
- [ ] **Observability:** Define metrics/logging/events schema.
- [ ] **Upgrade/Migration:** Define strategy for schema changes and config migration.

## 6. Data Model & Evidence Architecture
- [ ] **Event Model:** Define standard event schema for tool calls (who, when, tool, params metadata, result summary).
- [ ] **Report Schemas:** Define deterministic schemas for compliance reports (JSON).
