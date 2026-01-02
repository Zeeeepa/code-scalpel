# Test Organization Structure

[20251227_REFACTOR] Tests organized into logical subdirectories for easier maintenance and targeted testing.

## Directory Structure

```
tests/
├── mcp/                    # MCP server and transport tests (23 tests)
│   ├── test_mcp.py
│   ├── test_mcp_transports_end_to_end.py
│   ├── test_mcp_http_transport_endpoints.py
│   └── ...
├── tools/                  # Tool-specific tests
│   ├── tiers/             # Tier-based feature tests (24 tests)
│   │   ├── test_analyze_code_tiers.py
│   │   ├── test_extract_code_tiers.py
│   │   ├── test_security_scan_tiers.py
│   │   └── ...
│   └── individual/        # Individual tool functionality tests (16 tests)
│       ├── test_get_call_graph.py
│       ├── test_get_project_map.py
│       ├── test_scan_dependencies.py
│       └── ...
├── autonomy/              # Autonomy engine tests (18 tests)
│   ├── test_autonomy_engine_integration.py
│   ├── test_policy_engine.py
│   ├── test_sandbox.py
│   └── ...
├── agents/                # Agent framework integration tests (14 tests)
│   ├── test_agents.py
│   ├── test_autogen_scalpel.py
│   ├── test_crewai_integration.py
│   └── ...
├── core/                  # Core functionality tests
│   ├── ast/              # AST analysis tests (7 tests)
│   ├── pdg/              # PDG tests (7 tests)
│   ├── parsers/          # Parser tests (28 tests)
│   ├── cache/            # Cache tests (2 tests)
│   └── *.py              # Misc core tests (7 tests)
├── security/              # Security scanning tests (18 tests)
│   ├── test_security_scan.py
│   ├── test_adversarial.py
│   ├── test_taint_tracker.py
│   └── ...
├── symbolic/              # Symbolic execution tests (9 tests)
│   ├── test_symbolic_state.py
│   ├── test_constraint_solver.py
│   └── ...
├── cli/                   # CLI tests (4 tests)
├── integration/           # Integration tests (14 tests)
├── coverage/              # Coverage/quality tests (26 tests)
└── licensing/             # License tier tests (existing)
```

## Test Count Summary

| Category | Count | Status |
|----------|-------|--------|
| **MCP** | 23 | ✅ Most working |
| **Tools (Tiers)** | 24 | ⚠️ Need MCP server mock |
| **Tools (Individual)** | 16 | ⚠️ Need MCP server mock |
| **Autonomy** | 18 | ✅ Working |
| **Agents** | 14 | ⚠️ Some import issues |
| **Core (AST)** | 7 | ✅ Working |
| **Core (PDG)** | 7 | ✅ Working |
| **Core (Parsers)** | 28 | ✅ Working |
| **Core (Cache)** | 2 | ✅ Working |
| **Core (Other)** | 7 | ✅ Working |
| **Security** | 18 | ✅ Working |
| **Symbolic** | 9 | ✅ Working |
| **CLI** | 4 | ✅ Working |
| **Integration** | 14 | ✅ Working |
| **Coverage** | 26 | ✅ Working |
| **Licensing** | 10 | ✅ Fixed and working |
| **Total** | **217** | **~180 working (83%)** |

## Known Issues

### Import Errors (37 tests)

**MCP Server Dependency:**
- Files: `tests/tools/tiers/test_*_tiers.py` (24 files)
- Files: `tests/tools/individual/test_*.py` (13 files)
- Error: `ModuleNotFoundError: No module named 'mcp.server'`
- Cause: Missing `fastmcp` or `mcp` package installation
- Fix: Install dependencies or mock MCP server imports

**Command to install:**
```bash
pip install mcp fastmcp
```

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run specific category:
```bash
pytest tests/mcp/                  # MCP tests only
pytest tests/tools/tiers/          # Tier tests only
pytest tests/tools/individual/     # Individual tool tests
pytest tests/licensing/            # Licensing tests
pytest tests/security/             # Security tests
pytest tests/core/                 # Core functionality tests
```

### Run excluding problematic tests:
```bash
pytest tests/ --ignore=tests/mcp_tool_verification --ignore=tests/agents/test_base_agent_errors.py
```

### Run specific test file:
```bash
pytest tests/licensing/test_jwt_integration.py -v
```

## Benefits of Organization

1. **Targeted Testing:** Run only tests for the component you're working on
2. **Faster Iteration:** Test specific functionality without full suite
3. **Better Maintenance:** Clear ownership of test files
4. **Easier Debugging:** Find tests related to specific features quickly
5. **Parallel Execution:** Run different categories in parallel

## Migration Notes

- All test files moved from `tests/` root to subdirectories
- Original directory structure preserved (licensing/, fixtures/, etc.)
- `__init__.py` files created for all new subdirectories
- No changes to test content or imports within test files
- conftest.py and other non-test files remain in root

## Next Steps

1. ✅ Fix licensing tests (COMPLETED - 10/10 passing)
2. ⏳ Install MCP dependencies to fix tier tests
3. ⏳ Fix agent import errors
4. ⏳ Re-run full test suite validation
5. ⏳ Update CI/CD to test categories independently

## Test Categories by Priority

### P0 - Critical (Must Pass for Release)
- `tests/licensing/` - License tier validation
- `tests/security/` - Security vulnerability detection
- `tests/core/` - Core functionality

### P1 - High (Should Pass)
- `tests/tools/` - Tool functionality and tiers
- `tests/mcp/` - MCP server integration
- `tests/symbolic/` - Symbolic execution

### P2 - Medium (Nice to Have)
- `tests/autonomy/` - Autonomy features
- `tests/agents/` - Agent integrations
- `tests/integration/` - Integration tests

### P3 - Low (Quality/Coverage)
- `tests/coverage/` - Coverage tracking
- `tests/cli/` - CLI functionality
