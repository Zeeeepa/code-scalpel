# Test Suite Component Breakdown - v3.3.0

**Purpose**: Organize the full test suite into isolated, independently runnable components  
**Created**: January 1, 2026  
**Scope**: Community, Pro, and Enterprise tier testing  

---

## Quick Navigation

| Component | Duration | Commands | Tests | Dependencies |
|-----------|----------|----------|-------|--------------|
| [1. Unit Tests](#1-unit-tests) | 2-3 min | `pytest tests/unit/` | ~800 | None |
| [2. Integration Tests](#2-integration-tests) | 3-4 min | `pytest tests/integration/` | ~400 | Unit tests |
| [3. MCP Tools Contracts](#3-mcp-tools-contracts) | 5-7 min | `pytest tests/mcp_tool_verification/` | ~132 | Integration |
| [4. Security Tests](#4-security-tests) | 3-5 min | `pytest tests/security/` | ~300 | Unit tests |
| [5. Tier System Tests](#5-tier-system-tests) | 2-3 min | `pytest tests/tier_validation/` | ~200 | Unit tests |
| [6. Code Quality Checks](#6-code-quality-checks) | 2-3 min | Ruff, Black, Pyright | ~50 | None |
| [7. Documentation Tests](#7-documentation-tests) | 1-2 min | `pytest tests/docs/` | ~50 | None |
| [8. End-to-End Tests](#8-end-to-end-tests) | 5-10 min | Example scripts | ~20 | All components |
| **FULL SUITE** | **23-37 min** | All commands | **~1,952** | Sequential |

---

## 1. Unit Tests

**Purpose**: Test individual functions, classes, and modules in isolation  
**Duration**: 2-3 minutes  
**Scope**: Pure logic without external dependencies  

### 1.1 Core Module Tests

```bash
# Analyzer components
pytest tests/unit/code_scalpel/mcp/ -v --tb=short
pytest tests/unit/code_scalpel/analyzer/ -v --tb=short
pytest tests/unit/code_scalpel/refactor/ -v --tb=short
pytest tests/unit/code_scalpel/security_analyzers/ -v --tb=short
pytest tests/unit/code_scalpel/surgery/ -v --tb=short
```

### 1.2 Utility & Helper Tests

```bash
# Cache and storage
pytest tests/unit/code_scalpel/cache/ -v --tb=short

# Utilities
pytest tests/unit/code_scalpel/utils/ -v --tb=short

# Language-specific parsers
pytest tests/unit/code_scalpel/language_processors/ -v --tb=short
```

### 1.3 Type System Tests

```bash
# Type checking and inference
pytest tests/unit/code_scalpel/type_system/ -v --tb=short

# TypedDict validation
pytest tests/unit/code_scalpel/schema_validation/ -v --tb=short
```

### 1.4 Single Command - All Unit Tests

```bash
# Run ALL unit tests together
pytest tests/unit/ -v --tb=short \
  --cov=src/code_scalpel \
  --cov-report=term-missing:skip-covered \
  --durations=10

# Expected: ~800 tests passing in 2-3 minutes
# Pass threshold: ≥ 99% (≤ 8 failures acceptable)
```

**Expected Output**:
```
collected 800 items

tests/unit/code_scalpel/mcp/test_server.py .......... [ 10%]
tests/unit/code_scalpel/analyzer/test_*.py ......... [ 30%]
tests/unit/code_scalpel/refactor/test_*.py ........ [ 50%]
tests/unit/code_scalpel/security_analyzers/test_*.py .. [ 70%]
tests/unit/code_scalpel/surgery/test_*.py .......... [ 90%]
tests/unit/code_scalpel/cache/test_*.py ........... [100%]

======================== 800 passed in 2m45s ========================
```

---

## 2. Integration Tests

**Purpose**: Test components working together  
**Duration**: 3-4 minutes  
**Scope**: File I/O, module interactions, workflow sequences  
**Depends on**: Unit tests passing

### 2.1 Analyzer Integration

```bash
# End-to-end analysis workflows
pytest tests/integration/test_analyze_code_workflow.py -v --tb=short
pytest tests/integration/test_extract_code_workflow.py -v --tb=short
pytest tests/integration/test_update_symbol_workflow.py -v --tb=short
```

### 2.2 File System & Cache Integration

```bash
# File operations with caching
pytest tests/integration/test_file_operations.py -v --tb=short
pytest tests/integration/test_cache_integration.py -v --tb=short
```

### 2.3 Cross-Module Integration

```bash
# Security analysis integration
pytest tests/integration/test_security_analysis_workflow.py -v --tb=short

# Type checking integration
pytest tests/integration/test_type_checking_workflow.py -v --tb=short

# Refactoring workflows
pytest tests/integration/test_refactoring_workflow.py -v --tb=short
```

### 2.4 Single Command - All Integration Tests

```bash
# Run ALL integration tests
pytest tests/integration/ -v --tb=short \
  --cov=src/code_scalpel \
  --cov-report=term-missing:skip-covered

# Expected: ~400 tests passing in 3-4 minutes
# Pass threshold: ≥ 98%
```

---

## 3. MCP Tools Contracts

**Purpose**: Validate MCP protocol compliance across all 22 tools × 2 transports × 3 tiers = **132 scenarios**  
**Duration**: 5-7 minutes  
**Scope**: stdio and HTTP/SSE transports, all tier levels  
**Depends on**: Integration tests passing

### 3.1 Standard Input/Output (stdio) Transport

```bash
# Community tier (all tools enabled)
CODE_SCALPEL_TIER=community \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_stdio.py \
  -v --tb=short --timeout=30

# Pro tier (additional capabilities)
CODE_SCALPEL_TIER=pro \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_stdio.py \
  -v --tb=short --timeout=30

# Enterprise tier (full feature set)
CODE_SCALPEL_TIER=enterprise \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_stdio.py \
  -v --tb=short --timeout=30
```

### 3.2 HTTP/Server-Sent Events (SSE) Transport

```bash
# Community tier via HTTP
CODE_SCALPEL_TIER=community \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_http.py \
  -v --tb=short --timeout=30

# Pro tier via HTTP
CODE_SCALPEL_TIER=pro \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_http.py \
  -v --tb=short --timeout=30

# Enterprise tier via HTTP
CODE_SCALPEL_TIER=enterprise \
pytest tests/mcp_tool_verification/test_mcp_tools_contracts_http.py \
  -v --tb=short --timeout=30
```

### 3.3 Individual Tool Verification

```bash
# Test a specific tool across all tiers
pytest tests/mcp_tool_verification/ \
  -k "analyze_code" \
  -v --tb=short

# Test specific transport
pytest tests/mcp_tool_verification/ \
  -k "stdio" \
  -v --tb=short

# Test specific tier
pytest tests/mcp_tool_verification/ \
  -k "community" \
  -v --tb=short
```

### 3.4 Single Command - All MCP Contracts

```bash
# Run ALL MCP contract tests (22 tools × 2 transports × 3 tiers)
# WARNING: This takes 5-7 minutes and requires multiple server starts
CODE_SCALPEL_RUN_MCP_CONTRACT=1 \
pytest tests/mcp_tool_verification/ \
  -v --tb=short --timeout=30 \
  --durations=10

# Expected: ~132 scenario tests
# Pass threshold: 100% (all scenarios must pass)
```

**22 Tools Tested**:
1. `analyze_code` - Code structure analysis
2. `extract_code` - Surgical code extraction
3. `update_symbol` - Safe code modification
4. `security_scan` - Vulnerability detection
5. `symbolic_execute` - Execution path analysis
6. `generate_unit_tests` - Test generation
7. `simulate_refactor` - Safety verification
8. `crawl_project` - Project analysis
9. `get_graph_neighborhood` - Graph analysis
10. `get_symbol_references` - Reference tracking
11. `get_file_context` - File overview
12. `get_call_graph` - Call hierarchy
13. `code_policy_check` - Policy compliance
14. `unified_sink_detect` - Sink detection
15. `type_evaporation_scan` - Type system scan
16. `get_project_map` - Project structure
17. `verify_policy_integrity` - Policy verification
18. `cross_file_security_scan` - Cross-file analysis
19. `rename_symbol` - Symbol renaming
20. `get_graph_neighborhood` (Pro) - Enhanced graph
21. `type_evaporation_scan` (Pro) - Pro features
22. Plus 10+ tier-specific variants

---

## 4. Security Tests

**Purpose**: Validate security controls, attack vectors, and integrity checks  
**Duration**: 3-5 minutes  
**Scope**: JWT forgery, cache poisoning, privilege escalation, policy integrity  
**Depends on**: Unit tests passing

### 4.1 Authentication & Authorization

```bash
# JWT signature validation
pytest tests/security/test_jwt_signature_forgery.py -v --tb=short

# JWT expiration handling
pytest tests/security/test_jwt_expiration_bypass.py -v --tb=short

# Algorithm confusion attacks
pytest tests/security/test_jwt_algo_confusion.py -v --tb=short

# Tier escalation attempts
pytest tests/security/test_tier_escalation_env.py -v --tb=short
```

### 4.2 Cache Security

```bash
# Cache poisoning attacks
pytest tests/security/test_cache_poisoning.py -v --tb=short

# Cache TTL bypass
pytest tests/security/test_cache_ttl_bypass.py -v --tb=short

# Cache collision attacks
pytest tests/security/test_cache_collision.py -v --tb=short
```

### 4.3 Policy & Manifest Integrity

```bash
# Manifest signature verification
pytest tests/security/test_manifest_signature.py -v --tb=short

# Policy hash mismatch detection
pytest tests/security/test_policy_hash_mismatch.py -v --tb=short

# Policy mutation detection
pytest tests/security/test_policy_mutation.py -v --tb=short
```

### 4.4 Input Validation & Injection

```bash
# Command injection prevention
pytest tests/security/test_code_injection_prevention.py -v --tb=short

# Path traversal prevention
pytest tests/security/test_path_traversal.py -v --tb=short

# XML/YAML parsing safety
pytest tests/security/test_safe_parsing.py -v --tb=short
```

### 4.5 Single Command - All Security Tests

```bash
# Run ALL security tests
pytest tests/security/ -v --tb=short \
  -m security \
  --durations=10

# Expected: ~300 tests
# Pass threshold: 100% (security failures are critical)
```

---

## 5. Tier System Tests

**Purpose**: Validate Community, Pro, and Enterprise tier separation and capabilities  
**Duration**: 2-3 minutes  
**Scope**: Tier detection, feature gating, license validation  
**Depends on**: Unit tests passing

### 5.1 Community Tier Tests

```bash
# Verify Community tier limits (basic features only)
CODE_SCALPEL_TIER=community \
pytest tests/tier_validation/test_community_tier.py -v --tb=short

# Verify Pro features are disabled
CODE_SCALPEL_TIER=community \
pytest tests/tier_validation/test_pro_features_disabled.py -v --tb=short

# Verify Enterprise features are disabled
CODE_SCALPEL_TIER=community \
pytest tests/tier_validation/test_enterprise_features_disabled.py -v --tb=short
```

### 5.2 Pro Tier Tests

```bash
# Verify Pro tier capabilities
CODE_SCALPEL_TIER=pro \
pytest tests/tier_validation/test_pro_tier.py -v --tb=short

# Verify Pro feature enhancements
CODE_SCALPEL_TIER=pro \
pytest tests/tier_validation/test_pro_enhancements.py -v --tb=short
```

### 5.3 Enterprise Tier Tests

```bash
# Verify Enterprise tier capabilities
CODE_SCALPEL_TIER=enterprise \
pytest tests/tier_validation/test_enterprise_tier.py -v --tb=short

# Verify compliance features
CODE_SCALPEL_TIER=enterprise \
pytest tests/tier_validation/test_compliance_features.py -v --tb=short
```

### 5.4 License & Authentication Tests

```bash
# JWT validation
pytest tests/tier_validation/test_jwt_validation.py -v --tb=short

# License revalidation
pytest tests/tier_validation/test_license_revalidation.py -v --tb=short

# Tier environment variable detection
pytest tests/tier_validation/test_tier_detection.py -v --tb=short
```

### 5.5 Single Command - All Tier Tests

```bash
# Run ALL tier validation tests
pytest tests/tier_validation/ -v --tb=short \
  --durations=10

# Expected: ~200 tests across all tier levels
# Pass threshold: ≥ 99%
```

---

## 6. Code Quality Checks

**Purpose**: Validate style, type safety, and static analysis  
**Duration**: 2-3 minutes  
**Scope**: Linting, formatting, type checking, complexity  
**Depends on**: None (can run in parallel)

### 6.1 Linting with Ruff

```bash
# Check all Python files
ruff check src/ tests/ --output-format=json > /tmp/ruff_report.json

# Show violations
ruff check src/ tests/ --show-source

# Auto-fix violations (safe)
ruff check src/ tests/ --fix
```

**Expected**: ≤ 50 violations (GO threshold)

### 6.2 Code Formatting with Black

```bash
# Check formatting compliance
black --check src/ tests/

# Report differences
black --diff src/ tests/

# Auto-format
black src/ tests/
```

**Expected**: 100% compliant (all files formatted)

### 6.3 Import Sorting with isort

```bash
# Check import organization
isort --check-only --diff src/ tests/

# Sort imports
isort src/ tests/
```

**Expected**: All imports properly organized

### 6.4 Type Checking with Pyright

```bash
# Full type check (basic mode)
pyright src/ --outputjson > /tmp/pyright_report.json

# Show detailed diagnostics
pyright src/ --verbose

# Type coverage analysis
pyright src/ --statistics
```

**Expected**: 
- 0 errors, 0 warnings (P0 requirement)
- ≥ 85% type coverage (P1 requirement) → **Actual: 95.6% ✅**

### 6.5 Complexity Analysis

```bash
# McCabe cyclomatic complexity (C901)
ruff check --select C901 src/

# Function length violations (PLR0915)
ruff check --select PLR0915 src/

# Too many arguments (PLR0913)
ruff check --select PLR0913 src/

# Too many branches (PLR0912)
ruff check --select PLR0912 src/
```

**Expected**: See thresholds in main checklist

### 6.6 Single Command - All Code Quality

```bash
# Run all checks sequentially
echo "=== LINTING ===" && \
ruff check src/ tests/ && \

echo "=== FORMATTING ===" && \
black --check src/ tests/ && \

echo "=== IMPORTS ===" && \
isort --check-only src/ tests/ && \

echo "=== TYPE CHECKING ===" && \
pyright src/ && \

echo "✅ All code quality checks passed"
```

---

## 7. Documentation Tests

**Purpose**: Validate documentation accuracy, examples, and links  
**Duration**: 1-2 minutes  
**Scope**: API docs, examples, broken links, README accuracy  
**Depends on**: None (can run in parallel)

### 7.1 API Documentation Tests

```bash
# Verify docstrings in public APIs
pytest tests/docs/test_api_documentation.py -v --tb=short

# Test docstring examples
pytest tests/docs/test_docstring_examples.py -v --tb=short
```

### 7.2 README & Guide Tests

```bash
# Verify README accuracy
pytest tests/docs/test_readme_accuracy.py -v --tb=short

# Test setup instructions
pytest tests/docs/test_setup_instructions.py -v --tb=short

# Test quick start examples
pytest tests/docs/test_quickstart_examples.py -v --tb=short
```

### 7.3 Link Validation

```bash
# Check for broken links in markdown
pytest tests/docs/test_broken_links.py -v --tb=short

# Verify cross-document references
pytest tests/docs/test_cross_references.py -v --tb=short
```

### 7.4 Claims Verification

```bash
# Validate documentation claims vs actual code
python scripts/validate_documentation_claims.py \
  --report /tmp/docs_evidence.json

# Expected: ≥ 95% claim accuracy
```

### 7.5 Single Command - All Documentation Tests

```bash
# Run all documentation tests
pytest tests/docs/ -v --tb=short

# Expected: ~50 tests
# Pass threshold: ≥ 95%
```

---

## 8. End-to-End Tests

**Purpose**: Test complete workflows from CLI and as library  
**Duration**: 5-10 minutes  
**Scope**: Full feature workflows, example scripts, real-world scenarios  
**Depends on**: All other test suites passing

### 8.1 CLI Integration Tests

```bash
# Test command-line interface
pytest tests/e2e/test_cli_integration.py -v --tb=short

# Test help commands
pytest tests/e2e/test_cli_help.py -v --tb=short

# Test error handling
pytest tests/e2e/test_cli_error_handling.py -v --tb=short
```

### 8.2 Library Integration Tests

```bash
# Test Python API usage
pytest tests/e2e/test_python_api.py -v --tb=short

# Test MCP server mode
pytest tests/e2e/test_mcp_server_mode.py -v --tb=short
```

### 8.3 Real-World Example Tests

```bash
# Run all example scripts
bash scripts/run_all_examples.sh

# Expected: All examples complete without errors
# Time: 2-5 minutes
```

### 8.4 Version Consistency Tests

```bash
# Verify version consistency across all files
python scripts/verify_version_consistency.py --version 3.3.0

# Expected: All version strings match 3.3.0
```

### 8.5 Distribution Testing

```bash
# Fresh venv install test
python -m venv /tmp/test_venv
/tmp/test_venv/bin/pip install dist/*.whl
/tmp/test_venv/bin/code-scalpel --help

# Expected: Tool runs successfully in fresh environment
```

### 8.6 Single Command - All E2E Tests

```bash
# Run all end-to-end tests
pytest tests/e2e/ -v --tb=short \
  --timeout=60 \
  --durations=10

# Expected: ~20 tests
# Pass threshold: ≥ 95%
```

---

## Test Execution Plans

### Plan A: Quick Validation (7-10 minutes)

```bash
#!/bin/bash
set -e

echo "=== QUICK VALIDATION SUITE ==="
echo "Time: ~7-10 minutes"
echo ""

echo "[1/3] Unit + Integration Tests..."
pytest tests/unit/ tests/integration/ -v --tb=short -q

echo "[2/3] Code Quality Checks..."
ruff check src/ tests/ --quiet && \
black --check src/ tests/ --quiet && \
pyright src/ --quiet

echo "[3/3] Tier System Verification..."
pytest tests/tier_validation/ -v --tb=short -q

echo ""
echo "✅ Quick validation passed!"
```

### Plan B: Standard Release (20-25 minutes)

```bash
#!/bin/bash
set -e

echo "=== STANDARD RELEASE VALIDATION ==="
echo "Time: ~20-25 minutes"
echo ""

echo "[1/5] Unit Tests..."
pytest tests/unit/ -v --tb=short -q

echo "[2/5] Integration Tests..."
pytest tests/integration/ -v --tb=short -q

echo "[3/5] Code Quality..."
ruff check src/ tests/ && \
black --check src/ tests/ && \
pyright src/

echo "[4/5] Security Tests..."
pytest tests/security/ -v --tb=short -q

echo "[5/5] Tier Validation..."
pytest tests/tier_validation/ -v --tb=short -q

echo ""
echo "✅ Standard validation passed!"
```

### Plan C: Full Release (35-45 minutes)

```bash
#!/bin/bash
set -e

echo "=== FULL RELEASE VALIDATION ==="
echo "Time: ~35-45 minutes (including MCP contract tests)"
echo ""

echo "[1/7] Unit Tests..."
pytest tests/unit/ -v --tb=short -q

echo "[2/7] Integration Tests..."
pytest tests/integration/ -v --tb=short -q

echo "[3/7] Code Quality..."
ruff check src/ tests/ && \
black --check src/ tests/ && \
pyright src/

echo "[4/7] Security Tests..."
pytest tests/security/ -v --tb=short -q

echo "[5/7] Tier Validation..."
pytest tests/tier_validation/ -v --tb=short -q

echo "[6/7] MCP Tools Contracts (22 tools × 2 transports × 3 tiers)..."
CODE_SCALPEL_RUN_MCP_CONTRACT=1 \
pytest tests/mcp_tool_verification/ -v --tb=short -q

echo "[7/7] End-to-End Tests..."
pytest tests/e2e/ -v --tb=short -q

echo ""
echo "✅ Full validation passed!"
```

### Plan D: Continuous Integration (30 minutes)

```bash
#!/bin/bash
set -e

echo "=== CI/CD VALIDATION PIPELINE ==="
echo "Time: ~30 minutes"
echo ""

# Parallel execution where possible
echo "[PARALLEL] Code quality checks..."
(
  ruff check src/ tests/ --output-format=json > /tmp/ruff.json &
  black --check src/ tests/ > /tmp/black.txt &
  isort --check-only src/ tests/ > /tmp/isort.txt &
  wait
)

echo "[PARALLEL] Type checking..."
pyright src/ --outputjson > /tmp/pyright.json

echo "[SEQUENTIAL] Unit tests..."
pytest tests/unit/ -v --tb=short -q

echo "[SEQUENTIAL] Integration tests..."
pytest tests/integration/ -v --tb=short -q

echo "[SEQUENTIAL] Security tests..."
pytest tests/security/ -v --tb=short -q

echo "[SEQUENTIAL] Tier validation..."
pytest tests/tier_validation/ -v --tb=short -q

echo ""
echo "✅ CI/CD pipeline passed!"
```

---

## Debugging & Troubleshooting

### Single Test Execution

```bash
# Run one specific test
pytest tests/unit/test_file.py::TestClass::test_method -vv

# Show print output
pytest tests/unit/test_file.py -vv -s

# Drop into pdb on failure
pytest tests/unit/test_file.py --pdb

# Show local variables on failure
pytest tests/unit/test_file.py -l
```

### Test Filtering

```bash
# Run tests by keyword
pytest -k "analyze_code" -v

# Run tests by marker
pytest -m "security" -v

# Run tests by file pattern
pytest tests/unit/code_scalpel/*/test_*.py -v

# Run all except slow tests
pytest -m "not slow" -v
```

### Coverage Analysis

```bash
# Generate HTML coverage report
pytest tests/ \
  --cov=src/code_scalpel \
  --cov-report=html \
  --cov-report=term-missing

# Show files with low coverage
coverage report --skip-covered --sort=Cover
```

### Performance Analysis

```bash
# Show slowest 10 tests
pytest tests/ --durations=10

# Profile test execution
pytest tests/ --profile

# Measure specific test time
time pytest tests/unit/test_file.py
```

---

## Success Criteria

### Unit Tests
- ✅ ≥ 99% pass rate (≤ 8 failures of ~800)
- ✅ ≥ 90% code coverage
- ✅ All P0 tests passing

### Integration Tests
- ✅ ≥ 98% pass rate
- ✅ No hanging processes
- ✅ Clean file system state after tests

### MCP Contracts
- ✅ 100% of 132 scenarios passing (22 tools × 2 transports × 3 tiers)
- ✅ All stdio tests passing
- ✅ All HTTP/SSE tests passing
- ✅ No timeout errors

### Security Tests
- ✅ 100% pass rate (no failures allowed)
- ✅ All attack vectors detected
- ✅ All privilege escalation attempts blocked

### Tier Validation
- ✅ Community tier features working
- ✅ Pro tier upgrades detected
- ✅ Enterprise tier features available
- ✅ No tier leakage (features not bleeding between tiers)

### Code Quality
- ✅ Ruff: ≤ 50 violations
- ✅ Black: 100% formatted
- ✅ Pyright: 0 errors, 0 warnings
- ✅ Type coverage: ≥ 85% (actual 95.6%)

### Documentation
- ✅ No broken links
- ✅ ≥ 95% claim accuracy
- ✅ Examples runnable

### End-to-End
- ✅ ≥ 95% pass rate
- ✅ All examples complete
- ✅ CLI works correctly
- ✅ Version consistency verified

---

## Recommended Test Execution Schedule

### Pre-Commit (5 min)
1. Unit tests only
2. Quick code quality checks

### Pre-PR (15 min)
1. Unit + Integration tests
2. Code quality checks
3. Tier validation

### Pre-Release (40 min)
1. Full test suite (all components)
2. All code quality checks
3. Security tests
4. MCP contract tests
5. End-to-end tests
6. Documentation validation

### Post-Release (5 min)
1. Smoke tests (quick health check)
2. Version consistency verification
