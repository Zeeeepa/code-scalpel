# Testing Framework - Phase 2 Test Adapters

## Overview

Phase 2 implements a comprehensive test adapter framework that makes tier-aware testing easier and more consistent across the Code Scalpel codebase.

## What Are Test Adapters?

Test adapters are helper utilities that allow tests to:
1. **Run tests across multiple tiers** with different expectations
2. **Skip tests for unavailable tiers** automatically
3. **Assert capabilities** are correctly enforced
4. **Inject tier-specific fixtures** automatically
5. **Validate tier-specific behavior** with clear assertions

## Core Components

### 1. TierAdapter Class

The `TierAdapter` is the main entry point for tier-aware testing.

```python
from code_scalpel.testing import TierAdapter

# Create adapter for specific tier
adapter = TierAdapter("pro")

# Check tool availability
if adapter.tool_available("get_file_context"):
    # Tool is available in Pro tier
    print(f"Available tools: {adapter.get_available_tools()}")
else:
    # Tool is locked in this tier
    print(f"Locked tools: {adapter.get_unavailable_tools()}")

# Get tool information
limits = adapter.get_tool_limits("analyze_code")
capabilities = adapter.get_tool_capabilities("analyze_code")

# Assert tool availability
adapter.assert_tool_available("analyze_code")  # Passes
adapter.assert_tool_available("get_file_context")  # Raises for Enterprise
```

### 2. TierAdapterFactory

Create multiple adapters for testing scenarios.

```python
from code_scalpel.testing import TierAdapterFactory

# Create adapters for all tiers
all_adapters = TierAdapterFactory.create_for_all_tiers()

# Create adapters for specific tiers
pro_enterprise = TierAdapterFactory.create_for_tiers("pro", "enterprise")

# Create single adapter
community = TierAdapterFactory.create("community")
```

### 3. Pytest Markers

Mark tests with tier requirements:

```python
import pytest
from code_scalpel.testing import requires_tier, requires_tool, tier_aware

@pytest.mark.requires_tier("pro", "enterprise")
def test_pro_feature():
    """Only runs if Pro or Enterprise tier is available."""
    pass

@pytest.mark.requires_tool("get_file_context")
def test_get_file_context():
    """Only runs if get_file_context tool is available."""
    pass

@pytest.mark.tier_aware
def test_all_tiers(tier_adapter):
    """Runs for all tiers, test handles both available and locked tools."""
    if tier_adapter.tool_available("get_file_context"):
        # Test available features
        pass
    else:
        # Test locked features or graceful degradation
        pass

@pytest.mark.performance
def test_performance():
    """Performance test - may be skipped in CI."""
    pass

@pytest.mark.security
def test_tier_enforcement():
    """Security test - validates tier enforcement."""
    pass
```

### 4. Assertion Helpers

Clear assertions for tier-based testing:

```python
from code_scalpel.testing import (
    assert_tool_available,
    assert_tool_unavailable,
    assert_capability_present,
    assert_limit_value,
    assert_tool_count,
    assert_tier_detected,
)

# Tool availability
assert_tool_available("analyze_code", "pro")
assert_tool_unavailable("get_file_context", "enterprise")

# Capabilities
assert_capability_present("analyze_code", "code_smell_detection", "pro")

# Limits
assert_limit_value("analyze_code", "max_file_size_mb", 1, "community")

# Tool counts
assert_tool_count("pro", 19)  # Pro has 19 tools

# Tier detection
assert_tier_detected(license_path="/path/to/license.jwt", expected_tier="pro")
```

### 5. Pytest Fixtures

Automatic fixture injection for tests:

```python
import pytest

@pytest.fixture
def tier_adapter():
    """Provides TierAdapter for current test."""
    pass

@pytest.fixture
def community_adapter():
    """Provides community tier adapter."""
    pass

@pytest.fixture
def pro_adapter():
    """Provides pro tier adapter."""
    pass

@pytest.fixture
def enterprise_adapter():
    """Provides enterprise tier adapter."""
    pass

@pytest.fixture
def all_adapters():
    """Provides adapters for all tiers."""
    pass

@pytest.fixture
def with_pro_license():
    """Temporarily sets Pro license for test."""
    pass

@pytest.fixture
def with_enterprise_license():
    """Temporarily sets Enterprise license for test."""
    pass

@pytest.fixture
def with_community_tier():
    """Temporarily sets Community tier (no license)."""
    pass

@pytest.fixture
def clear_all_caches():
    """Clears tier and capability caches before/after test."""
    pass
```

