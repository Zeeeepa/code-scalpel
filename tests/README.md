# Code Scalpel Test Suite

This document describes the test suite organization and how to run tests.

## Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=code_scalpel --cov-report=html

# Run specific categories (see below)
pytest tests/core/          # Core parsers and analysis
pytest tests/tools/         # MCP tool tests
pytest tests/mcp/           # MCP protocol tests
pytest tests/integration/   # Integration tests
```

## Test Categories

### Core Tests (`tests/core/`)
Parser logic, import resolution, config loading, and fundamental analysis.

**Speed**: Fast (< 30 seconds)
**Dependencies**: No external services

Key directories:
- `tests/core/parsers/` - Parser unit tests
- `tests/core/test_config_loader.py` - Configuration loading
- `tests/core/test_import_resolver.py` - Import resolution logic

### Tools Tests (`tests/tools/`)
MCP tool contract validation and tier-based access control.

**Speed**: Moderate (1-3 minutes)
**Dependencies**: License JWTs required for tier tests

Key directories:
- `tests/tools/individual/` - Per-tool validation (call graphs, extractors, etc.)
- `tests/tools/tiers/` - Tier-based access control (Community/Pro/Enterprise)
- `tests/tools/security_scan/` - Security scanning tool tests
- `tests/tools/rename_symbol/` - Symbol renaming tool tests
- `tests/tools/oracle/` - Oracle AI integration tests
- `tests/tools/validation/` - Import path and tool compliance validation

### MCP Tests (`tests/mcp/`)
MCP protocol-level tests: tool contracts, resources, REST API, and middleware.

**Speed**: Moderate (1-2 minutes)
**Dependencies**: MCP transport setup

Key files:
- `tests/mcp/test_mcp.py` - Core MCP protocol tests
- `tests/mcp/test_mcp_all_tools_contract.py` - All-tools contract validation (3 transports)
- `tests/mcp/test_mcp_resources.py` - MCP resource tests
- `tests/mcp/test_rest_api_server.py` - REST API server tests
- `tests/mcp/test_oracle_middleware.py` - Oracle middleware tests

### MCP Transport Contract Test

The file `test_mcp_all_tools_contract.py` validates all 35+ MCP tools across 3 transports:
- `stdio` - Standard I/O transport
- `streamable-http` - HTTP streaming transport
- `sse` - Server-Sent Events transport

Run with transport selection:
```bash
MCP_CONTRACT_TRANSPORT=stdio pytest tests/mcp/test_mcp_all_tools_contract.py
MCP_CONTRACT_TRANSPORT=streamable-http pytest tests/mcp/test_mcp_all_tools_contract.py
MCP_CONTRACT_TRANSPORT=sse pytest tests/mcp/test_mcp_all_tools_contract.py
```

### Integration Tests (`tests/integration/`)
End-to-end integration scenarios combining multiple components.

**Speed**: Slow (2-5 minutes)
**Dependencies**: May require file system access

### Security Tests (`tests/pdg_tools/security/`)
Adversarial and security analysis tests for the PDG (Program Dependency Graph) tools.

**Speed**: Moderate (1-2 minutes)

### Coverage Tests (`tests/coverage/`)
Tests specifically targeting coverage gaps. These ensure code coverage meets thresholds.

**Speed**: Moderate (1-3 minutes)

### CLI Tests (`tests/cli/`)
Command-line interface tests.

**Speed**: Fast (< 30 seconds)

## License Requirements

Tests in `tests/tools/tiers/` and `tests/capabilities/` require valid JWT licenses.

### In CI
Licenses are automatically injected via GitHub Secrets. See [docs/GITHUB_SECRETS.md](../docs/GITHUB_SECRETS.md).

### Locally
Option 1: Set environment variable
```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/your/license.jwt
pytest tests/tools/tiers/
```

Option 2: Mock the tier
```bash
# Tests without valid license will skip tier-specific assertions
pytest tests/tools/tiers/ -v
```

## Shared Fixtures

Pytest fixtures shared across tests are defined in conftest.py files at various levels:
- `tests/tools/get_graph_neighborhood/conftest.py` - Graph neighborhood fixtures
- `tests/tools/get_project_map/conftest.py` - Project map fixtures
- `tests/tools/rename_symbol/conftest.py` - Symbol rename fixtures
- `tests/tools/oracle/conftest.py` - Oracle integration fixtures
- `tests/tools/update_symbol/conftest.py` - Symbol update fixtures

## Test Configuration

Test settings are in [pytest.ini](../pytest.ini). Key settings:
- Default timeout: 600 seconds per test
- Asyncio mode: auto
- Coverage source: `code_scalpel`

## Adding New Tests

When adding new tests:
1. Place them in the appropriate category directory (see above)
2. Follow existing naming conventions: `test_<feature>.py`
3. Use shared fixtures from conftest.py where applicable
4. Ensure tests pass with `pytest tests/<your-file>.py -v`
5. Run `./scripts/verify.sh` to verify full suite passes
