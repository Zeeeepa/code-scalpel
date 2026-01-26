# Symbolic Tools

Advanced code analysis and testing tools for symbolic execution, test generation, and refactoring simulation.

**Tools in this category:**
- `symbolic_execute` - Perform symbolic execution to explore code paths and find constraints
- `generate_unit_tests` - Generate unit tests from code using symbolic execution
- `simulate_refactor` - Simulate code changes and detect potential safety issues

---

## symbolic_execute

Perform symbolic execution on code to explore execution paths and analyze constraints.

### Overview

`symbolic_execute` analyzes code using symbolic execution techniques to:
- Explore multiple execution paths through code
- Identify and track constraints
- Support loop unrolling with configurable depth
- Handle various data types (Community: basic types; Pro+: complex types)
- Optimize path exploration (Pro+: smart prioritization)

**Use cases:**
- Find all possible code paths through a function
- Understand constraint systems and variable dependencies
- Test edge cases by exploring symbolic paths
- Detect unreachable code or dead branches
- Verify control flow properties

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `code` | string | Yes | ✓ | ✓ | ✓ | Python source code to analyze |
| `max_paths` | integer | No | ✓ (50) | ✓ | ✓ | Maximum execution paths to explore |
| `max_depth` | integer | No | ✓ (10) | ✓ (100) | ✓ | Maximum loop unroll depth |

#### Tier-Specific Constraints

**Community:**
- Max paths: 50 (configurable, but capped at 50)
- Max depth: 10 loop iterations
- Constraint types: `int`, `bool`, `string`, `float`
- Basic symbolic execution only
- Simple constraints

**Pro:**
- Max paths: Unlimited
- Max depth: 100 loop iterations
- Constraint types: All basic types + `list`, `dict`
- Smart path prioritization
- Constraint optimization
- Concolic execution (concrete + symbolic)