## Usage Patterns

### Pattern 1: Single Tier Testing

Test a specific tier's functionality:

```python
def test_pro_tier_smells(pro_adapter):
    """Test Pro tier code smell detection."""
    pro_adapter.assert_tool_available("analyze_code")
    
    # Code to test Pro tier features
    # ...
```

### Pattern 2: Multi-Tier Testing

Test different behavior across tiers:

```python
@pytest.mark.tier_aware
def test_tool_availability(tier_adapter):
    """Test that tool availability matches tier."""
    tool_id = "get_file_context"
    
    if tier_adapter.get_tier() == "pro":
        tier_adapter.assert_tool_available(tool_id)
    else:
        tier_adapter.assert_tool_unavailable(tool_id)
```

### Pattern 3: License Injection

Test with specific licenses:

```python
def test_pro_feature(with_pro_license):
    """Test Pro features with actual Pro license."""
    from code_scalpel.mcp.server import _get_current_tier
    
    # License is now active
    assert _get_current_tier() == "pro"
    
    # Test Pro-specific behavior
    # ...

def test_community_tier(with_community_tier):
    """Test Community tier features."""
    from code_scalpel.mcp.server import _get_current_tier
    
    # No license is active
    assert _get_current_tier() == "community"
    
    # Test Community tier behavior
    # ...
```

### Pattern 4: Capability Assertions

Validate specific capabilities:

```python
def test_analyze_code_capabilities(tier_adapter):
    """Verify analyze_code has expected capabilities."""
    tool_id = "analyze_code"
    tier = tier_adapter.get_tier()
    
    # All tiers have basic AST parsing
    assert_capability_present(tool_id, "basic_ast", tier)
    
    # Only Pro+ has code smell detection
    if tier in ("pro", "enterprise"):
        assert_capability_present(tool_id, "code_smell_detection", tier)
    else:
        # Can't directly assert it's missing since we don't have that capability
        # in all tiers, but we verify the tool is available
        pass
```

### Pattern 5: Limit Validation

Check tool limits:

```python
def test_analyze_code_limits(tier_adapter):
    """Verify analyze_code limits are correct per tier."""
    tool_id = "analyze_code"
    tier = tier_adapter.get_tier()
    
    limits = tier_adapter.get_tool_limits(tool_id)
    
    if tier == "community":
        assert limits["max_file_size_mb"] == 1
    elif tier == "pro":
        assert limits["max_file_size_mb"] == 10
    # Enterprise may have different limits
```

## Tier Architecture

### Community Tier
- **22/22 tools** available
- All basic features enabled
- Limited file sizes
- No advanced features

### Pro Tier
- **19/22 tools** available
- 3 enterprise-specific tools locked:
  - Tier-specific advanced analysis tools
- Higher file size limits than Community
- Advanced capabilities enabled

### Enterprise Tier
- **10/22 tools** available
- Different, more focused toolset
- Highest limits
- Specialized enterprise features

## Test Organization

### Recommended Structure

```
tests/
├── testing/
│   ├── test_adapters.py          # Test adapter framework itself
│   └── conftest.py              # Testing-specific fixtures
│
└── tools/
    ├── tiers/                    # Tier-specific tests
    │   ├── conftest.py          # Tier fixtures
    │   └── test_*_tiers.py      # Per-tool tier tests
    │
    └── analyze_code/
        ├── test_community_tier.py  # Community-only tests
        ├── test_pro_tier.py       # Pro-only tests
        └── test_enterprise_tier.py # Enterprise-only tests
```

## Best Practices

### 1. Use Adapters for Clarity

❌ **Don't:**
```python
def test_tool(monkeypatch):
    monkeypatch.setattr(helpers, "get_current_tier_from_license", lambda: "pro")
    # Hard to understand what tier is being tested
```

