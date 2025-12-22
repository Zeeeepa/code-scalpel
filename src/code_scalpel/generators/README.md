# Generators Module

**Purpose:** Code generation and simulation tools

## Overview

This module provides tools for:
- Test case generation from symbolic execution
- Refactoring simulation and safety verification
- Code transformation and template generation

## Key Components

### test_generator.py (34,549 LOC)
Generates unit tests from symbolic execution paths:
- `TestGenerationResult` - Test case data structure
- `GeneratedTestCase` - Individual test with inputs/assertions
- Pytest and unittest format generation
- Coverage-driven test selection
- Symbolic path exploration for edge cases

**Key Features:**
- Automatically discovers execution paths
- Generates concrete input values that trigger each path
- Creates assertions based on expected outputs
- Supports pytest and unittest frameworks

**Example:**
```python
from code_scalpel.generators import TestGenerator

generator = TestGenerator()
result = generator.generate_tests(
    code="def calculate(x): return x * 2 if x > 0 else 0",
    function_name="calculate",
    framework="pytest"
)
print(result.pytest_code)
```

### refactor_simulator.py (18,773 LOC)
Simulates code refactoring to verify safety before applying:
- `RefactorSimulationResult` - Safety verdict and analysis
- Structural change detection (function renames, signature changes)
- Security issue detection (new vulnerabilities introduced)
- Behavioral equivalence verification
- Diff-based and direct code comparison

**Key Features:**
- Detects breaking changes before applying refactors
- Identifies new security vulnerabilities
- Verifies behavioral preservation
- Supports both patch and direct code comparison

**Example:**
```python
from code_scalpel.generators import RefactorSimulator

simulator = RefactorSimulator()
result = simulator.simulate_refactor(
    original_code="def add(a, b): return a + b",
    new_code="def add(a: int, b: int) -> int: return a + b"
)
assert result.is_safe  # Type hints are safe
```

## Integration

Used by:
- `mcp/server.py` - MCP tools: `generate_unit_tests`, `simulate_refactor`
- `symbolic_execution_tools/engine.py` - Symbolic execution backend
- `autonomy/` - Automated refactoring workflows

## Architecture

Both modules rely on:
- **Symbolic Execution:** `symbolic_execution_tools/engine.py` for path exploration
- **Security Analysis:** `symbolic_execution_tools/security_analyzer.py` for vulnerability detection
- **AST Analysis:** `ast_tools/analyzer.py` for structural analysis
- **PDG Analysis:** `pdg_tools/analyzer.py` for control/data flow

## v3.0.5 Status

- Test generation: Stable, 100% coverage
- Refactor simulation: Stable, 100% coverage
- Supports Python, JavaScript, TypeScript, Java