**Enterprise:**
- Max paths: Unlimited
- Max depth: Unlimited loop unrolling
- Constraint types: All types including complex objects
- Custom solvers
- Formal verification
- Equivalence checking
- Distributed execution
- Memory modeling

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "symbolic_execute",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "paths_explored": 12,
    "max_paths_limit": 50,
    "execution_paths": [
      {
        "path_id": 1,
        "constraints": [
          "x > 0",
          "y < 100"
        ],
        "return_value": "true",
        "branch_taken": "if x > 0"
      }
    ],
    "coverage_metrics": {
      "branches_covered": 8,
      "total_branches": 10,
      "coverage_percentage": 80
    },
    "constraint_summary": {
      "total_constraints": 24,
      "constraint_types": ["int_comparison", "bool_expr", "string_match"],
      "unresolvable_constraints": 0
    }
  }
}
```

#### Tier-Specific Output Variations

**Community:**
- Limited to 50 paths maximum
- Basic constraint tracking
- Paths for simple data types only

**Pro:**
- Unlimited path exploration
- Smart path ordering (prioritized by likelihood)
- Complex type support (lists, dicts)
- Concolic execution results included

**Enterprise:**
- Distributed execution results
- Memory state modeling
- Formal verification results
- Custom solver metrics

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max paths** | 50 | Unlimited | Unlimited |
| **Max loop depth** | 10 | 100 | Unlimited |
| **Basic types** | ✓ | ✓ | ✓ |
| **List/Dict types** | ✗ | ✓ | ✓ |
| **Complex object types** | ✗ | ✗ | ✓ |
| **Smart path prioritization** | ✗ | ✓ | ✓ |
| **Constraint optimization** | ✗ | ✓ | ✓ |
| **Concolic execution** | ✗ | ✓ | ✓ |
| **Custom solvers** | ✗ | ✗ | ✓ |
| **Formal verification** | ✗ | ✗ | ✓ |
| **Distributed execution** | ✗ | ✗ | ✓ |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid code or parameters
- `not_implemented` - Language or feature not supported
- `timeout` - Symbolic execution timeout
- `resource_exhausted` - Hit path limit (Community only)
- `internal_error` - Execution error

### Example Requests & Responses

#### Example 1: Simple Path Exploration (Community)

**Request:**
```json
{
  "code": "def classify_number(x):\n    if x > 0:\n        return 'positive'\n    elif x < 0:\n        return 'negative'\n    else:\n        return 'zero'",
  "max_paths": 3,
  "max_depth": 5
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "symbolic_execute",
  "duration_ms": 120,
  "data": {
    "success": true,
    "paths_explored": 3,
    "max_paths_limit": 50,
    "execution_paths": [
      {
        "path_id": 1,
        "constraints": ["x > 0"],
        "return_value": "'positive'",
        "branch_taken": "if x > 0"
      },
      {
        "path_id": 2,
        "constraints": ["x < 0"],
        "return_value": "'negative'",
        "branch_taken": "elif x < 0"
      },
      {
        "path_id": 3,
        "constraints": ["x == 0"],
        "return_value": "'zero'",
        "branch_taken": "else"
      }
    ],
    "coverage_metrics": {
      "branches_covered": 3,
      "total_branches": 3,
      "coverage_percentage": 100
    }
  }
}
```

#### Example 2: Complex Constraints with Lists (Pro)

**Request:**
```json
{
  "code": "def process_list(items, threshold):\n    result = []\n    for item in items:\n        if item > threshold:\n            result.append(item * 2)\n        else:\n            result.append(item)\n    return result",
  "max_paths": null,
  "max_depth": 50
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "symbolic_execute",
  "duration_ms": 450,
  "data": {
    "success": true,
    "paths_explored": 256,
    "max_paths_limit": null,
    "execution_paths": [
      {
        "path_id": 1,
        "constraints": [
          "len(items) == 0"
        ],
        "return_value": "[]",
        "branch_taken": "empty list"
      },
      {
        "path_id": 2,
        "constraints": [
          "len(items) > 0",
          "items[0] > threshold"
        ],
        "return_value": "[items[0] * 2, ...]",
        "branch_taken": "if item > threshold"
      }
    ],
    "coverage_metrics": {
      "branches_covered": 2,
      "total_branches": 2,
      "coverage_percentage": 100
    },
    "constraint_summary": {
      "total_constraints": 256,
      "constraint_types": ["list_operation", "int_comparison"],
      "unresolvable_constraints": 0
    },
    "concolic_metrics": {
      "concrete_tests_generated": 8,
      "hybrid_execution_paths": 248
    }
  }
}
```

### Performance Considerations

- **Community** (50 paths max): 50-300ms
- **Pro** (unlimited paths): 200-2000ms depending on code complexity
- **Enterprise** (distributed): 500-5000ms

### Upgrade Paths

**Community → Pro:**
- Unlimited path exploration (from 50 paths)
- Deep loop unrolling (100 iterations)
- Complex type support (lists, dicts)
- Smart path prioritization

**Pro → Enterprise:**
- Unlimited loop depth
- Custom solvers
- Formal verification
- Distributed execution across multiple cores

---

## generate_unit_tests

Generate unit tests from code using symbolic execution and constraint analysis.

### Overview

`generate_unit_tests` automatically creates test cases by analyzing code paths and constraints:
- Generate tests from functions using symbolic execution
- Support multiple testing frameworks (pytest, unittest, etc.)
- Data-driven tests with parameterized inputs (Pro+)
- Bug reproduction from crash logs (Enterprise)
- Edge case detection (Pro+)
- Custom test templates (Enterprise)

**Use cases:**
- Generate initial test suite for untested functions
- Create parameterized tests for multiple input scenarios
- Generate tests from crash logs to reproduce bugs
- Improve test coverage with edge cases
- Bootstrap test infrastructure

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `code` | string | No | ✓ | ✓ | ✓ | Function source code (or use `file_path`) |
| `file_path` | string | No | ✓ | ✓ | ✓ | Path to file containing function |
| `function_name` | string | No | ✓ | ✓ | ✓ | Name of function to test |
| `framework` | string | No | ✓ | ✓ | ✓ | Test framework (`pytest`, `unittest`) |
| `data_driven` | boolean | No | ✗ | ✓ | ✓ | Generate parameterized tests |
| `crash_log` | string | No | ✗ | ✗ | ✓ | Crash log for bug reproduction |

#### Tier-Specific Constraints

**Community:**
- Max test cases: 5
- Basic test generation only
- Frameworks: `pytest` only
- No data-driven tests
- No bug reproduction

**Pro:**
- Max test cases: 20
- Advanced test generation with edge cases
- Frameworks: `pytest`, `unittest`
- Data-driven tests available
- No bug reproduction

**Enterprise:**
- Max test cases: Unlimited
- All features available
- Frameworks: All supported
- Data-driven tests included
- Bug reproduction from crash logs
- Custom test templates
- Coverage optimization

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "generate_unit_tests",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "function_name": "calculate_discount",
    "test_count": 5,
    "total_test_cases": 8,
    "framework_used": "pytest",
    "max_test_cases_limit": 5,
    "data_driven_enabled": false,
    "bug_reproduction_enabled": false,
    "tests": [
      {
        "test_id": 1,
        "name": "test_calculate_discount_basic",
        "code": "def test_calculate_discount_basic():\n    assert calculate_discount(100, 0.1) == 90",
        "input": {"price": 100, "discount_rate": 0.1},
        "expected": 90,
        "category": "normal_case"
      }
    ]
  }
}
```