✅ **Do:**
```python
def test_tool(pro_adapter):
    pro_adapter.assert_tool_available("analyze_code")
    # Clear what tier and what we're validating
```

### 2. Mark Tier-Aware Tests

✅ **Do:**
```python
@pytest.mark.tier_aware
def test_multi_tier(tier_adapter):
    if tier_adapter.tool_available("get_file_context"):
        # Test available path
    else:
        # Test locked path
```

### 3. Clear Assertions

❌ **Don't:**
```python
def test_tool_available(pro_adapter):
    available = pro_adapter.get_available_tools()
    assert "analyze_code" in available
```

✅ **Do:**
```python
def test_tool_available(pro_adapter):
    pro_adapter.assert_tool_available("analyze_code")
    # Clearer intent and better error messages
```

### 4. Handle License Absence Gracefully

✅ **Do:**
```python
def test_pro_feature(with_pro_license):
    # License is required for this test
    # If not available, test is skipped
    pass
```

### 5. Use Type Hints

✅ **Do:**
```python
from code_scalpel.testing import TierAdapter

def test_something(tier_adapter: TierAdapter) -> None:
    if tier_adapter.tool_available("tool_id"):
        pass
```

## Integration with CI/CD

### GitHub Actions Integration

Tests are automatically:
- Injected with GitHub Secrets licenses
- Run with all available tiers
- Skipped for unavailable tiers
- Reported with tier information

### Test Skipping

Tests automatically skip if:
- Required tier not available (via license)
- Required tool not available in current tier
- Required capability not present

### CI/CD Example

```yaml
# In .github/workflows/ci.yml
- name: Setup test licenses for tier testing
  run: |
    mkdir -p tests/licenses
    echo "${{ secrets.TEST_PRO_LICENSE_JWT }}" > tests/licenses/code_scalpel_license_pro.jwt
    echo "${{ secrets.TEST_ENTERPRISE_LICENSE_JWT }}" > tests/licenses/code_scalpel_license_enterprise.jwt

- name: Run tests with tier adapters
  run: pytest tests/tools/tiers/ -v
  # Tests automatically use injected licenses
```

## Troubleshooting

### License Not Found

If you see "License not available" errors:

1. **Local Development:**
   ```bash
   # Place test license in tests/licenses/
   cp your_license.jwt tests/licenses/code_scalpel_license_pro_20260101_190345.jwt
   ```

2. **CI/CD:**
   - Verify GitHub Secrets are configured
   - Check secret names match in `.github/workflows/ci.yml`
   - Ensure CI writes to `tests/licenses/`

### Test Skipped Unexpectedly

If test skips but should run:

1. Check that tool is available in current tier:
   ```python
   def test_debug(tier_adapter):
       print(f"Available: {tier_adapter.get_available_tools()}")
   ```

2. Verify test markers are correct:
   ```python
   @pytest.mark.requires_tool("tool_id")  # Exact tool ID
   def test_something():
       pass
   ```

### Cache Issues

If tests behave inconsistently:

1. Use `clear_all_caches` fixture
2. Call `reload_limits_cache()` in test setup
3. Verify test order independence

## Migration Guide

### From Old Pattern to Adapters

#### Before (Manual Mocking)

```python
def test_pro_feature(monkeypatch):
    monkeypatch.setattr(
        helpers, "get_current_tier_from_license", lambda: "pro"
    )
    caps = get_tool_capabilities("analyze_code", "pro")
    # Manual capability checking
```

#### After (Test Adapters)

```python
def test_pro_feature(pro_adapter):
    pro_adapter.assert_tool_available("analyze_code")
    # Clear intent, automatic validation
```

## See Also

- `src/code_scalpel/testing/adapters/tier_adapter.py` - TierAdapter implementation
- `src/code_scalpel/testing/assertions.py` - Assertion helpers
- `src/code_scalpel/testing/markers.py` - Pytest markers
- `src/code_scalpel/testing/fixtures.py` - Pytest fixtures
- `docs/GITHUB_SECRETS.md` - License setup for CI/CD
- `docs/CAPABILITIES.md` - Capability reference
