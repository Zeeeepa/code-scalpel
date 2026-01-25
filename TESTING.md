# Code Scalpel Testing Strategy v1.0.1

This document describes the comprehensive testing approach for Code Scalpel, covering all 22 tools, tier-based feature gating, and MCP protocol compliance.

## Table of Contents

1. [Overview](#overview)
2. [Test Organization](#test-organization)
3. [Testing Tiers](#testing-tiers)
4. [Test Categories](#test-categories)
5. [Running Tests](#running-tests)
6. [Continuous Integration](#continuous-integration)
7. [Adding New Tests](#adding-new-tests)

## Overview

Code Scalpel's test suite validates:

- **All 22 Tools**: Complete functionality for each MCP tool
- **Tier Limits**: Community/Pro/Enterprise limits enforced correctly
- **Feature Gating**: Capabilities available only at appropriate tiers
- **MCP Protocol**: Compliance with MCP response envelope requirements
- **Language Support**: Polyglot language capabilities per tool
- **Integration**: Cross-tool workflows and data consistency
- **Performance**: Large-scale operations and timeout handling

### Statistics

- **Total Tests**: 7,900+ (as of v1.0.1)
- **Test Files**: 44+ dedicated test files
- **Coverage**: ≥90% for all core tools
- **Tiers Tested**: Community, Pro, Enterprise (3 tiers × 22 tools)

## Test Organization

### Directory Structure

```
tests/
├── tools/
│   ├── tiers/                          # Tier-specific tests (21 files)
│   │   ├── test_analyze_code_tiers.py
│   │   ├── test_code_policy_check_tiers.py
│   │   ├── test_validate_paths_tiers.py
│   │   └── ... (18 more)
│   │
│   ├── individual/                     # Per-tool functionality tests
│   │   └── test_*.py
│   │
│   └── {tool_name}/                    # Tool-specific test directories
│       ├── test_core_functionality.py
│       ├── test_edge_cases.py
│       └── conftest.py (optional)
│
├── limits/                              # Configuration testing
│   ├── test_limits_toml_loading.py      # Config file discovery/merging
│   └── test_limits_enforcement.py       # Boundary testing
│
├── features/                            # Feature gating tests
│   ├── test_features_capability_gating.py
│   └── test_features_tier_inheritance.py
│
├── languages/                           # Polyglot language support
│   └── test_polyglot_support.py
│
├── integration/                         # Cross-tool workflows
│   └── test_tool_pipelines.py
│
├── mcp/                                 # MCP protocol tests
│   ├── test_mcp_all_tools_protocol.py
│   └── test_mcp_error_handling.py
│
├── utils/
│   ├── tier_setup.py                   # Tier activation fixtures
│   ├── config_loaders.py               # Config file loading helpers
│   └── ... (other helpers)
│
└── conftest.py                         # Global test configuration
```

## Testing Tiers

### Community Tier Testing

Community tier tests verify:
- Strict numeric limits (100 files, 3 depth, 50 findings, etc.)
- Basic features only (no advanced analysis)
- Graceful handling of limit boundaries
- No marketing upsells or hidden features

**Example**:
```python
def test_extract_code_community_max_depth_zero(community_tier):
    """Community tier does not allow cross-file dependency extraction."""
    caps = get_tool_capabilities("extract_code", "community")
    assert caps["limits"]["max_depth"] == 0
```

### Pro Tier Testing

Pro tier tests verify:
- Mid-range limits (1000 files, 50 depth, unlimited findings)
- Extended features (context-aware analysis, multiple frameworks)
- Correct upgrade path from Community

**Example**:
```python
def test_extract_code_pro_allows_one_level_deps(pro_tier):
    """Pro tier allows limited cross-file extraction."""
    caps = get_tool_capabilities("extract_code", "pro")
    assert caps["limits"]["max_depth"] == 1
```

### Enterprise Tier Testing

Enterprise tier tests verify:
- No numeric limits (None values)
- All features enabled (custom rules, governance, etc.)
- Highest capability tier

**Example**:
```python
def test_extract_code_enterprise_unlimited(enterprise_tier):
    """Enterprise tier allows unlimited cross-file extraction."""
    caps = get_tool_capabilities("extract_code", "enterprise")
    assert caps["limits"]["max_depth"] is None
```

## Test Categories

### 1. Tool Functionality Tests

**Location**: `tests/tools/individual/` and tool-specific directories

**Purpose**: Verify each tool works correctly with valid inputs

**Coverage**:
- Happy path scenarios
- Edge cases (empty input, max input, special characters)
- Error handling (file not found, invalid syntax, timeout)
- Output schema validation

**Example**:
```python
@pytest.mark.asyncio
async def test_analyze_code_complexity_metrics():
    """analyze_code should calculate cyclomatic complexity."""
    result = await analyze_code(code="def f(): return 1")
    assert result.complexity >= 1
```

### 2. Tier Limit Tests

**Location**: `tests/tools/tiers/test_*_tiers.py`

**Purpose**: Verify limits are enforced per tier

**Coverage**:
- Community tier hard limits
- Pro tier higher limits
- Enterprise tier unlimited (None)
- Numeric progression (community ≤ pro ≤ enterprise)

**Example**:
```python
@pytest.mark.parametrize("tier,expected_limit", [
    ("community", 3),
    ("pro", 50),
    ("enterprise", None),
])
def test_get_call_graph_depth_limits(tier, expected_limit):
    caps = get_tool_capabilities("get_call_graph", tier)
    assert caps["limits"]["max_depth"] == expected_limit
```

### 3. Feature Gating Tests

**Location**: `tests/features/test_features_capability_gating.py`

**Purpose**: Verify features are available only at appropriate tiers

**Coverage**:
- Basic features (all tiers)
- Extended features (Pro+)
- Governance/compliance features (Enterprise only)
- Correct inheritance across tiers

**Example**:
```python
def test_code_policy_check_hipaa_compliance_enterprise_only():
    """HIPAA compliance checking is Enterprise-only."""
    assert has_capability("code_policy_check", "hipaa_compliance", "enterprise")
    assert not has_capability("code_policy_check", "hipaa_compliance", "community")
```

### 4. Configuration Tests

**Location**: `tests/limits/` and `tests/features/`

**Purpose**: Verify limits.toml and features.py are consistent

**Coverage**:
- limits.toml loads correctly
- Configuration cascading works
- All tools documented
- Tier progression is monotonic
- Omission semantics (None = unlimited)

**Example**:
```python
def test_limits_toml_tier_progression():
    """Each tier should have >= limits than previous tier."""
    community = get_tier_limit("get_project_map", "community", "max_files")
    pro = get_tier_limit("get_project_map", "pro", "max_files")
    assert pro >= community
```

### 5. MCP Protocol Tests

**Location**: `tests/mcp/test_mcp_all_tools_protocol.py`

**Purpose**: Verify MCP protocol compliance

**Coverage**:
- Response envelope (tier, applied_limits, metadata)
- Error response format
- Parameter validation
- JSON serialization
- All tools in schema

**Example**:
```python
@pytest.mark.asyncio
async def test_tool_response_includes_tier():
    """All tool responses should include tier field."""
    result = await extract_code(...)
    assert "tier" in result
    assert result["tier"] in ["community", "pro", "enterprise"]
```

### 6. Integration Tests

**Location**: `tests/integration/test_tool_pipelines.py`

**Purpose**: Test cross-tool workflows

**Coverage**:
- Tool chaining (call_graph → neighborhood → security_scan)
- Data consistency across tools
- Tier limits in pipelines
- Error propagation
- Large-scale operations

**Example**:
```python
@pytest.mark.asyncio
async def test_graph_pipeline():
    """Test: call_graph → neighborhood → security_scan"""
    # 1. Get call graph
    graph = await get_call_graph(...)

    # 2. Extract neighborhood
    neighborhood = await get_graph_neighborhood(
        center_node_id=graph.nodes[0],
        k=2
    )

    # 3. Run security scan
    findings = await security_scan(code=neighborhood.code)

    # Verify consistency
```

### 7. Language Support Tests

**Location**: `tests/languages/test_polyglot_support.py`

**Purpose**: Verify language support claims are accurate

**Coverage**:
- Supported languages work correctly
- Unsupported languages handled gracefully
- Language-specific vulnerabilities detected
- Multi-language projects handled
- Language roadmap tracking

**Example**:
```python
def test_security_scan_python_full_support():
    """Python should have full SQL injection detection."""
    code = "cursor.execute(f'SELECT * FROM users WHERE id = {id}')"
    result = security_scan(code)
    assert any("SQL injection" in f.title for f in result.findings)
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Tests for Specific Tool

```bash
pytest tests/tools/extract_code/
pytest tests/tools/tiers/test_extract_code_tiers.py
```

### Run Tests by Category

```bash
# Tier tests
pytest tests/tools/tiers/

# Feature tests
pytest tests/features/

# Configuration tests
pytest tests/limits/

# Integration tests
pytest tests/integration/

# Language tests
pytest tests/languages/

# MCP protocol tests
pytest tests/mcp/test_mcp_all_tools_protocol.py
```

### Run Tests for Specific Tier

```bash
# Community tier only
pytest tests/ -k "community_tier"

# Pro tier only
pytest tests/ -k "pro_tier"

# Enterprise tier only
pytest tests/ -k "enterprise_tier"
```

### Run with Verbose Output

```bash
pytest tests/ -v --tb=short
```

### Run Slow Tests (large-scale)

```bash
pytest tests/ -m slow
```

### Generate Coverage Report

```bash
pytest tests/ --cov=src/code_scalpel --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

### GitHub Actions Workflow

All tests run on:
- Every commit (unit/integration tests)
- Pull requests (full suite)
- Nightly (performance tests, large-scale tests)

**Expected Status**:
- Unit tests: <5 minutes
- Integration tests: <10 minutes
- Full suite: <30 minutes

### Test Requirements

- **Python**: 3.10+
- **Dependencies**: pytest, pytest-asyncio
- **Licenses**: Pro/Enterprise test licenses required (in tests/licenses/)

### CI Secrets Required

```
CODE_SCALPEL_LICENSE_PATH: Path to Pro license JWT
CODE_SCALPEL_SECRET_KEY: HS256 secret for signing test licenses
```

## Adding New Tests

### When to Add Tests

Add tests when:
- Adding a new tool
- Adding new tier functionality
- Fixing a bug
- Supporting new language
- Changing limits or features
- Updating configuration

### Test Template

```python
"""Tests for {tool_name} MCP tool.

Tests verify {specific aspect being tested}.

[{DATE}_TEST] Created/updated by {author}
"""

from __future__ import annotations
import pytest


class Test{ToolName}{Aspect}:
    """Test {aspect} for {tool_name}."""

    @pytest.mark.asyncio
    async def test_specific_scenario(self, community_tier):
        """Specific behavior to verify."""
        # Arrange
        from code_scalpel.mcp.server import tool_name

        # Act
        result = await tool_name(...)

        # Assert
        assert result.expected_field == expected_value
```

### Test Naming Convention

- `test_<tool>_<tier>_<aspect>`
- `test_<tool>_<feature>_available`
- `test_<tool>_<limit>_enforcement`

**Examples**:
- `test_extract_code_community_no_cross_file_deps`
- `test_security_scan_context_aware_scanning_pro_only`
- `test_get_call_graph_depth_clamping`

### Fixtures to Use

```python
# Tier activation
def test_something(community_tier):
    """Automatically activates Community tier for test."""
    pass

def test_something(pro_tier):
    """Automatically activates Pro tier for test."""
    pass

def test_something(enterprise_tier):
    """Automatically activates Enterprise tier for test."""
    pass

# Configuration loading
from tests.utils.config_loaders import (
    load_limits_toml,
    get_tool_capabilities,
    get_tier_limit,
)
```

## Troubleshooting Tests

### Common Issues

#### License Files Not Found

```
pytest.skip: No valid pro license file found for tests
```

**Solution**: Generate test licenses or use mock tier fixtures:
```bash
make generate-test-licenses
```

#### Tier Cache Leakage

**Solution**: Use `clear_tier_cache` fixture (autouse):
```python
@pytest.fixture(autouse=True)
def clear_tier_cache():
    # Automatically runs before each test
```

#### Timeout Errors

**Solution**: Check for infinite loops in test code, or use `@pytest.mark.timeout(30)`:
```python
@pytest.mark.timeout(30)
def test_something():
    """This test must complete in 30 seconds."""
    pass
```

## Test Coverage Goals

### Current Coverage (v1.0.1)

- **Core tools**: ≥90%
- **Tier enforcement**: ≥95%
- **Feature gating**: ≥90%
- **MCP protocol**: ≥85%

### Coverage by Tool

See individual `TEST_SUMMARY.md` in each tool directory:
- `tests/tools/extract_code/TEST_SUMMARY.md`
- `tests/tools/security_scan/TEST_SUMMARY.md`
- etc.

## Documentation

### Test Documentation

Each test file should include:
- Module docstring explaining what is being tested
- Test class docstrings (for grouped tests)
- Test function docstrings (one-line summary)
- Comments for non-obvious test logic

### Test README Files

Tool-specific directories should have `TEST_SUMMARY.md`:
```markdown
# Extract Code Test Summary

## Test Coverage
- Functionality: 95%
- Edge Cases: 90%
- Tier Enforcement: 100%

## Test Files
- test_core_functionality.py: 42 tests
- test_edge_cases.py: 18 tests
- test_tier_enforcement.py: 15 tests

## Known Limitations
- Cross-repo extraction not tested (needs network)
- Large-scale tests need 10GB disk space
```

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Code Scalpel Architecture](./ARCHITECTURE.md)
- [Tier System Documentation](./docs/TIERS.md)
- [Tool Documentation](./docs/roadmaps/)