#### Tier-Specific Output Variations

**Community:**
- Max 5 basic tests
- Simple test cases only
- Pytest format

**Pro:**
- Up to 20 tests
- Edge cases included
- Multiple frameworks supported
- Parameterized test format (data-driven)

**Enterprise:**
- Unlimited tests
- Custom templates applied
- All frameworks
- Bug reproduction tests
- Coverage metrics

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Basic test generation** | ✓ | ✓ | ✓ |
| **Max test cases** | 5 | 20 | Unlimited |
| **Test frameworks** | pytest | pytest, unittest | All |
| **Data-driven tests** | ✗ | ✓ | ✓ |
| **Edge case detection** | ✗ | ✓ | ✓ |
| **Bug reproduction** | ✗ | ✗ | ✓ |
| **Custom templates** | ✗ | ✗ | ✓ |
| **Coverage optimization** | ✗ | ✗ | ✓ |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid code or function name
- `not_found` - Function not found
- `not_implemented` - Framework not supported
- `upgrade_required` - Feature (data-driven, bug_reproduction) requires higher tier
- `internal_error` - Test generation error

#### Example Error Response

```json
{
  "tier": "community",
  "tool_id": "generate_unit_tests",
  "duration_ms": 45,
  "error": {
    "error": "Data-driven test generation requires Pro tier or higher.",
    "error_code": "upgrade_required"
  },
  "data": null,
  "upgrade_hints": [
    "Upgrade to Pro tier to enable parameterized/data-driven tests"
  ]
}
```

### Example Requests & Responses

#### Example 1: Basic Test Generation (Community)

**Request:**
```json
{
  "code": "def add(a, b):\n    return a + b",
  "function_name": "add",
  "framework": "pytest"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "generate_unit_tests",
  "duration_ms": 80,
  "data": {
    "success": true,
    "function_name": "add",
    "test_count": 3,
    "total_test_cases": 3,
    "framework_used": "pytest",
    "max_test_cases_limit": 5,
    "data_driven_enabled": false,
    "tests": [
      {
        "test_id": 1,
        "name": "test_add_positive_numbers",
        "code": "def test_add_positive_numbers():\n    assert add(2, 3) == 5",
        "input": {"a": 2, "b": 3},
        "expected": 5,
        "category": "normal_case"
      },
      {
        "test_id": 2,
        "name": "test_add_with_zero",
        "code": "def test_add_with_zero():\n    assert add(5, 0) == 5",
        "input": {"a": 5, "b": 0},
        "expected": 5,
        "category": "edge_case"
      },
      {
        "test_id": 3,
        "name": "test_add_negative_numbers",
        "code": "def test_add_negative_numbers():\n    assert add(-2, -3) == -5",
        "input": {"a": -2, "b": -3},
        "expected": -5,
        "category": "boundary_case"
      }
    ]
  }
}
```

