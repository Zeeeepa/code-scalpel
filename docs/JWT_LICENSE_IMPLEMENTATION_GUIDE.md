# JWT License System Implementation Guide

[20251225_FEATURE] v3.3.0 - Complete JWT license validation system

## Overview

The JWT License System is now fully implemented and ready for tool handler integration. This document provides:

1. **What's been implemented**
2. **How to use it in tool handlers**
3. **Testing and validation**
4. **Deployment checklist**

## ✅ Completed Components

### Core JWT System

| Component | Status | File | Tests |
|-----------|--------|------|-------|
| **JWT Validator** | ✅ Complete | `jwt_validator.py` | `test_jwt_validator.py` |
| **JWT Generator** | ✅ Complete | `jwt_generator.py` | Tested via CLI |
| **Licensing Module** | ✅ Updated | `__init__.py` | Integrated tests |
| **Dependencies** | ✅ Added | `requirements.txt`, `pyproject.toml` | PyJWT 2.8.0+, cryptography 41.0.0+ |
| **Licensing README** | ✅ Updated | `src/code_scalpel/licensing/README.md` | Reference docs |
| **Example Code** | ✅ Created | `examples/jwt_license_example.py` | Runnable examples |

### Test Coverage

- **Unit Tests**: 40+ tests for JWT validation, token generation, grace periods
- **Integration Tests**: 25+ tests for tool handler integration, tier capabilities
- **Edge Cases**: Error handling, malformed tokens, signature verification

### Documentation

- **JWT License System**: Complete system documentation with quick start
- **Architectural Decisions**: Rationale for design choices
- **API Reference**: All public functions and classes documented
- **Examples**: 7 comprehensive examples of using the system

## Ready for Tool Handler Integration

The JWT system is production-ready and designed for easy integration into tool handlers.

### Simple 3-Step Pattern

```python
from code_scalpel.licensing import get_current_tier, get_tool_capabilities

def tool_handler(params):
    # 1. Get current tier
    tier = get_current_tier()
    
    # 2. Get capabilities for this tool
    caps = get_tool_capabilities("tool_name", tier)
    
    # 3. Apply limits and add features based on capabilities
    result = process(params)
    if caps.limits.get("max_results"):
        result = result[:caps.limits["max_results"]]
    
    return result
```

## API Summary

### Primary Functions (for Tool Handlers)

```python
# Get current tier (MOST IMPORTANT)
from code_scalpel.licensing import get_current_tier
tier = get_current_tier()  # Returns: "community", "pro", or "enterprise"

# Get tool capabilities for a tier
from code_scalpel.licensing import get_tool_capabilities
caps = get_tool_capabilities("security_scan", tier)
# Returns: {"capabilities": [...], "limits": {...}}

# Get detailed license info (for status display)
from code_scalpel.licensing import get_license_info
info = get_license_info()
```

### For License Management

```python
# Validate JWT tokens
from code_scalpel.licensing import JWTLicenseValidator
validator = JWTLicenseValidator()
result = validator.validate()

# Generate test licenses
from code_scalpel.licensing.jwt_generator import generate_license
token = generate_license(tier="pro", customer_id="test", duration_days=365)
```

## License Installation (Users)

Users can install licenses three ways:

### 1. Environment Variable
```bash
export CODE_SCALPEL_LICENSE_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. License File
```bash
echo "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." > .scalpel-license
```

### 3. User Config
```bash
mkdir -p ~/.config/code-scalpel
echo "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." > ~/.config/code-scalpel/license
```

## License Generation (Admins)

### Generate Pro License
```bash
python -m code_scalpel.licensing.jwt_generator \
    --tier pro \
    --customer "customer_id" \
    --organization "Company Name" \
    --duration 365 \
    --output .scalpel-license
```

### Generate Enterprise License with Seats
```bash
python -m code_scalpel.licensing.jwt_generator \
    --tier enterprise \
    --customer "customer_id" \
    --organization "Company Name" \
    --seats 100 \
    --duration 730
```

### Generate Test License
```bash
python -m code_scalpel.licensing.jwt_generator \
    --tier pro \
    --customer "test" \
    --duration 365 \
    --algorithm HS256 \
    --secret "test_secret_key_12345" \
    --print
