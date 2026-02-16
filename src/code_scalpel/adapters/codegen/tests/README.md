# Codegen Adapter Tests

[20260216_TEST] Comprehensive test suite for all Codegen adapter modules

## Overview

This directory contains tests for all Codegen adapter modules in Code Scalpel. The tests validate:

1. **Import Validation**: All adapters can be imported without errors
2. **Function Existence**: All expected functions/classes exist
3. **Passthrough Behavior**: Functions correctly pass through to Codegen SDK
4. **Docstring Coverage**: All functions have proper docstrings with tier annotations
5. **Module Re-exports**: Module-level re-exports work correctly

## Test Files

| Test File | Coverage |
|-----------|----------|
| `test_all_imports.py` | Validates all adapter imports work |
| `test_codegen_codebase_analysis.py` | Tests for codebase analysis adapter |
| `test_codegen_tools.py` | Tests for tools adapter |
| `test_codegen_mcp.py` | Tests for MCP adapter |
| `test_codegen_lsp.py` | Tests for LSP adapter |
| `test_codegen_codebase.py` | Tests for Codebase class adapter |

## Running Tests

### Run All Adapter Tests
```bash
pytest src/code_scalpel/adapters/codegen/tests/
```

### Run Specific Test File
```bash
pytest src/code_scalpel/adapters/codegen/tests/test_codegen_tools.py
```

### Run With Coverage
```bash
pytest --cov=src/code_scalpel/adapters/codegen src/code_scalpel/adapters/codegen/tests/
```

### Run Verbose
```bash
pytest -vv src/code_scalpel/adapters/codegen/tests/
```

## Test Strategy

### Mocking Approach
Tests use `unittest.mock.patch` to mock Codegen SDK imports. This allows:
- Testing without requiring full Codegen installation
- Fast test execution
- Isolation from Codegen SDK changes
- Focus on adapter behavior, not Codegen SDK behavior

### Example Test Pattern
```python
@patch("code_scalpel.adapters.codegen.codegen_tools._commit")
def test_commit_passthrough(self, mock_commit):
    """Test that commit passes through to Codegen SDK"""
    from code_scalpel.adapters.codegen.codegen_tools import commit

    mock_commit.return_value = {"status": "success"}
    result = commit("test message")

    mock_commit.assert_called_once_with("test message")
    assert result == {"status": "success"}
```

## Test Coverage Goals

- **Import Tests**: 100% coverage of all adapter modules
- **Function Tests**: 100% coverage of all exported functions
- **Passthrough Tests**: Validate all functions correctly pass arguments
- **Docstring Tests**: Validate all functions have proper documentation

## Adding New Tests

When adding a new adapter:

1. Create `test_codegen_<adapter_name>.py`
2. Follow the existing test pattern
3. Include:
   - Import validation test
   - Function existence tests
   - Passthrough behavior tests
   - Docstring validation tests
4. Add to `test_all_imports.py`

## CI/CD Integration

These tests are part of the main test suite and run on:
- Every commit
- Every pull request
- Before releases

## Notes

- Tests use mocking to avoid requiring Codegen SDK installation
- Tests focus on adapter behavior, not Codegen SDK functionality
- All tests should be fast (<1s per test file)
- Tests validate the adapter contract, not implementation details