#### Example 2: Data-Driven Tests (Pro)

**Request:**
```json
{
  "code": "def calculate_discount(price, discount_rate):\n    return price * (1 - discount_rate)",
  "function_name": "calculate_discount",
  "framework": "pytest",
  "data_driven": true
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "generate_unit_tests",
  "duration_ms": 250,
  "data": {
    "success": true,
    "function_name": "calculate_discount",
    "test_count": 1,
    "total_test_cases": 8,
    "framework_used": "pytest",
    "max_test_cases_limit": 20,
    "data_driven_enabled": true,
    "tests": [
      {
        "test_id": 1,
        "name": "test_calculate_discount_parameterized",
        "code": "@pytest.mark.parametrize('price,discount_rate,expected', [\n    (100, 0.1, 90),\n    (100, 0.5, 50),\n    (100, 0.0, 100),\n    (0, 0.1, 0),\n    (100, 1.0, 0),\n])\ndef test_calculate_discount_parameterized(price, discount_rate, expected):\n    assert calculate_discount(price, discount_rate) == expected",
        "parameters": [
          {"price": 100, "discount_rate": 0.1, "expected": 90},
          {"price": 100, "discount_rate": 0.5, "expected": 50},
          {"price": 100, "discount_rate": 0.0, "expected": 100},
          {"price": 0, "discount_rate": 0.1, "expected": 0},
          {"price": 100, "discount_rate": 1.0, "expected": 0}
        ],
        "category": "parametrized"
      }
    ]
  }
}
```

#### Example 3: Bug Reproduction (Enterprise)

**Request:**
```json
{
  "file_path": "/src/payment.py",
  "function_name": "process_payment",
  "crash_log": "Traceback (most recent call last):\n  File 'payment.py', line 42, in process_payment\n    result = calculate_fee(amount, fee_rate)\nZeroDivisionError: float division by zero",
  "framework": "pytest"
}
```

**Response:**
```json
{
  "tier": "enterprise",
  "tool_id": "generate_unit_tests",
  "duration_ms": 1200,
  "data": {
    "success": true,
    "function_name": "process_payment",
    "test_count": 6,
    "total_test_cases": 12,
    "framework_used": "pytest",
    "max_test_cases_limit": null,
    "data_driven_enabled": true,
    "bug_reproduction_enabled": true,
    "tests": [
      {
        "test_id": 1,
        "name": "test_process_payment_bug_reproduction",
        "code": "def test_process_payment_zero_division():\n    \"\"\"Reproduces: ZeroDivisionError in calculate_fee\"\"\"\n    with pytest.raises(ZeroDivisionError):\n        process_payment(100, fee_rate=0)",
        "input": {"amount": 100, "fee_rate": 0},
        "category": "bug_reproduction"
      }
    ]
  }
}
```

### Performance Considerations

- **Community** (5 tests): 100-400ms
- **Pro** (20 tests): 300-1000ms
- **Enterprise** (unlimited, with bug reproduction): 1000-5000ms

### Upgrade Paths

**Community → Pro:**
- Increase from 5 to 20 test cases
- Data-driven test support (parameterized)
- Edge case detection
- Multiple framework support

**Pro → Enterprise:**
- Unlimited test cases
- Bug reproduction from crash logs
- Custom test templates
- Coverage optimization

---

## simulate_refactor

Simulate applying code changes and detect potential safety issues.

### Overview

`simulate_refactor` analyzes code changes before applying them to detect:
- Structural differences between old and new code
- Behavior preservation analysis
- Type checking for refactorings
- Compliance validation (Enterprise)
- Strict mode analysis for safety