```

## Tool Handler Integration Checklist

For each of the 20 tool handlers:

- [ ] Import `get_current_tier` and `get_tool_capabilities`
- [ ] Call `tier = get_current_tier()` at function start
- [ ] Call `caps = get_tool_capabilities(tool_name, tier)`
- [ ] Apply tier-based limits from `caps.limits`
- [ ] Add tier-specific features from `caps.capabilities`
- [ ] Return results without upgrade hints
- [ ] Test with all three tiers (community, pro, enterprise)
- [ ] Verify limits are enforced correctly
- [ ] Verify features are available as expected

## Testing Guide

### Run Unit Tests
```bash
# All JWT tests
pytest tests/licensing/test_jwt_validator.py -v

# JWT integration tests
pytest tests/licensing/test_jwt_integration.py -v

# All licensing tests
pytest tests/licensing/ -v
```

### Manual Testing
```bash
# Run examples
python examples/jwt_license_example.py

# Check tier in Python
python -c "from code_scalpel.licensing import get_current_tier; print(get_current_tier())"

# Check license info
python -c "from code_scalpel.licensing import get_license_info; import json; print(json.dumps(get_license_info(), indent=2))"
```

### Test with Different Tiers

```bash
# Community (default, no license)
python -m code_scalpel.mcp_server

# Pro
export CODE_SCALPEL_LICENSE_KEY="<pro_jwt_token>"
python -m code_scalpel.mcp_server

# Enterprise
export CODE_SCALPEL_LICENSE_KEY="<enterprise_jwt_token>"
python -m code_scalpel.mcp_server
```

## Key Features & Implementation

### ✅ Offline Validation
- No network required for license verification
- Public key verification (RS256) or shared secret (HS256)
- Works in air-gapped environments

### ✅ Tamper-Proof
- Cryptographic signatures prevent modification
- Changing any claim invalidates signature
- Impossible to create fake licenses without private key

### ✅ Grace Period
- 7-day grace period after expiration
- Keeps working during grace period
- Downgrades to Community after grace expires

### ✅ Multiple Load Paths
- Environment variable: `CODE_SCALPEL_LICENSE_KEY`
- License files: `.scalpel-license`, `~/.config/code-scalpel/license`, etc.
- Defaults to Community when no license found

### ✅ Feature Gating
- Community: Basic capabilities, global limits
- Pro: Advanced features, higher limits, additional tools
- Enterprise: All features, no limits, org-level controls

## Deployment Checklist

### Before Release (v3.3.0)

- [x] JWT validator implementation
- [x] JWT generator implementation
- [x] Licensing module integration
- [x] Dependencies added (PyJWT, cryptography)
- [x] Unit tests (40+ tests)
- [x] Integration tests (25+ tests)
- [x] Documentation (README, examples, guide)
- [x] API reference

### For Tool Handler Team (parallel work)

- [ ] Refactor security_scan with manual checks
- [ ] Refactor crawl_project with manual checks
- [ ] Refactor extract_code with manual checks
- [ ] Refactor symbolic_execute with manual checks
- [ ] Complete remaining 16 tool handlers
- [ ] Add capability tests for each tool
- [ ] Verify limits are enforced
- [ ] Test all three tiers for each tool

### For Release v3.3.0

- [ ] All 20 tools using JWT system
- [ ] 60 unit tests for tool tiers (20 tools × 3 tiers)
- [ ] Integration tests passing
- [ ] License generation working
- [ ] User documentation complete
- [ ] Release notes finalized
- [ ] Public key in distribution

## Troubleshooting

### PyJWT Not Installed
```bash
pip install PyJWT>=2.8.0 cryptography>=41.0.0
```

### License Not Found
```bash
# Check environment variable
echo $CODE_SCALPEL_LICENSE_KEY

# Check license file
ls -la .scalpel-license
ls -la ~/.config/code-scalpel/license

