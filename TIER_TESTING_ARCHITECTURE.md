# Code Scalpel Tier Testing Architecture

## Overview

This document describes the existing tier testing patterns in Code Scalpel and provides a roadmap for implementing comprehensive tier-based testing for MCP tools, particularly the Oracle feature suite.

**Current Status**: Tier testing infrastructure is established for core tools. Oracle tools have basic oracle AI feedback tests but lack tier-specific tests.

---

## Existing Tier Testing Infrastructure

### 1. Unit-Level Tier Tests

#### Location: `tests/tools/analyze_code/test_tiers.py`

**Pattern**: Tests individual tools at each tier (Community, Pro, Enterprise) using real license files.

**Key Components**:
```python
# Fixtures for license setup
@pytest.fixture
def clear_license_env():
    """Cleans up license environment before/after tests"""

@pytest.fixture
def set_pro_license(clear_license_env, monkeypatch):
    """Sets up Pro tier using tests/licenses/code_scalpel_license_pro_*.jwt"""

@pytest.fixture
def set_enterprise_license(clear_license_env, monkeypatch):
    """Sets up Enterprise tier using tests/licenses/code_scalpel_license_enterprise_*.jwt"""
```

**Helper Function**:
```python
def _force_tier_or_license(monkeypatch, tier: str, license_path: Path):
    """
    Uses real license if valid, falls back to forced tier for testing.
    - Validates JWT signature and tier match
    - Sets CODE_SCALPEL_LICENSE_PATH environment variable
    - Falls back to CODE_SCALPEL_TEST_FORCE_TIER if validation fails
    """
```

**Test Structure**:
```python
class TestCommunityTierRealLicense:
    """Community tier tests with no license file (fallback behavior)"""
    def test_community_basic_extraction_no_license(self, clear_license_env):
        # Verify community tier behavior
        assert result.success
        assert len(result.functions) == expected_count

class TestProTierRealLicense:
    """Pro tier tests with valid Pro license"""
    def test_pro_feature_enabled(self, set_pro_license):
        # Verify Pro-specific feature is available
        assert result.has_pro_feature is True

class TestEnterpriseTierRealLicense:
    """Enterprise tier tests with valid Enterprise license"""
    def test_enterprise_feature_enabled(self, set_enterprise_license):
        # Verify Enterprise-specific feature is available
        assert result.has_enterprise_feature is True
```

**Real License Files**: 
- `tests/licenses/code_scalpel_license_pro_*.jwt` (multiple versions for backwards compat)
- `tests/licenses/code_scalpel_license_enterprise_*.jwt`
- `tests/licenses/code_scalpel_license_pro_test_broken.jwt` (for testing error handling)
- `tests/licenses/code_scalpel_license_enterprise_test_broken.jwt`

---

### 2. Enforcement-Level Tier Tests

#### Location: `tests/tools/code_policy_check/test_tier_enforcement.py`

**Pattern**: Tests that tier limits (file counts, rule counts) are actually enforced.

**Fixtures**:
```python
@pytest.fixture
def community_license(monkeypatch, tmp_path):
    """Forces Community tier (no license file)"""

@pytest.fixture
def pro_license(monkeypatch):
    """Uses actual Pro license file from tests/licenses/"""

@pytest.fixture
def enterprise_license(monkeypatch):
    """Uses actual Enterprise license file"""
```

**Test Structure**:
```python
class TestCommunityTierLimits:
    """Community tier enforces 100 file, 50 rule limits"""
    def test_community_file_limit_enforced(self, community_license):
        # Verify limit is enforced
        pass

class TestProTierLimits:
    """Pro tier enforces different limits than Community"""
    def test_pro_file_limit_exceeds_community(self, pro_license):
        # Verify Pro limits > Community limits
        pass

class TestEnterpriseTierLimits:
    """Enterprise tier has highest limits"""
    def test_enterprise_unlimited_files(self, enterprise_license):
        # Verify Enterprise has no practical limit
        pass
```

---

### 3. Integration-Level Tier Tests

#### Location: `scripts/mcp_validate_pro_tier.py` and `scripts/mcp_validate_enterprise_tier.py`

**Pattern**: Full end-to-end tests of all 23 MCP tools at each tier via MCP protocol.

**Key Test Areas**:
```python
# 1. Tool availability
EXPECTED_ALL_TOOLS = [
    "analyze_code", "code_policy_check", "extract_code", ...
]

# 2. Tool invocation (smoke tests)
async def test_all_tools_callable():
    for tool_name in EXPECTED_ALL_TOOLS:
        response = await call_tool(tool_name, sample_args)
        assert response.success or response.error_code in EXPECTED_ERRORS

# 3. Tier-specific features
def test_pro_features_enabled(pro_tier):
    # rename_symbol should succeed (Pro feature)
    # code_policy_check should handle >100 files
    # Other Pro features should be enabled

# 4. Tier limits
def test_pro_limit_exceeded(pro_tier):
    # Verify limits are actually enforced
    # e.g., code_policy_check with 150 files

# 5. Cross-tier feature gating
def test_enterprise_only_features(enterprise_tier):
    # Verify enterprise flags are true
    # Verify enterprise compliance outputs are present
```

