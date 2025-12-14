# Release Artifacts

This directory contains evidence files and artifacts from Code Scalpel releases, organized by version.

## Directory Structure

```
release_artifacts/
├── v1.4.0/          # v1.4.0 "Surgical Precision" release artifacts
│   ├── v1.4_coverage.log
│   ├── v1.4_get_file_context_evidence.json
│   ├── v1.4_get_symbol_references_evidence.json
│   ├── v1.4_pdv_output.log
│   ├── v1.4_spec_tests.log
│   ├── v1.4_xxe_detection_evidence.json
│   └── temp_xxe_test.py
│
└── v1.5.0/          # v1.5.0 "Project Intelligence" release artifacts
    ├── v1.5.0_mcp_tools_evidence.json
    └── v1.5.0_test_evidence.json
```

## Release Evidence Files

### v1.4.0 "Surgical Precision"

**Evidence Files:**
- `v1.4_get_file_context_evidence.json` - Evidence for `get_file_context` MCP tool
- `v1.4_get_symbol_references_evidence.json` - Evidence for `get_symbol_references` MCP tool
- `v1.4_xxe_detection_evidence.json` - Evidence for XXE injection detection feature

**Logs & Test Output:**
- `v1.4_coverage.log` - Code coverage report
- `v1.4_spec_tests.log` - Test specification execution log
- `v1.4_pdv_output.log` - Program Dependence Graph validation output
- `temp_xxe_test.py` - Test file for XXE detection

### v1.5.0 "Project Intelligence"

**Evidence Files:**
- `v1.5.0_mcp_tools_evidence.json` - Specification and test evidence for all 3 new MCP tools:
  - `get_project_map` - Project structure analysis tool
  - `get_call_graph` - Call graph generation and tracing tool
  - `scan_dependencies` - Dependency vulnerability scanning tool

- `v1.5.0_test_evidence.json` - Test execution evidence:
  - 203 tests across v1.5.0 features
  - 100% pass rate
  - Coverage metrics by component
  - Feature test coverage matrix

## Evidence File Format

Each evidence JSON file follows a structured format documenting:

1. **Tool Specifications** (for MCP tool evidence)
   - Tool name and description
   - Parameters and return types
   - Capabilities and supported ecosystems
   - Test counts and coverage percentages

2. **Test Evidence** (for test execution evidence)
   - Total test count and pass rate
   - Test breakdown by component
   - Feature verification matrix
   - Code quality metrics

## Using These Files

These evidence files serve as:
- **Audit Trail**: Documented proof of feature completeness
- **Regression Testing**: Baseline for comparing across versions
- **Quality Metrics**: Performance and coverage data
- **Release Verification**: Checklist verification for acceptance criteria

For complete release information, see:
- [RELEASE_NOTES_v1.5.0.md](../RELEASE_NOTES_v1.5.0.md) - v1.5.0 Release Notes
- [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md) - Acceptance Criteria & Roadmap

## Adding New Releases

When creating evidence for a new release:

1. Create a new directory: `v{MAJOR}.{MINOR}.{PATCH}/`
2. Follow the naming convention: `v{VERSION}_{type}_evidence.json`
3. Include tool specifications, test counts, and coverage metrics
4. Update this README with the new version section

Example:
```
v1.6.0/
├── v1.6.0_mcp_tools_evidence.json
├── v1.6.0_test_evidence.json
└── v1.6.0_performance_evidence.json
```