**Use cases:**
- Test a refactoring before committing
- Detect breaking changes in code refactors
- Validate type safety of refactorings
- Check compliance constraints
- Analyze behavioral equivalence

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `original_code` | string | Yes | ✓ | ✓ | ✓ | Original code before refactor |
| `new_code` | string | No | ✓ | ✓ | ✓ | New code after refactor (or use `patch`) |
| `patch` | string | No | ✓ | ✓ | ✓ | Unified diff patch (alternative to `new_code`) |
| `strict_mode` | boolean | No | ✓ | ✓ | ✓ | Strict safety checks (default: false) |

#### Tier-Specific Constraints

**Community:**
- Max file size: 1 MB
- Basic simulation with structural diff only
- Limited analysis depth

**Pro:**
- Max file size: 10 MB
- Advanced simulation with behavior preservation checks
- Type checking
- Increased analysis depth

**Enterprise:**
- Max file size: 100 MB
- All features available
- Compliance validation
- Deep analysis

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "simulate_refactor",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "safe_to_apply": true,
    "original_checksum": "abc123...",
    "new_checksum": "def456...",
    "changes": {
      "lines_added": 5,
      "lines_removed": 3,
      "lines_modified": 2
    },
    "analysis": {
      "structural_changes": [...],
      "behavior_preserved": true,
      "type_safe": true,
      "warnings": []
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Structural diff** | ✓ | ✓ | ✓ |
| **Behavior preservation** | ✗ | ✓ | ✓ |
| **Type checking** | ✗ | ✓ | ✓ |
| **Compliance validation** | ✗ | ✗ | ✓ |
| **Max file size** | 1 MB | 10 MB | 100 MB |

### Error Handling

#### Standard Error Codes

- `invalid_argument` - Invalid code or patch format
- `too_large` - Code exceeds size limit (Community/Pro only)
- `internal_error` - Simulation error

### Example Requests & Responses

#### Example 1: Simple Refactoring (Community)

**Request:**
```json
{
  "original_code": "def get_user_name(user):\n    return user.first_name + ' ' + user.last_name",
  "new_code": "def get_user_name(user):\n    return f'{user.first_name} {user.last_name}'"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "simulate_refactor",
  "duration_ms": 65,
  "data": {
    "success": true,
    "safe_to_apply": true,
    "changes": {
      "lines_added": 1,
      "lines_removed": 1,
      "lines_modified": 1
    },
    "analysis": {
      "structural_changes": [
        "Changed string concatenation to f-string"
      ],
      "warnings": []
    }
  }
}
```

#### Example 2: Type Safety Check (Pro)

**Request:**
```json
{
  "original_code": "def calculate(x, y):\n    return x + y",
  "new_code": "def calculate(x, y):\n    return x * y",
  "strict_mode": true
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "simulate_refactor",
  "duration_ms": 234,
  "data": {
    "success": true,
    "safe_to_apply": false,
    "analysis": {
      "structural_changes": [
        "Operator changed from + to *"
      ],
      "behavior_preserved": false,
      "type_safe": true,
      "warnings": [
        "Behavior change detected: function result semantics differ",
        "In strict mode: behavior change requires explicit review"
      ]
    }
  }
}
```

### Performance Considerations

- **Community**: 50-200ms
- **Pro**: 150-800ms
- **Enterprise**: 300-2000ms

### Upgrade Paths

**Community → Pro:**
- Behavior preservation analysis
- Type checking
- Increased file size support (1 MB → 10 MB)
- Advanced safety checks

**Pro → Enterprise:**
- Compliance validation
- Deeper analysis
- Support for larger files (10 MB → 100 MB)

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "symbolic_execute|generate_unit_tests|simulate_refactor",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": { /* tool-specific */ }
}
```

See `README.md` for complete envelope specification.

## Related Tools

- **`extract_code`** (extraction-tools.md) - Extract code for testing
- **`analyze_code`** (analysis-tools.md) - Analyze code structure
- **`get_call_graph`** (graph-tools.md) - Understand function relationships