**Usage**:
```bash
CODE_SCALPEL_TIER=pro CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt \
  python scripts/mcp_validate_pro_tier.py --verbose

CODE_SCALPEL_TIER=enterprise CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt \
  python scripts/mcp_validate_enterprise_tier.py --verbose
```

---

## Oracle Tool Testing Status

### Current Tests: `tests/tools/oracle/`

#### Files with Tests:
1. **test_oracle_ai_feedback.py** (15 tests, all passing)
   - Feedback on wrong inputs
   - Error messages with suggestions
   - Tool consistency across tools
   - **Missing**: Tier-specific tests (Community, Pro, Enterprise)

2. **test_oracle_pipeline.py** (27 tests, all passing)
   - Tier limits and context lines
   - Pipeline initialization
   - Performance metrics
   - **Has**: Some tier limit tests (basic)

3. **test_spec_generator.py** (25 tests, all passing)
   - Constraint spec generation
   - Markdown generation
   - Tier-specific features
   - **Has**: Some tier tests

4. **test_constraint_analyzer.py** (26 tests, all passing)
   - Graph constraint analysis
   - Circular dependency detection

5. **test_symbol_extractor.py** (9 tests, all passing)
   - Symbol extraction
   - File parsing

**Total Oracle Tests**: 110 passing ✅

---

## Recommended Tier Testing for Oracle Tools

Based on the existing patterns, here's a roadmap for implementing comprehensive tier tests:

### Phase 1: Unit-Level Tier Tests (High Priority)

Create `tests/tools/oracle/test_oracle_tiers.py` following the pattern from `test_tiers.py`:

```python
"""
Tier-based tests for Oracle tools using REAL license files.

Tests:
- write_perfect_code at each tier
- analyze_code tier-specific features
- extract_code tier limits
- rename_symbol Pro/Enterprise availability
- generate_unit_tests tier features
"""

@pytest.fixture
def set_pro_license(clear_license_env, monkeypatch):
    """Setup Pro tier for Oracle tests"""

@pytest.fixture
def set_enterprise_license(clear_license_env, monkeypatch):
    """Setup Enterprise tier for Oracle tests"""

class TestOracleWritePerfectCodeTiers:
    """Test write_perfect_code at each tier"""
    
    def test_community_basic_generation(self, clear_license_env):
        # Community: basic code generation with limited context
        pass
    
    def test_pro_advanced_generation(self, set_pro_license):
        # Pro: larger files, more context lines, architectural analysis
        pass
    
    def test_enterprise_full_analysis(self, set_enterprise_license):
        # Enterprise: enterprise compliance, full graph analysis
        pass

class TestOracleExtractCodeTiers:
    """Test extract_code tier limits"""
    
    def test_community_context_limit(self, clear_license_env):
        # Community: 100 lines of context
        pass
    
    def test_pro_extended_context(self, set_pro_license):
        # Pro: 500 lines of context
        pass
    
    def test_enterprise_unlimited_context(self, set_enterprise_license):
        # Enterprise: unlimited context
        pass

class TestOracleGenerateUnitTestsTiers:
    """Test generate_unit_tests tier availability"""
    
    def test_community_disabled(self, clear_license_env):
        # Community: not available (returns upgrade_required error)
        assert response.error_code == "upgrade_required"
    
    def test_pro_enabled(self, set_pro_license):
        # Pro: available with limits
        assert response.success is True
    
    def test_enterprise_unlimited(self, set_enterprise_license):
        # Enterprise: unlimited generation
        pass
```

### Phase 2: Integration Tests (Medium Priority)

Extend `scripts/mcp_validate_pro_tier.py` to include Oracle-specific checks:

```python
# Add to pro tier validation:
- write_perfect_code generates constraints correctly
- analyze_code applies Pro limits (graph depth, context lines)
- extract_code uses Pro context limits
- rename_symbol succeeds (Pro feature)

# Add to enterprise tier validation:
- Full architectural analysis enabled
- Enterprise compliance checks included
- All constraints generated with enterprise scope
```

### Phase 3: Regression Tests (Low Priority)

Create `tests/tools/oracle/test_oracle_regression.py` for:
- Verifying tier changes don't break functionality
- Cross-tool consistency tests
- Error message consistency across tiers

---

## Testing Environment Variables

### License Configuration

```bash
# Option 1: Use actual license file
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt

# Option 2: Force tier for testing (when license validation fails)
export CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY=1
export CODE_SCALPEL_TEST_FORCE_TIER=1
export CODE_SCALPEL_TIER=pro

# Option 3: Explicit tier without license
export CODE_SCALPEL_TIER=enterprise
```

### Running Tier Tests