# Check tier
python -c "from code_scalpel.licensing import get_current_tier; print(get_current_tier())"
```

### Invalid Signature
Possible causes:
- License was modified
- Using wrong public/secret key
- Token corrupted during copy

Solution: Request new license from Code Scalpel

### Expired License
```python
from code_scalpel.licensing import get_license_info
info = get_license_info()
print(f"Expired: {info['is_expired']}")
print(f"Grace period: {info['is_in_grace_period']}")
print(f"Days: {info['days_until_expiration']}")
```

## Security Notes

### Production Deployment

**Public Key (RS256 - Recommended)**
- Embedded in Code Scalpel package
- Used for signature verification
- Can be rotated via package updates

**Private Key**
- Kept secure by Code Scalpel organization
- Used to sign license tokens
- Rotate annually for security

### Development/Testing (HS256)

**Secret Key**
- Used for both signing and verification
- Set via `CODE_SCALPEL_SECRET_KEY` environment variable
- Only for development/testing
- DO NOT commit to version control

## API Examples

### Example 1: Tool Handler with Tier Checking

```python
from code_scalpel.licensing import get_current_tier, get_tool_capabilities

def analyze_code_handler(code: str, options: dict):
    """Analyze code with tier-based capabilities."""
    
    # Get current tier
    tier = get_current_tier()
    
    # Get capabilities for this tool at this tier
    caps = get_tool_capabilities("analyze_code", tier)
    
    # Basic analysis (all tiers)
    result = {
        "complexity": calculate_cyclomatic(code),
        "functions": extract_functions(code),
        "classes": extract_classes(code),
    }
    
    # Pro+ features
    if "cognitive_complexity" in caps.capabilities:
        result["cognitive_complexity"] = calculate_cognitive(code)
    
    if "code_smell_detection" in caps.capabilities:
        result["code_smells"] = detect_code_smells(code)
    
    # Enterprise features
    if "custom_analysis_rules" in caps.capabilities:
        result["custom_rules"] = apply_custom_rules(code)
    
    return result
```

### Example 2: Check Feature Availability

```python
from code_scalpel.licensing import get_current_tier, has_capability

tier = get_current_tier()

if has_capability("security_scan", "remediation_suggestions", tier):
    # Add remediation suggestions
    pass
else:
    # Basic vulnerabilities only
    pass
```

### Example 3: License Info Display

```python
from code_scalpel.licensing import get_license_info

info = get_license_info()

print(f"Code Scalpel License Info")
print(f"  Tier: {info['tier']}")
print(f"  Valid: {info['is_valid']}")

if info['customer_id']:
    print(f"  Customer: {info['customer_id']}")
    
if info['organization']:
    print(f"  Organization: {info['organization']}")

if info['seats']:
    print(f"  Seats: {info['seats']}")

if info['days_until_expiration']:
    if info['is_expired']:
        print(f"  Expired {abs(info['days_until_expiration'])} days ago")
    else:
        print(f"  Expires in {info['days_until_expiration']} days")

if info['is_in_grace_period']:
    print(f"  Grace period active")
```

## Timeline (v3.3.0)

| Week | Activity | Status |
|------|----------|--------|
| Week 1 (Now) | JWT system implementation | ✅ Complete |
| Week 2 | Tool handler refactoring (4 proof-of-concept tools) | ⏳ In Progress |
| Week 3 | Remaining tool handlers (16 tools) | 📅 Planned |
| Week 4 | Testing, documentation, release | 📅 Planned |

## Next Steps

1. **Tool Handler Team**: Use this guide to refactor 20 tool handlers
2. **Testing Team**: Run full test suite with all three tiers
3. **Docs Team**: Update user-facing documentation with license info
4. **Release Team**: Generate production license keys for customers

## Reference Documentation

- [JWT License System README](src/code_scalpel/licensing/README.md)
- [Architectural Decisions](docs/architecture/ARCHITECTURAL_DECISIONS_v3.3.0.md)
- [All-Tools-Available Summary](docs/architecture/all_tools_available_summary.md)
- [JWT Validator API](src/code_scalpel/licensing/jwt_validator.py)
- [JWT Generator Usage](src/code_scalpel/licensing/jwt_generator.py)
- [Unit Tests](tests/licensing/test_jwt_validator.py)
- [Integration Tests](tests/licensing/test_jwt_integration.py)
- [Examples](examples/jwt_license_example.py)

---

**Status**: ✅ Implementation Complete
**Date**: December 25, 2025
**Version**: v3.3.0
**Ready for**: Tool Handler Integration