```bash
# Run all tier tests
pytest tests/tools/*/test_tiers.py -v

# Run oracle tier tests only
pytest tests/tools/oracle/test_oracle_tiers.py -v

# Run with specific tier
CODE_SCALPEL_TIER=pro pytest tests/tools/oracle/test_oracle_tiers.py -v

# Run integration validation
python scripts/mcp_validate_pro_tier.py --verbose
python scripts/mcp_validate_enterprise_tier.py --verbose
```

---

## Key Principles for Tier Testing

1. **Positive & Negative Tests**
   - Positive: Feature works at appropriate tier
   - Negative: Feature is denied/limited at lower tiers
   - Example: generate_unit_tests succeeds at Pro/Enterprise, fails at Community

2. **Real License Files**
   - Use actual JWT licenses from `tests/licenses/` when possible
   - Fall back to forced tier (`CODE_SCALPEL_TEST_FORCE_TIER`) if validation fails
   - This tests the full licensing pipeline, not just tier logic

3. **Limit Enforcement**
   - Test that tier limits are actually enforced
   - Examples: max files, max rules, context lines, graph depth
   - Verify limits increase with each tier

4. **Feature Gating**
   - Test that tier-specific features are accessible only at appropriate tiers
   - Use `UpgradeRequiredError` or `upgrade_hints` in response
   - Verify error messages guide users to upgrade

5. **Cross-Tool Consistency**
   - All tools should behave consistently at each tier
   - Same tier limits should apply across all analysis tools
   - Same features should require same tier across all tools

---

## Test Coverage Checklist

### Oracle Tools (Current Status)

- [x] write_perfect_code: Basic oracle feedback tests (missing: tier tests)
- [x] analyze_code: Basic oracle feedback tests (missing: tier-specific features)
- [x] extract_code: Basic oracle feedback tests (missing: tier context limits)
- [x] rename_symbol: Basic oracle feedback tests (missing: Pro availability test)
- [x] generate_unit_tests: Not in oracle feedback tests (missing: all tier tests)

### Tier Test Checklist (What to Add)

```
For Each Oracle Tool:
├── Community Tier Tests
│   ├── Basic functionality available
│   ├── Limits enforced (if any)
│   └── Upgrade required for Pro features
├── Pro Tier Tests
│   ├── Advanced features enabled
│   ├── Higher limits applied
│   └── Enterprise features still unavailable
└── Enterprise Tier Tests
    ├── Full features available
    ├── Highest limits applied
    └── Compliance outputs included

Total: ~45 additional tier tests for Oracle tools
```

---

## Resources

### Existing Test Files
- `tests/tools/analyze_code/test_tiers.py` - Reference pattern (135 lines)
- `tests/tools/code_policy_check/test_tier_enforcement.py` - Reference pattern (200+ lines)
- `tests/tools/oracle/test_oracle_pipeline.py` - Existing tier limits (some tests)

### Validation Scripts
- `scripts/mcp_validate_22_tools.py` - Smoke tests for all tools
- `scripts/mcp_validate_pro_tier.py` - Pro tier integration tests (400+ lines)
- `scripts/mcp_validate_enterprise_tier.py` - Enterprise tier integration tests (400+ lines)

### License Files
- `tests/licenses/code_scalpel_license_pro_*.jwt` - Real Pro licenses
- `tests/licenses/code_scalpel_license_enterprise_*.jwt` - Real Enterprise licenses

---

## Next Steps

1. **Immediate** (Recommended):
   - Review existing test patterns in `test_tiers.py` and `test_tier_enforcement.py`
   - Identify which Oracle tools need tier-specific tests most urgently

2. **Short-term** (1-2 weeks):
   - Create `tests/tools/oracle/test_oracle_tiers.py` with Community/Pro/Enterprise tests
   - Update `test_oracle_pipeline.py` to expand tier limit tests
   - Add tier tests to `test_spec_generator.py` for architecture constraints

3. **Medium-term** (1 month):
   - Extend `scripts/mcp_validate_pro_tier.py` with Oracle-specific checks
   - Create comprehensive integration tests
   - Document tier-specific features for each Oracle tool

4. **Long-term** (Ongoing):
   - Monitor tier test coverage in CI/CD pipeline
   - Ensure all new Oracle features include tier tests
   - Review and update tier limits in test suite quarterly

---

## Conclusion

Code Scalpel has a robust tier testing infrastructure established through:
- Unit-level real license tests (`test_tiers.py` pattern)
- Enforcement-level limit tests (`test_tier_enforcement.py` pattern)
- Integration-level validation scripts (`mcp_validate_*.py` pattern)

Oracle tools should follow this same pattern to ensure tier features work correctly and limits are enforced. The recommended first step is creating `tests/tools/oracle/test_oracle_tiers.py` with Community/Pro/Enterprise tests for each tool.

**Current Oracle Test Status**: ✅ 110 tests passing (basic functionality + oracle feedback)
**Recommended Addition**: ~45 tier-specific tests for comprehensive coverage

